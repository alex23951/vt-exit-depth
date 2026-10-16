"""EDC_LEGACY_Q=1 runs the tests with the 0.3.0 q rule as the default (q_window_ms=None,
recog_mv=None): test_q_window.py's test (g) uses it to run every 0.3.0 test that way."""
import dataclasses
import os

import pytest

from ecg_depth_criteria import Settings, measure


@pytest.fixture(autouse=True, scope="session")
def _legacy_q_rule():
    if os.environ.get("EDC_LEGACY_Q") != "1":
        yield
        return
    names = [f.name for f in dataclasses.fields(Settings)]
    old_init, old_kw = Settings.__init__.__defaults__, measure.measure_beat.__kwdefaults__["settings"]
    new = list(old_init)
    new[names.index("q_window_ms")] = None
    new[names.index("recog_mv")] = None
    Settings.__init__.__defaults__ = tuple(new)
    measure.measure_beat.__kwdefaults__["settings"] = Settings()
    assert Settings().q_window_ms is None and Settings().recog_mv is None
    yield
    Settings.__init__.__defaults__ = old_init
    measure.measure_beat.__kwdefaults__["settings"] = old_kw
