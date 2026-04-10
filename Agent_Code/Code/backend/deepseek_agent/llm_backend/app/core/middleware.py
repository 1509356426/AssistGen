from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import get_logger
from app.core.metrics import metrics
import time

logger = get_logger(service="http")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        # 计算处理时间
        process_time = time.time() - start_time

        # 记录性能指标
        metrics.record(
            endpoint=request.url.path,
            latency=process_time,
            status_code=response.status_code
        )

        # 记录请求日志
        logger.info(
            f"{request.client.host}:{request.client.port} - "
            f"\"{request.method} {request.url.path} HTTP/{request.scope.get('http_version', '1.1')}\" "
            f"{response.status_code} - {process_time:.2f}s"
        )

        return response
