"""Paper-stated individual filtering followed by filtered PPG averaging."""

import numpy as np

from cpc_ppg.data import TrainingRecord, TrainingWindow, segment_training_record

from .config import PreprocessingConfig
from .models import FloatArray, PreprocessedWindow
from .spectral import spectral_bandpass


def preprocess_window(
    window: TrainingWindow, config: PreprocessingConfig = PreprocessingConfig(),
) -> PreprocessedWindow:
    """Filter PPG1/PPG2/ACC separately, then average filtered PPGs.

    ECG is neither read nor filtered. BPM0 is copied as metadata and never
    influences any transform. The raw window is retained without mutation.
    """
    context = f"{window.record_id} window {window.index}"
    if window.end_sample - window.start_sample != config.fft_length:
        raise ValueError(
            f"{context}: expected {config.fft_length}-sample bounds; "
            f"observed [{window.start_sample}:{window.end_sample}]"
        )

    def filtered(name: str) -> FloatArray:
        signal = getattr(window, name)
        if not isinstance(signal, np.ndarray) or signal.shape != (config.fft_length,):
            raise ValueError(
                f"{context} {name}: expected shape ({config.fft_length},); "
                f"observed {getattr(signal, 'shape', type(signal).__name__)}"
            )
        try:
            return spectral_bandpass(signal, config.fs, config.low_hz, config.high_hz)
        except ValueError as exc:
            raise ValueError(f"{context} {name}: {exc}") from exc

    ppg1_f = filtered("ppg1")
    ppg2_f = filtered("ppg2")
    acc_x_f = filtered("acc_x")
    acc_y_f = filtered("acc_y")
    acc_z_f = filtered("acc_z")
    ppg_avg = 0.5 * (ppg1_f + ppg2_f)
    if not np.isfinite(ppg_avg).all():
        raise ValueError(f"{context}: expected finite filtered PPG mean; observed overflow/nonfinite values")
    ppg_avg.setflags(write=False)
    return PreprocessedWindow(
        window.record_id, window.index, window.start_sample, window.end_sample,
        window.start_time_s, window.end_time_s, window.bpm,
        ppg1_f, ppg2_f, ppg_avg, acc_x_f, acc_y_f, acc_z_f,
        config.fs, config.low_hz, config.high_hz,
    )


def preprocess_record(
    record: TrainingRecord, config: PreprocessingConfig = PreprocessingConfig(),
) -> list[PreprocessedWindow]:
    """Use Phase 2A segmentation and independently preprocess every full window."""
    return [preprocess_window(window, config) for window in segment_training_record(record)]
