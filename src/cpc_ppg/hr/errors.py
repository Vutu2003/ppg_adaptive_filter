"""Explicit HR input, sequence, tracking and numerical failures."""


class HRInputError(ValueError):
    pass


class HRAlignmentError(ValueError):
    pass


class HRTrackingError(ValueError):
    pass


class HRNumericalError(FloatingPointError):
    pass
