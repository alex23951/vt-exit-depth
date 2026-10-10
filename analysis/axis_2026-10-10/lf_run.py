"""Diagnostic lead fields for the superior-axis question (10 Oct 2026), control heart Y5HYEDL4.

Same command structure as sims/biv_model/08_torso.py leadfield (gregions 1 / 2 / 100 in the same order, imp and
phys regions with tags 1 and 2), plus a 4th gregion for tag 101 (cavity blood, mesh full_nofast_blood).
Usage: python lf_run.py <run_id> <mesh> <heart_scale> <g_blood> [np]
  heart_scale divides every heart g_i and g_e of calibration.json (4.08 puts the fibre values at Clerc 1976);
  g_blood is the tag-101 conductivity (S/m); torso stays 0.2 S/m.
Env: LF_CONFIG (3 = I, II, III only; default 12), ELLIP_OPTS (PETSc options file).
Vm projection: vm_first10ms.igb (first 10 ms of the template beat) to keep memory low."""
import json
import os
import subprocess
import sys

sys.path.insert(0, '/home/alex/vt-exit-depth/sims/biv_model')
from common import OUT, REPO  # noqa: E402
from carputils.leadfield import leadfield_setup  # noqa: E402

rid_name, full, scale, g_blood = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
np_ = int(sys.argv[5]) if len(sys.argv) > 5 else 2
HERE = os.path.dirname(os.path.abspath(__file__))
TOR = os.path.join(OUT, 'torso')
cal = json.load(open(os.path.join(OUT, 'calibration.json')))
G = {k: (cal[c]['gi'] / scale, cal[c]['ge'] / scale) for k, c in (('f', 'fibre'), ('s', 'sheet'), ('n', 'sheet_normal'))}
fast = (cal['fast_layer']['2.0']['gi'], cal['fast_layer']['2.0']['ge'])        # tag 2 is empty in the no-layer meshes
rid = os.path.join(REPO, 'runs', rid_name)
os.makedirs(rid, exist_ok=True)
LFC = int(os.environ.get('LF_CONFIG', '12'))
stim, elec, opts = leadfield_setup(LFC, os.path.join(TOR, 'electrodes'), lf_vmfile=os.path.join(HERE, 'vm_first10ms.igb'), ecg_timedt=10)
g = ['-num_gregions', 4,
     '-gregion[0].num_IDs', 1, '-gregion[0].ID[0]', 1,
     '-gregion[0].g_il', G['f'][0], '-gregion[0].g_el', G['f'][1], '-gregion[0].g_it', G['s'][0], '-gregion[0].g_et', G['s'][1],
     '-gregion[0].g_in', G['n'][0], '-gregion[0].g_en', G['n'][1],
     '-gregion[1].num_IDs', 1, '-gregion[1].ID[0]', 2]
for k in ('l', 't', 'n'):
    g += [f'-gregion[1].g_i{k}', fast[0], f'-gregion[1].g_e{k}', fast[1]]
g += ['-gregion[2].num_IDs', 1, '-gregion[2].ID[0]', 100]
for k in ('l', 't', 'n'):
    g += [f'-gregion[2].g_i{k}', 0.2, f'-gregion[2].g_e{k}', 0.2]
g += ['-gregion[3].num_IDs', 1, '-gregion[3].ID[0]', 101]
for k in ('l', 't', 'n'):
    g += [f'-gregion[3].g_i{k}', g_blood, f'-gregion[3].g_e{k}', g_blood]
phys = ['-num_phys_regions', 2,
        '-phys_region[0].ptype', 0, '-phys_region[0].num_IDs', 2, '-phys_region[0].ID[0]', 1, '-phys_region[0].ID[1]', 2,
        '-phys_region[1].ptype', 1, '-phys_region[1].num_IDs', 4, '-phys_region[1].ID[0]', 1, '-phys_region[1].ID[1]', 2,
        '-phys_region[1].ID[2]', 100, '-phys_region[1].ID[3]', 101]
cmd = ['mpiexec', '-n', np_, 'openCARP', '-meshname', os.path.join(TOR, full), '-simID', rid,
       '-bidomain', 0, '-dt', 10, '-tend', 10,
       '-num_imp_regions', 1, '-imp_region[0].im', 'Tomek', '-imp_region[0].num_IDs', 2,
       '-imp_region[0].ID[0]', 1, '-imp_region[0].ID[1]', 2] + g + phys + stim + elec + opts
if os.environ.get('ELLIP_OPTS'):                       # memory-light AMG (10 Oct; the default needed ~7 GB)
    cmd += ['-ellip_options_file', os.environ['ELLIP_OPTS']]
json.dump({'heart_scale': scale, 'g_blood': g_blood, 'G_heart': G, 'mesh': full, 'np': np_, 'lf_config': LFC, 'ellip_opts': os.environ.get('ELLIP_OPTS')}, open(os.path.join(rid, 'variant.json'), 'w'), indent=1)
with open(os.path.join(rid, 'openCARP.log'), 'w') as log:
    r = subprocess.run([str(c) for c in cmd], stdout=log, stderr=subprocess.STDOUT)
print(rid, 'exit', r.returncode)
sys.exit(r.returncode)
