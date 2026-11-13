"""Finite-data and exact raw-window/label contract checks."""

import numpy as np

from .errors import AlignmentError, DatasetValidationError, FiniteDataError
from .models import AlignmentSummary, NumericArray, TrainingRecord
from .protocol import CHANNEL_NAMES, FS, HOP_SAMPLES, WINDOW_SAMPLES, expected_window_count


def validate_numeric_array(value: object, *, context: str, ndim: int) -> NumericArray:
    """Require a finite, real numeric ndarray of the specified dimensionality."""
    if not isinstance(value, np.ndarray) or value.ndim != ndim:
        observed = getattr(value, "shape", type(value).__name__)
        raise DatasetValidationError(f"{context}: expected {ndim}-D ndarray; observed {observed}")
    if value.dtype.kind not in "iuf":
        raise DatasetValidationError(
            f"{context}: expected real integer/float data; observed dtype={value.dtype}"
        )
    bad_count = int(value.size - np.count_nonzero(np.isfinite(value)))
    if bad_count:
        raise FiniteDataError(
            f"{context}: expected finite data; observed {bad_count} NaN/Inf values"
        )
    return value


def validate_training_record(record: TrainingRecord) -> AlignmentSummary:
    """Validate raw channels, fixed Fs and exact number of supplied labels."""
    context = f"{record.record_id} [{record.signal_path}; {record.label_path}]"
    if record.fs != FS:
        raise DatasetValidationError(f"{context}: expected Fs={FS} Hz; observed {record.fs}")
    lengths = {}
    for name in CHANNEL_NAMES:
        channel = validate_numeric_array(getattr(record, name), context=f"{context} {name}", ndim=1)
        lengths[name] = channel.size
    n_samples = lengths["ecg"]
    if any(length != n_samples for length in lengths.values()):
        raise DatasetValidationError(
            f"{context}: expected equal channel lengths of {n_samples}; observed {lengths}"
        )
    bpm = validate_numeric_array(record.bpm, context=f"{context} BPM0", ndim=1)
    count = expected_window_count(n_samples)
    if bpm.size != count:
        raise AlignmentError(
            f"{context}: N={n_samples}, window={WINDOW_SAMPLES}, hop={HOP_SAMPLES}; "
            f"expected {count} BPM0 labels; observed {bpm.size}. No correction applied."
        )
    last_start = (count - 1) * HOP_SAMPLES if count else None
    return AlignmentSummary(
        record.record_id, n_samples, bpm.size, count,
        0 if count else None, WINDOW_SAMPLES if count else None,
        last_start, last_start + WINDOW_SAMPLES if last_start is not None else None,
    )
