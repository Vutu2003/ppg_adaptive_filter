"""Real 12-record validation and CLI success/failure behavior."""

import csv
import hashlib
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest
from scipy.io import loadmat
import yaml

from cpc_ppg.data import discover_training_pairs, load_all_training_records, segment_training_record, validate_segmented_windows
from cpc_ppg.data.protocol import CHANNEL_NAMES, FS, HOP_SAMPLES, WINDOW_SAMPLES

ROOT = Path(__file__).resolve().parents[2]
TRAINING = ROOT / "data/Training_data"
SCRIPT = ROOT / "scripts/validate_phase2a_loader.py"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.integration
@pytest.mark.skipif(not TRAINING.is_dir(), reason="Local Training dataset is not present")
def test_all_twelve_real_records_and_raw_integrity():
    pairs = discover_training_pairs(TRAINING)
    assert len(pairs) == 12
    paths = [path for pair in pairs for path in (pair.signal_path, pair.label_path)]
    before = {path: digest(path) for path in paths}
    schema = yaml.safe_load((ROOT / "data/metadata/dataset_schema.yaml").read_text())
    assert [p.signal_path.relative_to(ROOT).as_posix() for p in pairs] == schema["replication"]["primary_files"]
    assert (FS, WINDOW_SAMPLES, HOP_SAMPLES) == (125, 1000, 250)
    records = load_all_training_records(TRAINING)
    assert len(records) == 12
    for record in records:
        sig = loadmat(record.signal_path)["sig"]
        bpm = loadmat(record.label_path)["BPM0"].reshape(-1)
        assert sig.shape == (6, record.n_samples)
        for index, name in enumerate(CHANNEL_NAMES):
            np.testing.assert_array_equal(getattr(record, name), sig[index])
            assert getattr(record, name).dtype == sig.dtype
        np.testing.assert_array_equal(record.bpm, bpm)
        windows = segment_training_record(record)
        summary = validate_segmented_windows(record, windows)
        assert len(windows) == len(bpm) == summary.expected_windows
        assert windows[0].start_sample == 0
        assert windows[-1].end_sample <= record.n_samples
        assert windows[-1].start_sample + 250 + 1000 > record.n_samples
    assert {path: digest(path) for path in paths} == before


@pytest.mark.integration
@pytest.mark.skipif(not TRAINING.is_dir(), reason="Local Training dataset is not present")
def test_real_validation_cli_and_manifest(tmp_path):
    manifest = tmp_path / "alignment.csv"
    result = subprocess.run([sys.executable, str(SCRIPT), "--manifest", str(manifest)],
                            cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Training pairs found: 12" in result.stdout
    assert "Records loaded: 12" in result.stdout
    assert "Alignment failures: 0" in result.stdout
    assert "Finite-data failures: 0" in result.stdout
    assert "Overall status: PASS" in result.stdout
    with manifest.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 12
    assert all(row["expected_windows"] == row["actual_windows"] == row["bpm_count"] for row in rows)
    assert all(row["first_start"] == "0" and row["alignment_ok"] == "True" for row in rows)


def test_cli_rejects_missing_dataset(tmp_path):
    manifest = tmp_path / "must_not_exist.csv"
    result = subprocess.run([sys.executable, str(SCRIPT), "--training-dir", str(tmp_path / "absent"),
                             "--manifest", str(manifest)], capture_output=True, text=True)
    assert result.returncode != 0
    assert "Overall status: FAIL" in result.stdout
    assert not manifest.exists()


@pytest.mark.parametrize("bad_kind,expected_counter", [
    ("alignment", "Alignment failures: 1"), ("finite", "Finite-data failures: 1"),
    ("shape", "Other failures: 1"),
])
def test_cli_reports_bad_record_and_continues(tmp_path, write_pair, bad_kind, expected_counter):
    for index in range(1, 13):
        kwargs = {}
        if index == 1:
            if bad_kind == "alignment":
                kwargs["bpm"] = [70.]
            elif bad_kind == "finite":
                kwargs["bpm"] = [np.nan, 71.]
            else:
                kwargs["sig"] = np.zeros((5, 1250))
        write_pair(f"DATA_{index:02d}_TYPE02", **kwargs)
    result = subprocess.run([sys.executable, str(SCRIPT), "--training-dir", str(tmp_path)],
                            capture_output=True, text=True)
    assert result.returncode == 1
    assert "Records loaded: 11" in result.stdout
    assert "Total windows: 22" in result.stdout
    assert expected_counter in result.stdout
    assert "Overall status: FAIL" in result.stdout
