"""Bounded, cached Europe PMC/PROXI census. Prints aggregate JSON only."""
import argparse
from collections import defaultdict
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time
import urllib.error
import urllib.parse
import urllib.request

EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/"
PROXI = "https://proteomecentral.proteomexchange.org/api/proxi/v0.1/datasets/"
ACCESSION = re.compile(r"(?<![A-Za-z0-9])PXD[0-9]{6}(?![A-Za-z0-9])")

class Client:
    def __init__(self, cache, contact, pause=1.0, offline=False):
        self.cache = Path(cache).resolve()
        root = Path(__file__).resolve().parents[1]
        if self.cache == root or root in self.cache.parents:
            raise ValueError("cache must be outside this repository")
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", contact):
            raise ValueError("a contact email is required")
        if pause < 0.5:
            raise ValueError("pause must be at least 0.5 seconds")
        self.cache.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.agent = "Foundation0-overdue-data/0.1 (mailto:" + contact + ")"
        self.pause, self.offline = pause, offline

    def get(self, url):
        target = self.cache / (hashlib.sha256(url.encode()).hexdigest() + ".json")
        if target.exists():
            record = json.loads(target.read_text())
            return record["status"], record["body"]
        if self.offline:
            raise RuntimeError("cache miss in offline replay")
        request = urllib.request.Request(url, headers={"User-Agent": self.agent})
        for attempt in range(3):
            time.sleep(self.pause * (attempt + 1))
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    status, body = response.status, response.read().decode("utf-8", "replace")
            except urllib.error.HTTPError as error:
                status, body = error.code, error.read().decode("utf-8", "replace")
            except (OSError, TimeoutError):
                if attempt == 2:
                    raise RuntimeError("network request failed") from None
                continue
            if status == 429 or status >= 500:
                if attempt == 2:
                    raise RuntimeError("service unavailable after three attempts")
                continue
            record = {"status": status, "body": body,
                      "observed_at": datetime.now(timezone.utc).isoformat()}
            target.write_text(json.dumps(record))
            target.chmod(0o600)
            return status, body
        raise RuntimeError("request did not complete")

def dataset_status(status, text):
    try:
        data = json.loads(text)
    except ValueError:
        return "unknown", "unknown"
    def walk(value):
        if isinstance(value, dict):
            for key, val in value.items():
                yield key, val
                yield from walk(val)
        elif isinstance(value, list):
            for val in value:
                yield from walk(val)
    pairs = list(walk(data))
    private = any(v == "DatasetNotYetReleased" for _, v in pairs if isinstance(v, str))
    archive = next((v for k, v in pairs if k.lower() in ("repository", "repositoryname")
                    and isinstance(v, str) and v in ("PRIDE", "MassIVE", "iProX")), "unknown")
    # An arbitrary HTTP 200 response is not sufficient evidence of a public dataset.
    identity = any(isinstance(v, str) and ACCESSION.fullmatch(v)
                   for k, v in pairs if k.lower() in ("accession", "datasetaccession"))
    return ("private" if private else "public" if status == 200 and identity else "unknown"), archive

def papers(client, start, end, limit):
    query = f'("ProteomeXchange" OR "PRIDE partner repository") AND FIRST_PDATE:[{start} TO {end}] AND OPEN_ACCESS:y AND IN_EPMC:y'
    cursor, seen = "*", set()
    while True:
        url = EPMC + "search?" + urllib.parse.urlencode(
            {"query": query, "format": "json", "pageSize": 100, "resultType": "core", "cursorMark": cursor})
        status, text = client.get(url)
        if status != 200:
            raise RuntimeError("Europe PMC search failed")
        data = json.loads(text)
        rows = data["resultList"]["result"]
        if not rows:
            break
        for row in rows:
            key = row.get("pmcid")
            if not key or key in seen:
                continue
            seen.add(key)
            yield key, str(row.get("firstPublicationDate", row.get("pubYear", "unknown")))[:4]
            if limit and len(seen) >= limit:
                return
        next_cursor = data.get("nextCursorMark")
        if not next_cursor or next_cursor == cursor:
            break
        cursor = next_cursor

def census(client, start, end, limit):
    annual = defaultdict(lambda: {"papers_read": 0, "papers_unreadable": 0,
                                  "accessions": set(), "private_papers": set()})
    links = defaultdict(set)
    for pmc, year in papers(client, start, end, limit):
        status, body = client.get(EPMC + pmc + "/fullTextXML")
        if status != 200:
            annual[year]["papers_unreadable"] += 1
            continue
        annual[year]["papers_read"] += 1
        for accession in set(ACCESSION.findall(body)):
            annual[year]["accessions"].add(accession)
            links[accession].add((pmc, year))
    cells = defaultdict(lambda: {"accessions": set(), "private": set(), "unknown": set(),
                                "papers": set(), "private_papers": set()})
    for accession, occurrences in sorted(links.items()):
        state, archive = dataset_status(*client.get(PROXI + accession))
        for pmc, year in occurrences:
            cell = cells[(year, archive)]
            cell["accessions"].add(accession)
            cell["papers"].add(pmc)
            if state in ("private", "unknown"):
                cell[state].add(accession)
            if state == "private":
                cell["private_papers"].add(pmc)
                annual[year]["private_papers"].add(pmc)
    def counts(record):
        return {k: len(v) if isinstance(v, set) else v for k, v in record.items()}
    return {"period": [start, end], "paper_limit": limit,
            "years": {y: counts(v) for y, v in sorted(annual.items())},
            "by_year_archive": [{"year": y, "archive": a, **counts(v)}
                                for (y, a), v in sorted(cells.items())],
            "limits": ["Archive unknown is retained, never guessed.",
                       "Archive rows count citing papers; one paper can occur in several rows.",
                       "Private is a service status, not a finding of author wrongdoing.",
                       "Cached status describes the recorded observation, not current availability."]}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", required=True)
    parser.add_argument("--contact", required=True)
    parser.add_argument("--start", default="2020-01-01")
    parser.add_argument("--end", default="2025-06-30")
    parser.add_argument("--limit", type=int, default=100, help="0 for the full census")
    parser.add_argument("--pause", type=float, default=1.0)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    if date.fromisoformat(args.start) > date.fromisoformat(args.end) or args.limit < 0:
        parser.error("invalid period or limit")
    result = census(Client(args.cache, args.contact, args.pause, args.offline),
                    args.start, args.end, args.limit)
    print(json.dumps(result, indent=2))
if __name__ == "__main__":
    main()
