"""Standalone conventional real LMS, independent of target recordings."""

import numpy as np

from ._buffers import advance_regressor, finite_runtime, initial_regressor, initial_weights as make_weights, input_pair, readonly
from .config import LMSConfig
from .errors import AdaptiveFilterInputError
from .models import LMSResult, LMSState


def lms_filter(
    reference: np.ndarray, desired: np.ndarray, config: LMSConfig = LMSConfig(), *,
    initial_state: LMSState | None = None, initial_weights: np.ndarray | None = None,
    store_history: bool = False,
) -> LMSResult:
    """y=wᵀu; e=d-y; w_next=w+mu*e*u, with causal zero-padded history.

    Outputs use pre-update weights. Fresh calls use zero weights/history unless
    explicitly supplied; this is a reconstruction choice, not author-confirmed.
    Continued calls copy caller state and preserve reference delays. Final state
    is after the last update. Empty input returns an independent unchanged state.
    No normalization, clipping or step-size adaptation. O(M) per sample.
    """
    x, d = input_pair(reference, desired)
    if not isinstance(config, LMSConfig) or not isinstance(store_history, bool):
        raise AdaptiveFilterInputError("Expected LMSConfig and boolean store_history")
    if initial_state is not None and (not isinstance(initial_state, LMSState) or initial_weights is not None):
        raise AdaptiveFilterInputError("Use LMSState or initial_weights, not both")
    weights = make_weights(initial_state.weights if initial_state is not None else initial_weights, config.n_taps)
    history = np.zeros(config.n_taps - 1) if initial_state is None else initial_state.reference_history
    u = initial_regressor(history, config.n_taps)
    output, error = np.empty(x.size), np.empty(x.size)
    weight_history = np.empty((x.size + 1, config.n_taps)) if store_history else None
    if weight_history is not None:
        weight_history[0] = weights
    for index in range(x.size):
        advance_regressor(u, x[index])
        with np.errstate(over="ignore", invalid="ignore"):
            output[index] = weights @ u
            error[index] = d[index] - output[index]
            weights = weights + config.mu * error[index] * u
        finite_runtime("LMS", index, output=output[index], error=error[index], weights=weights)
        if weight_history is not None:
            weight_history[index + 1] = weights
    final_history = u[:-1].copy() if x.size else np.asarray(history, dtype=np.float64).copy()
    readonly(output, error, weights, final_history)
    if weight_history is not None:
        readonly(weight_history)
    return LMSResult(output, error, LMSState(weights, final_history), weight_history)
