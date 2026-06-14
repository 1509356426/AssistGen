"""
Sliding Window Performance Benchmark

Measures Token reduction from applying sliding window to conversation history.
Run: python tests/test_sliding_window.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.message_utils import sliding_window_messages, _estimate_tokens


def build_conversation(total_rounds: int, chars_per_msg: int = 200) -> list:
    """Build a conversation with N rounds of user+assistant messages."""
    messages = [{"role": "system", "content": "You are a helpful e-commerce assistant."}]

    for i in range(1, total_rounds + 1):
        user_text = f"第{i}轮对话：用户提问关于手机价格、功能和售后的问题，" + "请详细说明。" * (chars_per_msg // 30)
        messages.append({"role": "user", "content": user_text})

        assistant_text = f"第{i}轮回复：关于您的问题，" + "这款手机性能非常好，搭载了最新的处理器。" * (chars_per_msg // 25)
        messages.append({"role": "assistant", "content": assistant_text})

    return messages


def bench_sliding_window():
    print("=" * 75)
    print("  Sliding Window Token Reduction Benchmark")
    print("=" * 75)

    test_cases = [
        # (total_rounds, window_size, chars_per_msg)
        (20, 10, 200),
        (50, 10, 200),
        (100, 10, 200),
        (20, 10, 1000),
        (50, 10, 1000),
        (100, 10, 1000),
    ]

    print(f"\n{'Rounds':>8} | {'Window':>8} | {'MsgLen':>8} | {'Before(tokens)':>15} | {'After(tokens)':>15} | {'Reduction':>10} | {'Msgs':>10}")
    print("-" * 90)

    results = []
    for total_rounds, window, chars in test_cases:
        messages = build_conversation(total_rounds, chars)

        tokens_before = _estimate_tokens(messages)
        trimmed = sliding_window_messages(messages, max_rounds=window)
        tokens_after = _estimate_tokens(trimmed)

        reduction = (1 - tokens_after / tokens_before) * 100 if tokens_before > 0 else 0
        msgs_before = len(messages)
        msgs_after = len(trimmed)

        results.append((total_rounds, window, chars, tokens_before, tokens_after, reduction, msgs_before, msgs_after))
        print(f"{total_rounds:>8} | {window:>8} | {chars:>8} | {tokens_before:>14,} | {tokens_after:>14,} | {reduction:>9.1f}% | {msgs_before:>4} -> {msgs_after:>4}")

    return results


def bench_api_cost_impact():
    """Estimate API cost savings"""
    print("\n" + "=" * 75)
    print("  API Cost Impact Estimate (DeepSeek pricing)")
    print("=" * 75)

    # DeepSeek pricing: input ~$0.14/M tokens, output ~$0.28/M tokens
    input_price_per_m = 0.14
    output_price_per_m = 0.28

    print(f"\n  DeepSeek pricing: input=${input_price_per_m}/M tokens, output=${output_price_per_m}/M tokens")
    print(f"\n  {'Scenario':>25} | {'Before':>12} | {'After':>12} | {'Saved':>12}")
    print("  " + "-" * 70)

    scenarios = [
        ("50 rounds, 200 chars/msg", 50, 10, 200),
        ("100 rounds, 200 chars/msg", 100, 10, 200),
        ("50 rounds, 1000 chars/msg", 50, 10, 1000),
        ("100 rounds, 1000 chars/msg", 100, 10, 1000),
    ]

    for label, rounds, window, chars in scenarios:
        msgs = build_conversation(rounds, chars)
        trimmed = sliding_window_messages(msgs, max_rounds=window)

        t_before = _estimate_tokens(msgs)
        t_after = _estimate_tokens(trimmed)
        saved = t_before - t_after

        cost_before = t_before * input_price_per_m / 1_000_000
        cost_after = t_after * input_price_per_m / 1_000_000
        cost_saved = saved * input_price_per_m / 1_000_000

        print(f"  {label:>25} | ${cost_before:>10.4f} | ${cost_after:>10.4f} | ${cost_saved:>10.4f}")

    print(f"\n  Note: Per-request savings. At 1000 req/day with 100 rounds each:")
    worst = scenarios[-1]
    msgs_w = build_conversation(worst[1], worst[3])
    trimmed_w = sliding_window_messages(msgs_w, max_rounds=worst[2])
    daily_saved = (_estimate_tokens(msgs_w) - _estimate_tokens(trimmed_w)) * input_price_per_m / 1_000_000 * 1000
    print(f"    Daily savings: ~${daily_saved:.2f}")
    print(f"    Monthly savings: ~${daily_saved * 30:.2f}")


def print_summary(results):
    print("\n" + "=" * 75)
    print("  INTERVIEW-READY DATA")
    print("=" * 75)

    for r in results:
        total_rounds, window, chars, t_before, t_after, reduction, msgs_before, msgs_after = r
        if total_rounds == 50 and chars == 200:
            print(f"\n  [50-round conversation, 10-round window, 200 chars/msg]")
            print(f"    Tokens: {t_before:,} -> {t_after:,}  ({reduction:.0f}% reduction)")
            print(f"    Messages: {msgs_before} -> {msgs_after}")
        if total_rounds == 100 and chars == 1000:
            print(f"\n  [100-round conversation, 10-round window, 1000 chars/msg]")
            print(f"    Tokens: {t_before:,} -> {t_after:,}  ({reduction:.0f}% reduction)")
            print(f"    Messages: {msgs_before} -> {msgs_after}")

    print(f"\n  INTERVIEW PITCH:")
    r50 = next((r for r in results if r[0] == 50 and r[2] == 200), None)
    r100 = next((r for r in results if r[0] == 100 and r[2] == 200), None)
    if r50 and r100:
        print(f'  "The original code passed the entire conversation history to the LLM,')
        print(f'   causing unbounded token growth. I implemented a sliding window that')
        print(f'   keeps the system prompt + the latest 10 rounds of dialogue.')
        print(f'   For a 50-round chat, tokens dropped {r50[5]:.0f}%; for 100 rounds, {r100[5]:.0f}%.')
        print(f'   Each message is also capped at 2000 chars to prevent outliers.')
        print(f'   This directly reduces API cost and response latency."')


if __name__ == "__main__":
    results = bench_sliding_window()
    bench_api_cost_impact()
    print_summary(results)
    print("\nDone!")
