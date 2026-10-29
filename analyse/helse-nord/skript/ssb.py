"""Felles hjelpefunksjoner for SSB PxWebApi v2 (json-stat2)."""
import json, os, time, urllib.request, urllib.parse

V2 = "https://data.ssb.no/api/pxwebapi/v2/tables/"
HER = os.path.dirname(os.path.abspath(__file__))
RAA = os.path.normpath(os.path.join(HER, "..", "kilder", "data"))
UT = os.path.normpath(os.path.join(HER, "..", "data"))
UA = {"User-Agent": "nord-norge-dashbord/1.0 (analyse helse-nord)"}


def hent(url, fil=None, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            b = urllib.request.urlopen(req, timeout=300).read()
            if fil:
                with open(os.path.join(RAA, fil), "wb") as f:
                    f.write(b)
            return b
        except Exception as e:  # noqa
            if i == tries - 1:
                raise
            time.sleep(3)


def data(tab, p, fil=None):
    u = V2 + tab + "/data?" + urllib.parse.urlencode({"lang": "no", "outputFormat": "json-stat2", **p})
    return json.loads(hent(u, fil))


def celler(d):
    ids = d["id"]
    def orden(ix):
        return list(ix) if isinstance(ix, list) else sorted(ix, key=ix.get)
    keys = [orden(d["dimension"][i]["category"]["index"]) for i in ids]
    verdier = d["value"]
    if isinstance(verdier, dict):  # json-stat2 tillater glissen verdiliste
        n = 1
        for s_ in d["size"]:
            n *= s_
        verdier = [verdier.get(str(i)) for i in range(n)]
    for n, v in enumerate(verdier):
        rest, co = n, {}
        for i in range(len(ids) - 1, -1, -1):
            co[ids[i]] = keys[i][rest % d["size"][i]]
            rest //= d["size"][i]
        yield co, v


def etikett(d, dim, kode):
    return d["dimension"][dim]["category"].get("label", {}).get(kode, kode)
