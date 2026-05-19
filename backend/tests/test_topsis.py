import numpy as np

from backend.analytics.mcdm.topsis import topsis_rank


def test_topsis_ranks_best_cost_lowest():
    matrix = np.array([[1.0, 10.0], [1.5, 8.0]])
    weights = np.array([0.5, 0.5])
    closeness, ranks = topsis_rank(matrix, weights, ["min", "min"])
    assert ranks[0] == 1
    assert closeness[0] > closeness[1]


def test_topsis_single_alternative():
    matrix = np.array([[1.0, 2.0]])
    weights = np.array([0.5, 0.5])
    closeness, ranks = topsis_rank(matrix, weights, ["min", "min"])
    assert len(closeness) == 1
    assert ranks[0] == 1
