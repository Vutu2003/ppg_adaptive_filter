"""Validation must reject corruption and accept roundoff across signal scales."""

from dataclasses import replace

import numpy as np
import pytest

from cpc_ppg.preprocessing import preprocess_window, spectral_bandpass
from cpc_ppg.preprocessing.validation import PreprocessingValidationError, validate_preprocessed_window, validate_spectral_output


@pytest.mark.parametrize("scale", [0., 1e-100, 1., 1e100])
def test_scale_aware_second_fft_roundoff(scale):
    raw = scale * np.random.default_rng(11).normal(size=1000)
    metrics = validate_spectral_output(spectral_bandpass(raw))
    assert metrics.max_relative_out_of_band <= metrics.coefficient_relative_tolerance
    assert metrics.out_of_band_energy_fraction <= metrics.energy_fraction_tolerance


def test_unfiltered_real_signal_fails_spectral_support():
    t = np.arange(1000) / 125
    raw = np.sin(2 * np.pi * t) + .01 * np.sin(2 * np.pi * 4 * t)
    with pytest.raises(PreprocessingValidationError, match="out-of-band relative magnitude") as caught:
        validate_spectral_output(raw)
    assert caught.value.category == "spectral"


def test_wrong_validation_length_rejected():
    with pytest.raises(PreprocessingValidationError, match="shape"):
        validate_spectral_output(np.zeros(999))


@pytest.mark.parametrize("field,value", [("index", 1), ("bpm", 199.), ("end_sample", 1250), ("fs", 100)])
def test_metadata_tampering_detected(raw_window, field, value):
    output = replace(preprocess_window(raw_window), **{field: value})
    with pytest.raises(PreprocessingValidationError) as caught:
        validate_preprocessed_window(raw_window, output)
    assert caught.value.category == "alignment"


@pytest.mark.parametrize("value", [np.zeros(999), np.zeros((1, 1000)), [0.] * 1000])
def test_shape_tampering_detected(raw_window, value):
    output = replace(preprocess_window(raw_window), acc_x_filtered=value)
    with pytest.raises(PreprocessingValidationError) as caught:
        validate_preprocessed_window(raw_window, output)
    assert caught.value.category == "shape"


@pytest.mark.parametrize("value", [np.full(1000, np.nan), np.full(1000, np.inf), np.zeros(1000, dtype=np.complex128)])
def test_finite_and_real_output_contract(raw_window, value):
    output = replace(preprocess_window(raw_window), acc_z_filtered=value)
    with pytest.raises(PreprocessingValidationError) as caught:
        validate_preprocessed_window(raw_window, output)
    assert caught.value.category == "finite"


def test_average_tampering_detected(raw_window):
    output = preprocess_window(raw_window)
    corrupted = replace(output, ppg_avg=output.ppg_avg + .1)
    with pytest.raises(PreprocessingValidationError) as caught:
        validate_preprocessed_window(raw_window, corrupted)
    assert caught.value.category == "average"


def test_channel_spectral_tampering_has_context(raw_window):
    output = preprocess_window(raw_window)
    corrupt = replace(output, acc_y_filtered=raw_window.acc_y.copy())
    with pytest.raises(PreprocessingValidationError, match="DATA_01_TYPE01 window 0 acc_y_filtered") as caught:
        validate_preprocessed_window(raw_window, corrupt)
    assert caught.value.category == "spectral"
