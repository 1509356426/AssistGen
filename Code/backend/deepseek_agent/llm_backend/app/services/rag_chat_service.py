import json
import uuid
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List

import graphrag.api as api
from graphrag.callbacks.noop_query_callbacks import NoopQueryCallbacks
from graphrag.config.load_config import load_config
from graphrag.storage.file_pipeline_storage import FilePipelineStorage
from graphrag.utils.storage import load_table_from_storage

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(service="rag_chat")


class RAGChatService:
    """GraphRAG 查询服务。

    IndexingService 负责把用户文件构建成索引，本服务只负责加载索引并查询。
    """

    def __init__(self):
        self.project_dir = self._resolve_project_dir(settings.GRAPHRAG_PROJECT_DIR)
        self.data_dir = Path(self.project_dir) / settings.GRAPHRAG_DATA_DIR
        self.query_type = settings.GRAPHRAG_QUERY_TYPE.lower()
        self.response_type = settings.GRAPHRAG_RESPONSE_TYPE
        self.community_level = settings.GRAPHRAG_COMMUNITY_LEVEL
        self.dynamic_community = settings.GRAPHRAG_DYNAMIC_COMMUNITY
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _resolve_project_dir(self, configured_dir: str) -> Path:
        path = Path(configured_dir)
        if path.is_absolute():
            return path

        candidates = [
            Path.cwd() / path,
            Path(__file__).resolve().parents[2] / path,
            Path(__file__).resolve().parents[3] / path,
        ]

        for candidate in candidates:
            if candidate.exists():
                return candidate

        return candidates[0]

    def _resolve_output_dir(self, index_id: str, user_id: int | None = None) -> Path:
        path = Path(index_id)
        if path.is_absolute() and path.exists():
            return path

        relative_path = Path(index_id)
        candidates = [
            self.data_dir / "output" / relative_path,
            self.data_dir / relative_path,
            Path.cwd() / relative_path,
        ]

        if user_id is not None:
            user_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"user_{user_id}"))
            candidates.insert(0, self.data_dir / "output" / user_uuid)

        for candidate in candidates:
            if candidate.exists():
                return candidate

        raise FileNotFoundError(f"GraphRAG index output directory not found: {index_id}")

    async def _load_data(self, index_id: str, user_id: int | None = None) -> Dict[str, Any]:
        output_dir = self._resolve_output_dir(index_id, user_id)
        cache_key = str(output_dir.resolve())
        if cache_key in self._cache:
            return self._cache[cache_key]

        config = load_config(self.data_dir)
        storage = FilePipelineStorage(root_dir=str(output_dir))

        data: Dict[str, Any] = {
            "config": config,
            "entities": await load_table_from_storage("entities", storage),
            "text_units": await load_table_from_storage("text_units", storage),
            "communities": await load_table_from_storage("communities", storage),
            "community_reports": await load_table_from_storage("community_reports", storage),
            "relationships": await load_table_from_storage("relationships", storage),
        }

        try:
            data["covariates"] = await load_table_from_storage("covariates", storage)
        except Exception:
            data["covariates"] = None

        self._cache[cache_key] = data
        logger.info(f"Loaded GraphRAG index data from {output_dir}")
        return data

    def _last_user_query(self, messages: List[Dict[str, str]]) -> str:
        for message in reversed(messages):
            if message.get("role") == "user" and message.get("content"):
                return message["content"]
        raise ValueError("No user query found in messages")

    async def _query(self, query: str, index_id: str, user_id: int | None = None) -> str:
        data = await self._load_data(index_id, user_id)
        callbacks = [NoopQueryCallbacks()]

        if self.query_type == "global":
            response, _ = await api.global_search(
                config=data["config"],
                entities=data["entities"],
                communities=data["communities"],
                community_reports=data["community_reports"],
                community_level=self.community_level,
                dynamic_community_selection=self.dynamic_community,
                response_type=self.response_type,
                query=query,
                callbacks=callbacks,
            )
        elif self.query_type == "drift":
            response, _ = await api.drift_search(
                config=data["config"],
                entities=data["entities"],
                communities=data["communities"],
                community_reports=data["community_reports"],
                text_units=data["text_units"],
                relationships=data["relationships"],
                community_level=self.community_level,
                response_type=self.response_type,
                query=query,
                callbacks=callbacks,
            )
        elif self.query_type == "basic":
            response, _ = await api.basic_search(
                config=data["config"],
                text_units=data["text_units"],
                query=query,
                callbacks=callbacks,
            )
        else:
            response, _ = await api.local_search(
                config=data["config"],
                entities=data["entities"],
                communities=data["communities"],
                community_reports=data["community_reports"],
                text_units=data["text_units"],
                relationships=data["relationships"],
                covariates=data["covariates"],
                community_level=self.community_level,
                response_type=self.response_type,
                query=query,
                callbacks=callbacks,
            )

        return str(response)

    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        index_id: str,
        user_id: int | None = None,
    ) -> AsyncGenerator[str, None]:
        try:
            query = self._last_user_query(messages)
            response = await self._query(query, index_id, user_id)

            for i in range(0, len(response), 8):
                chunk = response[i:i + 8]
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        except Exception as e:
            logger.error(f"GraphRAG chat failed: {str(e)}", exc_info=True)
            error_msg = json.dumps(f"RAG问答失败: {str(e)}", ensure_ascii=False)
            yield f"data: {error_msg}\n\n"
