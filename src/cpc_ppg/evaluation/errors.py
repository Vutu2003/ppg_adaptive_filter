"""Evaluation failures never trigger exclusions or algorithm repairs."""


class EvaluationError(ValueError):
    pass


class EvaluationAlignmentError(EvaluationError):
    pass


class EvaluationNumericalError(EvaluationError):
    pass
