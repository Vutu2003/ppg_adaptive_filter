"""Exact half-open boundaries, label indices, raw integrity and validators."""

from dataclasses import replace

import numpy as np
import pytest

from cpc_ppg.data import AlignmentError, DatasetValidationError, segment_training_record, validate_segmented_windows, validate_training_record
from cpc_ppg.data.protocol import CHANNEL_NAMES, expected_window_count


@pytest.mark.parametrize("n_samples,bounds", [
    (0, []), (999, []), (1000, [(0, 1000)]),
    (1250, [(0, 1000), (250, 1250)]),
    (1499, [(0, 1000), (250, 1250)]),
    (1500, [(0, 1000), (250, 1250), (500, 1500)]),
])
def test_boundaries_labels_and_all_channels(make_record, n_samples, bounds):
    record = make_record(n_samples)
    windows = segment_training_record(record)
    assert [(w.start_sample, w.end_sample) for w in windows] == bounds
    assert len(windows) == expected_window_count(n_samples)
    summary = validate_segmented_windows(record, windows)
    assert summary.first_start == (0 if bounds else None)
    assert summary.first_end == (1000 if bounds else None)
    assert summary.last_start == (bounds[-1][0] if bounds else None)
    assert summary.last_end == (bounds[-1][1] if bounds else None)
    for index, window in enumerate(windows):
        start, end = bounds[index]
        assert window.record_id == record.record_id
        assert window.index == index
        assert window.start_time_s == index * 2
        assert window.end_time_s == index * 2 + 8
        assert window.bpm == record.bpm[index]
        for name in CHANNEL_NAMES:
            source = getattr(record, name)
            segment = getattr(window, name)
            assert segment.shape == (1000,)
            assert segment.dtype == source.dtype
            np.testing.assert_array_equal(segment, source[start:end])
            assert np.shares_memory(segment, source)
            assert not segment.flags.writeable


def test_no_original_array_or_label_mutation(make_record):
    record = make_record(1499, bpm=[88.25, 111.5])
    original = {name: getattr(record, name).copy() for name in (*CHANNEL_NAMES, "bpm")}
    flags = {name: getattr(record, name).flags.writeable for name in original}
    windows = segment_training_record(record)
    for name, values in original.items():
        np.testing.assert_array_equal(getattr(record, name), values)
        assert getattr(record, name).flags.writeable == flags[name]
    assert windows[0].ppg1[0] == -1024
    assert windows[0].bpm == 88.25
    assert windows[1].bpm == 111.5


@pytest.mark.parametrize("labels", [[], [70], [70, 71, 72]])
def test_segmentation_rejects_mismatched_labels(make_record, labels):
    with pytest.raises(AlignmentError, match="expected 2 BPM0 labels; observed"):
        segment_training_record(make_record(1250, bpm=labels))


def test_unequal_channel_lengths(make_record):
    record = make_record()
    with pytest.raises(DatasetValidationError, match="expected equal channel lengths"):
        validate_training_record(replace(record, acc_z=record.acc_z[:-1]))


def test_wrong_sampling_rate(make_record):
    with pytest.raises(DatasetValidationError, match="expected Fs=125 Hz; observed 100"):
        segment_training_record(replace(make_record(), fs=100))


def test_invalid_channel_dimension(make_record):
    record = make_record()
    with pytest.raises(DatasetValidationError, match="expected 1-D"):
        validate_training_record(replace(record, ppg1=record.ppg1.reshape(1, -1)))


def test_window_count_validator(make_record):
    record = make_record()
    with pytest.raises(AlignmentError, match="expected 2 windows; observed 1"):
        validate_segmented_windows(record, segment_training_record(record)[1:])


@pytest.mark.parametrize("field,value", [
    ("record_id", "wrong"), ("index", 1), ("start_sample", 250),
    ("end_sample", 999), ("start_time_s", 2.), ("end_time_s", 7.),
])
def test_metadata_validator_catches_offset(make_record, field, value):
    record = make_record()
    windows = segment_training_record(record)
    windows[0] = replace(windows[0], **{field: value})
    with pytest.raises(AlignmentError, match="expected metadata"):
        validate_segmented_windows(record, windows)


@pytest.mark.parametrize("mode", ["short", "changed", "dtype", "not_array"])
def test_window_data_validator(make_record, mode):
    record = make_record()
    windows = segment_training_record(record)
    altered = windows[0].ppg1.copy()
    if mode == "short":
        altered = altered[:-1]
    elif mode == "changed":
        altered[0] = 0
    elif mode == "dtype":
        altered = altered.astype(np.float32)
    else:
        altered = altered.tolist()
    windows[0] = replace(windows[0], ppg1=altered)
    with pytest.raises(AlignmentError, match="expected shape|expected unchanged samples"):
        validate_segmented_windows(record, windows)


def test_label_validator_catches_one_index_offset(make_record):
    record = make_record()
    windows = segment_training_record(record)
    windows[0] = replace(windows[0], bpm=record.bpm[1])
    with pytest.raises(AlignmentError, match=r"expected BPM0\[0\]"):
        validate_segmented_windows(record, windows)


def test_negative_sample_count_rejected():
    with pytest.raises(ValueError, match="nonnegative"):
        expected_window_count(-1)
