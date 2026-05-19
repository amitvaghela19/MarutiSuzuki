COUNTRY_NAMES: dict[str, str] = {
    "IN": "India",
    "TH": "Thailand",
    "MY": "Malaysia",
    "JP": "Japan",
    "DE": "Germany",
    "KR": "South Korea",
    "US": "United States",
    "CN": "China",
    "GB": "United Kingdom",
}


def country_name(code: str | None) -> str:
    if not code:
        return "—"
    key = code.strip().upper()
    return COUNTRY_NAMES.get(key, code)
