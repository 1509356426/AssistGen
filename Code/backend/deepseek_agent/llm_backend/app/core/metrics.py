"""
接口性能监控指标收集器

在内存中收集每个接口的：
  - 请求次数
  - 平均响应时间
  - P50/P95/P99 延迟
  - 错误率
  - QPS（每秒请求数）

面试价值：有完整的性能基线数据，证明你知道生产环境需要关注什么指标。
"""

import time
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from app.core.logger import get_logger

logger = get_logger(service="metrics")


@dataclass
class EndpointMetrics:
    """单个接口的指标数据"""
    endpoint: str
    total_requests: int = 0
    total_errors: int = 0
    total_latency: float = 0.0  # 累计延迟（秒）
    latencies: List[float] = field(default_factory=list)  # 最近N条延迟记录
    max_latency: float = 0.0
    min_latency: float = float("inf")
    start_time: float = field(default_factory=time.time)

    # 只保留最近 1000 条延迟记录（防止内存泄漏）
    MAX_LATENCY_RECORDS = 1000

    def record(self, latency: float, is_error: bool = False):
        self.total_requests += 1
        self.total_latency += latency
        if is_error:
            self.total_errors += 1
        self.latencies.append(latency)
        if len(self.latencies) > self.MAX_LATENCY_RECORDS:
            self.latencies = self.latencies[-self.MAX_LATENCY_RECORDS:]
        self.max_latency = max(self.max_latency, latency)
        self.min_latency = min(self.min_latency, latency)

    @property
    def avg_latency(self) -> float:
        return self.total_latency / self.total_requests if self.total_requests > 0 else 0

    @property
    def error_rate(self) -> float:
        return self.total_errors / self.total_requests * 100 if self.total_requests > 0 else 0

    @property
    def qps(self) -> float:
        elapsed = time.time() - self.start_time
        return self.total_requests / elapsed if elapsed > 0 else 0

    def percentile(self, p: float) -> float:
        """计算 P 延迟（如 P50, P95, P99）"""
        if not self.latencies:
            return 0
        sorted_lat = sorted(self.latencies)
        idx = int(len(sorted_lat) * p / 100)
        idx = min(idx, len(sorted_lat) - 1)
        return sorted_lat[idx]

    def to_dict(self) -> Dict:
        return {
            "endpoint": self.endpoint,
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "avg_latency_ms": round(self.avg_latency * 1000, 2),
            "p50_ms": round(self.percentile(50) * 1000, 2),
            "p95_ms": round(self.percentile(95) * 1000, 2),
            "p99_ms": round(self.percentile(99) * 1000, 2),
            "max_latency_ms": round(self.max_latency * 1000, 2),
            "min_latency_ms": round(self.min_latency * 1000, 2) if self.min_latency != float("inf") else 0,
            "error_rate": round(self.error_rate, 2),
            "qps": round(self.qps, 4),
        }


class MetricsCollector:
    """全局指标收集器（线程安全单例）"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._endpoints: Dict[str, EndpointMetrics] = {}
                    cls._instance._endpoint_lock = threading.Lock()
        return cls._instance

    def record(self, endpoint: str, latency: float, status_code: int = 200):
        """记录一次请求"""
        with self._endpoint_lock:
            if endpoint not in self._endpoints:
                self._endpoints[endpoint] = EndpointMetrics(endpoint=endpoint)
            is_error = status_code >= 400
            self._endpoints[endpoint].record(latency, is_error)

    def get_all(self) -> Dict[str, Dict]:
        """获取所有接口的指标"""
        with self._endpoint_lock:
            return {ep: m.to_dict() for ep, m in self._endpoints.items()}

    def get_endpoint(self, endpoint: str) -> Optional[Dict]:
        """获取单个接口的指标"""
        with self._endpoint_lock:
            m = self._endpoints.get(endpoint)
            return m.to_dict() if m else None

    def summary(self) -> str:
        """生成人类可读的摘要"""
        data = self.get_all()
        if not data:
            return "No metrics data yet."

        lines = []
        lines.append(f"{'Endpoint':<30} | {'Requests':>8} | {'Avg(ms)':>8} | {'P50(ms)':>8} | {'P95(ms)':>8} | {'P99(ms)':>8} | {'Errors':>6} | {'QPS':>6}")
        lines.append("-" * 100)

        for ep, m in sorted(data.items(), key=lambda x: x[1]["total_requests"], reverse=True):
            lines.append(
                f"{ep:<30} | {m['total_requests']:>8} | {m['avg_latency_ms']:>8.1f} | "
                f"{m['p50_ms']:>8.1f} | {m['p95_ms']:>8.1f} | {m['p99_ms']:>8.1f} | "
                f"{m['error_rate']:>5.1f}% | {m['qps']:>6.2f}"
            )
        return "\n".join(lines)


# 全局单例
metrics = MetricsCollector()
