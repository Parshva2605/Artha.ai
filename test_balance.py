#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from backend.pipeline.labeler import balance_dataset
from collections import Counter

# Simulate imbalanced data
# 80 negative, 15 positive, 5 neutral = bad balance
test_rows = []
for i in range(80):
    test_rows.append({
        "label_sentiment": "negative",
        "confidence": 0.90,
        "text_clean": f"terrible app {i}"
    })
for i in range(15):
    test_rows.append({
        "label_sentiment": "positive",
        "confidence": 0.92,
        "text_clean": f"great app {i}"
    })
for i in range(5):
    test_rows.append({
        "label_sentiment": "neutral",
        "confidence": 0.85,
        "text_clean": f"ok app {i}"
    })

print(f"Before balance: {len(test_rows)} rows")
print("Before distribution:")
before = Counter(r["label_sentiment"] for r in test_rows)
print(dict(before))

# Balance to 30 rows
balanced = balance_dataset(
    rows=test_rows,
    target_count=30,
    label_type="sentiment"
)

print(f"\nAfter balance: {len(balanced)} rows")
print("After distribution:")
after = Counter(r["label_sentiment"] for r in balanced)
print(dict(after))

# Verify balance
print("\nPer-label percentages:")
test_failed = False
for label, count in after.items():
    pct = count / len(balanced) * 100
    print(f"  {label}: {count} ({pct:.1f}%)")
    if pct > 40:
        print(f"    FAILED: {label} is {pct:.1f}% (max 40%)")
        test_failed = True

if not test_failed:
    print("\n✓ BALANCE TEST PASSED")
else:
    print("\n✗ BALANCE TEST FAILED")
