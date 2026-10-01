"""Public API for confirmed raw Training data and window/label alignment."""

from .discovery import discover_training_pairs
from .errors import AlignmentError, DatasetValidationError, FiniteDataError, PairingError
from .loader import load_all_training_records, load_training_record
from .models import AlignmentSummary, TrainingPair, TrainingRecord, TrainingWindow
from .segmentation import segment_training_record
from .validation import validate_segmented_windows, validate_training_record

__all__ = [
    "discover_training_pairs", "load_training_record", "load_all_training_records",
    "segment_training_record", "validate_training_record", "validate_segmented_windows",
    "TrainingPair", "TrainingRecord", "TrainingWindow", "AlignmentSummary",
    "DatasetValidationError", "PairingError", "FiniteDataError", "AlignmentError",
]
