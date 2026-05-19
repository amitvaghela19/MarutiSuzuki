import numpy as np


def topsis_rank(
    matrix: np.ndarray,
    weights: np.ndarray,
    directions: list[str],
) -> tuple[np.ndarray, np.ndarray]:
    """Returns closeness scores (higher better) and ranks (1=best)."""
    if matrix.size == 0:
        return np.array([]), np.array([])
    norm = matrix / np.sqrt((matrix**2).sum(axis=0) + 1e-12)
    weighted = norm * weights
    ideal = np.zeros(weighted.shape[1])
    nadir = np.zeros(weighted.shape[1])
    for j, d in enumerate(directions):
        if d == "max":
            ideal[j] = weighted[:, j].max()
            nadir[j] = weighted[:, j].min()
        else:
            ideal[j] = weighted[:, j].min()
            nadir[j] = weighted[:, j].max()
    d_pos = np.sqrt(((weighted - ideal) ** 2).sum(axis=1))
    d_neg = np.sqrt(((weighted - nadir) ** 2).sum(axis=1))
    closeness = d_neg / (d_pos + d_neg + 1e-12)
    order = np.argsort(-closeness)
    ranks = np.empty_like(order)
    ranks[order] = np.arange(1, len(order) + 1)
    return closeness, ranks
