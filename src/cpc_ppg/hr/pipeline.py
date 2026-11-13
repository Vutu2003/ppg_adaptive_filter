"""Generic ordered-window tracker; no BPM metadata read until copying results."""

from collections.abc import Callable, Iterable
from numbers import Integral, Real

import numpy as np

from .config import HRConfig
from .errors import HRAlignmentError, HRInputError
from .models import HRRecordingResult, HRWindowEstimate
from .periodogram import compute_periodogram, real_sequence
from .postprocessing import offline_postprocess, smooth_hr_sequence
from .spectral_peak import bin_to_bpm, bin_to_hz, select_initial_peak, select_tracked_peak

METADATA = ("record_id", "index", "start_sample", "end_sample", "start_time_s", "end_time_s")


def estimate_hr_record(windows: Iterable, signal_getter: Callable, config: HRConfig = HRConfig()) -> HRRecordingResult:
    """Each call initializes a recording; previous SELECTED bin alone drives tracking.

    Consume ordered generic windows (CPC/LMS/RLS/custom), requiring 1000-sample window bounds
    and contiguous indices starting 0. No sorting, dropping, padding or label use.
    Waveforms/spectra are discarded per window. Offline optional, default disabled.
    """
    if not isinstance(config, HRConfig) or not callable(signal_getter):
        raise HRInputError("Expected HRConfig and callable signal_getter")
    metadata, selected, raw = [], [], []
    record_id, previous_bin = None, None
    for expected_index, window in enumerate(windows):
        try:
            values = tuple(getattr(window, name) for name in METADATA)
        except AttributeError as exc:
            raise HRAlignmentError("Window lacks required alignment metadata") from exc
        rid, index, start, end, start_time, end_time = values
        if not isinstance(rid, str) or not rid or (record_id is not None and rid != record_id):
            raise HRAlignmentError(f"Window {expected_index}: mixed/invalid record_id")
        if any(isinstance(v, bool) or not isinstance(v, Integral) for v in (index, start, end)):
            raise HRAlignmentError(f"{rid} window {expected_index}: indices/bounds must be integers")
        if index != expected_index or start != expected_index*250 or end != start+1000:
            raise HRAlignmentError(f"{rid}: expected ordered window {expected_index} with [{expected_index*250}:{expected_index*250+1000}] bounds")
        if any(isinstance(v, bool) or not isinstance(v, Real) or not np.isfinite(v) for v in (start_time, end_time)):
            raise HRAlignmentError(f"{rid} window {index}: expected finite real sample times")
        if start_time != start/config.fs or end_time != end/config.fs:
            raise HRAlignmentError(f"{rid} window {index}: sample/time alignment mismatch")
        record_id = rid
        signal = real_sequence(signal_getter(window))
        if signal.shape != (1000,):
            raise HRAlignmentError(f"{rid} window {index}: expected one 1000-sample signal")
        spectrum = compute_periodogram(signal, config.fs, config.nfft)
        k = select_initial_peak(spectrum, config) if previous_bin is None else select_tracked_peak(spectrum, previous_bin, config)
        selected.append(k)
        raw.append(bin_to_bpm(k, config))
        metadata.append((values, getattr(window, "bpm", None)))  # labels only copied, never evaluated
        previous_bin = k
    if record_id is None:
        raise HRAlignmentError("Empty recording sequence; no record/window metadata")
    raw = np.asarray(raw, dtype=np.float64)
    smoothed = smooth_hr_sequence(raw, config)
    offline = offline_postprocess(smoothed) if config.offline_enabled else None
    estimates = tuple(HRWindowEstimate(*values, k, bin_to_hz(k, config), float(raw[i]), float(smoothed[i]),
                                       None if offline is None else float(offline[i]), bpm)
                      for i, ((values, bpm), k) in enumerate(zip(metadata, selected)))
    return HRRecordingResult(record_id, estimates)


def estimate_cpc_hr_record(source, config: HRConfig = HRConfig()) -> HRRecordingResult:
    """Convenience wrapper: TrainingRecord or CPC windows; paper mixing_lambda=.5 only."""
    from cpc_ppg.data import TrainingRecord
    from cpc_ppg.adaptive_filters import CPCWindow, run_cpc_record
    windows = run_cpc_record(source) if isinstance(source, TrainingRecord) else source

    def signal(window):
        if not isinstance(window, CPCWindow) or window.mixing_lambda != .5:
            raise HRInputError("Primary estimation requires CPCWindow with mixing_lambda=.5; use generic estimator for other sources")
        return window.output
    return estimate_hr_record(windows, signal, config)
