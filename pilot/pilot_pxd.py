# Pilot written on 19 Oct 2026 during Foundation0's scouting. The code below this header is unchanged.
#
# Kept only to document a pitfall. Do not use it to find unreleased datasets.
#
# This earlier version took accessions from Europe PMC's text-mining annotations instead of the full
# text. All 610 PXD accessions it found were public, and the same was true of 1,291 GEO accessions
# found the same way. The annotations seem to keep only accessions that resolve publicly, so an
# unreleased dataset never shows up. Take accessions from the full text (pilot_fulltext.py).
#
# Usage: python3 pilot/pilot_pxd.py results/pxd-annotations.json
import json, re, sys, time, urllib.request, urllib.parse, urllib.error
OUT = sys.argv[1]
def get(url):
    for i in range(3):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.status, r.read().decode('utf-8', 'replace')
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode('utf-8','replace')
        except Exception:
            time.sleep(2)
    return 0, ''
q = 'ACCESSION_TYPE:pxd AND FIRST_PDATE:[2025-01-01 TO 2025-03-31] AND OPEN_ACCESS:y'
pmcids = []; cursor='*'
while True:
    u = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?' + urllib.parse.urlencode({'query': q, 'format':'json','pageSize':1000,'resultType':'lite','cursorMark':cursor})
    st, t = get(u); d = json.loads(t); res = d['resultList']['result']
    if not res: break
    pmcids += [r['pmcid'] for r in res if r.get('pmcid')]
    nc = d.get('nextCursorMark')
    if not nc or nc == cursor: break
    cursor = nc
print('papers', len(pmcids), file=sys.stderr)
acc = {}
for i in range(0, len(pmcids), 8):
    ids = ','.join('PMC:'+p for p in pmcids[i:i+8])
    st, t = get('https://www.ebi.ac.uk/europepmc/annotations_api/annotationsByArticleIds?' + urllib.parse.urlencode({'articleIds': ids, 'type':'Accession Numbers', 'format':'JSON'}))
    try: arr = json.loads(t)
    except: continue
    for a in arr:
        for an in a.get('annotations', []):
            for m in re.findall(r'PXD\d{6}', an.get('exact','')):
                acc.setdefault(m, set()).add(a.get('pmcid'))
print('PXD accessions', len(acc), file=sys.stderr)
res = []
for g, ps in sorted(acc.items()):
    st, t = get('https://proteomecentral.proteomexchange.org/api/proxi/v0.1/datasets/' + g)
    if 'DatasetNotYetReleased' in t: s = 'private'
    elif st == 200: s = 'public'
    else: s = 'other:%s' % st
    res.append({'acc': g, 'papers': sorted(p for p in ps if p), 'status': s, 'detail': t[:200] if s.startswith('other') else ''})
    time.sleep(0.3)
json.dump(res, open(OUT,'w'), indent=1)
from collections import Counter
print(Counter(r['status'] for r in res), file=sys.stderr)
