"""Published 12-lead ECG criteria for an epicardial origin of a PVC or VT,
measured the way each paper defines them."""
from .criteria import CUTOFFS, CUTOFFS_BELOW, JOSEPHSON_LV, REGIONS, SUMMIT, bazan, evaluate, summit, valles_4step
from .fiducials import Settings
from .leads import LEADS, from_leads
from .measure import measure_beat

__version__ = "0.4.0"
__all__ = [
    "CUTOFFS", "CUTOFFS_BELOW", "JOSEPHSON_LV", "LEADS", "REGIONS", "SUMMIT", "Settings",
    "bazan", "evaluate", "from_leads", "measure_beat", "summit", "valles_4step",
]
