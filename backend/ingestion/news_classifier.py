from backend.config.models import AppConfig


def classify_articles(articles: list[dict], cfg: AppConfig) -> list[dict]:
    classified = []
    for art in articles:
        text = f"{art.get('title', '')} {art.get('summary', '')}".lower()
        severity = 1
        risk_type = "general"
        country_code = None
        for rule in cfg.news_keywords.rules:
            if any(kw.lower() in text for kw in rule.keywords):
                severity = max(severity, rule.severity)
                risk_type = rule.risk_type
                if rule.country_hints:
                    country_code = rule.country_hints[0]
        classified.append(
            {
                **art,
                "severity": severity,
                "risk_type": risk_type,
                "country_code": country_code,
            }
        )
    return classified
