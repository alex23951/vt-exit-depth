#!/usr/bin/env python
"""
PC jobs of 7 Oct 2026: one resumable command per job, started by Alex (offline is fine).
Job order agreed on 4-5 Oct 2026 (project review thread; no new PC yet, so this one):

  1 nofast_Y5HYEDL4  no-fast-layer control, control heart, full v5 grid (144 sites)
  2 new_Y5HYEDL4     control heart, normal layer: only the v5 sites that are new or moved
                     (75 % depth, new summit, Daniels territory); its CSV is the full 144-site
                     grid, the unchanged sites taken from the v3 runs re-scored with 0.3.0
  3 grid_6G8DD8S5    HF wide-QRS heart, full v5 grid, LBBB-like mesh (old v1 grid superseded)
  4 grid_7D98EVAR    HF narrow-QRS heart, full v5 grid (old v1 grid superseded)
  5-7 mono_<HEART>   monodomain agreement check, 9 beats per heart (batch S3 sites), plus the
                     eikonal run of each heart's original full-beat site
  8 purk_Y5HYEDL4    Purkinje-network arm (added 8 Oct; Alex chose "network run" on 7 Oct): all 144
                     sites with the His-Purkinje network of 14_purkinje.py (fast layer off), each
                     starting from its job-1 no-fast-layer activation
  9-10 purk_<HEART>  the network grid on the other two hearts (added 9 Oct; Alex chose the network as
                     the study's conduction model, 9 Oct 15:39 UTC). No job-1 grid there: the no-layer
                     field is only read for the summary when it exists. Needs the heart's network
                     (14_purkinje.py build), its graph scale (calib) and no-layer ECG weights.

Every beat goes through the batch driver's own items (batch_2026-10-03.py: eik_item,
mono_item; same model, weights and pseudo-Vm template as the pilot grids) and is scored by
10_measure_ecg.py with ecg_depth_criteria 0.3.0 in both onset modes (detected and true).
Run folders: runs/2026-10-07_<tag>_<HEART>_<site id>[_ecg]. Job folder runs/jobs_2026-10-07/<job>/
holds driver.log, progress.jsonl (one line per finished or failed beat), console.log, PAUSE.
CSV: analysis/grids_2026-10-07/<job>.csv, rebuilt at the end of every session (also partial).

Resume: start the job again; beats with a criteria.json are skipped, failed ones retried.
Pause: create runs/jobs_2026-10-07/<job>/PAUSE (jobs/stop.sh); running beats finish first.

Usage (the jobs/*.sh wrappers set up the environment):
  python jobs_2026-10-07.py <1-10>             run or resume
  python jobs_2026-10-07.py <1-10> --dry-run    check prerequisites and list the work, run nothing
  python jobs_2026-10-07.py <1-10> --only ID..  run just these site ids (smoke test)
  python jobs_2026-10-07.py <1-10> --csv        rebuild the CSV from finished beats
  python jobs_2026-10-07.py --status           one line per job, times in the PC's local time
"""

import argparse
import csv
import importlib.util
import json
import math
import os
import re
import sys
import time

B = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(B, '..', '..'))
JD = os.path.join(REPO, 'runs', 'jobs_2026-10-07')
CSV_DIR = os.path.join(REPO, 'analysis', 'grids_2026-10-07')
PKG = os.path.join(REPO, 'code', 'ecg_depth_criteria')
PREFIX = '2026-10-07'
LBBB = {'6G8DD8S5'}
JOBS = {1: ('nofast_Y5HYEDL4', 'Y5HYEDL4', 'nofast'), 2: ('new_Y5HYEDL4', 'Y5HYEDL4', 'new'),
        3: ('grid_6G8DD8S5', '6G8DD8S5', 'grid'), 4: ('grid_7D98EVAR', '7D98EVAR', 'grid'),
        5: ('mono_Y5HYEDL4', 'Y5HYEDL4', 'mono'), 6: ('mono_6G8DD8S5', '6G8DD8S5', 'mono'),
        7: ('mono_7D98EVAR', '7D98EVAR', 'mono'), 8: ('purk_Y5HYEDL4', 'Y5HYEDL4', 'purk'),
        9: ('purk_6G8DD8S5', '6G8DD8S5', 'purk'), 10: ('purk_7D98EVAR', '7D98EVAR', 'purk')}
GUESS_S = {'mono': 2700.0}            # per-beat guess before any beat has finished; eikonal: 70 s
AMPS = {'q_amplitude_mv': 'q_amp', 'r_amplitude_mv': 'r_amp', 's_amplitude_mv': 's_amp'}
_b = None


def batch():
    """The pilot batch driver as a module, redirected to this job's folder and prefix."""
    global _b
    if _b is None:
        spec = importlib.util.spec_from_file_location('batch_2026_10_03', os.path.join(B, 'batch_2026-10-03.py'))
        _b = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_b)
        _b.P = PREFIX
        _b.ENV0['ECG_PKG'] = PKG
    return _b


def heart_dir(h):
    return os.path.join(REPO, 'data', 'biv', h)


def sites(h):
    return json.load(open(os.path.join(heart_dir(h), 'sites.json')))


def variant(h):
    return 'lbbb' if h in LBBB else 'normal'


def v3_runs():
    """Control heart v3 grid runs (re-scored with 0.3.0 in the v4 table): id -> (prefix, node)."""
    old = {s['id']: s['node'] for s in json.load(open(os.path.join(heart_dir('Y5HYEDL4'), 'sites_v3.json')))}
    pref = {r['id']: r['run_prefix'] for r in csv.DictReader(open(os.path.join(REPO, 'analysis', 'pilot_grid_sites_v4.csv')))}
    return {i: (pref[i], n) for i, n in old.items() if i in pref}


def purk_tag(h):
    """Run tag of a network beat from the heart's network version: 'purk' = v3 (job 8), 'purk4' = v4 (Durrer-calibrated)."""
    f = os.path.join(heart_dir(h), 'purkinje', 'summary.json')
    v = json.load(open(f)).get('network_version', 'v3') if os.path.exists(f) else 'v3'
    return 'purk' if v == 'v3' else 'purk' + v[1:]


def plan(n):
    """Work list of job n: [(item name, kind, heart, site, tag, run id)]."""
    name, h, kind = JOBS[n]
    S = sites(h)
    if kind == 'nofast':
        return [(f'{name} {s["id"]}', 'eik', h, s, 'nofast', f'{PREFIX}_nofast_{h}_{s["id"]}') for s in S]
    if kind == 'purk':                      # slow beats: the depth-question families first, so a partial run is usable
        order = {'lv_free_wall': 0, 'lv_summit': 1, 'lv_vein_course': 2, 'rvot': 3, 'aortic_cusp': 4, 'lv_septum': 5, 'rv_free_wall': 6}
        S = sorted(S, key=lambda s: order[s['family']])
        t = purk_tag(h)
        return [(f'{name} {s["id"]}', 'purk', h, s, t, f'{PREFIX}_{t}_{h}_{s["id"]}') for s in S]
    if kind == 'new':
        old = v3_runs()
        S = [s for s in S if s['id'] not in old or old[s['id']][1] != s['node']]
    if kind in ('new', 'grid'):
        return [(f'{name} {s["id"]}', 'eik', h, s, 'eik', f'{PREFIX}_eik_{h}_{s["id"]}') for s in S]
    ag = batch().agreement_sites(h, S)
    return ([(f'{name} eik original', 'eik', h, ag[0], 'eik', f'{PREFIX}_eik_{h}_{ag[0]["id"]}')] +
            [(f'{name} mono {s["id"]}', 'mono', h, s, 'mono', f'{PREFIX}_mono_{h}_{s["id"]}') for s in ag])


def done(rid):
    return os.path.exists(os.path.join(REPO, 'runs', rid + '_ecg', 'criteria.json'))


def check(n):
    """Prerequisites; returns a list of problems (empty = ready)."""
    name, h, kind = JOBS[n]
    bad = []
    S = sites(h)
    if 'region_study' not in S[0] or len(S) != 144:
        bad.append(f'{h}: sites.json is not the v5 grid (run 11_site_grid.py)')
    tmpl = os.path.join(REPO, 'runs', '2026-10-02_biv_fullqrs' if h == 'Y5HYEDL4' else f'2026-10-03_{h}_fullqrs')
    if kind != 'mono' and not os.path.exists(os.path.join(tmpl, 'vm.igb')):
        bad.append(f'missing template beat {tmpl}/vm.igb')
    if kind == 'mono' and not os.path.exists(os.path.join(tmpl, 'summary_06.json')):
        bad.append(f'missing {tmpl}/summary_06.json')
    if kind == 'purk':
        if not os.path.exists(os.path.join(heart_dir(h), 'purkinje', 'network.npz')):
            bad.append(f'missing Purkinje network data/biv/{h}/purkinje (14_purkinje.py build)')
        if not os.path.exists(os.path.join(heart_dir(h), 'purkinje', 'graph_scale.json')):
            bad.append(f'missing graph scale data/biv/{h}/purkinje/graph_scale.json (14_purkinje.py calib)')
    w = 'nofast' if kind in ('nofast', 'purk') else variant(h)
    if not os.path.exists(os.path.join(heart_dir(h), f'ecgW_{w}.npz')):
        bad.append(f'missing ECG weights data/biv/{h}/ecgW_{w}.npz')
    if variant(h) == 'lbbb' and not os.path.exists(os.path.join(heart_dir(h), 'bivF_lbbb.elem')):
        bad.append(f'missing LBBB-like mesh data/biv/{h}/bivF_lbbb')
    ver = re.search(r'__version__ = "([^"]+)"', open(os.path.join(PKG, 'ecg_depth_criteria', '__init__.py')).read())
    if not ver or ver.group(1) != '0.3.0':
        bad.append(f'code/ecg_depth_criteria is not 0.3.0 ({ver and ver.group(1)})')
    for m, (other, _, _) in JOBS.items():
        if m != n and alive(other):
            bad.append(f'job {m} ({other}) is still running; run one job at a time')
    return bad


def alive(name):
    f = os.path.join(JD, name, 'pid')
    if not os.path.exists(f):
        return False
    pid = open(f).read().strip()
    try:
        return 'jobs_2026-10-07' in open(f'/proc/{pid}/cmdline').read()
    except OSError:
        return False


def purk_item(h, site, rid):
    """Network beat (14_purkinje.py site): starts from the site's job-1 activation, then one eikonal run."""
    b = batch()
    ecg = rid + '_ecg'
    if done(rid):
        return 'skip'
    os.makedirs(os.path.join(REPO, 'runs', rid), exist_ok=True)
    t0 = os.path.join(REPO, 'runs', f'{PREFIX}_nofast_{h}_{site["id"]}')
    b.sh([b.PY, '14_purkinje.py', 'site', '--ID', rid, '--site-node', site['node'],
          '--ecg-dir', os.path.join(REPO, 'runs', ecg, 'POSTPROC_DIR')]
         + (['--t0-run', t0] if os.path.exists(os.path.join(t0, 'act.igb')) else []), h, os.path.join(REPO, 'runs', rid, 'driver_purk.log'))
    s = json.load(open(os.path.join(REPO, 'runs', rid, 'summary_12.json')))
    b.score(h, ecg, s['total_activation_ms'], site.get('bazan_region'))
    return {'run': rid, 'total_activation_ms': s['total_activation_ms'], 'sim_wall_s': s['sim_wall_s'],
            'pmj_exits': s.get('pmj_exits'), 'second_pass_max_gain_ms': s.get('second_pass_max_gain_ms')}


# ---------------------------------------------------------------- CSV
def fmt(v):
    if isinstance(v, float) and math.isinf(v):
        return 'inf' if v > 0 else '-inf'
    return v


def flatten(d):
    out = {'package_version': d['package_version']}
    for m in ('detected', 'true'):
        for k, val in d[m]['measurements'].items():
            if k in AMPS:
                for lead, a in val.items():
                    out[f'{m}_{AMPS[k]}_{lead}'] = fmt(a)
            elif not isinstance(val, (dict, list)):
                out[f'{m}_{k}'] = fmt(val)
        for k, val in d[m]['criteria'].items():
            out[f'{m}_{k}'] = fmt(val)
    return out


def result_row(h, s, rid, crit_name, method):
    run = os.path.join(REPO, 'runs', rid)
    cf = os.path.join(run + '_ecg', crit_name)
    if not os.path.exists(cf):
        return None
    summ = os.path.join(run, 'summary_06.json' if method == 'mono' else 'summary_12.json')
    sm = json.load(open(summ)) if os.path.exists(summ) else {}
    row = {'heart': h, 'method': method, 'run': rid, 'criteria_file': crit_name,
           'total_activation_ms': sm.get('total_activation_ms', sm.get('latest_activation_so_far_ms')),
           'sim_wall_s': sm.get('sim_wall_s')}
    row.update({k: v for k, v in s.items()})
    row.update(flatten(json.load(open(cf))))
    return row


def eik_source(h, s, v3):
    """Normal-layer eikonal run of a site: this job series' run, else (control heart) the v3 run."""
    rid = f'{PREFIX}_eik_{h}_{s["id"]}'
    if done(rid):
        return rid, 'criteria.json'
    if h == 'Y5HYEDL4' and s['id'] in v3 and v3[s['id']][1] == s['node']:
        return f'{v3[s["id"]][0]}_eik_{h}_{s["id"]}', 'criteria_v030.json'
    return None, None


def write_csv(n):
    name, h, kind = JOBS[n]
    rows = []
    v3 = v3_runs() if h == 'Y5HYEDL4' else {}
    if kind in ('nofast', 'purk'):
        rows = [result_row(h, s, rid, 'criteria.json', 'eik' if kind == 'nofast' else 'purk') for _, _, _, s, _, rid in plan(n)]
    elif kind in ('new', 'grid'):
        for s in sites(h):                              # the whole v5 grid, newest run per site
            rid, cf = eik_source(h, s, v3)
            rows.append(result_row(h, s, rid, cf, 'eik') if rid else None)
    else:
        for _, k, _, s, _, rid in plan(n):              # mono beat, then its eikonal twin
            if k == 'mono':
                rows.append(result_row(h, s, rid, 'criteria.json', 'mono'))
                erid, cf = eik_source(h, s, v3)
                rows.append(result_row(h, s, erid, cf, 'eik') if erid else None)
    rows = [r for r in rows if r]
    os.makedirs(CSV_DIR, exist_ok=True)
    path = os.path.join(CSV_DIR, f'{name}{"_" + purk_tag(h) if kind == "purk" and purk_tag(h) != "purk" else ""}.csv')
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    return path, len(rows)


# ---------------------------------------------------------------- status
def hm(s):
    s = int(round(s / 60.0))
    return f'{s // 60} h {s % 60:02d} min' if s >= 60 else f'{s} min'


def status_line(n):
    name, h, kind = JOBS[n]
    P = plan(n)
    total, ndone = len(P), sum(done(rid) for *_, rid in P)
    d = os.path.join(JD, name)
    prog = [json.loads(l) for l in open(os.path.join(d, 'progress.jsonl'))] if os.path.exists(os.path.join(d, 'progress.jsonl')) else []
    names = {p[0] for p in P}
    failed = sorted({p['item'] for p in prog if p['status'] == 'failed' and p['item'] in names} -
                    {p[0] for p in P if done(p[5])})
    unit = 'beats' if kind == 'mono' else 'sites'
    line = f'Job {n}  {name:16s} '
    if alive(name):
        start = float(open(os.path.join(d, 'started_epoch')).read())
        new = [p for p in prog if p['status'] == 'ok' and time.mktime(time.strptime(p['t'], '%Y-%m-%d %H:%M:%S')) >= start - 1]
        el = time.time() - start
        per = el / len(new) if new else GUESS_S.get(kind, 70.0)
        left = (total - ndone) * per
        state = 'PAUSING (finishing the beats now running)' if os.path.exists(os.path.join(d, 'PAUSE')) else 'RUNNING'
        line += (f'{state}: {ndone}/{total} {unit} done, {len(failed)} failed; '
                 f'about {hm(left)} left (finish ~{time.strftime("%H:%M", time.localtime(time.time() + left))})'
                 + ('' if new else ', rough guess until the first one finishes'))
    elif total and ndone == total:
        line += f'DONE: {ndone}/{total} {unit}; CSV analysis/grids_2026-10-07/{name}.csv'
    elif ndone or prog:
        line += f'STOPPED: {ndone}/{total} {unit} done, {len(failed)} failed (resume: bash jobs/start.sh {n})'
    else:
        line += f'not started ({total} {unit})'
    if failed:
        line += '\n        failed: ' + ', '.join(f.split(' ', 1)[1] for f in failed[:6]) + (' ...' if len(failed) > 6 else '')
    return line


# ---------------------------------------------------------------- run
def run(n, only=None, dry=False):
    name, h, kind = JOBS[n]
    d = os.path.join(JD, name)
    os.makedirs(d, exist_ok=True)
    bad = check(n)
    P = plan(n)
    if only:
        P = [p for p in P if p[3]['id'] in only]
    todo = [p for p in P if not done(p[5])]
    print(f'Job {n} {name}: {len(P)} items, {len(P) - len(todo)} already done, {len(todo)} to run')
    if bad:
        print('NOT READY:\n  ' + '\n  '.join(bad))
        sys.exit(1)
    if dry:
        for p in todo[:5]:
            print('  e.g.', p[0], '->', p[5])
        return
    b = batch()
    b.BD = d
    if os.path.exists(os.path.join(d, 'PAUSE')):
        os.remove(os.path.join(d, 'PAUSE'))
    open(os.path.join(d, 'pid'), 'w').write(str(os.getpid()))
    open(os.path.join(d, 'started_epoch'), 'w').write(str(time.time()))
    b.log(f'job {n} {name} start (pid {os.getpid()}), {len(todo)} of {len(P)} to run' + (f', only {sorted(only)}' if only else ''))
    var = variant(h)
    eik = [(p[0], b.eik_item, (h, p[3], 'normal' if kind == 'nofast' else var, kind == 'nofast', p[4]))
           for p in todo if p[1] == 'eik']
    try:
        if kind == 'mono':                               # one beat at a time (monodomain uses 6 cores)
            for it in eik:
                b.run_item(it[0], it[1], *it[2])
            for p in todo:
                if p[1] == 'mono' and not b.paused():
                    b.run_item(p[0], b.mono_item, h, p[3], var)
        elif kind == 'purk':                             # 2 at a time (6.8 of 7.9 GB); 3 ran out of memory (8 Oct)
            b.NPAR = int(os.environ.get('PURK_NPAR', '2'))
            b.run_parallel([(p[0], purk_item, (h, p[3], p[5])) for p in todo])
        else:
            b.run_parallel(eik)                          # 3 eikonal beats at a time
        path, nrows = write_csv(n)
        ndone = sum(done(p[5]) for p in plan(n))
        b.log(f'job {n} {name} stop: {ndone}/{len(plan(n))} done; CSV {path} ({nrows} rows)')
    finally:
        os.remove(os.path.join(d, 'pid'))
    print(status_line(n))


def main():
    a = argparse.ArgumentParser()
    a.add_argument('job', nargs='?')
    a.add_argument('--dry-run', action='store_true')
    a.add_argument('--csv', action='store_true')
    a.add_argument('--status', action='store_true')
    a.add_argument('--check', action='store_true')
    a.add_argument('--dir', action='store_true')
    a.add_argument('--only', nargs='+')
    x = a.parse_args()
    if x.status or x.job is None:
        print(time.strftime('PC jobs, %d %b %H:%M (PC time)'))
        for n in JOBS:
            print(status_line(n))
        return
    n = int(x.job) if x.job.isdigit() else next(k for k, v in JOBS.items() if v[0] == x.job)
    if x.dir:
        print(os.path.join(JD, JOBS[n][0]))
    elif x.check:
        bad = check(n)
        print('\n'.join(bad) if bad else 'ready')
        sys.exit(1 if bad else 0)
    elif x.csv:
        print(write_csv(n))
    else:
        run(n, set(x.only) if x.only else None, x.dry_run)


if __name__ == '__main__':
    main()
