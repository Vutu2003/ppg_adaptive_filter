"""Buffers, causal regressors and runtime input checks for LMS/RLS."""

import numpy as np

from .errors import AdaptiveFilterInputError, AdaptiveFilterNumericalError
from .models import FloatArray


def real_array(value: np.ndarray, name: str, shape: tuple[int, ...] | None = None) -> FloatArray:
    if not isinstance(value, np.ndarray) or value.ndim != (len(shape) if shape is not None else 1):
        raise AdaptiveFilterInputError(f"{name}: expected real ndarray with shape {shape or '(N,)'}; observed {getattr(value, 'shape', type(value).__name__)}")
    if shape is not None and value.shape != shape:
        raise AdaptiveFilterInputError(f"{name}: expected shape {shape}; observed {value.shape}")
    if value.dtype.kind not in "iuf" or not np.isfinite(value).all():
        raise AdaptiveFilterInputError(f"{name}: expected finite real numeric data; observed dtype={value.dtype}, possible NaN/Inf")
    with np.errstate(over="ignore", invalid="ignore"):
        array = np.asarray(value, dtype=np.float64)
    if not np.isfinite(array).all():
        raise AdaptiveFilterInputError(f"{name}: expected float64-representable values; observed conversion overflow")
    return array


def input_pair(reference: np.ndarray, desired: np.ndarray) -> tuple[FloatArray, FloatArray]:
    x, d = real_array(reference, "reference"), real_array(desired, "desired")
    if x.shape != d.shape:
        raise AdaptiveFilterInputError(f"Expected matching reference/desired lengths; observed {x.size}/{d.size}")
    return x, d


def initial_weights(value: np.ndarray | None, n_taps: int) -> FloatArray:
    return np.zeros(n_taps) if value is None else real_array(value, "initial weights", (n_taps,)).copy()


def initial_regressor(history: np.ndarray, n_taps: int) -> FloatArray:
    buffer = np.empty(n_taps)
    buffer[:-1] = real_array(history, "reference history", (n_taps - 1,))
    buffer[-1] = 0
    return buffer


def advance_regressor(buffer: FloatArray, sample: float) -> None:
    """Local-only causal buffer [x[n], x[n-1], ...]; no future/circular samples."""
    buffer[1:] = buffer[:-1]
    buffer[0] = sample


def covariance_buffer(value: np.ndarray, n_taps: int) -> FloatArray:
    covariance = real_array(value, "initial covariance", (n_taps, n_taps)).copy()
    validate_covariance(covariance, n_taps)
    return covariance


def validate_covariance(covariance: FloatArray, n_taps: int) -> None:
    """Check covariance policy without changing or allocating a corrected matrix."""
    # Accept roundoff-sized asymmetry in continued states, without correcting it.
    tolerance = 64 * np.finfo(np.float64).eps * n_taps * np.max(np.abs(covariance))
    with np.errstate(over="ignore", invalid="ignore"):
        asymmetry = np.max(np.abs(covariance - covariance.T))
    if asymmetry > tolerance:
        raise AdaptiveFilterInputError(f"Initial covariance must be symmetric within {tolerance:.3e}; observed asymmetry {asymmetry:.3e}")
    try:
        np.linalg.cholesky(covariance)
    except np.linalg.LinAlgError as exc:
        raise AdaptiveFilterInputError("Initial covariance must be positive definite") from exc


def finite_runtime(algorithm: str, index: int, **values: object) -> None:
    for name, value in values.items():
        if not np.isfinite(value).all():
            raise AdaptiveFilterNumericalError(f"{algorithm} sample {index}: expected finite {name}; observed overflow/NaN/Inf")


def readonly(*arrays: FloatArray) -> None:
    for array in arrays:
        array.setflags(write=False)
