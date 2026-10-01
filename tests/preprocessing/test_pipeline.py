"""Configuration, five independent filters, ordering and label independence."""

from dataclasses import FrozenInstanceError, replace

import numpy as np
import pytest

from cpc_ppg.data import segment_training_record
from cpc_ppg.preprocessing import PreprocessingConfig, preprocess_record, preprocess_window, spectral_bandpass
from cpc_ppg.preprocessing.validation import FILTERED_CHANNELS, OUTPUT_CHANNELS, validate_preprocessed_window


def test_baseline_config_and_frozen_model(raw_window):
    config = PreprocessingConfig()
    assert (config.fs, config.low_hz, config.high_hz, config.fft_length) == (125, .4, 3.5, 1000)
    output = preprocess_window(raw_window, config)
    with pytest.raises(FrozenInstanceError):
        config.low_hz = .5
    with pytest.raises(FrozenInstanceError):
        output.index = 999


@pytest.mark.parametrize("kwargs", [
    {"fs": 0}, {"fs": -125}, {"low_hz": -.1}, {"low_hz": 3.5},
    {"high_hz": 70}, {"low_hz": np.nan}, {"high_hz": np.inf}, {"fs": "125"},
    {"low_hz": True}, {"fs": 100}, {"fft_length": 2048}, {"fft_length": 1000.0},
    {"fft_mode": "global"}, {"zero_padding": True}, {"detrend": True},
    {"spectral_window": "hann"}, {"boundary_policy": "exclusive"},
])
def test_invalid_or_unsupported_config_rejected(kwargs):
    with pytest.raises(ValueError):
        PreprocessingConfig(**kwargs)


def test_all_five_distinct_channels_and_mean(raw_window):
    output = preprocess_window(raw_window)
    for index, name in enumerate(FILTERED_CHANNELS):
        expected = (index + 1) * np.sin(2 * np.pi * (1 + index * .5) * np.arange(1000) / 125)
        # Account for floating phase evaluation and FFT roundoff, scaled by amplitude.
        np.testing.assert_allclose(getattr(output, name), expected, rtol=0,
                                   atol=128 * np.finfo(np.float64).eps * (index + 1))
    np.testing.assert_array_equal(output.ppg_avg, (output.ppg1_filtered + output.ppg2_filtered) / 2)
    for name in OUTPUT_CHANNELS:
        assert not getattr(output, name).flags.writeable
        assert not np.shares_memory(getattr(output, name), raw_window.ppg1)
    validate_preprocessed_window(raw_window, output)


def test_instrumented_order_filters_original_five_arrays_before_mean(raw_window, monkeypatch):
    import cpc_ppg.preprocessing.pipeline as pipeline
    calls = []
    def instrument(signal, fs, low_hz, high_hz):
        calls.append(signal)
        assert (fs, low_hz, high_hz) == (125, .4, 3.5)
        return np.full(1000, len(calls), dtype=float)
    monkeypatch.setattr(pipeline, "spectral_bandpass", instrument)
    output = preprocess_window(raw_window)
    assert len(calls) == 5
    assert all(actual is getattr(raw_window, name) for actual, name in zip(calls, ("ppg1", "ppg2", "acc_x", "acc_y", "acc_z")))
    np.testing.assert_array_equal(output.ppg1_filtered, np.ones(1000))
    np.testing.assert_array_equal(output.ppg2_filtered, np.full(1000, 2.))
    np.testing.assert_array_equal(output.ppg_avg, np.full(1000, 1.5))


def test_ecg_not_read_and_bpm_does_not_influence_signals(raw_window):
    baseline = preprocess_window(raw_window)
    # A direct window call must not inspect ECG; only the five CPC inputs matter.
    altered = replace(raw_window, ecg=np.full(1000, np.nan), bpm=199.5)
    output = preprocess_window(altered)
    for name in OUTPUT_CHANNELS:
        np.testing.assert_array_equal(getattr(baseline, name), getattr(output, name))
    assert output.bpm == 199.5
    assert baseline.bpm == raw_window.bpm


@pytest.mark.parametrize("length,count", [(999, 0), (1000, 1), (1250, 2), (1499, 2)])
def test_record_convenience_alignment_and_raw_integrity(make_record, length, count):
    record = make_record(length)
    snapshots = {name: getattr(record, name).copy() for name in ("ecg", "ppg1", "ppg2", "acc_x", "acc_y", "acc_z", "bpm")}
    raw_windows = segment_training_record(record)
    outputs = preprocess_record(record)
    assert len(outputs) == len(raw_windows) == record.bpm.size == count
    for raw, output in zip(raw_windows, outputs):
        validate_preprocessed_window(raw, output)
    for name, before in snapshots.items():
        np.testing.assert_array_equal(getattr(record, name), before)
        assert getattr(record, name).flags.writeable


def test_pipeline_rejects_short_channel(raw_window):
    with pytest.raises(ValueError, match="ppg2: expected shape.*observed"):
        preprocess_window(replace(raw_window, ppg2=raw_window.ppg2[:-1]))


def test_pipeline_rejects_incomplete_bounds(raw_window):
    with pytest.raises(ValueError, match="expected 1000-sample bounds"):
        preprocess_window(replace(raw_window, end_sample=999))


def test_pipeline_error_includes_channel_and_window(raw_window):
    with pytest.raises(ValueError, match="DATA_01_TYPE01 window 0 acc_y:.*finite signal"):
        preprocess_window(replace(raw_window, acc_y=np.full(1000, np.nan)))


def test_explicit_other_valid_band_uses_its_own_mask(raw_window):
    config = PreprocessingConfig(low_hz=1.4, high_hz=1.6)
    output = preprocess_window(raw_window, config)
    np.testing.assert_array_equal(output.ppg2_filtered, spectral_bandpass(raw_window.ppg2, 125, 1.4, 1.6))
    validate_preprocessed_window(raw_window, output, config)
