# Pilot written on 19 Oct 2026 during Foundation0's scouting. The code below this header is unchanged.
#
# What it does: the same as pilot_fulltext.py, for GEO (the Gene Expression Omnibus). It takes
# open-access papers from January to March 2025 that say their data were deposited in GEO, collects
# every GEO series accession (GSE and digits) from the full text, and reads GEO's own page for each one.
# A private series says it is "currently private" and gives a scheduled release date.
#
# Usage: python3 pilot/pilot_fulltext_geo.py results/geo.json 500
#   The output file names papers and accessions, so it must never be committed.
#
# Known gaps, left as run: no contact email in the User-Agent and no cache. A series that GEO has
# deleted, and a reCAPTCHA page from GEO, both end up as "other"; look at those by hand.
import json, re, sys, time, urllib.request, urllib.parse, urllib.error
out, N = sys.argv[1], int(sys.argv[2])
def get(u):
    for i in range(3):
        try:
            with urllib.request.urlopen(u, timeout=60) as x: return x.status, x.read().decode('utf-8','replace')
        except urllib.error.HTTPError as e: return e.code, e.read().decode('utf-8','replace')
        except Exception: time.sleep(2)
    return 0, ''
q = '("deposited in the Gene Expression Omnibus" OR "deposited in GEO" OR "deposited to GEO" OR "deposited into GEO" OR "deposited in NCBI\'s Gene Expression Omnibus") AND FIRST_PDATE:[2025-01-01 TO 2025-03-31] AND OPEN_ACCESS:y AND IN_EPMC:y'
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
    for m in set(re.findall(r'GSE\d{4,7}', t)): acc.setdefault(m,set()).add(p)
    time.sleep(0.1)
print('GSE in full text', len(acc), file=sys.stderr)
res=[]
for a,ps in sorted(acc.items()):
    st,h = get('https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=%s&targ=self&form=text&view=brief' % a)
    m = re.search(r'currently private and is scheduled to be released on ([A-Za-z]{3} \d{1,2}, \d{4})', h)
    rel = None
    if m: s='private'; rel=m.group(1)
    elif 'Could not find a public or private accession' in h: s='notfound'
    elif 'Public on' in h: s='public'
    else: s='other'
    res.append({'acc':a,'papers':sorted(ps),'status':s,'release':rel}); time.sleep(0.4)
json.dump(res, open(out,'w'), indent=1)
from collections import Counter
print(Counter(x['status'].split(':')[0] for x in res), file=sys.stderr)
print('papers with a private GSE', len(set(p for x in res if x['status']=='private' for p in x['papers'])), file=sys.stderr)
