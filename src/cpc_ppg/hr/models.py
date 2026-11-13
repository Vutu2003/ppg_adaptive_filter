"""Compact spectra and immutable per-window/recording estimates; no waveform retention."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True, slots=True, eq=False)
class PeriodogramResult:
    bins: NDArray[np.int64]
    frequencies_hz: NDArray[np.float64]
    power: NDArray[np.float64]
    fs: float
    nfft: int
    n_samples: int


@dataclass(frozen=True, slots=True)
class HRWindowEstimate:
    record_id: str
    index: int
    start_sample: int
    end_sample: int
    start_time_s: float
    end_time_s: float
    selected_bin: int
    selected_frequency_hz: float
    raw_hr_bpm: float
    smoothed_hr_bpm: float
    offline_hr_bpm: float | None
    bpm: float | None = None  # metadata only; never participates in HR calculations


@dataclass(frozen=True, slots=True)
class HRRecordingResult:
    record_id: str
    windows: tuple[HRWindowEstimate, ...]

    def _series(self, name, dtype=np.float64):
        values = np.asarray([getattr(w, name) for w in self.windows], dtype=dtype)
        values.setflags(write=False)
        return values

    @property
    def selected_bins(self):
        return self._series("selected_bin", np.int64)

    @property
    def raw_hr_bpm(self):
        return self._series("raw_hr_bpm")

    @property
    def smoothed_hr_bpm(self):
        return self._series("smoothed_hr_bpm")

    @property
    def offline_hr_bpm(self):
        return None if not self.windows or self.windows[0].offline_hr_bpm is None else self._series("offline_hr_bpm")
