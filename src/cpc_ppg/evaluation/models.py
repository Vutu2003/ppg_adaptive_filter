"""Scalar summaries and small HR trajectories; no retained cleaned waveforms."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True, eq=False)
class BlandAltmanResult:
    mean_pair: np.ndarray
    difference: np.ndarray
    bias_bpm: float
    sd_diff_bpm: float
    loa_lower_bpm: float
    loa_upper_bpm: float
    inside_count: int
    inside_percent: float
    ddof: int

    def summary(self):
        return {"n_windows": self.difference.size, "bias_bpm": self.bias_bpm,
                "sd_diff_bpm": self.sd_diff_bpm, "loa_lower_bpm": self.loa_lower_bpm,
                "loa_upper_bpm": self.loa_upper_bpm, "loa_inside_count": self.inside_count,
                "loa_inside_percent": self.inside_percent, "ddof": self.ddof}
