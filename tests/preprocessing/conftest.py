"""Synthetic channels at distinct FFT-bin frequencies, with raw labels."""

from pathlib import Path

import numpy as np
import pytest

from cpc_ppg.data import TrainingRecord, segment_training_record
from cpc_ppg.data.protocol import CHANNEL_NAMES, FS, expected_window_count


@pytest.fixture
def make_record():
    def make(n_samples=1250):
        t = np.arange(n_samples) / FS
        channels = {"ecg": np.sin(2 * np.pi * 7 * t)}
        for index, name in enumerate(CHANNEL_NAMES[1:]):
            frequency = 1 + index * .5
            channels[name] = (index + 1) * np.sin(2 * np.pi * frequency * t) + 2 * np.sin(2 * np.pi * 4 * t) + 10
        return TrainingRecord("DATA_01_TYPE01", Path("DATA_01_TYPE01.mat"),
                              Path("DATA_01_TYPE01_BPMtrace.mat"), FS, **channels,
                              bpm=80 + np.arange(expected_window_count(n_samples), dtype=float))
    return make


@pytest.fixture
def raw_window(make_record):
    return segment_training_record(make_record())[0]
