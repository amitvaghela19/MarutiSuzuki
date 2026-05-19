import numpy as np


def derive_weights(pairwise: list[list[float]] | None, direct: list[float] | None) -> list[float]:
    if direct and sum(direct) > 0:
        s = sum(direct)
        return [w / s for w in direct]
    if not pairwise:
        return []
    m = np.array(pairwise, dtype=float)
    col_sums = m.sum(axis=0)
    norm = m / col_sums
    weights = norm.mean(axis=1)
    return (weights / weights.sum()).tolist()
