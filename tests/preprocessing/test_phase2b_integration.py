"""Every real Training window, integrity and CLI/figures regression."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from cpc_ppg.data import load_all_training_records, segment_training_record
from cpc_ppg.data.protocol import CHANNEL_NAMES
from cpc_ppg.preprocessing import preprocess_record
from cpc_ppg.preprocessing.validation import OUTPUT_CHANNELS, validate_preprocessed_window

ROOT = Path(__file__).resolve().parents[2]
TRAINING = ROOT / "data/Training_data"
SCRIPT = ROOT / "scripts/validate_phase2b_preprocessing.py"


@pytest.mark.integration
@pytest.mark.skipif(not TRAINING.is_dir(), reason="Local Training dataset is not present")
def test_all_twelve_records_all_windows_and_integrity():
    paths = sorted(TRAINING.glob("*.mat"))
    before_files = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    records = load_all_training_records(TRAINING)
    assert len(records) == 12
    inputs_total = outputs_total = 0
    for record in records:
        before_arrays = {name: getattr(record, name).copy() for name in (*CHANNEL_NAMES, "bpm")}
        raw_windows = segment_training_record(record)
        outputs = preprocess_record(record)
        assert len(raw_windows) == len(outputs) == len(record.bpm)
        inputs_total += len(raw_windows)
        outputs_total += len(outputs)
        for raw, output in zip(raw_windows, outputs):
            validate_preprocessed_window(raw, output)
            for name in ("record_id", "index", "start_sample", "end_sample", "start_time_s", "end_time_s", "bpm"):
                assert getattr(output, name) == getattr(raw, name)
            for name in OUTPUT_CHANNELS:
                channel = getattr(output, name)
                assert channel.shape == (1000,)
                assert np.isfinite(channel).all()
                assert not channel.flags.writeable
            np.testing.assert_array_equal(output.ppg_avg, (output.ppg1_filtered + output.ppg2_filtered) / 2)
        for name, before in before_arrays.items():
            np.testing.assert_array_equal(getattr(record, name), before)
            assert not getattr(record, name).flags.writeable
    assert inputs_total == outputs_total == 1768
    assert before_files == {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


@pytest.mark.integration
@pytest.mark.skipif(not TRAINING.is_dir(), reason="Local Training dataset is not present")
def test_validation_cli_all_records_and_figures(tmp_path):
    summary_path = tmp_path / "summary.json"
    figure_dir = tmp_path / "figures"
    result = subprocess.run([sys.executable, str(SCRIPT), "--summary-json", str(summary_path),
                             "--figures-dir", str(figure_dir)], cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    summary = json.loads(summary_path.read_text())
    assert summary["overall_status"] == "PASS"
    assert summary["training_records"] == 12
    assert summary["input_windows"] == summary["preprocessed_windows"] == 1768
    assert summary["spectra_checked"] == 5 * 1768
    assert all(value == 0 for name, value in summary.items() if name.endswith(("failures", "mismatches")))
    assert summary["first_retained_hz"] == .5
    assert summary["last_retained_hz"] == 3.5
    assert len(summary["figures"]) == 4
    for path in summary["figures"]:
        assert Path(path).read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert "Overall status: PASS" in result.stdout


def test_cli_nonzero_for_missing_dataset(tmp_path):
    result = subprocess.run([sys.executable, str(SCRIPT), "--training-dir", str(tmp_path / "absent")],
                            capture_output=True, text=True)
    assert result.returncode == 1
    assert "Overall status: FAIL" in result.stdout
