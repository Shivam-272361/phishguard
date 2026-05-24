

import re
from urllib.parse import urlparse
from typing import Dict, List, Any

# Well-known legitimate domains (short whitelist for common false positives)
WELL_KNOWN_DOMAINS = {
    # Search & Google Services
    "google.com", "www.google.com", "mail.google.com", "drive.google.com", "cloud.google.com",
    "youtube.com", "www.youtube.com",
    
    # Social Media & Networking
    "facebook.com", "www.facebook.com",
    "twitter.com", "x.com", "www.twitter.com", "www.x.com",
    "instagram.com", "www.instagram.com",
    "linkedin.com", "www.linkedin.com",
    "reddit.com", "www.reddit.com",
    "tiktok.com", "www.tiktok.com",
    "whatsapp.com", "www.whatsapp.com", "web.whatsapp.com",
    
    # Developer & Tech Platforms
    "github.com", "www.github.com",
    "stackoverflow.com", "www.stackoverflow.com",
    "microsoft.com", "www.microsoft.com", "azure.com",
    "apple.com", "www.apple.com",
    "aws.amazon.com",
    
    # E-commerce & Payments
    "amazon.com", "www.amazon.com",
    "paypal.com", "www.paypal.com",
    "ebay.com", "www.ebay.com",
    
    # AI & Tools
    "openai.com", "www.openai.com", "chatgpt.com", "platform.openai.com",
    
    # Entertainment & Reference
    "netflix.com", "www.netflix.com",
    "spotify.com", "www.spotify.com",
    "wikipedia.org", "www.wikipedia.org",
    
    # Cloud Storage & Documents
    "dropbox.com", "www.dropbox.com",
    "adobe.com", "www.adobe.com", "documentcloud.adobe.com",
    
    # Corporate & Communication
    "slack.com", "www.slack.com",
    "zoom.us", "www.zoom.us",
    "salesforce.com", "www.salesforce.com",
    
    # Legacy Webmail
    "yahoo.com", "www.yahoo.com", "mail.yahoo.com",
    
    # Major Banking
    "chase.com", "www.chase.com",
}

# Suspicious TLDs commonly used for phishing
SUSPICIOUS_TLDS = {
    "tk", "ml", "ga", "cf", "gq", "top", "xyz", "club", "online",
    "site", "work", "bid", "win", "men", "date", "wang", "party",
    "racing", "stream", "trade", "review", "download", "science",
    "click", "link", "country", "kim", "cricket", "space", "cc",
    "zip", "mov", "quest", "rest", "support",
}

# Free hosting / suspicious platforms
SUSPICIOUS_HOSTS = {
    "firebaseapp.com", "web.app", "weeblysite.com", "weebly.com",
    "pantheonsite.io", "github.io", "herokuapp.com", "netlify.app",
    "vercel.app", "glitch.me", "repl.co", "pythonanywhere.com",
    "000webhostapp.com", "blogspot.com", "wixsite.com", "appspot.com",
}

# Sensitive keywords (high-risk only — benign edu/app paths excluded)
SENSITIVE_KEYWORDS = [
    "signin", "verify", "verification", "password", "credential",
    "wallet", "bank", "payment", "checkout", "billing",
    "authenticate", "confirm", "validate", "unlock", "restore",
    "recover", "reset",
]

# Never penalize these in path/query (common on legitimate sites)
BENIGN_PATH_KEYWORDS = {
    "study", "batch", "session", "login", "auth", "dashboard",
    "course", "class", "classes", "student", "learn", "video",
    "home", "profile", "settings", "account", "secure", "update", "alert",
}

# Common social-engineering lures used in phishing domains.
DOMAIN_LURE_KEYWORDS = [
    "parcel", "track", "tracking", "delivery", "courier", "shipment",
    "package", "alert", "notice", "support", "service", "security",
]

# Brand names commonly targeted by typosquatting
TARGET_BRANDS = [
    "paypal", "apple", "microsoft", "amazon", "google", "facebook",
    "netflix", "bank", "wells", "chase", "citi", "amex", "visa",
    "mastercard", "bitcoin", "crypto", "wallet", "blockchain",
]


def extract_domain_parts(url: str) -> Dict[str, str]:
    """Parse URL and extract domain components."""
    parsed = urlparse(url)
    netloc = parsed.netloc or parsed.path.split("/")[0]
    if ":" in netloc:
        netloc = netloc.split(":")[0]
    parts = netloc.split(".")
    if len(parts) >= 2:
        tld = parts[-1].lower()
        sld = parts[-2].lower()
        domain = f"{sld}.{tld}"
    else:
        tld = netloc.lower()
        sld = netloc.lower()
        domain = netloc.lower()
    return {
        "netloc": netloc.lower(),
        "domain": domain,
        "sld": sld,
        "tld": tld,
        "path": parsed.path.lower(),
        "query": parsed.query.lower(),
    }


def detect_typosquatting(domain: str) -> List[str]:
    """Detect common typosquatting patterns in a domain name."""
    indicators = []
    domain_clean = re.sub(r"^www\.", "", domain)
    sld = domain_clean.split(".")[0]

    # Digit-for-letter substitutions
    substitutions = {
        "0": "o", "1": "l", "3": "e", "4": "a", "5": "s",
        "6": "g", "7": "t", "8": "b", "9": "g",
    }
    normalized = sld
    for digit, letter in substitutions.items():
        normalized = normalized.replace(digit, letter)

    # Check if normalized version matches a target brand
    for brand in TARGET_BRANDS:
        if normalized == brand and sld != brand:
            indicators.append(f"typosquatting_{brand}")
            break
        # Also check for added prefix/suffix on brand
        if len(sld) > len(brand) and brand in sld:
            # e.g., "paypal-verify" contains "paypal"
            indicators.append(f"brand_impersonation_{brand}")
            break

    # Double characters that shouldn't be there
    if re.search(r"(.)\1{2,}", sld):
        indicators.append("repeated_chars")

    # Mixed scripts / homograph (basic check for non-ascii)
    if any(ord(c) > 127 for c in sld):
        indicators.append("non_ascii_domain")

    return indicators


def score_url_risk(url: str, features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute a rule-based phishing risk score for a URL.

    Returns dict with:
        - score (float): 0-100+ risk score
        - probability (float): 0.0-1.0 normalized phishing probability
        - classification (str): "Legitimate", "Suspicious", or "Phishing"
        - indicators (list): human-readable risk indicators
        - method (str): "rule_based"
    """
    score = 0.0
    indicators: List[str] = []
    parts = extract_domain_parts(url)
    domain = parts["domain"]
    sld = parts["sld"]
    tld = parts["tld"]
    url_lower = url.lower()

    # ===== WHITELIST OVERRIDE =====
    netloc_no_www = re.sub(r"^www\.", "", parts["netloc"])
    if netloc_no_www in WELL_KNOWN_DOMAINS or domain in WELL_KNOWN_DOMAINS:
        return {
            "score": 0.0,
            "probability": 0.0,
            "classification": "Legitimate",
            "indicators": ["well_known_domain"],
            "method": "rule_based",
        }

    # ===== CORE HEURISTICS =====

    # 1. IP address as domain (+40)
    if features.get("IsDomainIP", 0) == 1:
        score += 40
        indicators.append("ip_address_domain")

    # 2. Suspicious TLD (+30)
    if tld in SUSPICIOUS_TLDS:
        score += 30
        indicators.append(f"suspicious_tld_{tld}")

    # 3. Suspicious hosting platform (+25)
    if any(host in parts["netloc"] for host in SUSPICIOUS_HOSTS):
        score += 25
        indicators.append("suspicious_hosting")

    # 4. No HTTPS (+20)
    if features.get("IsHTTPS", 0) == 0:
        score += 20
        indicators.append("no_https")

    # 5. Hyphen in domain (+12)
    if features.get("HasHyphenInDomain", 0) == 1:
        score += 12
        indicators.append("hyphen_in_domain")

    # 6. At symbol in URL (+20)
    if features.get("HasAtSymbol", 0) == 1:
        score += 20
        indicators.append("at_symbol_in_url")

    # 7. Double slash after protocol (+15)
    if features.get("HasDoubleSlash", 0) == 1:
        score += 15
        indicators.append("double_slash")

    # 8. Excessive subdomains (+8 each beyond 2)
    subdomains = int(features.get("NoOfSubDomain", 0))
    if subdomains > 2:
        extra = subdomains - 2
        score += 8 * extra
        indicators.append(f"excessive_subdomains_{subdomains}")

    # 9. Very long URL — query strings on legit sites should not dominate score
    url_length = int(features.get("URLLength", 0))
    if url_length > 200:
        score += 5
        indicators.append("very_long_url")
    elif url_length > 120:
        score += 2
        indicators.append("very_long_url")

    # 10. High special char ratio (+8)
    special_ratio = float(features.get("SpacialCharRatioInURL", 0))
    if special_ratio > 0.15:
        score += 8
        indicators.append("high_special_char_ratio")

    # 11. Obfuscation (+15)
    if features.get("HasObfuscation", 0) == 1:
        score += 15
        indicators.append("url_obfuscation")

    # 12. Typosquatting (+20)
    typo_indicators = detect_typosquatting(domain)
    if typo_indicators:
        score += 20
        indicators.extend(typo_indicators)

    # 13. Sensitive keywords in path (+5 each, max 10) — skip benign app paths
    path_query = f"{parts['path']} {parts['query']}"
    sens_found = [
        kw for kw in SENSITIVE_KEYWORDS
        if kw in path_query and kw not in BENIGN_PATH_KEYWORDS
    ]
    sens_score = min(len(sens_found) * 5, 10)
    if sens_score:
        score += sens_score
        indicators.append(f"sensitive_keywords_{sens_found}")

    # 14. Free/gift/prize/crypto/airdrop keywords in domain (+14)
    bait_words = ["free", "gift", "prize", "win", "bonus", "reward",
                  "airdrop", "giveaway", "claim", "lucky", "selected"]
    bait_found = [w for w in bait_words if w in sld]
    if bait_found:
        score += 14
        indicators.append(f"bait_keywords_{bait_found}")

    # 15. Delivery/account-alert lures in domain (+18)
    lure_found = [w for w in DOMAIN_LURE_KEYWORDS if w in sld]
    if lure_found:
        score += min(len(lure_found) * 9, 18)
        indicators.append(f"domain_lure_keywords_{lure_found}")

    # 16. Very low TLD legitimacy probability from feature extractor (+12)
    if float(features.get("TLDLegitimateProb", 1)) <= 0.005:
        score += 12
        indicators.append("very_low_tld_legitimacy")

    # 17. Compound suspicious pattern bonus (+10)
    if (
        features.get("IsHTTPS", 0) == 0
        and features.get("HasHyphenInDomain", 0) == 1
        and (lure_found or bait_found or tld in SUSPICIOUS_TLDS)
    ):
        score += 10
        indicators.append("compound_domain_risk")

    # 18. Very short SLD — only flag unknown non-HTTPS brands (pw.live is legitimate)
    if (
        len(sld) < 3
        and domain not in WELL_KNOWN_DOMAINS
        and features.get("IsHTTPS", 0) == 0
    ):
        score += 5
        indicators.append("very_short_domain")

    # 19. Excessive dots in domain (+5)
    dots_in_domain = int(features.get("NoOfDotsInDomain", 0))
    if dots_in_domain > 2:
        score += 5
        indicators.append("many_dots_in_domain")

    # ===== CLASSIFICATION =====
    # Normalize probability (score tends to max around 120)
    probability = min(score / 80.0, 1.0)

    if score >= 50:
        classification = "Phishing"
    elif score >= 20:
        classification = "Suspicious"
    else:
        classification = "Legitimate"

    return {
        "score": round(score, 2),
        "probability": round(probability, 4),
        "classification": classification,
        "indicators": indicators,
        "method": "rule_based",
    }
