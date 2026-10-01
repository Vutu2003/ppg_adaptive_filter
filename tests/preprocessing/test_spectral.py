"""Analytical FFT-bin signals and independent transform references."""

import numpy as np
import pytest

from cpc_ppg.preprocessing import spectral_bandpass

FS = 125
N = 1000


def sinusoid(frequency, length=N):
    return np.sin(2 * np.pi * frequency * np.arange(length) / FS)


def test_mixture_removes_dc_and_stopband_preserves_passband():
    expected = 2 * sinusoid(1) + 3 * sinusoid(2.5)
    raw = 9 + sinusoid(.25) + expected + 4 * sinusoid(4)
    before = raw.copy()
    output = spectral_bandpass(raw)
    np.testing.assert_allclose(output, expected, rtol=0, atol=4e-13)
    np.testing.assert_array_equal(raw, before)
    assert output.shape == (N,)
    assert output.dtype == np.float64
    assert np.isfinite(output).all()
    assert not output.flags.writeable


@pytest.mark.parametrize("frequency,retained", [(.375, False), (.5, True), (3.5, True), (3.625, False)])
def test_discrete_boundaries(frequency, retained):
    raw = sinusoid(frequency)
    expected = raw if retained else np.zeros(N)
    np.testing.assert_allclose(spectral_bandpass(raw), expected, rtol=0, atol=3e-14)


def test_frequency_grid_is_derived_not_redefined_band():
    frequencies = np.fft.rfftfreq(N, d=1 / FS)
    retained = frequencies[(frequencies >= .4) & (frequencies <= 3.5)]
    assert frequencies[1] - frequencies[0] == .125
    assert retained[0] == .5
    assert retained[-1] == 3.5
    assert .375 not in retained
    assert retained.size == int((3.5 - .5) / .125) + 1


def test_direct_rfft_mask_reference():
    raw = np.random.default_rng(23).normal(size=N) + 13
    spectrum = np.fft.rfft(raw, n=N)
    frequencies = np.fft.rfftfreq(N, 1 / FS)
    spectrum[(frequencies < .4) | (frequencies > 3.5)] = 0
    expected = np.fft.irfft(spectrum, n=N)
    np.testing.assert_array_equal(spectral_bandpass(raw), expected)


def test_two_sided_reference_preserves_conjugate_frequency_support():
    raw = sinusoid(1) + .4 * sinusoid(2.5) + 2 * sinusoid(4)
    spectrum = np.fft.fft(raw)
    frequencies = np.abs(np.fft.fftfreq(N, 1 / FS))
    spectrum[(frequencies < .4) | (frequencies > 3.5)] = 0
    expected = np.fft.ifft(spectrum)
    np.testing.assert_allclose(spectral_bandpass(raw), expected.real, rtol=0, atol=1e-14)
    assert np.max(np.abs(expected.imag)) < 1e-14


@pytest.mark.parametrize("length", [999, 1000, 1001])
def test_primitive_length_no_padding_or_odd_length_loss(length):
    assert spectral_bandpass(np.zeros(length)).shape == (length,)
    np.testing.assert_array_equal(spectral_bandpass(np.zeros(length)), np.zeros(length))


@pytest.mark.parametrize("dtype", [np.int16, np.float32, np.float64])
def test_numeric_input_preserved_and_output_is_float64(dtype):
    raw = (7 * sinusoid(1) + 12).astype(dtype)
    before = raw.copy()
    output = spectral_bandpass(raw)
    np.testing.assert_array_equal(raw, before)
    assert raw.dtype == dtype
    assert output.dtype == np.float64


@pytest.mark.parametrize("raw", [np.zeros((1, N)), np.zeros((6, N)), np.zeros(0), [1, 2, 3]])
def test_invalid_shape_rejected(raw):
    with pytest.raises(ValueError, match="nonempty 1-D ndarray"):
        spectral_bandpass(raw)


@pytest.mark.parametrize("bad", [np.nan, np.inf, -np.inf])
def test_nonfinite_rejected(bad):
    raw = np.zeros(N)
    raw[123] = bad
    with pytest.raises(ValueError, match="finite signal"):
        spectral_bandpass(raw)


@pytest.mark.parametrize("dtype", [np.complex128, object, bool])
def test_complex_nonnumeric_and_bool_rejected(dtype):
    with pytest.raises(ValueError, match="real integer/float"):
        spectral_bandpass(np.ones(N, dtype=dtype))


def test_fft_overflow_fails_instead_of_returning_nan():
    with pytest.raises(ValueError, match="finite float64 FFT coefficients"):
        spectral_bandpass(np.full(N, 1e308))


def test_inclusive_dc_and_nyquist_when_explicitly_requested():
    raw = 3 + (-1.) ** np.arange(N)
    np.testing.assert_allclose(spectral_bandpass(raw, low_hz=0, high_hz=FS / 2), raw, rtol=0, atol=1e-14)
