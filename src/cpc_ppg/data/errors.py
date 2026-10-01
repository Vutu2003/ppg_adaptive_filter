"""Explicit failures for raw Training data and alignment."""


class DatasetValidationError(ValueError):
    """A file or array violates the Training data contract."""


class PairingError(DatasetValidationError):
    """Training signal/label discovery is missing or ambiguous."""


class FiniteDataError(DatasetValidationError):
    """A raw signal or label contains NaN or infinity."""


class AlignmentError(DatasetValidationError):
    """Signal windows and supplied BPM0 labels do not align exactly."""
