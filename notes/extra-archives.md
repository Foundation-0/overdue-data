# Three additional archive adapters

Status: draft extractors and saved-response classifiers. Synthetic tests pass;
the three 50-paper pilots and live schema checks remain undone. Refs #2.

`pilot/archive_adapters.py` extracts MetaboLights, Metabolomics Workbench and
BioProject accessions, including BioProject's NCBI, ENA and DDBJ prefixes. It
deduplicates within text and rejects identifiers embedded in longer tokens.
Its `request_url` function gives a read-only API URL; it does not make requests.

The response classifier requires an exact matching identifier in successful
metadata. It calls this `public_metadata`, which does not establish that every
data file is public. Failure, malformed data, a schema mismatch or an absent
record is `unknown`. There is deliberately no private label without a documented
explicit private-status response. An empty search or HTTP 401 is insufficient.

```sh
python3 -m unittest discover -s tests -v
python3 pilot/archive_adapters.py /private/tmp/archive-responses.json
```

Each private input row has `archive`, `accession`, `status` (integer HTTP status),
and `body` (response text). Use one observation per accession. Keep response
timestamps and source URLs beside that file. The tool prints aggregate counts
only and refuses an input path within the checkout. Do not commit input records.

Before connecting a network runner, verify each URL and schema against a public
control and a documented unavailable control. Use a real contact address,
throttling and a private cache. Then select 50 papers per archive with fixed
queries and dates, record full-text failures, and publish only counts. A reader
must inspect any proposed private case before it is included in a report.

Sources: [MetaboLights download guide](https://www.ebi.ac.uk/training/online/courses/metabolights-quick-tour/getting-data-from-metabolights/),
[MetaboLights API](https://www.ebi.ac.uk/metabolights/ws/api/spec.html),
[Workbench REST API](https://www.metabolomicsworkbench.org/tools/MWRestAPIv1.0.pdf),
[BioProject accession prefixes](https://support.nlm.nih.gov/knowledgebase/article/KA-03434/en-us),
and [NCBI EFetch documentation](https://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.EFetch).
The MetaboLights API schema was inaccessible to the browser during this review;
its response shape here is provisional and fails to unknown if it differs.
