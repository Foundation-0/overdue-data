# Pilot written on 19 Oct 2026 during Foundation0's scouting. The code below this header is unchanged.
#
# What it does: takes open-access papers in Europe PMC from January to March 2025 that mention
# ProteomeXchange, reads each paper's full text, collects every ProteomeXchange accession (PXD and six
# digits), and asks the ProteomeXchange PROXI API about each one. The answer "DatasetNotYetReleased"
# means the archive still keeps the dataset private.
#
# Usage: python3 pilot/pilot_fulltext.py results/pxd.json 500
#   The first argument is the output file. It names papers and accessions, so it must never be
#   committed (.gitignore excludes results/*.json). The second is the number of papers (the pilot used 500).
#   Counts are printed to stderr.
#
# Known gaps, left as run: no contact email in the User-Agent and no cache. Add both before scaling up.
import json, re, sys, time, urllib.request, urllib.parse, urllib.error
out, N = sys.argv[1], int(sys.argv[2])
def get(u):
    for i in range(3):
        try:
            with urllib.request.urlopen(u, timeout=60) as x: return x.status, x.read().decode('utf-8','replace')
        except urllib.error.HTTPError as e: return e.code, e.read().decode('utf-8','replace')
        except Exception: time.sleep(2)
    return 0, ''
q = '("ProteomeXchange" OR "PRIDE partner repository") AND FIRST_PDATE:[2025-01-01 TO 2025-03-31] AND OPEN_ACCESS:y AND IN_EPMC:y'
pm=[]; cursor='*'
while len(pm) < N:
    st,t = get('https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':q,'format':'json','pageSize':500,'resultType':'lite','cursorMark':cursor}))
    d=json.loads(t); res=d['resultList']['result']
    if not res: break
    pm += [x['pmcid'] for x in res if x.get('pmcid')]
    nc=d.get('nextCursorMark')
    if not nc or nc==cursor: break
    cursor=nc
pm=pm[:N]; print('papers', len(pm), 'hits', d.get('hitCount'), file=sys.stderr)
acc={}
for p in pm:
    st,t = get('https://www.ebi.ac.uk/europepmc/webservices/rest/%s/fullTextXML' % p)
    for m in set(re.findall(r'PXD\d{6}', t)): acc.setdefault(m,set()).add(p)
    time.sleep(0.1)
print('PXD in full text', len(acc), file=sys.stderr)
res=[]
for a,ps in sorted(acc.items()):
    st,t = get('https://proteomecentral.proteomexchange.org/api/proxi/v0.1/datasets/'+a)
    s = 'private' if 'DatasetNotYetReleased' in t else ('public' if st==200 else 'other:%s:%s' % (st, t[:120].replace('\n',' ')))
    res.append({'acc':a,'papers':sorted(ps),'status':s}); time.sleep(0.3)
json.dump(res, open(out,'w'), indent=1)
from collections import Counter
print(Counter(x['status'].split(':')[0] for x in res), file=sys.stderr)
print('papers with a private PXD', len(set(p for x in res if x['status']=='private' for p in x['papers'])), file=sys.stderr)
