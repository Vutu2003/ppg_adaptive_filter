"""Separate three-stage ANC branches, with fresh state at every call/window.

Paper §3.2 specifies separate X -> Y -> Z references and sequential stages.
Error chaining, zero initialization, order-as-taps, forgetting-factor RLS,
P0=I and window reset are explicit reconstruction assumptions, not author code.
"""

from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from typing import Literal

import numpy as np

from cpc_ppg.data import TrainingRecord
from cpc_ppg.preprocessing import PreprocessedWindow, preprocess_record

from ._buffers import real_array
from .config import LMSConfig, RLSConfig, paper_lms_config, paper_rls_reconstruction_config
from .errors import AdaptiveFilterInputError, AdaptiveFilterNumericalError
from .lms import lms_filter
from .models import FloatArray, LMSResult, LMSState, RLSResult, RLSState
from .rls import rls_filter

Branch = Literal["LMS", "RLS"]


def paper_cascaded_lms_reconstruction_config() -> LMSConfig:
    """Reported mu/order; zero state and order-as-taps remain reconstruction."""
    return paper_lms_config()


def paper_cascaded_rls_reconstruction_config() -> RLSConfig:
    """Reported .999/55; forgetting-factor, order-as-taps and P0=I are assumed."""
    return paper_rls_reconstruction_config(initial_covariance_scale=1.0)


@dataclass(frozen=True, slots=True, eq=False)
class CascadeStageResult:
    stage_name: str
    reference_name: str
    error: FloatArray
    final_state: LMSState | RLSState
    desired: FloatArray | None = None
    prediction: FloatArray | None = None


@dataclass(frozen=True, slots=True, eq=False)
class CascadeResult:
    branch: Branch
    stage_x: CascadeStageResult
    stage_y: CascadeStageResult
    stage_z: CascadeStageResult

    @property
    def stages(self) -> tuple[CascadeStageResult, ...]:
        return self.stage_x, self.stage_y, self.stage_z

    @property
    def final_output(self) -> FloatArray:
        """Final ANC error; same buffer as stage Z, never adaptive prediction."""
        return self.stage_z.error


class CascadeNumericalError(AdaptiveFilterNumericalError):
    """Preserve primitive failure plus exact branch/stage; never retry or repair."""

    def __init__(self, branch: Branch, stage: str, error: str):
        self.branch, self.stage = branch, stage
        super().__init__(f"{branch} stage {stage}: {error}")


def _run_three_stage_cascade(
    desired: np.ndarray, acc_x: np.ndarray, acc_y: np.ndarray, acc_z: np.ndarray,
    runner: Callable[[FloatArray, FloatArray], LMSResult | RLSResult],
    branch: Branch, *, details: bool,
) -> CascadeResult:
    if not isinstance(details, bool):
        raise AdaptiveFilterInputError("details: expected boolean")
    d = real_array(desired, "ppg")
    references = [real_array(x, name, shape=d.shape) for x, name in
                  zip((acc_x, acc_y, acc_z), ("acc_x", "acc_y", "acc_z"))]
    # A read-only view avoids changing caller flags or duplicating samples.
    d = d.view()
    d.setflags(write=False)
    stages = []
    for axis, reference in zip(("X", "Y", "Z"), references):
        try:
            result = runner(reference, d)  # always fresh; no initial_state argument
        except AdaptiveFilterNumericalError as exc:
            raise CascadeNumericalError(branch, axis, str(exc)) from exc
        stages.append(CascadeStageResult(
            axis, f"ACC-{axis}", result.error, result.final_state,
            d if details else None, result.output if details else None,
        ))
        d = result.error
    return CascadeResult(branch, *stages)


def cascaded_lms(
    ppg: np.ndarray, acc_x: np.ndarray, acc_y: np.ndarray, acc_z: np.ndarray,
    config: LMSConfig = paper_cascaded_lms_reconstruction_config(), *, details: bool = False,
) -> CascadeResult:
    """Three independent fresh LMS stages; optional diagnostics, no weight histories."""
    if not isinstance(config, LMSConfig):
        raise AdaptiveFilterInputError("Expected LMSConfig")
    return _run_three_stage_cascade(
        ppg, acc_x, acc_y, acc_z, lambda x, d: lms_filter(x, d, config), "LMS", details=details,
    )


def cascaded_rls(
    ppg: np.ndarray, acc_x: np.ndarray, acc_y: np.ndarray, acc_z: np.ndarray,
    config: RLSConfig = paper_cascaded_rls_reconstruction_config(), *, details: bool = False,
) -> CascadeResult:
    """Three independent fresh RLS stages; baseline P0=I, no covariance histories."""
    if not isinstance(config, RLSConfig):
        raise AdaptiveFilterInputError("Expected RLSConfig")
    return _run_three_stage_cascade(
        ppg, acc_x, acc_y, acc_z, lambda x, d: rls_filter(x, d, config), "RLS", details=details,
    )


@dataclass(frozen=True, slots=True, eq=False)
class CascadedWindow:
    """Branch-distinct output, alignment metadata only; no raw channel buffers."""

    record_id: str
    index: int
    start_sample: int
    end_sample: int
    start_time_s: float
    end_time_s: float
    bpm: float
    cascade: CascadeResult

    @property
    def branch(self) -> Branch:
        return self.cascade.branch

    @property
    def final_output(self) -> FloatArray:
        return self.cascade.final_output


def _window(window: PreprocessedWindow, runner: Callable, config: LMSConfig | RLSConfig,
            details: bool) -> CascadedWindow:
    if not isinstance(window, PreprocessedWindow):
        raise AdaptiveFilterInputError("Expected PreprocessedWindow")
    signals = (window.ppg_avg, window.acc_x_filtered, window.acc_y_filtered, window.acc_z_filtered)
    if window.fs != 125 or window.end_sample - window.start_sample != 1000 or any(
        np.shape(signal) != (1000,) for signal in signals
    ):
        raise AdaptiveFilterInputError("Expected 125 Hz, 1000-sample preprocessed window/bounds")
    result = runner(*signals, config, details=details)
    # BPM is read only here, after adaptation, and copied without transformation.
    return CascadedWindow(window.record_id, window.index, window.start_sample, window.end_sample,
                          window.start_time_s, window.end_time_s, window.bpm, result)


def run_cascaded_lms_window(window: PreprocessedWindow,
                            config: LMSConfig = paper_cascaded_lms_reconstruction_config(), *,
                            details: bool = False) -> CascadedWindow:
    return _window(window, cascaded_lms, config, details)


def run_cascaded_rls_window(window: PreprocessedWindow,
                            config: RLSConfig = paper_cascaded_rls_reconstruction_config(), *,
                            details: bool = False) -> CascadedWindow:
    return _window(window, cascaded_rls, config, details)


def _windows(source: TrainingRecord | Iterable[PreprocessedWindow]) -> Iterable[PreprocessedWindow]:
    return preprocess_record(source) if isinstance(source, TrainingRecord) else source


def run_cascaded_lms_record(source: TrainingRecord | Iterable[PreprocessedWindow],
                            config: LMSConfig = paper_cascaded_lms_reconstruction_config(), *,
                            details: bool = False) -> Iterator[CascadedWindow]:
    """Yield one fresh LMS cascade/window; consumer controls retention of outputs."""
    for window in _windows(source):
        yield run_cascaded_lms_window(window, config, details=details)


def run_cascaded_rls_record(source: TrainingRecord | Iterable[PreprocessedWindow],
                            config: RLSConfig = paper_cascaded_rls_reconstruction_config(), *,
                            details: bool = False) -> Iterator[CascadedWindow]:
    """Yield one fresh RLS cascade/window; consumer controls retention of outputs."""
    for window in _windows(source):
        yield run_cascaded_rls_window(window, config, details=details)
