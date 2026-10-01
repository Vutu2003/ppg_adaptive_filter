"""Explicit Phase 2B reconstruction; FFT details are not author-confirmed."""

from dataclasses import dataclass
from numbers import Integral, Real
from typing import Literal

import numpy as np

from cpc_ppg.data.protocol import FS, WINDOW_SAMPLES

LOW_HZ = 0.4  # PAPER-SPECIFIED: CPC section 3.1.
HIGH_HZ = 3.5


def _validate_band(fs: float, low_hz: float, high_hz: float) -> None:
    for name, value in (("fs", fs), ("low_hz", low_hz), ("high_hz", high_hz)):
        if isinstance(value, bool) or not isinstance(value, Real) or not np.isfinite(value):
            raise ValueError(f"{name}: expected a finite real scalar; observed {value!r}")
    if fs <= 0 or not 0 <= low_hz < high_hz <= fs / 2:
        raise ValueError(
            f"Expected fs > 0 and 0 <= low_hz < high_hz <= fs/2; "
            f"observed fs={fs}, low_hz={low_hz}, high_hz={high_hz}"
        )


@dataclass(frozen=True, slots=True)
class PreprocessingConfig:
    """Per-window baseline options, all explicit and unsupported modes rejected.

    Fs comes from Phase 2A. Per-window rFFT/irFFT, L=1000, inclusive bounds,
    no padding/detrend/taper are RECONSTRUCTION-ASSUMPTION choices. The default
    requested band is PAPER-SPECIFIED; a different valid band is an explicit
    alternative configuration, not the replication baseline.
    """

    fs: int = FS
    low_hz: float = LOW_HZ
    high_hz: float = HIGH_HZ
    fft_mode: Literal["per_window"] = "per_window"
    fft_length: int = WINDOW_SAMPLES
    zero_padding: bool = False
    detrend: bool = False
    spectral_window: None = None
    boundary_policy: Literal["inclusive"] = "inclusive"

    def __post_init__(self) -> None:
        _validate_band(self.fs, self.low_hz, self.high_hz)
        if (self.fs != FS or isinstance(self.fft_length, bool)
                or not isinstance(self.fft_length, Integral) or self.fft_length != WINDOW_SAMPLES):
            raise ValueError(
                f"Phase 2B Training baseline expects fs={FS}, fft_length={WINDOW_SAMPLES}; "
                f"observed fs={self.fs}, fft_length={self.fft_length}"
            )
        if (self.fft_mode != "per_window" or self.zero_padding is not False
                or self.detrend is not False or self.spectral_window is not None
                or self.boundary_policy != "inclusive"):
            raise ValueError(
                "Supported reconstruction: per_window, no padding/detrend/taper, inclusive boundaries; "
                f"observed {self}"
            )
