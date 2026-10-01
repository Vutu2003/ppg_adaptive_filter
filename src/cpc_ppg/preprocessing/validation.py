"""Alignment/shape/mean checks and scale-aware spectral leakage validation."""

from dataclasses import dataclass

import numpy as np

from cpc_ppg.data import TrainingWindow

from .config import PreprocessingConfig
from .models import PreprocessedWindow
from .spectral import _validate_signal

FILTERED_CHANNELS = (
    "ppg1_filtered", "ppg2_filtered", "acc_x_filtered", "acc_y_filtered", "acc_z_filtered",
)
OUTPUT_CHANNELS = (*FILTERED_CHANNELS, "ppg_avg")


class PreprocessingValidationError(ValueError):
    """A classified failed output contract for readable script statistics."""

    def __init__(self, category: str, message: str):
        super().__init__(message)
        self.category = category


@dataclass(frozen=True, slots=True)
class SpectralValidation:
    """Dimensionless second-FFT leakage metrics and engineering tolerances."""

    max_relative_out_of_band: float
    out_of_band_energy_fraction: float
    coefficient_relative_tolerance: float
    energy_fraction_tolerance: float


def validate_spectral_output(
    signal: np.ndarray, config: PreprocessingConfig = PreprocessingConfig(),
) -> SpectralValidation:
    """Require negligible out-of-band coefficients/energy after a second FFT.

    Normalize FFT magnitudes by their maximum to avoid unit-dependent absolute
    thresholds and squaring overflow. For float64 and length L, engineering
    relative tolerance is 64*eps*L; the energy-fraction limit is its square.
    These are conservative roundoff checks, not preprocessing parameters.
    """
    _validate_signal(signal)
    if signal.shape != (config.fft_length,):
        raise PreprocessingValidationError(
            "shape", f"Expected spectral validation shape ({config.fft_length},); observed {signal.shape}"
        )
    spectrum = np.fft.rfft(np.asarray(signal, dtype=np.float64), n=config.fft_length)
    if not np.isfinite(spectrum).all():
        raise PreprocessingValidationError("finite", "Expected finite validation FFT; observed overflow")
    frequencies = np.fft.rfftfreq(config.fft_length, d=1 / config.fs)
    mask = (frequencies >= config.low_hz) & (frequencies <= config.high_hz)
    with np.errstate(over="ignore"):
        magnitude = np.abs(spectrum)
    if not np.isfinite(magnitude).all():
        raise PreprocessingValidationError("finite", "Expected finite validation FFT magnitudes; observed overflow")
    scale = float(magnitude.max())
    relative_tolerance = 64 * np.finfo(np.float64).eps * config.fft_length
    normalized = magnitude / scale if scale else magnitude
    outside = normalized[~mask]
    max_relative = float(outside.max(initial=0))
    total_energy = float(np.sum(normalized ** 2))
    energy_fraction = float(np.sum(outside ** 2) / total_energy) if total_energy else 0.
    result = SpectralValidation(max_relative, energy_fraction, relative_tolerance, relative_tolerance ** 2)
    if max_relative > result.coefficient_relative_tolerance or energy_fraction > result.energy_fraction_tolerance:
        raise PreprocessingValidationError(
            "spectral", f"Expected out-of-band relative magnitude <= {relative_tolerance:.3e} and "
            f"energy fraction <= {result.energy_fraction_tolerance:.3e}; "
            f"observed {max_relative:.3e}, {energy_fraction:.3e}"
        )
    return result


def validate_preprocessed_window(
    raw: TrainingWindow, output: PreprocessedWindow,
    config: PreprocessingConfig = PreprocessingConfig(),
) -> tuple[SpectralValidation, ...]:
    """Validate copied metadata, six outputs, filtered mean and spectral support."""
    context = f"{raw.record_id} window {raw.index}"
    fields = ("record_id", "index", "start_sample", "end_sample", "start_time_s", "end_time_s", "bpm")
    expected = tuple(getattr(raw, name) for name in fields)
    observed = tuple(getattr(output, name) for name in fields)
    if observed != expected or (output.fs, output.low_hz, output.high_hz) != (config.fs, config.low_hz, config.high_hz):
        raise PreprocessingValidationError(
            "alignment", f"{context}: expected copied metadata {expected} and matching config; observed {observed}"
        )
    for name in OUTPUT_CHANNELS:
        signal = getattr(output, name)
        if not isinstance(signal, np.ndarray) or signal.shape != (config.fft_length,):
            raise PreprocessingValidationError(
                "shape", f"{context} {name}: expected shape ({config.fft_length},); "
                f"observed {getattr(signal, 'shape', type(signal).__name__)}"
            )
        if signal.dtype != np.float64 or not np.isfinite(signal).all():
            raise PreprocessingValidationError(
                "finite", f"{context} {name}: expected finite real float64 output; observed dtype={signal.dtype}"
            )
    expected_avg = 0.5 * (output.ppg1_filtered + output.ppg2_filtered)
    # Identical arithmetic on the same buffers must agree exactly.
    if not np.array_equal(output.ppg_avg, expected_avg):
        raise PreprocessingValidationError("average", f"{context}: expected arithmetic mean of filtered PPGs")
    results = []
    for name in FILTERED_CHANNELS:
        try:
            results.append(validate_spectral_output(getattr(output, name), config))
        except PreprocessingValidationError as exc:
            raise PreprocessingValidationError(exc.category, f"{context} {name}: {exc}") from exc
    return tuple(results)
