#!/usr/bin/env python3
"""Validate raw integrity and CPC baseline preprocessing on all Training pairs."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cpc_ppg.data import (  # noqa: E402
    DatasetValidationError, discover_training_pairs, load_training_record,
    segment_training_record, validate_segmented_windows,
)
from cpc_ppg.data.protocol import CHANNEL_NAMES  # noqa: E402
from cpc_ppg.preprocessing import PreprocessingConfig, preprocess_record  # noqa: E402
from cpc_ppg.preprocessing.validation import (  # noqa: E402
    PreprocessingValidationError, validate_preprocessed_window,
)


def main(argv: list[str] | None = None) -> int:
    """Return 0 only when every record/window/integrity check passes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-dir", type=Path, default=PROJECT_ROOT / "data/Training_data")
    parser.add_argument("--figures-dir", type=Path, help="Generate four diagnostics for first record/window")
    parser.add_argument("--summary-json", type=Path, help="Optional machine-readable validation evidence")
    args = parser.parse_args(argv)
    config = PreprocessingConfig()
    frequencies = np.fft.rfftfreq(config.fft_length, d=1 / config.fs)
    retained = frequencies[(frequencies >= config.low_hz) & (frequencies <= config.high_hz)]
    totals = {
        "training_records": 0, "input_windows": 0, "preprocessed_windows": 0,
        "window_count_mismatches": 0, "shape_failures": 0, "finite_output_failures": 0,
        "ppg_average_failures": 0, "out_of_band_spectral_failures": 0,
        "raw_integrity_failures": 0, "alignment_failures": 0, "other_failures": 0,
    }
    categories = {"shape": "shape_failures", "finite": "finite_output_failures",
                  "average": "ppg_average_failures", "spectral": "out_of_band_spectral_failures",
                  "alignment": "alignment_failures"}
    record_rows = []
    max_coefficient_leakage = max_energy_fraction = 0.
    spectra_checked = 0
    representative = None
    figure_paths = []
    try:
        pairs = discover_training_pairs(args.training_dir)
    except (DatasetValidationError, OSError) as exc:
        pairs = []
        totals["other_failures"] += 1
        print(f"FAIL discovery: {exc}")

    for pair in pairs:
        failed_before = sum(value for key, value in totals.items() if key.endswith(("failures", "mismatches")))
        try:
            paths = (pair.signal_path, pair.label_path)
            before_files = {}
            for path in paths:
                with path.open("rb") as handle:
                    before_files[path] = hashlib.file_digest(handle, "sha256").hexdigest()
            record = load_training_record(*paths)
            totals["training_records"] += 1
            snapshots = {name: getattr(record, name).copy() for name in (*CHANNEL_NAMES, "bpm")}
            flags = {name: getattr(record, name).flags.writeable for name in snapshots}
            raw_windows = segment_training_record(record)
            validate_segmented_windows(record, raw_windows)
            outputs = preprocess_record(record, config)
            totals["input_windows"] += len(raw_windows)
            totals["preprocessed_windows"] += len(outputs)
            if not len(raw_windows) == len(outputs) == len(record.bpm):
                totals["window_count_mismatches"] += 1
                print(f"FAIL {record.record_id}: counts raw={len(raw_windows)}, processed={len(outputs)}, BPM0={len(record.bpm)}")
            for raw, output in zip(raw_windows, outputs):
                try:
                    metrics = validate_preprocessed_window(raw, output, config)
                    spectra_checked += len(metrics)
                    max_coefficient_leakage = max(max_coefficient_leakage, *(m.max_relative_out_of_band for m in metrics))
                    max_energy_fraction = max(max_energy_fraction, *(m.out_of_band_energy_fraction for m in metrics))
                except PreprocessingValidationError as exc:
                    totals[categories[exc.category]] += 1
                    print(f"FAIL {exc}")
            if representative is None and raw_windows and outputs:
                representative = (raw_windows[0], outputs[0])
            arrays_unchanged = all(
                np.array_equal(getattr(record, name), values)
                and getattr(record, name).dtype == values.dtype
                and getattr(record, name).flags.writeable == flags[name]
                for name, values in snapshots.items()
            )
            files_unchanged = True
            for path, digest in before_files.items():
                with path.open("rb") as handle:
                    files_unchanged &= hashlib.file_digest(handle, "sha256").hexdigest() == digest
            if not arrays_unchanged or not files_unchanged:
                totals["raw_integrity_failures"] += 1
                print(f"FAIL {record.record_id}: raw arrays/labels/flags or MAT files changed")
            # Recheck raw window slices after all preprocessing.
            validate_segmented_windows(record, raw_windows)
            failed_after = sum(value for key, value in totals.items() if key.endswith(("failures", "mismatches")))
            status = "PASS" if failed_after == failed_before else "FAIL"
            record_rows.append({"record_id": record.record_id, "input_windows": len(raw_windows),
                                "preprocessed_windows": len(outputs), "status": status})
            print(f"{record.record_id}: input={len(raw_windows)}, preprocessed={len(outputs)}, {status}")
        except (DatasetValidationError, ValueError, OSError) as exc:
            totals["other_failures"] += 1
            print(f"FAIL {pair.record_id}: {exc}")

    failures = sum(value for key, value in totals.items() if key.endswith(("failures", "mismatches")))
    passed = bool(pairs) and totals["training_records"] == len(pairs) and len(record_rows) == len(pairs) and failures == 0
    if passed and args.figures_dir and representative:
        try:
            from cpc_ppg.preprocessing.diagnostics import save_diagnostic_figures
            figure_paths = save_diagnostic_figures(*representative, args.figures_dir)
        except (ValueError, OSError) as exc:
            totals["other_failures"] += 1
            passed = False
            print(f"FAIL figures: {exc}")
    summary = {
        **totals, "overall_status": "PASS" if passed else "FAIL", "records": record_rows,
        "fs": config.fs, "window_samples": config.fft_length, "fft_length": config.fft_length,
        "bin_spacing_hz": config.fs / config.fft_length,
        "requested_passband_hz": [config.low_hz, config.high_hz],
        "first_retained_hz": float(retained[0]), "last_retained_hz": float(retained[-1]),
        "retained_rfft_bins": int(retained.size), "spectra_checked": spectra_checked,
        "max_relative_out_of_band": max_coefficient_leakage,
        "max_out_of_band_energy_fraction": max_energy_fraction,
        "figures": [str(path) for path in figure_paths],
        "representative": {"record_id": representative[0].record_id, "index": representative[0].index} if representative else None,
    }
    if args.summary_json:
        try:
            args.summary_json.parent.mkdir(parents=True, exist_ok=True)
            args.summary_json.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        except OSError as exc:
            totals["other_failures"] += 1
            passed = False
            print(f"FAIL summary output: {exc}")

    for key, value in totals.items():
        labels = {"training_records": "Training records", "window_count_mismatches": "Window-count mismatches",
                  "finite_output_failures": "Finite-output failures", "raw_integrity_failures": "Raw-integrity failures",
                  "ppg_average_failures": "PPG-average failures",
                  "out_of_band_spectral_failures": "Out-of-band spectral failures"}
        print(f"{labels.get(key, key.replace('_', ' ').capitalize())}: {value}")
    print(f"Fs: {config.fs} Hz; window samples: {config.fft_length}; FFT length: {config.fft_length}")
    print(f"FFT bin spacing: {config.fs / config.fft_length} Hz")
    print(f"Requested passband: {config.low_hz}–{config.high_hz} Hz")
    print(f"First/last retained FFT bins: {retained[0]} / {retained[-1]} Hz; retained rFFT bins: {retained.size}")
    print(f"Spectra checked: {spectra_checked}; max out-of-band energy fraction: {max_energy_fraction:.3e}")
    print(f"Overall status: {'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
