"""Deterministic discovery of Training MAT signal/BPMtrace pairs."""

from pathlib import Path
import re

from .errors import PairingError
from .models import TrainingPair
from .protocol import EXPECTED_TRAINING_RECORDS

_FILENAME = re.compile(
    r"DATA_(\d{2})_TYPE(\d{2})(_BPMtrace)?\.mat", re.IGNORECASE
)


def parse_training_filename(path: Path) -> tuple[str, bool] | None:
    """Return canonical identifier and label flag, or None for unrelated files."""
    match = _FILENAME.fullmatch(path.name)
    if match is None:
        return None
    return f"DATA_{match[1]}_TYPE{match[2]}", match[3] is not None


def discover_training_pairs(
    training_dir: str | Path,
    *,
    expected_count: int | None = EXPECTED_TRAINING_RECORDS,
) -> list[TrainingPair]:
    """Discover matching MAT files, reject ambiguity, and sort by record ID.

    The primary set requires 12 pairs by default. Set expected_count explicitly
    (or None) for fixtures/subsets. Matching is case-insensitive, so duplicate
    case variants are rejected rather than chosen by filesystem order.
    """
    folder = Path(training_dir)
    if not folder.is_dir():
        raise PairingError(f"{folder}: expected an existing Training directory")
    if expected_count is not None and expected_count < 0:
        raise PairingError(f"{folder}: expected_count must be nonnegative; observed {expected_count}")
    signals: dict[str, Path] = {}
    labels: dict[str, Path] = {}
    for path in sorted(folder.iterdir()):
        parsed = parse_training_filename(path)
        if parsed is None:
            continue
        record_id, is_label = parsed
        if not path.is_file():
            raise PairingError(f"{record_id} [{path}]: expected a MAT file; observed a non-file entry")
        target = labels if is_label else signals
        if record_id in target:
            role = "label" if is_label else "signal"
            raise PairingError(
                f"{record_id}: expected one {role} file; observed duplicates "
                f"{target[record_id]} and {path}"
            )
        target[record_id] = path
    missing = sorted(signals.keys() - labels.keys())
    orphans = sorted(labels.keys() - signals.keys())
    if missing or orphans:
        raise PairingError(
            f"{folder}: expected one signal and one BPMtrace per record; "
            f"missing labels={missing}, orphan labels={orphans}"
        )
    if expected_count is not None and len(signals) != expected_count:
        raise PairingError(
            f"{folder}: expected {expected_count} Training pairs; observed {len(signals)}"
        )
    return [TrainingPair(key, signals[key], labels[key]) for key in sorted(signals)]
