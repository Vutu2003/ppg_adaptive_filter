"""Frozen spectral HR reconstruction; no evaluation metrics or label-based tuning."""

from .config import HRConfig
from .errors import HRAlignmentError, HRInputError, HRNumericalError, HRTrackingError
from .models import HRRecordingResult, HRWindowEstimate, PeriodogramResult
from .periodogram import compute_periodogram
from .pipeline import estimate_cpc_hr_record, estimate_hr_record
from .postprocessing import offline_postprocess, smooth_hr_sequence
from .spectral_peak import (bin_to_bpm, bin_to_hz, search_band_bins, select_initial_peak,
                            select_tracked_peak, tracking_candidates)

__all__ = ["HRConfig", "PeriodogramResult", "HRWindowEstimate", "HRRecordingResult",
           "HRInputError", "HRAlignmentError", "HRTrackingError", "HRNumericalError",
           "compute_periodogram", "bin_to_hz", "bin_to_bpm", "search_band_bins", "tracking_candidates",
           "select_initial_peak", "select_tracked_peak", "smooth_hr_sequence", "offline_postprocess",
           "estimate_hr_record", "estimate_cpc_hr_record"]
