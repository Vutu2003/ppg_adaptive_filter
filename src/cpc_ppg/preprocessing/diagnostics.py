"""Standalone FFT diagnostic figures; no HR estimator or parameter tuning."""

from pathlib import Path

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import numpy as np

from cpc_ppg.data import TrainingWindow

from .models import PreprocessedWindow


def save_diagnostic_figures(
    raw: TrainingWindow, output: PreprocessedWindow, output_dir: str | Path,
) -> list[Path]:
    """Save four fixed spectral diagnostics for the caller-selected raw window.

    Display |rFFT|²/L² as diagnostic coefficient power, with no taper/padding
    and no HR peaks/ground-truth markers. The identity of the paper window is
    unknown; these figures are representative dataset diagnostics only.
    """
    folder = Path(output_dir)
    folder.mkdir(parents=True, exist_ok=True)
    groups = (
        ("A_ppg1_raw_filtered_spectrum.png", "PPG1: raw and filtered",
         (("Raw PPG1", raw.ppg1), ("Filtered PPG1", output.ppg1_filtered))),
        ("B_ppg2_raw_filtered_spectrum.png", "PPG2: raw and filtered",
         (("Raw PPG2", raw.ppg2), ("Filtered PPG2", output.ppg2_filtered))),
        ("C_filtered_ppg_average_spectrum.png", "Filtered PPGs and their arithmetic mean",
         (("Filtered PPG1", output.ppg1_filtered), ("Filtered PPG2", output.ppg2_filtered),
          ("Mean of filtered PPGs", output.ppg_avg))),
        ("D_filtered_acc_spectra.png", "Filtered accelerometer axes",
         (("Filtered ACC-X", output.acc_x_filtered), ("Filtered ACC-Y", output.acc_y_filtered),
          ("Filtered ACC-Z", output.acc_z_filtered))),
    )
    paths = []
    for filename, title, channels in groups:
        figure = Figure(figsize=(8, 5), layout="constrained")
        FigureCanvasAgg(figure)
        axes = figure.subplots()
        for label, signal in channels:
            frequencies = np.fft.rfftfreq(signal.size, d=1 / output.fs)
            power = (np.abs(np.fft.rfft(signal)) / signal.size) ** 2
            axes.semilogy(frequencies, power, label=label, linewidth=1.5)
        axes.axvspan(output.low_hz, output.high_hz, color="#22a884", alpha=.12,
                     label=f"Requested band {output.low_hz}–{output.high_hz} Hz")
        axes.set(xlim=(0, 8), xlabel="Frequency (Hz)", ylabel="FFT coefficient power |rFFT|²/L² (a.u.)")
        figure.suptitle("Replication diagnostic — representative dataset window", fontsize=11)
        axes.set_title(f"{title}\n{raw.record_id}, window {raw.index}, samples [{raw.start_sample}:{raw.end_sample}]",
                       fontsize=10)
        axes.grid(True, which="major", alpha=.25)
        axes.legend(fontsize=8, loc="upper right")
        path = folder / filename
        figure.savefig(path, dpi=160)
        paths.append(path)
    return paths
