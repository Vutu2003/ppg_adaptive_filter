"""Confirmed Training protocol (dataset README and CPC §§2, 4.3)."""

from typing import Final

FS: Final = 125
WINDOW_SECONDS: Final = 8
HOP_SECONDS: Final = 2
WINDOW_SAMPLES: Final = FS * WINDOW_SECONDS
HOP_SAMPLES: Final = FS * HOP_SECONDS
EXPECTED_TRAINING_RECORDS: Final = 12
# Tuple positions are the confirmed zero-based rows of Training sig.
CHANNEL_NAMES: Final = ("ecg", "ppg1", "ppg2", "acc_x", "acc_y", "acc_z")


def expected_window_count(n_samples: int) -> int:
    """Count full windows, including window zero and excluding an incomplete tail."""
    if n_samples < 0:
        raise ValueError(f"Expected a nonnegative sample count; observed {n_samples}")
    if n_samples < WINDOW_SAMPLES:
        return 0
    return (n_samples - WINDOW_SAMPLES) // HOP_SAMPLES + 1
