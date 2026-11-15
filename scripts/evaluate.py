"""Measures correction quality against the labelled test set.

Reports accuracy per unique transcript and weighted by how often each
transcript actually occurred. Clarifications are counted separately,
and split by whether the intended target was among the candidates: a
clarification that does not offer the right answer is no better than a
rejection.
"""

import csv
import sys
from collections import Counter
from pathlib import Path

from app.corrector.rules import RuleCorrector

LABELS = Path("data/labels.csv")
REPORT = Path("data/baseline_errors.csv")
SKIP = {"", "unclear"}


def read_labels(path: Path) -> list[dict]:
    raw = path.read_text(encoding="utf-8-sig")
    header = raw.splitlines()[0]
    delimiter = ";" if header.count(";") > header.count(",") else ","
    rows = list(csv.DictReader(raw.splitlines(), delimiter=delimiter))
    if not rows or "transcript" not in rows[0]:
        sys.exit(f"Unexpected columns in {path}: {list(rows[0]) if rows else 'empty'}")
    return rows


def classify(result, want_action: str, want_entity: str) -> str:
    """Puts one outcome into exactly one bucket."""
    wants_nothing = want_action == "none"

    if result.status == "command":
        if wants_nothing:
            return "false positive"
        if result.action == want_action and result.entity == want_entity:
            return "correct"
        return "wrong command"

    if result.status == "clarify":
        if wants_nothing:
            return "false positive"
        if any(c.entity == want_entity for c in result.candidates):
            return "clarify, target offered"
        return "clarify, target missing"

    return "correctly rejected" if wants_nothing else "rejected"


GOOD = {"correct", "correctly rejected"}
RECOVERABLE = {"clarify, target offered"}


def main() -> None:
    if not LABELS.exists():
        sys.exit(f"{LABELS} not found. Export the labelled sheet as CSV first.")

    rows = read_labels(LABELS)
    corrector = RuleCorrector()

    buckets: Counter[str] = Counter()
    weighted: Counter[str] = Counter()
    skipped = 0
    problems: list[dict] = []

    for row in rows:
        text = (row.get("transcript") or "").strip()
        want_action = (row.get("expected_action") or "").strip()
        want_entity = (row.get("expected_entity") or "").strip()
        count = int((row.get("count") or "1").strip() or 1)

        if not text or want_action in SKIP or want_entity in SKIP:
            skipped += 1
            continue

        result = corrector.correct(text)
        bucket = classify(result, want_action, want_entity)
        buckets[bucket] += 1
        weighted[bucket] += count

        if bucket not in GOOD:
            problems.append({
                "transcript": text,
                "count": count,
                "expected": f"{want_action} {want_entity}",
                "status": result.status,
                "got": f"{result.action or 'none'} {result.entity or 'none'}",
                "candidates": " | ".join(f"{c.entity}={c.confidence}" for c in result.candidates),
                "confidence": result.confidence,
                "bucket": bucket,
            })

    total = sum(buckets.values())
    w_total = sum(weighted.values())
    if total == 0:
        sys.exit("No usable rows. Did you fill in expected_action and expected_entity?")

    good = sum(buckets[b] for b in GOOD)
    w_good = sum(weighted[b] for b in GOOD)
    rec = sum(buckets[b] for b in RECOVERABLE)
    w_rec = sum(weighted[b] for b in RECOVERABLE)

    print(f"Backend:              {corrector.name}")
    print(f"Labelled rows:        {len(rows)}  (skipped: {skipped})")
    print(f"Evaluated:            {total} unique / {w_total} occurrences")
    print()
    print(f"Handled directly:     {good}/{total} = {good / total:.1%}"
          f"   |  weighted {w_good}/{w_total} = {w_good / w_total:.1%}")
    print(f"Plus after asking:    {good + rec}/{total} = {(good + rec) / total:.1%}"
          f"   |  weighted {w_good + w_rec}/{w_total} = {(w_good + w_rec) / w_total:.1%}")
    print()
    print("Breakdown (unique / weighted):")
    for bucket, n in buckets.most_common():
        print(f"  {n:3} / {weighted[bucket]:3}   {bucket}")

    if problems:
        with REPORT.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(problems[0]))
            writer.writeheader()
            writer.writerows(problems)
        print(f"\nDetails -> {REPORT}")


if __name__ == "__main__":
    main()
