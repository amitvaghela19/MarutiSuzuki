from typing import Any

from backend.config.loader import _load_yaml
from backend.settings import settings
from backend.utils.strategic import normalize_bullet_list, normalize_swot_pestle_block


def load_supplier_strategic_raw() -> dict:
    return _load_yaml(settings.config_dir / "supplier_strategic.yaml")


def normalize_supplier_strategic_payload(raw: dict[str, Any]) -> dict[str, Any]:
    suppliers_out = []
    for s in raw.get("suppliers") or []:
        if not isinstance(s, dict):
            continue
        suppliers_out.append(
            {
                "id": s.get("id"),
                "name": s.get("name"),
                "country": s.get("country"),
                "swot": {
                    k: normalize_bullet_list(v) for k, v in (s.get("swot") or {}).items()
                },
                "pestle": normalize_swot_pestle_block(s.get("pestle")),
            }
        )
    return {
        "disclaimer": raw.get("disclaimer", ""),
        "suppliers": suppliers_out,
        "total": len(suppliers_out),
    }
