
from urllib.parse import urlparse
from typing import Any, Dict, List, Optional

TRUSTED_DOMAINS = frozenset({
    "google.com", "gmail.com", "googlemail.com", "github.com",
    "microsoft.com", "live.com", "office.com", "outlook.com",
    "youtube.com", "linkedin.com", "apple.com", "amazon.com",
    "pw.live",
})

# Benign path/query tokens — do not treat as phishing lures on trusted domains
BENIGN_PATH_KEYWORDS = frozenset({
    "study", "batch", "session", "login", "auth", "dashboard",
    "course", "class", "classes", "student", "learn", "video",
    "home", "profile", "settings", "account", "signup", "register",
})

TRUSTED_SCORE_CAP = 35
TRUSTED_ML_OVERRIDE = 92


def normalize_host(url: str) -> str:
    try:
        host = (urlparse(url).hostname or "").lower()
        return host.replace("www.", "")
    except Exception:
        return ""


def is_trusted_host(host: str) -> bool:
    if not host:
        return False
    for trusted in TRUSTED_DOMAINS:
        if host == trusted or host.endswith(f".{trusted}"):
            return True
    return False


def ui_verdict_from_score(score: int) -> str:
    if score >= 56:
        return "DANGEROUS"
    if score >= 50:
        return "CAUTION"
    return "SAFE"


def ui_message_for_verdict(verdict: str) -> str:
    return {
        "SAFE": "No significant phishing indicators detected.",
        "CAUTION": "Some suspicious patterns detected — proceed with care.",
        "DANGEROUS": "High-risk phishing indicators detected.",
    }.get(verdict, "Scan complete.")


def apply_trusted_cap(host: str, score: float, ml_score: Optional[float] = None) -> float:
    if not is_trusted_host(host):
        return score
    if ml_score is not None and ml_score >= TRUSTED_ML_OVERRIDE:
        return score
    return min(score, TRUSTED_SCORE_CAP)


def balance_final_score(
    heuristic: float,
    ml: Optional[float],
    whois: Optional[float],
    host: str,
    uses_https: bool = True,
) -> Dict[str, Any]:
    trust_reduction = 0.0
    if is_trusted_host(host):
        trust_reduction += 15.0
    if uses_https:
        trust_reduction += 5.0

    components: Dict[str, float] = {"heuristic": float(heuristic)}
    weights: Dict[str, float] = {"heuristic": 0.55}

    if ml is not None:
        components["ml"] = float(ml)
        weights["ml"] = 0.75
        weights["heuristic"] = 0.25
    if whois is not None:
        components["whois"] = float(whois)
        weights["whois"] = 0.50
        if "ml" in weights:
            weights["ml"] = 0.40
            weights["heuristic"] = 0.10

    total_w = sum(weights.values())
    weights = {k: v / total_w for k, v in weights.items()}

    raw = sum(components[k] * weights[k] for k in components)
    raw = max(0.0, raw - trust_reduction)
    capped = apply_trusted_cap(host, raw, ml)
    final = int(max(0, min(100, round(capped))))

    return {
        "raw_ml_score": ml,
        "heuristic_score": int(round(heuristic)),
        "trust_score": int(round(trust_reduction)),
        "final_normalized_score": final,
        "ui_verdict": ui_verdict_from_score(final),
        "components": {k: int(round(v)) for k, v in components.items()},
        "weights": weights,
        "trusted_host": is_trusted_host(host),
    }
