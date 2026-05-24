

import os
import re
import urllib.parse
from typing import Dict, Optional
import logging

logger = logging.getLogger("FeatureExtractor")

# Suspicious TLDs commonly abused in phishing
SUSPICIOUS_TLDS = {"tk", "ml", "ga", "cf", "top", "xyz", "bid", "work", "date", "party", "link", "download"}

# Load TLD frequency map if available
TLD_FREQ_MAP: Dict[str, int] = {}
TLD_FREQ_PATH = os.path.join("models", "tld_frequency_map.json")
if os.path.exists(TLD_FREQ_PATH):
    import json
    with open(TLD_FREQ_PATH, "r", encoding="utf-8") as f:
        TLD_FREQ_MAP = json.load(f)
    logger.info("Loaded TLD frequency map with %d entries.", len(TLD_FREQ_MAP))
else:
    logger.warning("TLD frequency map not found at %s; TLD_FreqEnc will default to 0.", TLD_FREQ_PATH)

# Estimated TLD legitimacy probabilities (derived from dataset statistics)
TLD_PROBS = {
    "com": 0.5229, "org": 0.0800, "net": 0.0800, "edu": 0.9900, "gov": 0.9900,
    "de": 0.0327, "uk": 0.0286, "us": 0.0500, "fr": 0.0400, "jp": 0.0600,
    "in": 0.0051, "co": 0.0300, "io": 0.0200, "info": 0.0100,
    "tk": 0.0001, "ml": 0.0001, "ga": 0.0001, "cf": 0.0001,
    "top": 0.0010, "xyz": 0.0010, "bid": 0.0010, "work": 0.0010,
    "date": 0.0010, "party": 0.0010, "link": 0.0010, "download": 0.0010,
}


def _estimate_url_similarity_index(url: str, parsed: urllib.parse.ParseResult) -> float:
    """
    Heuristic for URLSimilarityIndex (dataset range ~0-100).
    Higher = more similar to a legitimate baseline.
    """
    score = 100.0

    # Penalize HTTP
    if not url.startswith("https://"):
        score -= 15.0

    # Penalize IP addresses
    domain = parsed.netloc
    if re.match(r"^(\d{1,3}\.){3}\d{1,3}$", domain.replace("www.", "")):
        score -= 40.0

    # Penalize suspicious TLDs
    tld = domain.split(".")[-1] if "." in domain else ""
    if tld in SUSPICIOUS_TLDS:
        score -= 25.0

    # Penalize suspicious symbols
    if "@" in url or "//" in url.replace("://", ""):
        score -= 15.0

    # Penalize excessive length
    if len(url) > 100:
        score -= 10.0
    elif len(url) > 75:
        score -= 5.0

    # Penalize many dots
    if url.count(".") > 5:
        score -= 5.0

    # Penalize hyphens in domain
    if "-" in domain:
        score -= 5.0

    return max(0.0, min(100.0, score))


def _estimate_char_continuation_rate(url: str) -> float:
    """
    Heuristic for CharContinuationRate (dataset range 0-1).
    Measures how uniform the character classes are in the URL.
    Higher = more continuous / uniform character types.
    """
    if len(url) <= 1:
        return 1.0

    transitions = 0
    for i in range(1, len(url)):
        prev = url[i - 1]
        curr = url[i]
        prev_type = "alpha" if prev.isalpha() else ("digit" if prev.isdigit() else "other")
        curr_type = "alpha" if curr.isalpha() else ("digit" if curr.isdigit() else "other")
        if prev_type != curr_type:
            transitions += 1

    rate = 1.0 - (transitions / (len(url) - 1))
    return round(max(0.0, min(1.0, rate)), 6)


def _estimate_url_char_prob(url: str) -> float:
    """
    Heuristic for URLCharProb (dataset range ~0.02-0.09).
    Probability-like score based on character rarity / entropy.
    """
    if not url:
        return 0.06

    unique_chars = len(set(url))
    prob = unique_chars / len(url)
    # Scale to match dataset range roughly
    scaled = 0.02 + (prob * 0.07)
    return round(min(0.09, scaled), 6)


def _estimate_obfuscation_ratio(url: str) -> float:
    """Estimate obfuscation ratio from URL encoding patterns."""
    encoded = url.count("%")
    hex_pattern = len(re.findall(r"%[0-9a-fA-F]{2}", url))
    if len(url) == 0:
        return 0.0
    return round((encoded + hex_pattern * 2) / len(url), 6)


def _estimate_topic_features(url: str, html_text: str = "") -> Dict[str, float]:
    """Estimate Bank, Pay, Crypto indicators."""
    combined = (url + " " + html_text).lower()
    return {
        "Bank": float(int(any(w in combined for w in ["bank", "secure-bank", "onlinebank", "netbank"]))),
        "Pay": float(int(any(w in combined for w in ["paypal", "paynow", "payment-gateway"]))),
        "Crypto": float(int(any(w in combined for w in ["crypto-wallet", "bitcoin-reward", "eth-giveaway"]))),
    }


def fetch_page_features(url: str, timeout: int = 5) -> Dict[str, float]:
    """
    Fetch the webpage and extract HTML-based features.
    Falls back to empty dict on any error (timeout, SSL, blocked, etc.).
    """
    try:
        import requests
    except ImportError:
        logger.warning("requests not installed; skipping page fetch.")
        return {}

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        resp = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)
        html = resp.text
        html_lower = html.lower()
        lines = html.splitlines()
        line_of_code = len(lines)
        largest_line_length = max((len(ln) for ln in lines), default=0)

        # Title extraction
        title_match = re.search(r"<title[^>]*>([^<]*)</title>", html, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else ""
        has_title = int(bool(title))

        # Favicon
        has_favicon = int(bool(re.search(r'rel=["\']?(?:shortcut )?icon["\']?', html_lower)))

        # Image count
        no_of_image = len(re.findall(r"<img[\s/]", html_lower))

        # CSS count
        no_of_css = len(re.findall(r'rel=["\']?stylesheet["\']?', html_lower))

        # JS count
        no_of_js = len(re.findall(r"<script[\s/]", html_lower))

        # Links
        all_links = re.findall(r'href=["\']([^"\']+)["\']', html_lower)
        domain = urllib.parse.urlparse(url).netloc.lower().replace("www.", "")
        no_of_self_ref = sum(1 for link in all_links if domain in link or link.startswith("/"))
        no_of_external_ref = sum(1 for link in all_links if link.startswith("http") and domain not in link)
        no_of_empty_ref = sum(1 for link in all_links if link in ("", "#", "javascript:void(0)"))

        # iFrames
        no_of_iframe = len(re.findall(r"<iframe[\s/]", html_lower))

        # External form submit
        forms = re.findall(r'<form[^>]*action=["\']([^"\']+)["\'][^>]*>', html_lower)
        has_external_form_submit = int(any(
            act.startswith("http") and domain not in act for act in forms
        ))

        # Social networks
        social = ["facebook", "twitter", "instagram", "linkedin", "youtube", "github", "tiktok"]
        has_social_net = int(any(net in html_lower for net in social))

        # Submit button
        has_submit_button = int(bool(re.search(r'<(?:input|button)[^>]*type=["\']?submit["\']?', html_lower)))

        # Hidden fields
        has_hidden_fields = int(bool(re.search(r'<input[^>]*type=["\']?hidden["\']?', html_lower)))

        # Password field
        has_password_field = int(bool(re.search(r'<input[^>]*type=["\']?password["\']?', html_lower)))

        # Copyright
        has_copyright = int(any(k in html_lower for k in ["copyright", "&copy;", "&#169;"]))

        # Description meta
        has_description = int(bool(re.search(r'name=["\']?description["\']?', html_lower)))

        # Responsive
        is_responsive = int(bool(re.search(r'name=["\']?viewport["\']?', html_lower)))

        # Robots meta
        robots = int(bool(re.search(r'name=["\']?robots["\']?', html_lower)))

        # Popups (heuristic: common JS popup patterns)
        no_of_popup = (
            html_lower.count("alert(") + html_lower.count("confirm(") +
            html_lower.count("prompt(") + html_lower.count("window.open(")
        )

        # Redirects
        no_of_url_redirect = len(re.findall(r'http-equiv=["\']?refresh["\']?', html_lower))
        no_of_self_redirect = sum(1 for link in all_links if link.rstrip("/") == url.rstrip("/"))

        # Title match scores
        domain_clean = domain
        title_clean = title.lower()
        if domain_clean and title_clean:
            domain_score = sum(1 for c in domain_clean if c in title_clean) / len(domain_clean) * 100
            url_score = sum(1 for c in url.lower() if c in title_clean) / len(url) * 100
            domain_title_match = min(100.0, domain_score)
            url_title_match = min(100.0, url_score)
        else:
            domain_title_match = 0.0
            url_title_match = 0.0

        # Topic features from HTML
        topics = _estimate_topic_features(url, html)

        return {
            "LineOfCode": float(line_of_code),
            "LargestLineLength": float(largest_line_length),
            "HasTitle": float(has_title),
            "HasFavicon": float(has_favicon),
            "NoOfImage": float(no_of_image),
            "NoOfCSS": float(no_of_css),
            "NoOfJS": float(no_of_js),
            "NoOfSelfRef": float(no_of_self_ref),
            "NoOfEmptyRef": float(no_of_empty_ref),
            "NoOfExternalRef": float(no_of_external_ref),
            "NoOfiFrame": float(no_of_iframe),
            "HasExternalFormSubmit": float(has_external_form_submit),
            "HasSocialNet": float(has_social_net),
            "HasSubmitButton": float(has_submit_button),
            "HasHiddenFields": float(has_hidden_fields),
            "HasPasswordField": float(has_password_field),
            "HasCopyrightInfo": float(has_copyright),
            "HasDescription": float(has_description),
            "IsResponsive": float(is_responsive),
            "Robots": float(robots),
            "NoOfPopup": float(no_of_popup),
            "NoOfURLRedirect": float(no_of_url_redirect),
            "NoOfSelfRedirect": float(no_of_self_redirect),
            "DomainTitleMatchScore": float(domain_title_match),
            "URLTitleMatchScore": float(url_title_match),
            **topics,
        }

    except Exception as exc:
        logger.warning("Page fetch failed for %s: %s", url, exc)
        return {}


def extract_url_features(url: str) -> Dict[str, float]:
    """
    Extract handcrafted features from a raw URL string.
    Also computes heuristics for features normally derived from
    the full dataset or HTML parsing.
    """
    if not url:
        raise ValueError("URL cannot be empty.")

    url_orig = url.strip()
    url = url_orig.lower()
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
        url_orig = "http://" + url_orig

    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc
    path = parsed.path
    query = parsed.query

    # Remove port if present
    if ":" in domain:
        domain = domain.split(":")[0]

    # --- URL-level features ---
    url_length = len(url)
    num_dots_url = url.count(".")
    num_special_chars = len(re.findall(r"[^a-zA-Z0-9\.\/:]", url))
    has_at = int("@" in url)
    has_double_slash = int(url.count("//") > 1)
    has_https = int(url.startswith("https://"))

    # --- Domain-level features ---
    domain_length = len(domain)
    num_dots_domain = domain.count(".")
    has_hyphen_domain = int("-" in domain)
    has_www = int(domain.startswith("www."))

    # Check for IP address in domain
    is_domain_ip = int(bool(re.match(r"^(\d{1,3}\.){3}\d{1,3}$", domain)))

    # TLD extraction
    tld = ""
    if "." in domain:
        tld = domain.split(".")[-1]
    tld_length = len(tld)
    has_suspicious_tld = int(tld in SUSPICIOUS_TLDS)
    tld_freq_enc = float(TLD_FREQ_MAP.get(tld, 0.0))

    # Subdomain count
    domain_no_www = domain[4:] if domain.startswith("www.") else domain
    num_subdomains = max(0, domain_no_www.count("."))

    # --- Path / Query features ---
    num_equals = query.count("=")
    num_qmark = url.count("?")
    num_ampersand = url.count("&")

    # --- Derived ratios ---
    letter_ratio = sum(c.isalpha() for c in url) / len(url) if url else 0.0
    digit_ratio = sum(c.isdigit() for c in url) / len(url) if url else 0.0
    special_ratio = num_special_chars / len(url) if url else 0.0

    # --- Heuristic features ---
    url_similarity_index = _estimate_url_similarity_index(url, parsed)
    char_continuation_rate = _estimate_char_continuation_rate(url)
    tld_legitimate_prob = TLD_PROBS.get(tld, 0.01)
    url_char_prob = _estimate_url_char_prob(url)
    obfuscation_ratio = _estimate_obfuscation_ratio(url)
    no_of_obfuscated_char = int(obfuscation_ratio * len(url))

    # --- Topic heuristics ---
    topics = _estimate_topic_features(url)

    # Build feature dict (all float for JSON compat)
    features = {
        "URLLength": float(url_length),
        "DomainLength": float(domain_length),
        "IsDomainIP": float(is_domain_ip),
        "URLSimilarityIndex": float(url_similarity_index),
        "CharContinuationRate": float(char_continuation_rate),
        "TLDLegitimateProb": float(tld_legitimate_prob),
        "URLCharProb": float(url_char_prob),
        "TLDLength": float(tld_length),
        "NoOfSubDomain": float(num_subdomains),
        "HasObfuscation": float(int(obfuscation_ratio > 0)),
        "NoOfObfuscatedChar": float(no_of_obfuscated_char),
        "ObfuscationRatio": float(obfuscation_ratio),
        "NoOfLettersInURL": float(sum(c.isalpha() for c in url)),
        "LetterRatioInURL": float(letter_ratio),
        "NoOfDegitsInURL": float(sum(c.isdigit() for c in url)),
        "DegitRatioInURL": float(digit_ratio),
        "NoOfEqualsInURL": float(num_equals),
        "NoOfQMarkInURL": float(num_qmark),
        "NoOfAmpersandInURL": float(num_ampersand),
        "NoOfOtherSpecialCharsInURL": float(num_special_chars),
        "SpacialCharRatioInURL": float(special_ratio),
        "IsHTTPS": float(has_https),
        "NoOfDotsInURL": float(num_dots_url),
        "NoOfSpecialCharsInURL": float(num_special_chars),
        "HasAtSymbol": float(has_at),
        "HasDoubleSlash": float(has_double_slash),
        "HasWWW": float(has_www),
        "HasSuspiciousTLD": float(has_suspicious_tld),
        "NoOfDotsInDomain": float(num_dots_domain),
        "HasHyphenInDomain": float(has_hyphen_domain),
        "TLD_FreqEnc": float(tld_freq_enc),
        **topics,
    }

    return features


def extract_all_features(url: str, fetch_html: bool = False) -> Dict[str, float]:
    """
    Combine URL-based features with optional HTML-fetched features.
    This is the recommended entry-point for the API.
    """
    features = extract_url_features(url)

    if fetch_html:
        try:
            page_features = fetch_page_features(url, timeout=5)
            features.update(page_features)
            logger.info("Fetched %d HTML features for %s", len(page_features), url)
        except Exception as exc:
            logger.warning("HTML fetch failed for %s: %s", url, exc)

    return features
