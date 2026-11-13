"""Standalone exponentially weighted RLS baseline, with unresolved author details."""

import numpy as np

from ._buffers import advance_regressor, covariance_buffer, finite_runtime, initial_regressor, initial_weights as make_weights, input_pair, readonly, validate_covariance
from .config import RLSConfig
from .errors import AdaptiveFilterInputError, AdaptiveFilterNumericalError
from .models import RLSResult, RLSState


def rls_filter(
    reference: np.ndarray, desired: np.ndarray, config: RLSConfig, *,
    initial_state: RLSState | None = None, initial_weights: np.ndarray | None = None,
    store_history: bool = False,
) -> RLSResult:
    """Conventional forgetting-factor RLS; .999 interpretation is an assumption.

    y=wᵀu; e=d-y; gamma=lambda+uᵀPu; k=Pu/gamma;
    w_next=w+k*e; P_next=(P-k*uᵀP)/lambda.
    Initial covariance scale is required and used only on fresh calls; explicit
    state carries w, P and past inputs. Outputs use state before the update.
    No epsilon, clipping, covariance reset/loading/symmetrization, normalization
    or covariance-history allocation. O(M²) per sample; boundary P checks O(M³).
    """
    x, d = input_pair(reference, desired)
    if not isinstance(config, RLSConfig) or not isinstance(store_history, bool):
        raise AdaptiveFilterInputError("Expected RLSConfig and boolean store_history")
    if initial_state is not None and (not isinstance(initial_state, RLSState) or initial_weights is not None):
        raise AdaptiveFilterInputError("Use RLSState or initial_weights, not both")
    weights = make_weights(initial_state.weights if initial_state is not None else initial_weights, config.n_taps)
    covariance = covariance_buffer(
        config.initial_covariance_scale * np.eye(config.n_taps) if initial_state is None else initial_state.covariance,
        config.n_taps,
    )
    history = np.zeros(config.n_taps - 1) if initial_state is None else initial_state.reference_history
    u = initial_regressor(history, config.n_taps)
    output, error = np.empty(x.size), np.empty(x.size)
    weight_history = np.empty((x.size + 1, config.n_taps)) if store_history else None
    if weight_history is not None:
        weight_history[0] = weights
    for index in range(x.size):
        advance_regressor(u, x[index])
        with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
            projection = covariance @ u
            denominator = config.forgetting_factor + u @ projection
            if not np.isfinite(denominator) or denominator <= 0:
                raise AdaptiveFilterNumericalError(
                    f"RLS sample {index}: expected finite positive denominator; observed {denominator}"
                )
            output[index] = weights @ u
            error[index] = d[index] - output[index]
            gain = projection / denominator
            weights = weights + gain * error[index]
            covariance = (covariance - np.outer(gain, u @ covariance)) / config.forgetting_factor
        finite_runtime("RLS", index, output=output[index], error=error[index], gain=gain, weights=weights, covariance=covariance)
        if weight_history is not None:
            weight_history[index + 1] = weights
    if x.size:
        try:
            validate_covariance(covariance, config.n_taps)
        except AdaptiveFilterInputError as exc:
            raise AdaptiveFilterNumericalError(
                f"RLS final state after {x.size} samples: covariance lost the continuation contract: {exc}"
            ) from exc
    final_history = u[:-1].copy() if x.size else np.asarray(history, dtype=np.float64).copy()
    readonly(output, error, weights, covariance, final_history)
    if weight_history is not None:
        readonly(weight_history)
    return RLSResult(output, error, RLSState(weights, covariance, final_history), weight_history)
