"""Published 12-lead ECG criteria for an epicardial origin of a PVC or VT,
measured the way each paper defines them."""
from .criteria import CUTOFFS, JOSEPHSON_LV, REGIONS, bazan, evaluate, valles_4step
from .fiducials import Settings
from .leads import LEADS, from_leads
from .measure import measure_beat

__version__ = "0.1.0"
__all__ = [
    "CUTOFFS", "JOSEPHSON_LV", "LEADS", "REGIONS", "Settings",
    "bazan", "evaluate", "from_leads", "measure_beat", "valles_4step",
]
