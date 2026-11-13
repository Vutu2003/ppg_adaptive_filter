"""Separate invalid configurations/inputs from numerical runtime failures."""


class AdaptiveFilterInputError(ValueError):
    """An input/configuration/state violates the supported real-valued contract."""


class AdaptiveFilterNumericalError(FloatingPointError):
    """A recurrence produces nonfinite state or a nonpositive RLS denominator."""
