"""Small identifiable raw records; MAT files live only in pytest temp dirs."""

from pathlib import Path

import numpy as np
import pytest
from scipy.io import savemat

from cpc_ppg.data import TrainingRecord
from cpc_ppg.data.protocol import CHANNEL_NAMES, FS, expected_window_count


@pytest.fixture
def make_record():
    def make(n_samples=1250, bpm=None, dtype=np.float64):
        sig = (np.arange(6)[:, None] * 10000 + np.arange(n_samples)[None, :]).astype(dtype)
        if n_samples:
            sig[1, 0] = -1024
        labels = np.arange(expected_window_count(n_samples), dtype=np.float64) + 70 if bpm is None else np.asarray(bpm)
        return TrainingRecord(
            "DATA_01_TYPE01", Path("DATA_01_TYPE01.mat"), Path("DATA_01_TYPE01_BPMtrace.mat"),
            FS, **{name: sig[i] for i, name in enumerate(CHANNEL_NAMES)}, bpm=labels,
        )
    return make


@pytest.fixture
def write_pair(tmp_path, make_record):
    def write(record_id="DATA_01_TYPE01", *, n_samples=1250, sig=None, bpm=None, row_labels=False):
        record = make_record(n_samples)
        signal_path = tmp_path / f"{record_id}.mat"
        label_path = tmp_path / f"{record_id}_BPMtrace.mat"
        signal = np.stack([getattr(record, name) for name in CHANNEL_NAMES]) if sig is None else sig
        labels = record.bpm if bpm is None else np.asarray(bpm)
        if labels.ndim == 1:
            labels = labels.reshape(1, -1) if row_labels else labels.reshape(-1, 1)
        savemat(signal_path, {"sig": signal})
        savemat(label_path, {"BPM0": labels})
        return signal_path, label_path
    return write
