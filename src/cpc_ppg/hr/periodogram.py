"""Explicit raw rFFT power: no taper, detrend, normalization or extra filtering."""

from numbers import Integral, Real

import numpy as np

from .errors import HRInputError, HRNumericalError
from .models import PeriodogramResult


def real_sequence(value, name="signal", *, allow_empty=False):
    if not isinstance(value, np.ndarray) or value.ndim != 1 or value.dtype.kind not in "iuf":
        raise HRInputError(f"{name}: expected one-dimensional real numeric ndarray")
    if not allow_empty and value.size == 0:
        raise HRInputError(f"{name}: expected nonempty sequence")
    if not np.isfinite(value).all():
        raise HRInputError(f"{name}: NaN/Inf not allowed")
    with np.errstate(over="ignore", invalid="ignore"):
        array = np.asarray(value, dtype=np.float64)
    if not np.isfinite(array).all():
        raise HRInputError(f"{name}: values not representable in float64")
    return array


def compute_periodogram(signal: np.ndarray, fs: float = 125., nfft: int = 4096) -> PeriodogramResult:
    x = real_sequence(signal)
    if isinstance(fs, bool) or not isinstance(fs, Real) or not np.isfinite(fs) or fs <= 0:
        raise HRInputError("fs: expected positive finite real scalar")
    if isinstance(nfft, bool) or not isinstance(nfft, Integral) or nfft < 2 or nfft < x.size:
        raise HRInputError("nfft: expected integer >= 2 and >= signal length; never truncate")
    with np.errstate(over="ignore", invalid="ignore"):
        spectrum = np.fft.rfft(x, n=nfft)
        power = np.abs(spectrum)**2
    if not np.isfinite(power).all():
        raise HRNumericalError("Periodogram raw |X|^2 overflow/nonfinite; no scaling or repair applied")
    bins = np.arange(nfft//2+1, dtype=np.int64)
    frequencies = np.fft.rfftfreq(nfft, d=1/fs)
    for array in (bins, frequencies, power):
        array.setflags(write=False)
    return PeriodogramResult(bins, frequencies, power, float(fs), int(nfft), x.size)
