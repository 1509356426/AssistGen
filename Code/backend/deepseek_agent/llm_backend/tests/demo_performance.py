"""
性能对比演示脚本

Run: python tests/demo_performance.py
然后访问 http://localhost:8000/performance 查看可视化对比
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.metrics import metrics
import time
import random
import math


def demo_old_vs_new():
    """演示优化前后的性能差异"""
    print("=" * 60)
    print("  Performance Optimization Demo")
    print("=" * 60)

    print("\n[Simulating OLD style cache lookup - O(n) traversal]")
    print("Simulating 1000 cached items with 1ms Redis latency each...")

    n = 1000
    redis_latency = 0.001  # 1ms per Redis read

    t0 = time.perf_counter()
    total_latency = n * redis_latency
    time.sleep(total_latency)  # Simulate the wait
    old_time = (time.perf_counter() - t0) * 1000

    print(f"  OLD style traversal: {old_time:.0f}ms (you just waited)")
    print(f"  This is why cache was USELESS - checking cache took longer than API call!")

    print("\n[Simulating NEW style cache lookup - FAISS]")
    print("FAISS in-memory search, 0 Redis reads...")

    t0 = time.perf_counter()
    time.sleep(0.002)  # 2ms FAISS search
    new_time = (time.perf_counter() - t0) * 1000

    print(f"  NEW style FAISS: {new_time:.0f}ms")
    print(f"  Speedup: {old_time / new_time:.0f}x faster!")

    print("\n[Comparison]")
    print(f"  Before: Checking cache = {old_time:.0f}ms (slower than API!)")
    print(f"  After:  Checking cache = {new_time:.0f}ms (instant)")
    print(f"  Now cache is actually USEFUL - hit rate can save real API costs")


def demo_sliding_window():
    """演示滑动窗口的Token节省"""
    from app.services.message_utils import sliding_window_messages, _estimate_tokens

    print("\n" + "=" * 60)
    print("  Sliding Window Token Savings Demo")
    print("=" * 60)

    # Simulate a long conversation
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    for i in range(1, 51):
        messages.append({"role": "user", "content": f"Round {i}: User asks about phone specs, prices, warranty, etc. " * 10})
        messages.append({"role": "assistant", "content": f"Round {i}: Answer about the phone. " * 10})

    before_tokens = _estimate_tokens(messages)
    print(f"\n  50-round conversation BEFORE optimization:")
    print(f"    Messages: {len(messages)}")
    print(f"    Estimated tokens: {before_tokens:,}")
    print(f"    API cost (no cache): ~{before_tokens * 2 / 1_000_000:.4f} yuan")

    trimmed = sliding_window_messages(messages, max_rounds=10)
    after_tokens = _estimate_tokens(trimmed)

    print(f"\n  50-round conversation AFTER optimization:")
    print(f"    Messages: {len(trimmed)}")
    print(f"    Estimated tokens: {after_tokens:,}")
    print(f"    API cost (no cache): ~{after_tokens * 2 / 1_000_000:.4f} yuan")

    saved = before_tokens - after_tokens
    print(f"\n  Savings per request:")
    print(f"    Tokens saved: {saved:,} ({(1 - after_tokens/before_tokens)*100:.0f}% reduction)")
    print(f"    Cost saved: ~{saved * 2 / 1_000_000:.4f} yuan per request")
    print(f"    With 1000 daily users: ~{saved * 2 / 1_000_000 * 1000 * 30:.0f} yuan/month")


def demo_cache_hit_savings():
    """演示缓存命中省的钱"""
    print("\n" + "=" * 60)
    print("  Cache Hit Cost Savings Demo")
    print("=" * 60)

    # DeepSeek pricing
    CACHE_HIT = 0.2
    CACHE_MISS = 2.0
    OUTPUT = 3.0

    input_tokens = 500
    output_tokens = 800

    cost_miss = (input_tokens * CACHE_MISS + output_tokens * OUTPUT) / 1_000_000
    cost_hit = (input_tokens * CACHE_HIT + output_tokens * OUTPUT) / 1_000_000

    print(f"\n  Per-request cost (DeepSeek pricing):")
    print(f"    Input: ~{input_tokens} tokens, Output: ~{output_tokens} tokens")
    print(f"    Cache MISS: {cost_miss:.6f} yuan")
    print(f"    Cache HIT:  {cost_hit:.6f} yuan")
    print(f"    Saving per hit: {cost_miss - cost_hit:.6f} yuan")

    scenarios = [
        ("Small app", 100, "10%"),
        ("Your startup", 1000, "30%"),
        ("Growing fast", 10000, "40%"),
    ]

    print(f"\n  Monthly savings at different scales:")
    print(f"  {'App Size':<15} | {'Daily':>8} | {'Hit Rate':>10} | {'Monthly Saved':>15}")
    print("  " + "-" * 65)

    for name, daily, hit in scenarios:
        hit_rate = int(hit.rstrip("%")) / 100
        hits = int(daily * hit_rate)
        misses = daily - hits

        daily_cost = hits * cost_hit + misses * cost_miss
        daily_cost_no_cache = daily * cost_miss
        monthly = (daily_cost_no_cache - daily_cost) * 30

        print(f"  {name:<15} | {daily:>8,} | {hit:>10} | {monthly:>13.2f} yuan")


if __name__ == "__main__":
    demo_old_vs_new()
    demo_sliding_window()
    demo_cache_hit_savings()

    print("\n" + "=" * 60)
    print("  Demo complete!")
    print("  These optimizations save MONEY, not perceived latency.")
    print("  The real benefit is in reduced API costs at scale.")
    print("=" * 60)
