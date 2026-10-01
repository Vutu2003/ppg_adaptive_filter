"""Real FFT coefficient elimination, with no additional signal processing."""

import numpy as np

from cpc_ppg.data.protocol import FS

from .config import HIGH_HZ, LOW_HZ, _validate_band
from .models import FloatArray


def _validate_signal(signal: np.ndarray) -> None:
    if not isinstance(signal, np.ndarray) or signal.ndim != 1 or signal.size == 0:
        raise ValueError(
            f"Expected nonempty 1-D ndarray; observed {getattr(signal, 'shape', type(signal).__name__)}"
        )
    if signal.dtype.kind not in "iuf":
        raise ValueError(f"Expected real integer/float signal; observed dtype={signal.dtype}")
    if not np.isfinite(signal).all():
        raise ValueError("Expected finite signal; observed NaN/Inf")


def spectral_bandpass(
    signal: np.ndarray, fs: float = FS, low_hz: float = LOW_HZ, high_hz: float = HIGH_HZ,
) -> FloatArray:
    """Mask rFFT bins inclusively in [low_hz, high_hz], then irFFT at input length.

    No padding, taper, detrending, normalization or input mutation. Returns a
    read-only real float64 array. This rFFT reconstruction is an explicit
    baseline assumption, not a claim about the authors' FFT implementation.
    The general primitive accepts any nonempty length; the Training pipeline
    requires exactly the Phase 2A 1000-sample windows.
    """
    _validate_signal(signal)
    _validate_band(fs, low_hz, high_hz)
    length = signal.size
    frequencies = np.fft.rfftfreq(length, d=1 / fs)
    mask = (frequencies >= low_hz) & (frequencies <= high_hz)
    # Explicit promotion makes numerical validation use one known precision.
    with np.errstate(over="ignore", invalid="ignore"):
        coefficients = np.fft.rfft(np.asarray(signal, dtype=np.float64), n=length)
        if not np.isfinite(coefficients).all():
            raise ValueError("Expected finite float64 FFT coefficients; observed overflow/nonfinite values")
        coefficients[~mask] = 0
        output = np.fft.irfft(coefficients, n=length)
    if not np.isfinite(output).all():
        raise ValueError("Expected finite inverse FFT output; observed overflow/nonfinite values")
    output.setflags(write=False)
    return output
