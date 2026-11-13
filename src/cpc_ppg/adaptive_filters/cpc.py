"""Paper Eq.(2): convex interpolation of the two final cascade ANC errors.

PAPER-SPECIFIED: mixing_lambda in [0,1], main .5, sweep 0:.1:1.
ENGINEERING-DECISION: typed/read-only outputs, strict branch alignment, iterators.
Preprocessing and both adaptive branches use the same configured defaults. No HR estimation or lambda selection.
"""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from numbers import Real

import numpy as np

from cpc_ppg.data import AlignmentError, TrainingRecord
from cpc_ppg.preprocessing import PreprocessedWindow, preprocess_record

from ._buffers import finite_runtime, input_pair
from .cascade import CascadedWindow, run_cascaded_lms_window, run_cascaded_rls_window
from .errors import AdaptiveFilterInputError
from .models import FloatArray


@dataclass(frozen=True, slots=True, kw_only=True)
class CPCConfig:
    """Paper-reported main mixing value, distinct from RLS forgetting_factor."""

    mixing_lambda: float = .5

    def __post_init__(self) -> None:
        value = self.mixing_lambda
        if isinstance(value, bool) or not isinstance(value, Real) or not np.isfinite(value) or not 0 <= value <= 1:
            raise AdaptiveFilterInputError(f"mixing_lambda: expected finite real scalar in [0,1]; observed {value!r}")


def combine_cpc(lms_output: np.ndarray, rls_output: np.ndarray, mixing_lambda: float = .5) -> FloatArray:
    """Exactly a*LMS+(1-a)*RLS in float64; fresh read-only buffer, no transforms.

    Arrays may have any matching 1-D length (including zero). Both inputs must
    be finite even at endpoints. Scale each branch before adding; computing
    .5*(LMS+RLS) instead could overflow an otherwise representable mean.
    """
    config = CPCConfig(mixing_lambda=mixing_lambda)
    lms, rls = input_pair(lms_output, rls_output)
    with np.errstate(over="ignore", invalid="ignore"):
        output = config.mixing_lambda*lms + (1.0-config.mixing_lambda)*rls
    finite_runtime("CPC combination", 0, output=output)
    output.setflags(write=False)
    return output


@dataclass(frozen=True, slots=True, eq=False)
class CPCWindow:
    """Copied alignment metadata + CPC output, without retaining branch buffers."""

    record_id: str
    index: int
    start_sample: int
    end_sample: int
    start_time_s: float
    end_time_s: float
    bpm: float
    mixing_lambda: float
    output: FloatArray


class CPCAlignmentError(AlignmentError):
    """Two branch wrappers do not describe corresponding LMS/RLS windows."""


METADATA_FIELDS = ("record_id", "index", "start_sample", "end_sample", "start_time_s", "end_time_s", "bpm")


def _aligned(lms: CascadedWindow, rls: CascadedWindow) -> None:
    if not isinstance(lms, CascadedWindow) or not isinstance(rls, CascadedWindow):
        raise CPCAlignmentError("Expected corresponding CascadedWindow objects")
    context = f"{lms.record_id} window {lms.index}"
    if lms.branch != "LMS" or rls.branch != "RLS":
        raise CPCAlignmentError(f"{context}: expected branches LMS/RLS; observed {lms.branch}/{rls.branch}")
    for name in METADATA_FIELDS:
        left, right = getattr(lms, name), getattr(rls, name)
        if left != right:
            raise CPCAlignmentError(f"{context}: {name} mismatch; LMS={left!r}, RLS={right!r}")
    if lms.end_sample-lms.start_sample != 1000:
        raise CPCAlignmentError(f"{context}: expected 1000-sample bounds")
    if np.shape(lms.final_output) != np.shape(rls.final_output):
        raise CPCAlignmentError(f"{context}: final output shape mismatch; LMS={np.shape(lms.final_output)}, RLS={np.shape(rls.final_output)}")
    if np.shape(lms.final_output) != (1000,):
        raise AdaptiveFilterInputError(f"{context}: expected (1000,) final stage-Z errors")


def combine_cpc_windows(lms: CascadedWindow, rls: CascadedWindow, config: CPCConfig = CPCConfig()) -> CPCWindow:
    """Check identity/bounds/times/BPM and branch roles; combine only final Z errors."""
    if not isinstance(config, CPCConfig):
        raise AdaptiveFilterInputError("Expected CPCConfig")
    _aligned(lms, rls)
    output = combine_cpc(lms.final_output, rls.final_output, config.mixing_lambda)
    return CPCWindow(*(getattr(lms, name) for name in METADATA_FIELDS), float(config.mixing_lambda), output)


def run_cpc_window(window: PreprocessedWindow, config: CPCConfig = CPCConfig()) -> CPCWindow:
    """Run both branches with their documented default configurations."""
    if not isinstance(config, CPCConfig):
        raise AdaptiveFilterInputError("Expected CPCConfig")
    lms = run_cascaded_lms_window(window)
    rls = run_cascaded_rls_window(window)
    return combine_cpc_windows(lms, rls, config)


def run_cpc_record(source: TrainingRecord | Iterable[PreprocessedWindow],
                   config: CPCConfig = CPCConfig()) -> Iterator[CPCWindow]:
    """Yield one CPC/window, retaining no branch histories or cross-window state."""
    windows = preprocess_record(source) if isinstance(source, TrainingRecord) else source
    for window in windows:
        yield run_cpc_window(window, config)


def lambda_sweep_values() -> tuple[float, ...]:
    """Paper sweep exactly 11 deterministic values; division avoids accumulated drift."""
    return tuple(index/10 for index in range(11))


def sweep_cpc_windows(lms: CascadedWindow, rls: CascadedWindow) -> Iterator[CPCWindow]:
    """Yield each paper mixing value from an existing pair; no filter rerun or scoring."""
    for mixing_lambda in lambda_sweep_values():
        yield combine_cpc_windows(lms, rls, CPCConfig(mixing_lambda=mixing_lambda))
