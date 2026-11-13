"""Real LMS/RLS primitives, three-stage ANC cascades and paper CPC interpolation."""

from .cpc import (
    CPCAlignmentError, CPCConfig, CPCWindow, combine_cpc, combine_cpc_windows,
    lambda_sweep_values, run_cpc_window, run_cpc_record, sweep_cpc_windows,
)

from .cascade import (
    CascadeNumericalError, CascadeResult, CascadeStageResult, CascadedWindow,
    cascaded_lms, cascaded_rls, paper_cascaded_lms_reconstruction_config,
    paper_cascaded_rls_reconstruction_config, run_cascaded_lms_window,
    run_cascaded_rls_window, run_cascaded_lms_record, run_cascaded_rls_record,
)

from .config import LMSConfig, RLSConfig, paper_lms_config, paper_rls_reconstruction_config
from .errors import AdaptiveFilterInputError, AdaptiveFilterNumericalError
from .lms import lms_filter
from .models import LMSResult, LMSState, RLSResult, RLSState
from .rls import rls_filter

__all__ = [
    "LMSConfig", "LMSState", "LMSResult", "lms_filter",
    "RLSConfig", "RLSState", "RLSResult", "rls_filter",
    "paper_lms_config", "paper_rls_reconstruction_config",
    "AdaptiveFilterInputError", "AdaptiveFilterNumericalError",
    "CascadeResult", "CascadeStageResult", "CascadedWindow", "CascadeNumericalError",
    "cascaded_lms", "cascaded_rls", "paper_cascaded_lms_reconstruction_config",
    "paper_cascaded_rls_reconstruction_config", "run_cascaded_lms_window",
    "run_cascaded_rls_window", "run_cascaded_lms_record", "run_cascaded_rls_record",
    "CPCConfig", "CPCWindow", "CPCAlignmentError", "combine_cpc", "combine_cpc_windows",
    "run_cpc_window", "run_cpc_record", "lambda_sweep_values", "sweep_cpc_windows",
]
