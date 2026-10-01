"""MAT v5 loading and confirmed raw Training channel extraction."""

from pathlib import Path

import numpy as np
from scipy.io import loadmat

from .discovery import discover_training_pairs, parse_training_filename
from .errors import DatasetValidationError, PairingError
from .models import NumericArray, TrainingRecord
from .protocol import CHANNEL_NAMES, EXPECTED_TRAINING_RECORDS, FS
from .validation import validate_numeric_array, validate_training_record


def _read_variable(path: Path, variable: str, record_id: str) -> NumericArray:
    context = f"{record_id} [{path}]"
    try:
        content = loadmat(path, variable_names=[variable], squeeze_me=False)
    except Exception as exc:
        raise DatasetValidationError(
            f"{context}: expected readable MATLAB v5 file containing {variable}; "
            f"observed {type(exc).__name__}: {exc}"
        ) from exc
    if variable not in content:
        raise DatasetValidationError(f"{context}: expected variable {variable!r}; observed variable absent")
    return content[variable]


def load_training_record(signal_path: str | Path, label_path: str | Path) -> TrainingRecord:
    """Load a matched Training pair, preserving raw values, dtype and orientation.

    Require sig=(6,N), BPM0 as a vector, finite real data and exact 1000/250
    window alignment. Exposed arrays are read-only views; copy explicitly if
    later phases need writable buffers. Current MAT v5 files use scipy.io.loadmat.
    """
    signal_path, label_path = Path(signal_path), Path(label_path)
    signal_id = parse_training_filename(signal_path)
    label_id = parse_training_filename(label_path)
    if signal_id is None or signal_id[1] or label_id is None or not label_id[1] or signal_id[0] != label_id[0]:
        raise PairingError(
            f"[{signal_path}; {label_path}]: expected matching DATA_NN_TYPENN signal/BPMtrace names; "
            f"observed identifiers {signal_id}, {label_id}"
        )
    record_id = signal_id[0]
    sig = _read_variable(signal_path, "sig", record_id)
    validate_numeric_array(sig, context=f"{record_id} [{signal_path}] sig", ndim=2)
    if sig.shape[0] != len(CHANNEL_NAMES):
        raise DatasetValidationError(
            f"{record_id} [{signal_path}]: expected sig shape (6, N); observed {sig.shape}. No transpose applied."
        )
    labels = _read_variable(label_path, "BPM0", record_id)
    if not isinstance(labels, np.ndarray) or not (
        labels.ndim == 1 or (labels.ndim == 2 and 1 in labels.shape)
    ):
        raise DatasetValidationError(
            f"{record_id} [{label_path}]: expected BPM0 vector (M,), (M,1) or (1,M); "
            f"observed {getattr(labels, 'shape', type(labels).__name__)}"
        )
    bpm = labels.reshape(-1)
    validate_numeric_array(bpm, context=f"{record_id} [{label_path}] BPM0", ndim=1)
    sig.setflags(write=False)
    bpm.setflags(write=False)
    channels = {name: sig[index] for index, name in enumerate(CHANNEL_NAMES)}
    record = TrainingRecord(record_id, signal_path, label_path, FS, **channels, bpm=bpm)
    validate_training_record(record)
    return record


def load_all_training_records(
    training_dir: str | Path, *, expected_count: int | None = EXPECTED_TRAINING_RECORDS
) -> list[TrainingRecord]:
    """Discover and validate Training records in deterministic identifier order."""
    pairs = discover_training_pairs(training_dir, expected_count=expected_count)
    return [load_training_record(pair.signal_path, pair.label_path) for pair in pairs]
