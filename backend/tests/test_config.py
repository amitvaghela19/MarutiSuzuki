from backend.config.loader import load_config


def test_load_config():
    cfg = load_config()
    assert len(cfg.suppliers) >= 4
    assert len(cfg.parts) >= 3
    assert cfg.mcdm.criteria
