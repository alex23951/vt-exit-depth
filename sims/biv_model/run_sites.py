#!/usr/bin/env python
"""Run selected grid sites (by id) for one heart with the batch driver's eikonal item, NPAR at
a time, and score them with the current package. Usage: python run_sites.py HEART id1 id2 ..."""
import importlib.util, json, os, sys
from concurrent.futures import ThreadPoolExecutor
B = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('b', os.path.join(B, 'batch_2026-10-03.py'))
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
h, ids = sys.argv[1], set(sys.argv[2:])
sites = [s for s in json.load(open(os.path.join(b.heart_dir(h), 'sites.json'))) if s['id'] in ids]
var = 'lbbb' if h in b.LBBB else 'normal'
with ThreadPoolExecutor(b.NPAR) as ex:
    for s, r in zip(sites, ex.map(lambda s: b.eik_item(h, s, var, False, 'eik'), sites)):
        print(s['id'], r, flush=True)
