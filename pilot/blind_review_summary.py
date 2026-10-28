"""Compare two local blinded review files; emit counts without identifiers."""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path

CLASSES = {"real case", "typo", "withdrawn paper", "unclear"}

def load(path):
    rows = {}
    with Path(path).open(newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["case_id", "classification"]:
            raise ValueError("expected case_id,classification columns")
        for row in reader:
            key, label = row["case_id"], row["classification"]
            if not key or key in rows or label not in CLASSES:
                raise ValueError("invalid or duplicate review row")
            rows[key] = label
    if not rows:
        raise ValueError("empty review")
    return rows

def summarize(first, second):
    if set(first) != set(second):
        raise ValueError("reviewers must classify the same cases")
    if not first or any(x not in CLASSES for x in [*first.values(), *second.values()]):
        raise ValueError("invalid classifications")
    n = len(first)
    a, b = Counter(first.values()), Counter(second.values())
    agreement = sum(first[k] == second[k] for k in first)
    expected = sum(a[c] * b[c] for c in CLASSES) / n**2
    return {"sample_size": n, "first": dict(sorted(a.items())),
            "second": dict(sorted(b.items())), "agreements": agreement,
            "agreement_fraction": agreement/n,
            "cohen_kappa": None if expected == 1 else (agreement/n - expected)/(1 - expected),
            "scope": "Reader agreement only; classifications are not independently established facts."}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("first"); parser.add_argument("second")
    args = parser.parse_args()
    try:
        result = summarize(load(args.first), load(args.second))
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))
