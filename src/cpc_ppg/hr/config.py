"""Paper values and explicitly frozen HR reconstruction policies, never label-tuned."""

from dataclasses import dataclass
from numbers import Integral, Real

import numpy as np

from .errors import HRInputError


@dataclass(frozen=True, slots=True, kw_only=True)
class HRConfig:
    fs: float = 125.
    nfft: int = 4096
    search_low_hz: float = .4
    search_high_hz: float = 3.5
    tracking_radius_bins: int = 10
    current_weight: float = .90
    previous_weight: float = .05
    previous2_weight: float = .05
    first_window_policy: str = "global_peak_in_search_band"
    smoothing_startup_policy: str = "leave_first_two_unsmoothed"
    peak_tie_policy: str = "lowest_frequency"
    offline_enabled: bool = False

    def __post_init__(self):
        for name in ("fs", "search_low_hz", "search_high_hz", "current_weight", "previous_weight", "previous2_weight"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, Real) or not np.isfinite(value):
                raise HRInputError(f"{name}: expected finite real scalar")
        if self.fs <= 0 or not 0 <= self.search_low_hz < self.search_high_hz <= self.fs/2:
            raise HRInputError("Expected positive Fs and 0 <= search_low < search_high <= Nyquist")
        for name, minimum in (("nfft", 2), ("tracking_radius_bins", 0)):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, Integral) or value < minimum:
                raise HRInputError(f"{name}: expected integer >= {minimum}")
        weights = (self.current_weight, self.previous_weight, self.previous2_weight)
        if any(not 0 <= value <= 1 for value in weights) or abs(sum(weights)-1.) > 1e-12:
            raise HRInputError("Smoothing weights must be in [0,1] and sum to 1 within 1e-12")
        for name, supported in (("first_window_policy", "global_peak_in_search_band"),
                                ("smoothing_startup_policy", "leave_first_two_unsmoothed"),
                                ("peak_tie_policy", "lowest_frequency")):
            if getattr(self, name) != supported:
                raise HRInputError(f"{name}: only {supported!r} supported")
        if not isinstance(self.offline_enabled, bool):
            raise HRInputError("offline_enabled: expected boolean")
        freq = np.fft.rfftfreq(self.nfft, d=1/self.fs)
        if not ((freq >= self.search_low_hz) & (freq <= self.search_high_hz)).any():
            raise HRInputError("Search band contains no representable rFFT bins")
