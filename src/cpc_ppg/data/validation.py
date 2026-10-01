"""Finite-data and exact raw-window/label contract checks."""

from collections.abc import Sequence

import numpy as np

from .errors import AlignmentError, DatasetValidationError, FiniteDataError
from .models import AlignmentSummary, NumericArray, TrainingRecord, TrainingWindow
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


def validate_segmented_windows(
    record: TrainingRecord, windows: Sequence[TrainingWindow]
) -> AlignmentSummary:
    """Verify every window's count, bounds, times, raw values and BPM0 index."""
    summary = validate_training_record(record)
    context = f"{record.record_id} [{record.signal_path}; {record.label_path}]"
    if len(windows) != summary.expected_windows:
        raise AlignmentError(
            f"{context}: expected {summary.expected_windows} windows; observed {len(windows)}"
        )
    for index, window in enumerate(windows):
        start = index * HOP_SAMPLES
        end = start + WINDOW_SAMPLES
        expected = (record.record_id, index, start, end, start / FS, end / FS)
        observed = (window.record_id, window.index, window.start_sample, window.end_sample,
                    window.start_time_s, window.end_time_s)
        if observed != expected:
            raise AlignmentError(f"{context} window {index}: expected metadata {expected}; observed {observed}")
        for name in CHANNEL_NAMES:
            channel = getattr(window, name)
            source = getattr(record, name)[start:end]
            if not isinstance(channel, np.ndarray) or channel.shape != (WINDOW_SAMPLES,):
                raise AlignmentError(
                    f"{context} window {index} {name}: expected shape ({WINDOW_SAMPLES},); "
                    f"observed {getattr(channel, 'shape', type(channel).__name__)}"
                )
            if channel.dtype != source.dtype or not np.array_equal(channel, source):
                raise AlignmentError(
                    f"{context} window {index} {name}: expected unchanged samples [{start}:{end}] "
                    f"with dtype={source.dtype}; observed differing data/dtype"
                )
        if window.bpm != record.bpm[index]:
            raise AlignmentError(
                f"{context} window {index}: expected BPM0[{index}]={record.bpm[index]}; "
                f"observed {window.bpm}"
            )
    return summary
