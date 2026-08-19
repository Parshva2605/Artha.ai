from backend.pipeline.labeler import balance_dataset

# Build sample rows
rows = []
for i in range(150):
    rows.append({"label_sentiment": "negative", "confidence": 0.9})
for i in range(120):
    rows.append({"label_sentiment": "positive", "confidence": 0.85})
for i in range(13):
    rows.append({"label_sentiment": "neutral", "confidence": 0.95})

balanced = balance_dataset(rows, target_count=100, label_type="sentiment")

from collections import Counter
counts = Counter(r.get("label_sentiment") for r in balanced)

print("Total:", len(balanced))
print(dict(counts))

# Checks
assert len(balanced) == 100, f"Expected 100, got {len(balanced)}"
for label, cnt in counts.items():
    assert cnt <= int(100 * 0.51), f"Label {label} exceeds 51%: {cnt}"

print("BALANCE TEST PASSED - got exactly 100 rows and no label >51%")
