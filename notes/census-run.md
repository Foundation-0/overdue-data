# Run the expanded census

Status: draft implementation, checked on synthetic responses. The full census
and the independent check of 20 flagged cases have not run. Refs #1.

`pilot/batch_fulltext.py` reads full text from Europe PMC, follows search cursors,
deduplicates accessions, and asks PROXI once per accession. Its default period is
January 2020 through June 2025. The default limit is 100 papers; use `--limit 0`
only after checking a small batch. Supply the operator's real contact address.

```sh
python3 -m unittest discover -s tests -v
python3 pilot/batch_fulltext.py --cache /private/tmp/overdue-cache --contact YOU@example.org --limit 100
python3 pilot/batch_fulltext.py --cache /private/tmp/overdue-cache --contact YOU@example.org --limit 100 --offline
```

Use a private directory outside the repository for the cache. It contains paper
text and dataset metadata. Do not publish it. A cached response keeps its UTC
observation time; replay reports that observation, not current availability.
Use a new cache directory for a later availability check.

The JSON output contains counts only: papers read and unreadable by year, distinct
accessions, and papers citing explicitly private accessions. Archive rows count
citing papers, so a paper can occur in several rows. Unknown archives and unknown
statuses remain visible. An HTTP failure or an arbitrary successful response does
not prove that a dataset is private or public.

The search is limited to open-access full text indexed by Europe PMC and to the
two search phrases in the script. It is not an exhaustive census of proteomics.
The endpoint schema still needs comparison with saved real responses. In
particular, an unrecognized private response is counted as unknown.

Before reporting a result, record the query, script commit, cache date range,
counts, unknown share, and full-text failures. Have another reader inspect 20
flagged cases locally, checking the cited accession, paper publication date,
withdrawal status, and current archive response. Keep that case list private.
An archive status alone is not a finding of author wrongdoing.

API references: [Europe PMC REST service](https://europepmc.org/RestfulWebService)
and [ProteomeCentral PROXI](https://proteomecentral.proteomexchange.org/api/proxi/v0.1/datasets).
