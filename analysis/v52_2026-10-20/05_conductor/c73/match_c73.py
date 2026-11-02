"""C73 (4)'s match at the CT pose, from rimcap.py's outputs (ref_<H>.json, ref_<H>_<vessel>_surface.npz).

Per heart and vessel: rim nodes walked / distinct, rim sha256 (sorted walked ids, int64 little-endian), closed-surface pinch
edges (edges of more than two of its triangles; how many run from a fan apex to a node its loop passes twice), unpaired
directed edges, volume to 0.001 mL; all against C73's table. Exit status 1 on any mismatch.
usage: python -I match_c73.py C73_DIR
"""
import hashlib, json, sys
from collections import Counter
import numpy as np

REF = {('Y5HYEDL4', 'aorta'): (166, 165, 'd60e9b735a86fb8eb04c6ec77565500a99c6479fbbfdf3ca969d905138057bcc', 14.9224, 10, 8),
       ('Y5HYEDL4', 'PA'): (149, 142, '620156320cc797bdfa6339f32559dcbe7dd2166520a20670f66dd8ce090c29a4', 4.4917, 10, 7),
       ('6G8DD8S5', 'aorta'): (222, 216, 'd98e868d67837074f2383a66b7704e4d8244e40cea084de079eaa4f2ec8959d8', 28.7744, 10, 8),
       ('6G8DD8S5', 'PA'): (171, 169, '6665d91153c629a241734f7df1dfeab1ecdff1d31c1db900b2eea2b4d662de8c', 11.8278, 2, 2),
       ('7D98EVAR', 'aorta'): (179, 177, '0d962eaa3652fe87c62260eaefe36f0ffd825c027efd1549635ec86723c5cb60', 18.5132, 5, 5),
       ('7D98EVAR', 'PA'): (90, 90, 'aef3518a696c7d778b5354fcac6b9f93e4568acd958799e57f0d17b8f894f8dd', 5.2065, 0, 0)}
D = sys.argv[1]
out, ok_all = {}, True
for (h, v), (rw, rd, rsha, vol, npinch, napex) in REF.items():
    js = json.load(open(f'{D}/ref_{h}.json'))
    z = np.load(f'{D}/ref_{h}_{v}_surface.npz')
    T, rim, N = z['tris'], z['rim'], js['nodes']
    sha = hashlib.sha256(np.sort(np.array(rim, dtype='<i8')).tobytes()).hexdigest()
    E = np.sort(np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]), axis=1)
    cnt = Counter(map(tuple, E.tolist()))
    pinch = [e for e, c in cnt.items() if c > 2]
    # an apex-to-twice-walked-node pinch edge: one end is a fan apex (id >= N), the other a node its loop walks twice;
    # the loop of apex N + k is the k-th loop; only the rim's loop is saved, so count apex edges whose node is walked twice
    # in the rim or in any loop (a node of a hole walked twice): read from the fan triangles themselves
    apex_pinch = 0
    for a_, b_ in pinch:
        ap, nd = (b_, a_) if b_ >= N else ((a_, b_) if a_ >= N else (None, None))
        if ap is None: continue
        fan = T[(T[:, 2] == ap)]
        if (fan[:, 0] == nd).sum() >= 2: apex_pinch += 1
    de = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]])
    sde = set(map(tuple, de.tolist())); unpaired = sum((y, x) not in sde for x, y in sde)
    r = js[v]
    m = {'rim_walked': [len(rim), rw], 'rim_distinct': [len(set(rim.tolist())), rd], 'rim_sha256': [sha, rsha],
         'pinch_edges': [len(pinch), npinch], 'pinch_edges_apex_to_twice_walked_node': [apex_pinch, napex],
         'unpaired_directed_edges': [unpaired, 0], 'volume_mL': [r['volume_mL'], vol]}
    ok = (len(rim) == rw and len(set(rim.tolist())) == rd and sha == rsha and len(pinch) == npinch and apex_pinch == napex
          and unpaired == 0 and abs(r['volume_mL'] - vol) <= 0.001)
    m['match'] = bool(ok); ok_all &= ok
    m['holes'] = len(r['holes']); m['ring_top_mm'] = r['ring_top_mm']
    out[f'{h} {v}'] = m
    print(h, v, 'MATCH' if ok else 'MISMATCH', json.dumps({k: m[k] for k in m if k != 'rim_sha256'}), sha[:16], flush=True)
json.dump({'all_match': bool(ok_all), 'per_vessel': out}, open(f'{D}/match_c73.json', 'w'), indent=1)
sys.exit(0 if ok_all else 1)
