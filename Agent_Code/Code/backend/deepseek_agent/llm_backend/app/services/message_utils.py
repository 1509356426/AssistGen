"""
对话历史滑动窗口工具

解决：前端传入全量 messages，对话越长 Token 消耗越大。
策略：
  1. system message 始终保留
  2. 最近 K 轮对话完整保留（滑动窗口）
  3. 超出窗口的早期对话用 LLM 生成摘要（可选）
"""

from typing import List, Dict, Optional
from app.core.logger import get_logger

logger = get_logger(service="message_utils")

# 默认保留最近 10 轮对话（1轮 = 1条user + 1条assistant = 2条消息）
DEFAULT_MAX_ROUNDS = 10

# 单条消息最大字符数（超过则截断）
DEFAULT_MAX_CHARS_PER_MSG = 2000


def truncate_message(content: str, max_chars: int = DEFAULT_MAX_CHARS_PER_MSG) -> str:
    """截断过长的单条消息"""
    if len(content) <= max_chars:
        return content
    return content[:max_chars] + "...(内容已截断)"


def sliding_window_messages(
    messages: List[Dict[str, str]],
    max_rounds: int = DEFAULT_MAX_ROUNDS,
    max_chars_per_msg: int = DEFAULT_MAX_CHARS_PER_MSG,
) -> List[Dict[str, str]]:
    """
    对消息列表做滑动窗口裁剪。

    规则：
      - system 消息始终保留（放在最前面）
      - 保留最近 max_rounds 轮对话
      - 每条消息超过 max_chars_per_msg 时截断

    返回裁剪后的 messages（原始列表不会被修改）
    """
    if not messages:
        return messages

    # 分离 system 消息和对话消息
    system_msgs = []
    dialog_msgs = []

    for msg in messages:
        if msg.get("role") == "system":
            system_msgs.append(msg)
        else:
            dialog_msgs.append(msg)

    # 如果对话轮数没超限，直接返回（只做截断）
    dialog_rounds = _count_rounds(dialog_msgs)
    if dialog_rounds <= max_rounds:
        result = system_msgs + [_truncate(msg, max_chars_per_msg) for msg in dialog_msgs]
        if len(result) < len(messages):
            logger.info(f"Messages truncated: {len(messages)} chars total, some messages trimmed")
        return result

    # 超过窗口：保留最近 max_rounds 轮
    kept = _keep_last_rounds(dialog_msgs, max_rounds)
    result = system_msgs + [_truncate(msg, max_chars_per_msg) for msg in kept]

    original_tokens_est = _estimate_tokens(messages)
    trimmed_tokens_est = _estimate_tokens(result)
    reduction = (1 - trimmed_tokens_est / original_tokens_est) * 100 if original_tokens_est > 0 else 0

    logger.info(
        f"Sliding window applied: {len(messages)} -> {len(result)} messages, "
        f"~{original_tokens_est} -> ~{trimmed_tokens_est} tokens (est. {reduction:.0f}% reduction)"
    )

    return result


def _count_rounds(dialog_msgs: List[Dict]) -> int:
    """计算对话轮数（一个 user 消息算一轮）"""
    return sum(1 for m in dialog_msgs if m.get("role") == "user")


def _keep_last_rounds(dialog_msgs: List[Dict], max_rounds: int) -> List[Dict]:
    """保留最后 N 轮对话"""
    # 从后往前数 user 消息，找到截断点
    user_count = 0
    cut_idx = 0
    for i in range(len(dialog_msgs) - 1, -1, -1):
        if dialog_msgs[i].get("role") == "user":
            user_count += 1
            if user_count == max_rounds:
                cut_idx = i
                break
    return dialog_msgs[cut_idx:]


def _truncate(msg: Dict, max_chars: int) -> Dict:
    """截断单条消息（不修改原始对象）"""
    content = msg.get("content", "")
    if len(content) <= max_chars:
        return msg
    return {**msg, "content": truncate_message(content, max_chars)}


def _estimate_tokens(messages: List[Dict]) -> int:
    """粗略估算 Token 数（中文约 1.5 token/字，英文约 0.75 token/word）"""
    total_chars = sum(len(m.get("content", "")) for m in messages)
    return int(total_chars * 1.5)
