"""Raw Training records, paired paths and aligned windows."""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

NumericArray = NDArray[np.generic]


@dataclass(frozen=True, slots=True)
class TrainingPair:
    """Signal and BPMtrace files sharing a canonical record identifier."""

    record_id: str
    signal_path: Path
    label_path: Path


@dataclass(frozen=True, slots=True, eq=False)
class TrainingRecord:
    """Extracted raw channels and labels; loaded arrays are read-only views."""

    record_id: str
    signal_path: Path
    label_path: Path
    fs: int
    ecg: NumericArray
    ppg1: NumericArray
    ppg2: NumericArray
    acc_x: NumericArray
    acc_y: NumericArray
    acc_z: NumericArray
    bpm: NumericArray

    @property
    def n_samples(self) -> int:
        """Number of raw samples in each signal channel."""
        return self.ecg.size

    @property
    def duration_s(self) -> float:
        """Recording duration computed from the confirmed sampling rate."""
        return self.n_samples / self.fs


@dataclass(frozen=True, slots=True, eq=False)
class TrainingWindow:
    """One full raw window and its supplied BPM0 label (no transformation)."""

    record_id: str
    index: int
    start_sample: int
    end_sample: int
    start_time_s: float
    end_time_s: float
    ecg: NumericArray
    ppg1: NumericArray
    ppg2: NumericArray
    acc_x: NumericArray
    acc_y: NumericArray
    acc_z: NumericArray
    bpm: float


@dataclass(frozen=True, slots=True)
class AlignmentSummary:
    """Validated counts and half-open bounds; bounds are None for zero windows."""

    record_id: str
    n_samples: int
    bpm_count: int
    expected_windows: int
    first_start: int | None
    first_end: int | None
    last_start: int | None
    last_end: int | None
