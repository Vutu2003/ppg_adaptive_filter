"""Exact full-window slicing of raw Training records."""

from .models import TrainingRecord, TrainingWindow
from .protocol import CHANNEL_NAMES, HOP_SAMPLES, WINDOW_SAMPLES
from .validation import validate_training_record


def segment_training_record(record: TrainingRecord) -> list[TrainingWindow]:
    """Return aligned 1000-sample raw views every 250 samples, starting at zero.

    Reject a BPM0 count mismatch before producing any windows. Never pad the
    tail, interpolate labels or discard an initial/final complete window.
    """
    summary = validate_training_record(record)
    windows = []
    for index in range(summary.expected_windows):
        start = index * HOP_SAMPLES
        end = start + WINDOW_SAMPLES
        channels = {}
        for name in CHANNEL_NAMES:
            view = getattr(record, name)[start:end]
            view.setflags(write=False)
            channels[name] = view
        windows.append(TrainingWindow(
            record.record_id, index, start, end, start / record.fs, end / record.fs,
            **channels, bpm=float(record.bpm[index]),
        ))
    return windows
