#!/usr/bin/env python3
"""Felles hjelpefunksjoner for aa lese og skrive den store `const DATA = {...};`-
linjen i assets/data.js (linjen uten BEGIN/END-markoerer).

Linjen skrives tilbake med samme kompakte JSON-format som den ble lest i
(separators=(",", ":"), ensure_ascii=False), slik at diffen kun viser reelle
endringer. Bruk `roundtrip_ok()` for aa kontrollere at formatet bevares.
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
DATA_JS = HERE / "assets" / "data.js"
PREFIX = "const DATA = "


def _split():
    js = DATA_JS.read_text(encoding="utf-8")
    linjer = js.split("\n")
    idx = next(i for i, l in enumerate(linjer) if l.startswith(PREFIX))
    return linjer, idx


def load_data():
    linjer, idx = _split()
    return json.loads(linjer[idx][len(PREFIX):].rstrip().rstrip(";"))


def dump(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def roundtrip_ok():
    linjer, idx = _split()
    raw = linjer[idx][len(PREFIX):].rstrip().rstrip(";")
    return dump(json.loads(raw)) == raw


def save_data(D):
    linjer, idx = _split()
    linjer[idx] = PREFIX + dump(D) + ";"
    DATA_JS.write_text("\n".join(linjer), encoding="utf-8")


if __name__ == "__main__":
    print("Round-trip identisk:", roundtrip_ok())
