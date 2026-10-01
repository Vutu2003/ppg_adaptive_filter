"""Raw channel mapping, MAT vector handling and invalid-input checks."""

import numpy as np
import pytest
from scipy.io import loadmat, savemat

from cpc_ppg.data import AlignmentError, DatasetValidationError, FiniteDataError, PairingError, load_training_record
from cpc_ppg.data.protocol import CHANNEL_NAMES


@pytest.mark.parametrize("dtype", [np.float64, np.float32, np.int16])
def test_channels_preserve_mapping_dtype_and_clipping(write_pair, make_record, dtype):
    source = make_record(dtype=dtype)
    sig = np.stack([getattr(source, name) for name in CHANNEL_NAMES])
    record = load_training_record(*write_pair(sig=sig))
    assert record.n_samples == 1250
    assert record.fs == 125
    assert record.duration_s == 10
    for index, name in enumerate(CHANNEL_NAMES):
        channel = getattr(record, name)
        np.testing.assert_array_equal(channel, sig[index])
        assert channel.dtype == sig.dtype
        assert channel.shape == (1250,)
        assert not channel.flags.writeable
        with pytest.raises(ValueError):
            channel[0] = 0
    assert record.ppg1[0] == -1024
    assert not record.bpm.flags.writeable


@pytest.mark.parametrize("row", [True, False])
def test_matlab_row_and_column_labels(write_pair, row):
    paths = write_pair(bpm=[71.25, 99.75], row_labels=row)
    original = loadmat(paths[1])["BPM0"]
    assert original.shape == ((1, 2) if row else (2, 1))
    record = load_training_record(*paths)
    assert record.bpm.shape == (2,)
    np.testing.assert_array_equal(record.bpm, [71.25, 99.75])


def test_already_one_dimensional_labels(write_pair, monkeypatch):
    paths = write_pair()
    import cpc_ppg.data.loader as loader
    def fake_loadmat(path, **kwargs):
        return {"BPM0": np.array([70., 71.])} if path == paths[1] else loadmat(path, **kwargs)
    monkeypatch.setattr(loader, "loadmat", fake_loadmat)
    assert load_training_record(*paths).bpm.shape == (2,)


@pytest.mark.parametrize("shape", [(5, 1250), (7, 1250), (1250, 6), (6, 5, 2)])
def test_invalid_signal_shapes(write_pair, shape):
    with pytest.raises(DatasetValidationError, match="expected.*observed"):
        load_training_record(*write_pair(sig=np.zeros(shape)))


def test_one_dimensional_signal_rejected(write_pair, monkeypatch):
    paths = write_pair()
    import cpc_ppg.data.loader as loader
    # savemat promotes 1-D arrays to 2-D; inject the true invalid reader result.
    monkeypatch.setattr(loader, "loadmat", lambda *args, **kwargs: {"sig": np.zeros(1250)})
    with pytest.raises(DatasetValidationError, match="expected 2-D"):
        load_training_record(*paths)


@pytest.mark.parametrize("shape", [(2, 2), (1, 2, 1), (0, 0)])
def test_multidimensional_labels_rejected(write_pair, shape):
    with pytest.raises(DatasetValidationError, match="expected BPM0 vector"):
        load_training_record(*write_pair(bpm=np.zeros(shape)))


@pytest.mark.parametrize("variable,index", [("sig", 0), ("BPM0", 1)])
def test_missing_mat_variable(write_pair, variable, index):
    paths = write_pair()
    savemat(paths[index], {"wrong_name": np.ones((1, 1))})
    with pytest.raises(DatasetValidationError, match=f"expected variable '{variable}'.*absent"):
        load_training_record(*paths)


@pytest.mark.parametrize("target", ["sig", "bpm"])
@pytest.mark.parametrize("bad", [np.nan, np.inf, -np.inf])
def test_nonfinite_input_rejected(write_pair, target, bad):
    values = np.zeros((6, 1250)) if target == "sig" else np.array([70., 71.])
    values.flat[0] = bad
    with pytest.raises(FiniteDataError, match="expected finite.*1 NaN/Inf"):
        load_training_record(*write_pair(**{target: values}))


@pytest.mark.parametrize("target", ["sig", "bpm"])
@pytest.mark.parametrize("dtype", [np.complex128, object])
def test_nonreal_nonnumeric_input_rejected(write_pair, target, dtype):
    values = np.zeros((6, 1250), dtype=dtype) if target == "sig" else np.ones((1, 2), dtype=dtype)
    with pytest.raises(DatasetValidationError, match="expected real integer/float"):
        load_training_record(*write_pair(**{target: values}))


@pytest.mark.parametrize("labels", [[70.], [70., 71., 72.]])
def test_label_count_mismatch_fails_loading(write_pair, labels):
    with pytest.raises(AlignmentError, match="expected 2 BPM0 labels; observed"):
        load_training_record(*write_pair(bpm=labels))


@pytest.mark.parametrize("mode", ["missing", "corrupt"])
def test_reader_error_has_record_path_context(write_pair, mode):
    paths = write_pair()
    if mode == "missing":
        paths[0].unlink()
    else:
        paths[0].write_bytes(b"invalid MAT file")
    with pytest.raises(DatasetValidationError, match="DATA_01_TYPE01.*expected readable MATLAB v5"):
        load_training_record(*paths)


@pytest.mark.parametrize("mode", ["mismatch", "swapped", "invalid_name"])
def test_filename_pair_validation(write_pair, mode):
    signal, label = write_pair()
    if mode == "mismatch":
        label = label.with_name("DATA_02_TYPE02_BPMtrace.mat")
    elif mode == "swapped":
        signal, label = label, signal
    else:
        signal = signal.with_name("random.mat")
    with pytest.raises(PairingError, match="expected matching"):
        load_training_record(signal, label)


def test_short_record_with_empty_labels(write_pair):
    record = load_training_record(*write_pair(n_samples=999))
    assert record.n_samples == 999
    assert record.bpm.shape == (0,)
