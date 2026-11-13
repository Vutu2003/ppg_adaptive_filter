"""Reported parameters and explicitly assumed order/scalar interpretations."""

from dataclasses import dataclass
from numbers import Integral, Real
from typing import Final

import numpy as np

from .errors import AdaptiveFilterInputError

# PAPER-SPECIFIED values, CPC §4.1 p.21.
LMS_REPORTED_ORDER: Final = 27
LMS_REPORTED_MU: Final = .0001
RLS_REPORTED_ORDER: Final = 55
RLS_REPORTED_SCALAR: Final = .999
# RECONSTRUCTION-ASSUMPTION: reported order is coefficient count, not M-1.
ORDER_CONVENTION: Final = "reported_order_equals_number_of_taps"


def _positive_real(name: str, value: float) -> None:
    if isinstance(value, bool) or not isinstance(value, Real) or not np.isfinite(value) or value <= 0:
        raise AdaptiveFilterInputError(f"{name}: expected positive finite real scalar; observed {value!r}")


def _tap_count(value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, Integral) or value < 1:
        raise AdaptiveFilterInputError(f"n_taps: expected integer >= 1; observed {value!r}")


@dataclass(frozen=True, slots=True, kw_only=True)
class LMSConfig:
    """Standard LMS; order-as-taps and recurrence are reconstruction assumptions."""

    n_taps: int = LMS_REPORTED_ORDER
    mu: float = LMS_REPORTED_MU

    def __post_init__(self) -> None:
        _tap_count(self.n_taps)
        _positive_real("mu", self.mu)


@dataclass(frozen=True, slots=True, kw_only=True)
class RLSConfig:
    """Exponentially weighted RLS reconstruction with an explicit P0 scale.

    The .999 default interprets the paper-reported scalar as forgetting factor;
    that author interpretation remains UNRESOLVED. P0=scale*I on a fresh call.
    When continuing, initial_state.covariance is used unchanged instead of P0.
    No author-equivalent covariance scale or window reset policy is implied.
    """

    initial_covariance_scale: float
    n_taps: int = RLS_REPORTED_ORDER
    forgetting_factor: float = RLS_REPORTED_SCALAR

    def __post_init__(self) -> None:
        _tap_count(self.n_taps)
        _positive_real("forgetting_factor", self.forgetting_factor)
        if self.forgetting_factor > 1:
            raise AdaptiveFilterInputError(
                f"forgetting_factor: expected <= 1; observed {self.forgetting_factor}"
            )
        _positive_real("initial_covariance_scale", self.initial_covariance_scale)


def paper_lms_config() -> LMSConfig:
    """Reported mu=.0001/order=27, with the documented order-as-taps assumption."""
    return LMSConfig()


def paper_rls_reconstruction_config(*, initial_covariance_scale: float) -> RLSConfig:
    """Reported order=55/scalar=.999, assuming forgetting-factor RLS; P0 required."""
    return RLSConfig(initial_covariance_scale=initial_covariance_scale)
