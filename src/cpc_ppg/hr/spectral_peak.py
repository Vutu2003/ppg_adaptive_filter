"""Zero-based bin conversion, band-constrained peaks and inclusive previous-bin search."""

from numbers import Integral

import numpy as np

from .config import HRConfig
from .errors import HRInputError, HRTrackingError
from .models import PeriodogramResult


def _bin(k, config):
    if not isinstance(config, HRConfig):
        raise HRInputError("Expected HRConfig")
    if isinstance(k, bool) or not isinstance(k, Integral) or not 0 <= k <= config.nfft//2:
        raise HRInputError("Expected zero-based integer k within rFFT layout")
    return int(k)


def bin_to_hz(k: int, config: HRConfig = HRConfig()) -> float:
    return _bin(k, config)*config.fs/config.nfft


def bin_to_bpm(k: int, config: HRConfig = HRConfig()) -> float:
    """Paper N=k+1: (N-1)*60*Fs/NF = k*60*Fs/NF, no extra index shift."""
    return _bin(k, config)*60*config.fs/config.nfft


def search_band_bins(config: HRConfig = HRConfig()) -> np.ndarray:
    if not isinstance(config, HRConfig):
        raise HRInputError("Expected HRConfig")
    f = np.fft.rfftfreq(config.nfft, d=1/config.fs)
    bins = np.flatnonzero((f >= config.search_low_hz) & (f <= config.search_high_hz))
    bins.setflags(write=False)
    return bins


def tracking_candidates(previous_bin: int, config: HRConfig = HRConfig()) -> np.ndarray:
    previous = _bin(previous_bin, config)
    bins = search_band_bins(config)
    candidates = bins[(bins >= previous-config.tracking_radius_bins) &
                      (bins <= previous+config.tracking_radius_bins)]
    if candidates.size == 0:
        raise HRTrackingError("No candidates in previous-bin neighborhood intersected with search band; no fallback")
    candidates.setflags(write=False)
    return candidates


def _peak(periodogram: PeriodogramResult, candidates, config):
    if not isinstance(periodogram, PeriodogramResult):
        raise HRInputError("Expected PeriodogramResult")
    if any(not isinstance(a, np.ndarray) for a in (periodogram.bins, periodogram.frequencies_hz, periodogram.power)):
        raise HRInputError("Periodogram bins/frequencies/power must be ndarrays")
    size = config.nfft//2+1
    if periodogram.fs != config.fs or periodogram.nfft != config.nfft or any(
        np.shape(a) != (size,) for a in (periodogram.bins, periodogram.frequencies_hz, periodogram.power)
    ):
        raise HRInputError("Periodogram/config/layout mismatch")
    if not np.array_equal(periodogram.bins, np.arange(size)) or not np.array_equal(
        periodogram.frequencies_hz, np.fft.rfftfreq(config.nfft, d=1/config.fs)
    ):
        raise HRInputError("Malformed periodogram bin/frequency grid")
    if periodogram.power.dtype.kind not in "iuf" or not np.isfinite(periodogram.power).all() or (periodogram.power < 0).any():
        raise HRInputError("Periodogram power must be real, finite, nonnegative")
    # Candidates are in ascending order; first argmax explicitly implements exact ties.
    return int(candidates[np.argmax(periodogram.power[candidates])])


def select_initial_peak(periodogram: PeriodogramResult, config: HRConfig = HRConfig()) -> int:
    return _peak(periodogram, search_band_bins(config), config)


def select_tracked_peak(periodogram: PeriodogramResult, previous_bin: int, config: HRConfig = HRConfig()) -> int:
    return _peak(periodogram, tracking_candidates(previous_bin, config), config)
