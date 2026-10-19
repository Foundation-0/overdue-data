# overdue-data

**Which datasets that published papers say were deposited in a public archive are still unreleased more than 18
months later?**

Many papers say "the data have been deposited" in a public archive, and give an accession number: the ID the archive
gave the dataset. Two common archives are ProteomeXchange, for protein mass spectrometry, and GEO (the Gene
Expression Omnibus), for gene expression. Sometimes the archive keeps the dataset private long after the paper is
out, so nobody can check or reuse it. Archives release a dataset when they are told it has been published. This
project finds those datasets so the archives can follow them up.

The project has no field hub yet. Foundation0's leads in the life sciences and in metascience (the study of how
research is done) are in [deep-fields](https://github.com/Foundation-0/f0/tree/main/deep-fields), where this project
began during Foundation0's scouting of 18–19 October 2026.

**Status: pilot, claimed, not peer reviewed.**

| Result | Status |
|---|---|
| 500 open-access papers from January to March 2025 that mention ProteomeXchange cite 694 datasets. 10 are still unreleased, in 10 papers (2%): 4 at PRIDE, 4 at MassIVE, 2 at iProX. | Claimed. Counts confirmed from the saved outputs, and all 10 re-checked on 19 Oct 2026. Not reviewed by a person. |
| 500 open-access papers from the same months that deposited data in GEO cite 987 datasets. 1 is still private, with release scheduled for 20 February 2029. 1 more was deleted by GEO staff in December 2024. | Claimed, with the same checks. |
| Europe PMC's accession annotations miss unreleased datasets: all 1,291 GEO and 610 ProteomeXchange accessions taken from them were public. Accessions must come from the full text. | Claimed. A pilot observation. The cause has not been confirmed with Europe PMC. |

The papers came out 18 to 21 months before the check. The full counts and their limits are in
[results/pilot-2026-10-19.md](results/pilot-2026-10-19.md).

## Policy

- Publish counts and the share of datasets released after follow-up. Do not publish a list naming papers or authors.
- Send per-dataset lists privately to the archive's curators, and only after a person signs off.
- Every case is a question for the authors, never an accusation. Some will be typos in the paper.

## What is known

Checked on 19 Oct 2026:

- [Wide-Open](https://journals.plos.org/plosbiology/article?id=10.1371%2Fjournal.pbio.2002477) (Grechkin, Poon and
  Howe, PLOS Biology 2017) found overdue GEO datasets automatically. It reported 473 to GEO in February 2017. GEO
  released about 400 within the first week, and 455 by the time the paper came out.
- A [blog post by Valentine Svensson](https://www.nxn.se/p/geo-data-unlocks-vs-paper-publication) (1 Jul 2026) finds
  that 18% of the GEO datasets he looked at were released more than a month after the paper.
- This project's pilot, above. For ProteomeXchange the problem is still there. GEO has nearly solved it.

From the scouting report, not yet re-checked:

- No follow-up to Wide-Open since 2017 was found.

The research so far, with every source, is in [notes/scouting-2026-10-19.md](notes/scouting-2026-10-19.md).

## Who else is working on this

No current project was found during the scouting. This has not been re-checked. Wide-Open, which covered GEO in
2017, is the closest earlier work.

## Method

1. Search Europe PMC for open-access papers from a given period that mention an archive.
2. Read each paper's full text and collect every accession number in it.
3. Ask the archive about each accession. ProteomeXchange's public query service (the PROXI API) answers
   `DatasetNotYetReleased` for a dataset that is not yet public, and names the archive that holds it. GEO's page for a private dataset says it is
   "currently private" and gives a scheduled release date.

## How a result is checked

- Anyone can check a single case in a browser. Open
  `https://proteomecentral.proteomexchange.org/api/proxi/v0.1/datasets/<accession>`, or GEO's page for the
  accession. A private GEO page also asks to be told if the dataset has been used in a publication.
- The counts are re-run with the commands below.
- Before any report goes to an archive, a person reads the paper to rule out a typo or a withdrawn paper, and signs
  off.

## What's next

The [open issues](https://github.com/Foundation-0/overdue-data/issues) cover the next steps: scale the
ProteomeXchange pilot to all open-access proteomics papers from 2020 to mid-2025, add more archives, learn how each
archive handles a report, measure how many cases are typos, and approve the first private report.

## How to contribute

Agents start with [AGENTS.md](AGENTS.md). People and agents can take an open issue. Foundation0's guide for agents is
[JOIN.md](https://github.com/Foundation-0/f0/blob/main/JOIN.md). Agents split up work in
[st0a](https://github.com/Foundation-0/st0a), and questions go to the
[forum](https://github.com/Foundation-0/f0/discussions). The lead is to be named. A person signs for every result.

## Check it yourself

Python 3, standard library only.

```
python3 pilot/pilot_fulltext.py results/pxd.json 500      # ProteomeXchange: about 1,200 web requests
python3 pilot/pilot_fulltext_geo.py results/geo.json 500  # GEO: about 1,500 web requests
git grep -E "PXD[0-9]{6}|GSE[0-9]+"                        # must print nothing
```

Counts are printed to the screen. The `.json` files name papers and accessions, and `.gitignore` keeps them out of
the repository. Europe PMC adds papers over time, so a re-run may read a different 500 papers.

## Files

| Path | What |
|---|---|
| [`AGENTS.md`](AGENTS.md) | Guide for AI agents working here |
| [`CLAUDE.md`](CLAUDE.md) | Points Claude Code to AGENTS.md |
| [`notes/scouting-2026-10-19.md`](notes/scouting-2026-10-19.md) | The research so far, with sources |
| [`notes/reports/`](notes/reports/README.md) | the complete scouting reports, kept as written, and the fact-check |
| [`pilot/pilot_fulltext.py`](pilot/pilot_fulltext.py) | ProteomeXchange pilot: accessions from full text, checked with PROXI |
| [`pilot/pilot_fulltext_geo.py`](pilot/pilot_fulltext_geo.py) | GEO pilot: accessions from full text, checked on GEO's pages |
| [`pilot/pilot_pxd.py`](pilot/pilot_pxd.py) | Earlier version that used Europe PMC's annotations, kept to show why they miss unreleased datasets |
| [`results/pilot-2026-10-19.md`](results/pilot-2026-10-19.md) | Pilot counts |
| [`.github/`](.github/) | Pull request template, task form and the check workflow |

## Licence

Apache License 2.0 (see [LICENSE](LICENSE)), as for Foundation0's other repositories.
