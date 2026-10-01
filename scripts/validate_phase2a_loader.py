#!/usr/bin/env python3
"""Validate all raw Training pairs, exact windows and supplied BPM0 labels."""

import argparse
import csv
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cpc_ppg.data import (  # noqa: E402
    AlignmentError,
    DatasetValidationError,
    FiniteDataError,
    discover_training_pairs,
    load_training_record,
    segment_training_record,
    validate_segmented_windows,
)


def main(argv: list[str] | None = None) -> int:
    """Print per-record/aggregate checks; return zero only when all 12 pass."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-dir", type=Path, default=PROJECT_ROOT / "data/Training_data")
    parser.add_argument("--manifest", type=Path, help="Optional CSV output (written only on PASS)")
    args = parser.parse_args(argv)
    loaded = total_windows = alignment_failures = finite_failures = other_failures = 0
    rows = []
    try:
        pairs = discover_training_pairs(args.training_dir)
    except (DatasetValidationError, OSError) as exc:
        pairs = []
        other_failures += 1
        print(f"FAIL discovery: {exc}")

    print("record_id         N samples  duration_s  BPM0 expected segmented first[start:end] last[start:end] status")
    for pair in pairs:
        try:
            record = load_training_record(pair.signal_path, pair.label_path)
            loaded += 1
            windows = segment_training_record(record)
            summary = validate_segmented_windows(record, windows)
            total_windows += len(windows)
            first = f"[{summary.first_start}:{summary.first_end}]" if windows else "none"
            last = f"[{summary.last_start}:{summary.last_end}]" if windows else "none"
            print(f"{record.record_id:17} {record.n_samples:9d} {record.duration_s:11.2f} "
                  f"{summary.bpm_count:5d} {summary.expected_windows:8d} {len(windows):9d} "
                  f"{first:16} {last:15} PASS")
            rows.append(dict(
                record_id=record.record_id, signal_file=pair.signal_path.name,
                label_file=pair.label_path.name, n_samples=record.n_samples,
                duration_s=record.duration_s, bpm_count=summary.bpm_count,
                expected_windows=summary.expected_windows, actual_windows=len(windows),
                first_start=summary.first_start, first_end=summary.first_end,
                last_start=summary.last_start, last_end=summary.last_end, alignment_ok=True,
            ))
        except (DatasetValidationError, OSError) as exc:
            if isinstance(exc, AlignmentError):
                alignment_failures += 1
            elif isinstance(exc, FiniteDataError):
                finite_failures += 1
            else:
                other_failures += 1
            print(f"{pair.record_id:17} FAIL: {exc}")

    passed = bool(pairs) and len(rows) == len(pairs) and not (
        alignment_failures or finite_failures or other_failures
    )
    if passed and args.manifest:
        try:
            args.manifest.parent.mkdir(parents=True, exist_ok=True)
            with args.manifest.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
        except OSError as exc:
            passed = False
            other_failures += 1
            print(f"FAIL manifest [{args.manifest}]: {exc}")

    print(f"Training pairs found: {len(pairs)}")
    print(f"Records loaded: {loaded}")
    print(f"Total windows: {total_windows}")
    print(f"Alignment failures: {alignment_failures}")
    print(f"Finite-data failures: {finite_failures}")
    print(f"Other failures: {other_failures}")
    print(f"Overall status: {'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
