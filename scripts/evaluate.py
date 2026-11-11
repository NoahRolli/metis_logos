"""Measures correction quality against the labelled test set.

Reports two accuracies:
  - per unique transcript, so every phrasing counts once
  - weighted by how often each transcript actually occurred

The weighted number is the one that describes day to day use; the
unweighted one shows whether rare phrasings are handled too.
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


def main() -> None:
    if not LABELS.exists():
        sys.exit(f"{LABELS} not found. Export the labelled sheet as CSV first.")

    rows = read_labels(LABELS)
    corrector = RuleCorrector()

    total = weighted_total = 0
    hits = weighted_hits = 0
    skipped = 0
    reasons: Counter[str] = Counter()
    errors: list[dict] = []

    for row in rows:
        text = (row.get("transcript") or "").strip()
        want_action = (row.get("expected_action") or "").strip()
        want_entity = (row.get("expected_entity") or "").strip()
        count = int((row.get("count") or "1").strip() or 1)

        if not text or want_action in SKIP or want_entity in SKIP:
            skipped += 1
            continue

        result = corrector.correct(text)
        got_action = result.action or "none"
        got_entity = result.entity or "none"
        ok = (got_action == want_action) and (got_entity == want_entity)

        total += 1
        weighted_total += count
        if ok:
            hits += 1
            weighted_hits += count
        else:
            if want_action == "none":
                reason = "false positive: noise accepted as command"
            elif got_entity == "none":
                reason = "rejected: confidence below threshold"
            elif got_entity != want_entity:
                reason = "wrong entity"
            else:
                reason = "wrong action"
            reasons[reason] += 1
            errors.append({
                "transcript": text,
                "count": count,
                "expected": f"{want_action} {want_entity}",
                "got": f"{got_action} {got_entity}",
                "confidence": result.confidence,
                "reason": reason,
            })

    if total == 0:
        sys.exit("No usable rows. Did you fill in expected_action and expected_entity?")

    print(f"Backend:            {corrector.name}")
    print(f"Labelled rows:      {len(rows)}  (skipped: {skipped})")
    print(f"Evaluated:          {total} unique / {weighted_total} occurrences")
    print()
    print(f"Accuracy unique:    {hits}/{total} = {hits / total:.1%}")
    print(f"Accuracy weighted:  {weighted_hits}/{weighted_total} = {weighted_hits / weighted_total:.1%}")
    print()
    print("Errors by reason:")
    for reason, n in reasons.most_common():
        print(f"  {n:3}  {reason}")

    if errors:
        with REPORT.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(errors[0]))
            writer.writeheader()
            writer.writerows(errors)
        print(f"\nDetails -> {REPORT}")


if __name__ == "__main__":
    main()
