"""Figure curves/labels must represent the stated raw and filtered channels."""

from matplotlib.figure import Figure
import numpy as np

from cpc_ppg.preprocessing import preprocess_window
from cpc_ppg.preprocessing.diagnostics import save_diagnostic_figures


def test_figure_channel_identity_frequency_axes_and_power(raw_window, tmp_path, monkeypatch):
    output = preprocess_window(raw_window)
    captured = []
    savefig = Figure.savefig

    def capture(figure, *args, **kwargs):
        captured.append(figure)
        return savefig(figure, *args, **kwargs)

    monkeypatch.setattr(Figure, "savefig", capture)
    paths = save_diagnostic_figures(raw_window, output, tmp_path)
    channels = (
        (raw_window.ppg1, output.ppg1_filtered),
        (raw_window.ppg2, output.ppg2_filtered),
        (output.ppg1_filtered, output.ppg2_filtered, output.ppg_avg),
        (output.acc_x_filtered, output.acc_y_filtered, output.acc_z_filtered),
    )
    assert len(paths) == len(captured) == 4
    for path, figure, expected in zip(paths, captured, channels):
        assert path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
        axes = figure.axes[0]
        assert axes.get_xlabel() == "Frequency (Hz)"
        assert axes.get_xlim() == (0, 8)
        assert "DATA_01_TYPE01, window 0" in axes.get_title()
        assert len(axes.lines) == len(expected)
        for curve, signal in zip(axes.lines, expected):
            np.testing.assert_array_equal(curve.get_xdata(), np.fft.rfftfreq(1000, 1 / 125))
            np.testing.assert_array_equal(curve.get_ydata(), (np.abs(np.fft.rfft(signal)) / 1000) ** 2)
