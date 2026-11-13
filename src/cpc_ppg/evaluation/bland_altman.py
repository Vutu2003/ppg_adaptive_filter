"""Estimate minus reference, sample SD primary and population SD sensitivity."""

import numpy as np

from .errors import EvaluationNumericalError
from .metrics import paired_values, finite_scalars
from .models import BlandAltmanResult


def bland_altman(estimate, reference, *, ddof=1):
    e, r = paired_values(estimate, reference)
    if type(ddof) is not int or ddof not in (0, 1) or e.size < 2:
        raise EvaluationNumericalError("Bland–Altman needs >=2 pairs, ddof 0 or 1")
    with np.errstate(over="ignore", invalid="ignore"):
        means, differences = e/2+r/2, e-r
        bias = np.mean(differences)
        sd = np.std(differences, ddof=ddof)
        lower, upper = bias-1.96*sd, bias+1.96*sd
    finite_scalars([bias, sd, lower, upper])
    if not np.isfinite(means).all() or not np.isfinite(differences).all():
        raise EvaluationNumericalError("Nonfinite Bland–Altman pairs")
    count = int(np.count_nonzero((differences >= lower) & (differences <= upper)))
    for a in (means, differences):
        a.setflags(write=False)
    return BlandAltmanResult(means, differences, float(bias), float(sd), float(lower), float(upper),
                            count, 100*count/e.size, ddof)
