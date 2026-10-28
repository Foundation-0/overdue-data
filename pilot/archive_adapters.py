"""Extract three accession families and classify saved API responses conservatively."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import urllib.parse
import xml.etree.ElementTree as ET

PATTERNS = {
    "MetaboLights": re.compile(r"(?<![A-Za-z0-9])MTBLS[0-9]+(?![A-Za-z0-9])"),
    "Metabolomics Workbench": re.compile(r"(?<![A-Za-z0-9])ST[0-9]{6}(?![A-Za-z0-9])"),
    "BioProject": re.compile(r"(?<![A-Za-z0-9])PRJ(?:NA|EB|DB)[0-9]+(?![A-Za-z0-9])"),
}

def extract(text):
    return {name: sorted(set(pattern.findall(text))) for name, pattern in PATTERNS.items()}

def request_url(archive, accession):
    if archive not in PATTERNS or not PATTERNS[archive].fullmatch(accession):
        raise ValueError("invalid archive or accession")
    if archive == "MetaboLights":
        return "https://www.ebi.ac.uk/metabolights/ws/studies/" + accession
    if archive == "Metabolomics Workbench":
        return "https://www.metabolomicsworkbench.org/rest/study/study_id/" + accession + "/summary"
    return "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" + urllib.parse.urlencode(
        {"db": "bioproject", "id": accession, "retmode": "xml"})

def classify(archive, accession, status, body):
    request_url(archive, accession)  # validate before interpreting any response
    if status != 200:
        return "unknown"
    if archive == "BioProject":
        try:
            root = ET.fromstring(body)
        except ET.ParseError:
            return "unknown"
        found = any(node.tag.rsplit("}", 1)[-1] == "ArchiveID" and
                    node.get("accession") == accession for node in root.iter())
        return "public_metadata" if found else "unknown"
    try:
        data = json.loads(body)
    except (TypeError, ValueError):
        return "unknown"
    if archive == "MetaboLights":
        study = data.get("content", {}) if isinstance(data, dict) else {}
        if isinstance(study, dict) and study.get("studyIdentifier") == accession:
            return "public_metadata"
    if archive == "Metabolomics Workbench":
        rows = [data] if isinstance(data, dict) and "study_id" in data else (
            list(data.values()) if isinstance(data, dict) else [])
        if any(isinstance(row, dict) and row.get("study_id") == accession for row in rows):
            return "public_metadata"
    return "unknown"

def aggregate(records):
    seen, counts = set(), Counter()
    for record in records:
        key = (record["archive"], record["accession"])
        if key in seen:
            raise ValueError("duplicate response: select one observation per accession")
        seen.add(key)
        state = classify(*key, record["status"], record["body"])
        counts[(key[0], state)] += 1
    return [{"archive": archive, "status": status, "count": count}
            for (archive, status), count in sorted(counts.items())]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("responses", help="private JSON array of saved responses outside the repository")
    args = parser.parse_args()
    path = Path(args.responses).resolve()
    root = Path(__file__).resolve().parents[1]
    if path == root or root in path.parents:
        parser.error("responses must be outside this repository")
    try:
        result = aggregate(json.loads(path.read_text()))
    except (ValueError, KeyError, OSError) as error:
        parser.error("invalid saved-response input")
    print(json.dumps(result, indent=2))
