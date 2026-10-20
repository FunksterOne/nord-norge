"""Hjelpefunksjon: les JSON-stat2 fra SSB til en ordbok {(kode1, kode2, ...): verdi}."""
import json
from itertools import product
from pathlib import Path


def les(fil):
    d = json.loads(Path(fil).read_text(encoding="utf-8"))
    ids, size = d["id"], d["size"]
    koder = []
    for dim in ids:
        idx = d["dimension"][dim]["category"]["index"]
        if isinstance(idx, dict):
            koder.append(sorted(idx, key=idx.get))
        else:
            koder.append(list(idx))
    etiketter = {dim: d["dimension"][dim]["category"].get("label", {}) for dim in ids}
    verdier = d["value"]
    ut = {}
    for i, k in enumerate(product(*koder)):
        v = verdier[i] if isinstance(verdier, list) else verdier.get(str(i))
        ut[k] = v
    return ids, koder, etiketter, ut
