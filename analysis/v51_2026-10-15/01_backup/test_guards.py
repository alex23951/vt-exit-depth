"""Step 1.3 guard tests (v5.1 brief, decision G). Each guard fires in a test call; no real data file is touched.
Run (repo root, venv): PYTHONDONTWRITEBYTECODE=1 python -B -m pytest -p no:cacheprovider analysis/v51_2026-10-15/01_backup/test_guards.py
"""
import importlib.util
import os
import sys

import pytest

os.environ['HEART'] = 'Y5HYEDL4'                     # 14_purkinje / common read the heart at import
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
OLD_CACHE = os.path.join(REPO, 'analysis', 'v5_grid_2026-10-13', 'cache')
HEARTS = ['Y5HYEDL4', '6G8DD8S5', '7D98EVAR']
sys.path.insert(0, os.path.join(REPO, 'sims', 'biv_model'))  # as v5_grid.py: its common.py, not site-packages' common


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


PK = module('pk_test', os.path.join(REPO, 'sims', 'biv_model', '14_purkinje.py'))
VG = module('vgg_test', os.path.join(HERE, 'v5_grid_guarded.py'))


def test_k_file_missing_stops():
    with pytest.raises(FileNotFoundError, match='never fall back to k = 1.0'):
        PK.graph_scale(path='/nonexistent_v51_test/graph_scale.json')


def test_k_file_present_logs_hash(capsys):
    assert PK.graph_scale() == 1.0685
    err = capsys.readouterr().err
    assert 'graph_scale: k = 1.0685' in err and 'sha256 ' in err


def test_wrong_fibre_hash_stops():
    with pytest.raises(ValueError, match='is not the expected'):
        VG.Heart('E', 'Y5HYEDL4', expect_fibre_sha256='0' * 64)


def test_heart_env_mismatch_stops():
    with pytest.raises(ValueError, match='is not 6G8DD8S5'):
        VG.Heart('E', '6G8DD8S5')


@pytest.mark.parametrize('h', HEARTS)
def test_new_key_misses_every_old_cache_entry(h):
    lonf = os.path.join(REPO, 'analysis', 'v5_grid_2026-10-13', 'fibres_E', h, 'bivF.lon')
    sp = VG.speeds('E', h)
    inp, key = VG.cache_inputs(h, lonf, sp)
    old = sorted(os.listdir(OLD_CACHE))
    assert len(old) == 8
    assert f'myo_{h}_{key[:16]}.npz' not in old
    assert all(len(n.split('_')) == 5 for n in old)       # old names: myo_<H>_<E|v3>_<s>_<n>.npz (no hash)
    # the key changes with each input
    assert VG.cache_inputs(h, lonf, (0.60, sp[1], sp[2] + 1e-4))[1] != key
    assert VG.cache_inputs(h, lonf, (0.61, sp[1], sp[2]))[1] != key
    assert VG.cache_inputs(h, os.path.join(REPO, 'data', 'biv', h, 'bivF.lon'), sp)[1] != key
