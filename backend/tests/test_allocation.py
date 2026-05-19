from backend.analytics.allocation import compute_part_allocation
from backend.config.loader import load_config
from backend.config.models import PartConfig


def _part(**kwargs) -> PartConfig:
    defaults = {
        "id": "PART-TEST",
        "name": "Test part",
        "category": "test",
        "criticality": 3,
        "main_commodity": "metals",
        "supplier_ids": ["SUP-A", "SUP-B", "SUP-C"],
        "primary_supplier_id": "SUP-A",
    }
    defaults.update(kwargs)
    return PartConfig(**defaults)


def test_single_source_when_low_risk():
    cfg = load_config()
    ranks = {"SUP-A": 1, "SUP-B": 2, "SUP-C": 3}
    risks = {"SUP-A": 45.0, "SUP-B": 50.0, "SUP-C": 55.0}
    alloc, drivers, mode = compute_part_allocation(
        cfg, _part(), sorted(ranks.items(), key=lambda x: x[1]), risks, max_stockout=0.1
    )
    assert mode == "single_source"
    assert alloc == {"SUP-A": 1.0}


def test_not_fixed_sixty_forty_on_stockout():
    cfg = load_config()
    ranks = {"SUP-A": 1, "SUP-B": 2}
    risks = {"SUP-A": 55.0, "SUP-B": 48.0}
    alloc, _, mode = compute_part_allocation(
        cfg,
        _part(criticality=5),
        sorted(ranks.items(), key=lambda x: x[1]),
        risks,
        max_stockout=0.45,
    )
    assert mode in ("dual_source", "multi_source")
    assert abs(alloc["SUP-A"] - 0.6) > 0.05 or abs(alloc["SUP-B"] - 0.4) > 0.05


def test_emergency_shift_not_eighty_twenty():
    cfg = load_config()
    ranks = {"SUP-A": 1, "SUP-B": 2}
    risks = {"SUP-A": 90.0, "SUP-B": 60.0}
    alloc, _, mode = compute_part_allocation(
        cfg,
        _part(criticality=5),
        sorted(ranks.items(), key=lambda x: x[1]),
        risks,
        max_stockout=0.2,
    )
    assert mode == "emergency_shift"
    assert alloc["SUP-A"] < 0.8
