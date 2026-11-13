"""Post-update states and results; filter-produced arrays are read-only."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


@dataclass(frozen=True, slots=True, eq=False)
class LMSState:
    """Before next sample: weights w[n], newest-first previous M-1 references."""

    weights: FloatArray
    reference_history: FloatArray


@dataclass(frozen=True, slots=True, eq=False)
class RLSState:
    """Before next sample: w[n], P[n], newest-first previous M-1 references."""

    weights: FloatArray
    covariance: FloatArray
    reference_history: FloatArray


@dataclass(frozen=True, slots=True, eq=False)
class LMSResult:
    """y is adaptive prediction; e=d-y is the ANC cleaned-signal candidate.

    Optional weight_history has shape (N+1,M): row 0 is initial weights,
    row n+1 is weights AFTER sample n. No history allocation by default.
    """

    output: FloatArray
    error: FloatArray
    final_state: LMSState
    weight_history: FloatArray | None = None

    @property
    def final_weights(self) -> FloatArray:
        """Post-update weights, sharing the returned state buffer without duplication."""
        return self.final_state.weights


@dataclass(frozen=True, slots=True, eq=False)
class RLSResult:
    """y/e and post-update RLS state; optional (N+1,M) weight history, no P history."""

    output: FloatArray
    error: FloatArray
    final_state: RLSState
    weight_history: FloatArray | None = None

    @property
    def final_weights(self) -> FloatArray:
        """Post-update weights, sharing the returned state buffer without duplication."""
        return self.final_state.weights
