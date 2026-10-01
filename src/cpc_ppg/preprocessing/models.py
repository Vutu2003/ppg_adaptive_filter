"""Preprocessing output separate from raw Phase 2A objects."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


@dataclass(frozen=True, slots=True, eq=False)
class PreprocessedWindow:
    """Filtered float64 buffers and copied alignment metadata; no raw copies."""

    record_id: str
    index: int
    start_sample: int
    end_sample: int
    start_time_s: float
    end_time_s: float
    bpm: float
    ppg1_filtered: FloatArray
    ppg2_filtered: FloatArray
    ppg_avg: FloatArray
    acc_x_filtered: FloatArray
    acc_y_filtered: FloatArray
    acc_z_filtered: FloatArray
    fs: int
    low_hz: float
    high_hz: float
