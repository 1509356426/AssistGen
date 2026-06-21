from typing import List, Dict, AsyncGenerator, Callable, Optional
from openai import AsyncOpenAI
from app.core.config import settings
import json
from app.core.logger import get_logger
from app.core.database import AsyncSessionLocal
from app.models.conversation import Conversation, DialogueType
from app.models.message import Message
from app.services.redis_semantic_cache import RedisSemanticCache
from app.services.message_utils import sliding_window_messages
import time
import asyncio

logger = get_logger(service="deepseek")

class DeepseekService:
    def __init__(self, model: str = "deepseek-chat"):
        logger.info("Initializing Deepseek Service")
        self.client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )
        # 优先使用配置中的 DEEPSEEK_MODEL，其次使用传入的 model
        self.model = settings.DEEPSEEK_MODEL or model
        # 根据配置决定是否启用语义缓存
        self.cache_enabled = settings.ENABLE_SEMANTIC_CACHE
        if self.cache_enabled:
            self.cache = RedisSemanticCache(prefix="deepseek")
            logger.info("Semantic cache enabled")
        else:
            self.cache = None
            logger.info("Semantic cache disabled")

    async def _stream_cached_response(self, response: str, delay: float = 0.05) -> AsyncGenerator[str, None]:
        """模拟流式返回缓存的响应"""
        # 每次返回4个字符
        chunks = [response[i:i + 4] for i in range(0, len(response), 4)]
        for chunk in chunks:
            await asyncio.sleep(delay)  # 50ms延迟
            yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

    async def generate_stream(
        self,
        messages: List[Dict],
        user_id: Optional[int] = None,
        conversation_id: Optional[int] = None,
        on_complete: Optional[Callable[[int, int, List[Dict], str], None]] = None
    ) -> AsyncGenerator[str, None]:
        """流式生成回复"""
        try:
            # 滑动窗口裁剪：控制 Token 消耗
            trimmed_messages = sliding_window_messages(messages)

            # 根据配置决定是否使用缓存
            if self.cache_enabled:
                # 为每个用户创建独立的缓存实例
                cache = RedisSemanticCache(prefix="deepseek", user_id=user_id)
            else:
                cache = None

            start_time = time.time()

            # 检查缓存（仅当启用时）
            cached_response = None
            if cache:
                cached_response = await cache.lookup(trimmed_messages)

            if cached_response:
                response_time = time.time() - start_time
                logger.info(f"Cache hit! Response time: {response_time:.4f} seconds")

                # 模拟流式返回，因为速率太快了
                async for chunk in self._stream_cached_response(cached_response):
                    yield chunk

                if on_complete and user_id is not None and conversation_id is not None:
                    await on_complete(user_id, conversation_id, messages, cached_response)
                yield "data: [DONE]\n\n"
                return

            # 缓存未命中,调用API
            full_response = []
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=trimmed_messages,
                stream=True
            )

            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response.append(content)
                    yield f"data: {json.dumps(content, ensure_ascii=False)}\n\n"
            
            # 完整响应
            complete_response = "".join(full_response)

            # 更新缓存（仅当启用时）
            if cache:
                await cache.update(trimmed_messages, complete_response)

            response_time = time.time() - start_time
            logger.info(f"Request completed. Response time: {response_time:.4f} seconds")
            
            # 如果有回调，执行回调
            if on_complete and user_id is not None and conversation_id is not None:
                await on_complete(user_id, conversation_id, messages, complete_response)
            yield "data: [DONE]\n\n"
                
        except Exception as e:
            logger.error(f"Error in generate_stream: {str(e)}", exc_info=True)
            error_event = {
                "type": "error",
                "message": f"生成回复时出错: {str(e)}",
            }
            yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

    async def generate(self, messages: List[Dict]) -> str:
        """非流式生成回复"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Generation error: {str(e)}")
            raise
