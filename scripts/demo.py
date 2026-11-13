#!/usr/bin/env python3
"""Run the core PPG → LMS/RLS → CPC → heart-rate pipeline on Training data."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np

from cpc_ppg.adaptive_filters import (
    combine_cpc_windows,
    run_cascaded_lms_window,
    run_cascaded_rls_window,
)
from cpc_ppg.data import discover_training_pairs, load_training_record, segment_training_record
from cpc_ppg.evaluation import average_absolute_error
from cpc_ppg.hr import estimate_hr_record
from cpc_ppg.preprocessing import preprocess_window


def positive_integer(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("Số cửa sổ phải lớn hơn 0.")
    return number


def run_demo(record, windows):
    """Keep the three branches aligned and use labels only after estimation."""
    branches = {"LMS": [], "RLS": [], "CPC": []}
    for raw_window in windows:
        # Lọc riêng PPG và ACC, rồi mới lấy trung bình hai kênh PPG.
        filtered = preprocess_window(raw_window)
        lms = run_cascaded_lms_window(filtered)
        rls = run_cascaded_rls_window(filtered)
        cpc = combine_cpc_windows(lms, rls)
        branches["LMS"].append(lms)
        branches["RLS"].append(rls)
        branches["CPC"].append(cpc)

    # Cùng một bộ ước lượng HR cho cả ba phương pháp; BPM0 không điều khiển lọc.
    estimates = {}
    for method, signals in branches.items():
        getter = (lambda w: w.output) if method == "CPC" else (lambda w: w.final_output)
        estimates[method] = estimate_hr_record(signals, getter).smoothed_hr_bpm

    reference = np.asarray([window.bpm for window in windows])
    print(f"Bản ghi: {record.record_id} | {len(windows)} cửa sổ | Fs = {record.fs} Hz")
    print("LMS: 27 hệ số, μ = 0.0001 | RLS: 55 hệ số, f = 0.999, P0 = I | CPC: λ = 0.5")
    print("AAE trên các cửa sổ vừa chạy (BPM):")
    for method, values in estimates.items():
        print(f"  {method}: {average_absolute_error(values, reference):.3f}")
    print("\nCác cửa sổ đầu — nhãn và HR nhân quả (BPM):")
    print("  Cửa sổ       BPM0        LMS        RLS        CPC")
    for i in range(min(5, len(windows))):
        print(f"  {i:7d} {reference[i]:10.3f} {estimates['LMS'][i]:10.3f}"
              f" {estimates['RLS'][i]:10.3f} {estimates['CPC'][i]:10.3f}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data/Training_data")
    parser.add_argument("--record", default="DATA_01_TYPE01", help="Mã bản ghi Training.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--windows", type=positive_integer, default=10,
                       help="Số cửa sổ đầu cần chạy (mặc định: 10).")
    group.add_argument("--full-record", action="store_true", help="Chạy toàn bộ bản ghi.")
    args = parser.parse_args(argv)
    try:
        pairs = discover_training_pairs(args.data_dir, expected_count=None)
        pair = next((pair for pair in pairs if pair.record_id == args.record), None)
        if pair is None:
            parser.error(f"Không tìm thấy bản ghi {args.record} trong {args.data_dir}.")
        record = load_training_record(pair.signal_path, pair.label_path)
        windows = segment_training_record(record)
        if not args.full_record:
            if args.windows > len(windows):
                parser.error(f"Bản ghi chỉ có {len(windows)} cửa sổ; hãy giảm --windows.")
            windows = windows[:args.windows]
        run_demo(record, windows)
    except (ValueError, OSError) as exc:
        print(f"Không chạy được demo: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
