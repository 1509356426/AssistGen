from typing import Dict, List, Optional
import redis
import hashlib
import numpy as np
import faiss
import json
import time
import aiohttp
from app.core.config import settings
from app.core.logger import get_logger
import asyncio
from datetime import datetime

logger = get_logger(service="redis_cache")


class RedisSemanticCache:
    """基于语义的 Redis 缓存实现（FAISS 加速检索版）"""

    def __init__(
        self,
        redis_url: str = None,
        model_name: str = None,
        score_threshold: float = None,
        prefix: str = "cache",
        user_id: Optional[int] = None,
        max_cache_size: int = 1000,
        cleanup_interval: int = 3600
    ):
        self.redis = redis.from_url(redis_url or settings.REDIS_URL)
        self.model_name = model_name or settings.OLLAMA_EMBEDDING_MODEL
        self.score_threshold = score_threshold or settings.REDIS_CACHE_THRESHOLD
        self.prefix = f"{prefix}:{user_id}" if user_id else prefix
        self.max_cache_size = max_cache_size
        self.cleanup_interval = cleanup_interval

        # FAISS 索引（内存中，启动时从 Redis 重建）
        self.faiss_index = None
        # FAISS 内部 id → Redis hash_id 的映射
        self.id_to_hash: List[str] = []

        # 启动时从 Redis 重建 FAISS 索引
        self._rebuild_index()

        # 启动自动清理任务
        asyncio.create_task(self._auto_cleanup())

    # ==================== 向量归一化 ====================

    def _normalize(self, vector: np.ndarray) -> np.ndarray:
        """L2 归一化，使内积等价于余弦相似度"""
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm

    # ==================== FAISS 索引管理 ====================

    def _rebuild_index(self):
        """从 Redis 重建 FAISS 索引（启动时 + 清理后调用）"""
        try:
            pattern = f"{self.prefix}:vec:*"
            all_keys = [key.decode("utf-8") for key in self.redis.keys(pattern)]

            if not all_keys:
                self.faiss_index = faiss.IndexFlatIP(1024)  # bge-m3 默认维度
                self.id_to_hash = []
                logger.info("FAISS index rebuilt: empty (0 vectors)")
                return

            vectors = []
            hash_ids = []
            for vec_key in all_keys:
                raw = self.redis.get(vec_key.encode("utf-8"))
                if raw:
                    vec = np.array(json.loads(raw.decode("utf-8")), dtype=np.float32)
                    vec = self._normalize(vec)
                    vectors.append(vec)
                    hash_id = vec_key.split(":")[-1]
                    hash_ids.append(hash_id)

            if vectors:
                dim = vectors[0].shape[0]
                self.faiss_index = faiss.IndexFlatIP(dim)
                matrix = np.stack(vectors).astype(np.float32)
                self.faiss_index.add(matrix)
                self.id_to_hash = hash_ids
                logger.info(f"FAISS index rebuilt: {len(hash_ids)} vectors, dim={dim}")
            else:
                self.faiss_index = faiss.IndexFlatIP(1024)
                self.id_to_hash = []

        except Exception as e:
            logger.error(f"Error rebuilding FAISS index: {str(e)}", exc_info=True)
            # 降级：空索引，不影响主流程
            self.faiss_index = faiss.IndexFlatIP(1024)
            self.id_to_hash = []

    def _add_to_index(self, vector: np.ndarray, hash_id: str):
        """向 FAISS 索引添加单条向量"""
        vec = self._normalize(vector).astype(np.float32).reshape(1, -1)

        # 如果维度不匹配，重建索引
        if self.faiss_index is None or self.faiss_index.d != vec.shape[1]:
            self._rebuild_index()
            return

        self.faiss_index.add(vec)
        self.id_to_hash.append(hash_id)

    # ==================== Embedding ====================

    async def _get_ollama_embedding(self, text: str) -> List[float]:
        """使用 Ollama 生成文本向量"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{settings.OLLAMA_BASE_URL}/api/embed",
                    json={"model": self.model_name, "input": text}
                ) as response:
                    result = await response.json()
                    return result["embeddings"][0]
        except Exception as e:
            logger.error(f"Error getting Ollama embedding: {str(e)}", exc_info=True)
            raise

    async def _get_embedding(self, text: str) -> List[float]:
        """获取文本向量"""
        try:
            embedding = await self._get_ollama_embedding(text)
            if not embedding:
                raise ValueError("Failed to get embedding")
            return embedding
        except Exception as e:
            logger.error(f"Error in get_embedding: {str(e)}", exc_info=True)
            raise

    # ==================== Key 生成 ====================

    def _get_vector_key(self, message: str) -> str:
        message_hash = hashlib.md5(message.encode()).hexdigest()
        return f"{self.prefix}:vec:{message_hash}"

    def _get_response_key(self, message: str) -> str:
        message_hash = hashlib.md5(message.encode()).hexdigest()
        return f"{self.prefix}:resp:{message_hash}"

    def _get_metadata_key(self, message: str) -> str:
        message_hash = hashlib.md5(message.encode()).hexdigest()
        return f"{self.prefix}:meta:{message_hash}"

    def _get_last_user_message(self, messages: List[Dict]) -> str:
        """获取最后一条用户消息"""
        for msg in reversed(messages):
            if msg["role"] == "user":
                return msg["content"]
        return ""

    # ==================== 缓存核心操作 ====================

    async def lookup(self, messages: List[Dict]) -> Optional[str]:
        """查找缓存的响应（FAISS 加速版）"""
        try:
            user_message = self._get_last_user_message(messages)
            if not user_message:
                return None

            # 如果 FAISS 索引为空，直接返回
            if self.faiss_index is None or self.faiss_index.ntotal == 0:
                return None

            current_vector = await self._get_embedding(user_message)
            query_vec = self._normalize(np.array(current_vector, dtype=np.float32)).reshape(1, -1)

            # FAISS 检索 Top-1
            scores, indices = self.faiss_index.search(query_vec, 1)
            best_score = float(scores[0][0])
            best_idx = int(indices[0][0])

            if best_score >= self.score_threshold and best_idx < len(self.id_to_hash):
                hash_id = self.id_to_hash[best_idx]
                resp_key = f"{self.prefix}:resp:{hash_id}"
                cached_response = self.redis.get(resp_key.encode("utf-8"))

                if cached_response:
                    await self._update_metadata(user_message)
                    logger.info(f"Cache hit (FAISS) with similarity: {best_score:.4f}")
                    return cached_response.decode("utf-8")

            return None

        except Exception as e:
            logger.error(f"Error in lookup: {str(e)}", exc_info=True)
            return None

    async def update(self, messages: List[Dict], response: str, expire: int = None):
        """更新缓存"""
        try:
            user_message = self._get_last_user_message(messages)
            if not user_message:
                return

            vector = await self._get_embedding(user_message)

            vec_key = self._get_vector_key(user_message)
            resp_key = self._get_response_key(user_message)
            meta_key = self._get_metadata_key(user_message)

            expire = expire or settings.REDIS_CACHE_EXPIRE

            # 存储到 Redis
            self.redis.set(vec_key, json.dumps(vector), ex=expire)
            self.redis.set(resp_key, response.encode("utf-8"), ex=expire)

            metadata = {
                "created_at": datetime.now().timestamp(),
                "last_access": datetime.now().timestamp(),
                "access_count": 1
            }
            self.redis.set(meta_key, json.dumps(metadata), ex=expire)

            # 同步到 FAISS 索引
            hash_id = hashlib.md5(user_message.encode()).hexdigest()
            self._add_to_index(np.array(vector, dtype=np.float32), hash_id)

            logger.info(f"Cache updated for message: {user_message[:50]}...")

        except Exception as e:
            logger.error(f"Error in update: {str(e)}", exc_info=True)

    # ==================== 元数据与清理 ====================

    async def _update_metadata(self, message: str):
        """更新缓存项的元数据"""
        try:
            meta_key = self._get_metadata_key(message)
            current_meta = self.redis.get(meta_key)
            if current_meta:
                current_meta = json.loads(current_meta.decode("utf-8"))
            else:
                current_meta = {"access_count": 0}

            metadata = {
                "last_access": datetime.now().timestamp(),
                "access_count": current_meta["access_count"] + 1
            }
            self.redis.set(meta_key, json.dumps(metadata), ex=settings.REDIS_CACHE_EXPIRE)
        except Exception as e:
            logger.error(f"Error updating metadata: {str(e)}", exc_info=True)

    async def _auto_cleanup(self):
        """自动清理过期和超量的缓存"""
        while True:
            try:
                pattern = f"{self.prefix}:meta:*"
                all_keys = [key.decode("utf-8") for key in self.redis.keys(pattern)]

                if len(all_keys) > self.max_cache_size:
                    cache_items = []
                    for key in all_keys:
                        metadata = json.loads(self.redis.get(key.encode("utf-8")).decode("utf-8"))
                        cache_items.append((key, metadata.get("last_access", 0)))

                    cache_items.sort(key=lambda x: x[1])

                    items_to_remove = len(all_keys) - self.max_cache_size
                    for key, _ in cache_items[:items_to_remove]:
                        hash_id = key.split(":")[-1]
                        await self._remove_cache_item(hash_id)

                    # 清理后重建 FAISS 索引
                    self._rebuild_index()

                logger.info(f"Cache cleanup completed for prefix {self.prefix}")

            except Exception as e:
                logger.error(f"Error in cache cleanup: {str(e)}", exc_info=True)

            await asyncio.sleep(self.cleanup_interval)

    async def _remove_cache_item(self, hash_id: str):
        """删除一个缓存项的所有相关键"""
        try:
            self.redis.delete(
                f"{self.prefix}:vec:{hash_id}".encode("utf-8"),
                f"{self.prefix}:resp:{hash_id}".encode("utf-8"),
                f"{self.prefix}:meta:{hash_id}".encode("utf-8")
            )
        except Exception as e:
            logger.error(f"Error removing cache item: {str(e)}", exc_info=True)
