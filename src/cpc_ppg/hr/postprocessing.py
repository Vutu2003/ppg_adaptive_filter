"""Separate causal raw-history smoothing and optional literal noncausal correction."""

import numpy as np

from .config import HRConfig
from .errors import HRInputError, HRNumericalError
from .periodogram import real_sequence


def smooth_hr_sequence(raw_hr: np.ndarray, config: HRConfig = HRConfig()) -> np.ndarray:
    if not isinstance(config, HRConfig):
        raise HRInputError("Expected HRConfig")
    raw = real_sequence(raw_hr, "raw HR", allow_empty=True)
    output = raw.copy()
    with np.errstate(over="ignore", invalid="ignore"):
        output[2:] = (config.current_weight*raw[2:] + config.previous_weight*raw[1:-1]
                      + config.previous2_weight*raw[:-2])
    if not np.isfinite(output).all():
        raise HRNumericalError("Smoothing overflow/nonfinite")
    output.setflags(write=False)
    return output


def offline_postprocess(smoothed_hr: np.ndarray) -> np.ndarray:
    """Original eight values i-4:i+4, ddof=0; edges unchanged, strict >.

    abs(BPM-mean) > variance(BPM²) is dimensionally unusual but reproduced
    literally. Do not use sqrt, shrink/pad context or recursively edited values.
    """
    hr = real_sequence(smoothed_hr, "smoothed HR", allow_empty=True)
    output = hr.copy()
    for index in range(4, hr.size-3):
        with np.errstate(over="ignore", invalid="ignore"):
            values = hr[index-4:index+4]
            mean = np.mean(values)
            variance = np.var(values, ddof=0)
            difference = abs(hr[index]-mean)
        if not np.isfinite([mean, variance, difference]).all():
            raise HRNumericalError(f"Offline index {index}: nonfinite mean/variance/difference")
        if difference > variance:
            output[index] = mean
    output.setflags(write=False)
    return output
