"""Deterministic pairing and fail-fast discovery contracts."""

import pytest

from cpc_ppg.data import PairingError, discover_training_pairs, load_all_training_records


def test_sorted_pairing_and_loading(tmp_path, write_pair):
    for record_id in ("DATA_12_TYPE02", "DATA_01_TYPE01", "DATA_02_TYPE02"):
        write_pair(record_id)
    (tmp_path / "README.txt").write_text("unrelated")
    (tmp_path / "random.mat").touch()
    pairs = discover_training_pairs(tmp_path, expected_count=3)
    assert [p.record_id for p in pairs] == ["DATA_01_TYPE01", "DATA_02_TYPE02", "DATA_12_TYPE02"]
    for pair in pairs:
        assert pair.signal_path.name == pair.record_id + ".mat"
        assert pair.label_path.name == pair.record_id + "_BPMtrace.mat"
    assert [r.record_id for r in load_all_training_records(tmp_path, expected_count=3)] == [p.record_id for p in pairs]


@pytest.mark.parametrize("remove,match", [(1, "missing labels"), (0, "orphan labels")])
def test_unpaired_files_rejected(tmp_path, write_pair, remove, match):
    paths = write_pair()
    paths[remove].unlink()
    with pytest.raises(PairingError, match=match):
        discover_training_pairs(tmp_path, expected_count=None)


@pytest.mark.parametrize("index", [0, 1])
def test_duplicate_case_alias_rejected(tmp_path, write_pair, index):
    paths = write_pair()
    (tmp_path / paths[index].name.lower()).touch()
    with pytest.raises(PairingError, match="duplicates"):
        discover_training_pairs(tmp_path, expected_count=1)


def test_primary_count_required(tmp_path, write_pair):
    write_pair()
    with pytest.raises(PairingError, match="expected 12 Training pairs; observed 1"):
        discover_training_pairs(tmp_path)


def test_missing_directory(tmp_path):
    with pytest.raises(PairingError, match="existing Training directory"):
        discover_training_pairs(tmp_path / "absent")


def test_negative_expected_count(tmp_path):
    with pytest.raises(PairingError, match="nonnegative"):
        discover_training_pairs(tmp_path, expected_count=-1)


def test_matching_directory_is_not_a_file(tmp_path):
    (tmp_path / "DATA_01_TYPE01.mat").mkdir()
    with pytest.raises(PairingError, match="non-file"):
        discover_training_pairs(tmp_path)


def test_empty_subset_explicitly_allowed(tmp_path):
    assert discover_training_pairs(tmp_path, expected_count=None) == []
