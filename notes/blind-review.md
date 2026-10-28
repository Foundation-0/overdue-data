# Blind review of flagged cases

Status: draft review procedure and tested summary tool. No paper has been
classified under this procedure yet. Refs #4.

Freeze a private sample from the cached census and record its hash, sampling seed,
and observation date locally. Give both readers the same paper and accession
evidence with opaque case IDs. Hide the first reader's labels from the second.
Keep paper titles, accessions, quotations, names and case-level judgments outside
this repository. No archive or author is contacted by this procedure.

Each reader saves a CSV with exactly `case_id,classification` columns and one of:

- `real case`: the paper cites this accession, the archive explicitly says it is
  unreleased, and the paper is neither withdrawn nor a detected typo.
- `typo`: the paper's accession is demonstrably mistyped; record the evidence locally.
- `withdrawn paper`: the publication record explicitly marks the paper withdrawn.
- `unclear`: evidence is missing, contradictory, inaccessible, or supports several explanations.

These are review categories, not allegations. A `real case` label still requires
human sign-off before any private report. Do not resolve uncertainty by guessing.
Record reasons in a separate private file. The public summary tool never reads it.

```sh
python3 -m unittest discover -s tests -v
python3 pilot/blind_review_summary.py /private/tmp/reader-a.csv /private/tmp/reader-b.csv
```

The tool rejects different case sets, empty samples, duplicate IDs and unknown
labels. It emits each reader's counts, agreement, and Cohen's kappa. Kappa is null
when both readers use only the same class because its denominator is zero.
Agreement measures consistency, not correctness. Resolve disagreements only after
preserving the independent judgments; report both the initial agreement and the
number of cases changed after discussion. Keep disputed cases out of a report.

Acceptance still requires the actual sample, two independent reviews, aggregate
counts and a human decision on whether the evidence is sufficient to contact an archive.
