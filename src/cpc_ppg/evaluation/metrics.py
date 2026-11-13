"""Exact paired errors; no NaN-aware reduction, calibration or alignment search."""

import numpy as np
from scipy.stats import pearsonr

from .errors import EvaluationAlignmentError, EvaluationNumericalError


def paired_values(estimate, reference):
    arrays = []
    for name, value in (("estimate", estimate), ("reference", reference)):
        a = np.asarray(value)
        if a.ndim != 1 or a.dtype.kind not in "iuf" or not a.size:
            raise EvaluationAlignmentError(f"{name}: expected nonempty 1-D real sequence")
        with np.errstate(over="ignore", invalid="ignore"):
            a = np.asarray(a, dtype=np.float64)
        if not np.isfinite(a).all():
            raise EvaluationNumericalError(f"{name}: nonfinite or float64 conversion overflow")
        arrays.append(a)
    if arrays[0].shape != arrays[1].shape:
        raise EvaluationAlignmentError("Estimate/reference lengths differ; no trimming or alignment search")
    return tuple(arrays)


def finite_scalars(values):
    if not all(np.isfinite(v) for v in values):
        raise EvaluationNumericalError("Nonfinite metric; no skipping/repair")


def average_absolute_error(estimate, reference):
    e, r = paired_values(estimate, reference)
    with np.errstate(over="ignore", invalid="ignore"):
        value = np.mean(np.abs(e-r))
    finite_scalars([value])
    return float(value)


def pearson_correlation(estimate, reference):
    e, r = paired_values(estimate, reference)
    if e.size < 2 or np.all(e == e[0]) or np.all(r == r[0]):
        raise EvaluationNumericalError("Pearson undefined for <2 samples or constant estimate/reference")
    value = float(pearsonr(e, r).statistic)
    finite_scalars([value])
    return value


def error_metrics(estimate, reference):
    e, r = paired_values(estimate, reference)
    if e.size < 2:
        raise EvaluationNumericalError("Sample SD requires at least two pairs")
    with np.errstate(over="ignore", invalid="ignore"):
        d = e-r
        absolute = np.abs(d)
        values = {"aae_bpm": np.mean(absolute), "bias_bpm": np.mean(d),
                  "rmse_bpm": np.sqrt(np.mean(d*d)), "error_sd_bpm": np.std(d, ddof=1),
                  "median_absolute_error_bpm": np.median(absolute),
                  "p95_absolute_error_bpm": np.percentile(absolute, 95, method="linear"),
                  "max_absolute_error_bpm": np.max(absolute)}
    finite_scalars(values.values())
    return {"n_windows": e.size, **{k: float(v) for k, v in values.items()}}


def aggregate_aae(pairs):
    checked = [paired_values(*pair) for pair in pairs]
    if not checked:
        raise EvaluationAlignmentError("No records to aggregate")
    per_record = [average_absolute_error(e, r) for e, r in checked]
    with np.errstate(over="ignore", invalid="ignore"):
        macro = float(np.mean(per_record))
    finite_scalars([macro])
    return {"macro_aae_bpm": macro,
            "micro_aae_bpm": average_absolute_error(np.concatenate([e for e, _ in checked]),
                                                    np.concatenate([r for _, r in checked]))}
