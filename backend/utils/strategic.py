from typing import Any


def normalize_bullet(item: Any) -> dict[str, str | None]:
    if isinstance(item, str):
        return {"text": item, "source_url": None, "source_label": None}
    if isinstance(item, dict):
        url = item.get("source_url") or item.get("url")
        return {
            "text": str(item.get("text", "")),
            "source_url": str(url) if url else None,
            "source_label": item.get("source_label") or item.get("source_title") or None,
        }
    return {"text": str(item), "source_url": None, "source_label": None}


def normalize_bullet_list(items: Any) -> list[dict[str, str | None]]:
    if not items:
        return []
    if not isinstance(items, list):
        return []
    return [normalize_bullet(x) for x in items]


def normalize_swot_pestle_block(block: Any) -> dict[str, list[dict[str, str | None]]]:
    if not isinstance(block, dict):
        return {}
    return {key: normalize_bullet_list(val) for key, val in block.items()}


def normalize_strategic_payload(raw: dict[str, Any]) -> dict[str, Any]:
    maruti = raw.get("maruti_suzuki") or {}
    partners_out = []
    for p in raw.get("partners") or []:
        if not isinstance(p, dict):
            continue
        partners_out.append(
            {
                **p,
                "swot_summary": {
                    k: normalize_bullet_list(v)
                    for k, v in (p.get("swot_summary") or {}).items()
                },
                "pestle_highlights": {
                    k: normalize_bullet_list(v)
                    for k, v in (p.get("pestle_highlights") or {}).items()
                },
            }
        )
    return {
        "maruti_suzuki": {
            "swot": normalize_swot_pestle_block(maruti.get("swot")),
            "pestle": normalize_swot_pestle_block(maruti.get("pestle")),
        },
        "partners": partners_out,
        "sources_note": raw.get(
            "sources_note",
            "Each bullet links to a public reference used for this demo synthesis.",
        ),
    }
