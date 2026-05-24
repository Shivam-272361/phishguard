"""
Phishing Detection API - Example Client
========================================
Demonstrates how to call the Flask REST API for phishing URL detection.

Usage:
    python request_example.py --url "https://www.google.com"
    python request_example.py --batch
    python request_example.py --features

Author: AI Assistant
Date: 2026-05-09
"""

import sys
import json
import argparse

import requests

DEFAULT_BASE_URL = "http://127.0.0.1:5000"
BASE_URL = DEFAULT_BASE_URL


def health_check():
    """Call the /health endpoint."""
    resp = requests.get(f"{BASE_URL}/health")
    print("\n=== /health ===")
    print(json.dumps(resp.json(), indent=2))


def get_info():
    """Call the /info endpoint."""
    resp = requests.get(f"{BASE_URL}/info")
    print("\n=== /info ===")
    data = resp.json()
    print(json.dumps(data, indent=2))


def predict_single():
    """Call /predict with a single pre-scaled feature vector."""
    payload = {
        "features": {
            "URLLength": 0.0103,
            "DomainLength": 0.7136,
            "IsDomainIP": -0.0521,
            "URLSimilarityIndex": 0.7444,
            "CharContinuationRate": -1.7048,
            "TLDLegitimateProb": -0.9215,
            "URLCharProb": 0.5071,
            "TLDLength": -1.2747,
            "NoOfSubDomain": 1.3898,
            "HasObfuscation": -0.0454,
            "NoOfObfuscatedChar": -0.0133,
            "ObfuscationRatio": -0.0363,
            "NoOfLettersInURL": 0.0196,
            "LetterRatioInURL": 0.4465,
            "NoOfDegitsInURL": -0.1582,
            "DegitRatioInURL": -0.4036,
            "NoOfEqualsInURL": -0.0666,
            "NoOfQMarkInURL": -0.1519,
            "NoOfAmpersandInURL": -0.0300,
            "NoOfOtherSpecialCharsInURL": 0.1870,
            "SpacialCharRatioInURL": 0.7005,
            "IsHTTPS": 0.5270,
            "LineOfCode": 0.7375,
            "LargestLineLength": -0.0218,
            "HasTitle": 0.4014,
            "DomainTitleMatchScore": -1.0092,
            "URLTitleMatchScore": -1.0508,
            "HasFavicon": 1.3282,
            "Robots": -0.6028,
            "IsResponsive": 0.7754,
            "NoOfURLRedirect": -0.3924,
            "NoOfSelfRedirect": -0.2044,
            "HasDescription": 1.1277,
            "NoOfPopup": -0.0573,
            "NoOfiFrame": -0.1021,
            "HasExternalFormSubmit": -0.2145,
            "HasSocialNet": 1.0910,
            "HasSubmitButton": 1.1890,
            "HasHiddenFields": 1.2833,
            "HasPasswordField": -0.3375,
            "Bank": -0.3816,
            "Pay": 1.7942,
            "Crypto": -0.1550,
            "HasCopyrightInfo": -0.9739,
            "NoOfImage": -0.1521,
            "NoOfCSS": -0.0579,
            "NoOfJS": -0.1130,
            "NoOfSelfRef": -0.3513,
            "NoOfEmptyRef": -0.1348,
            "NoOfExternalRef": -0.0762,
            "NoOfDotsInURL": 0.8051,
            "NoOfSpecialCharsInURL": 0.1130,
            "HasAtSymbol": -0.0802,
            "HasDoubleSlash": 0.0,
            "HasWWW": 0.5783,
            "HasSuspiciousTLD": -0.2003,
            "NoOfDotsInDomain": 1.3898,
            "HasHyphenInDomain": 2.1618,
            "TLD_FreqEnc": -0.9301
        }
    }
    resp = requests.post(f"{BASE_URL}/predict", json=payload)
    print("\n=== /predict (single) ===")
    print(json.dumps(resp.json(), indent=2))


def predict_batch():
    """Call /predict_batch with two samples."""
    payload = {
        "features": [
            {
                "URLLength": 0.0103,
                "DomainLength": 0.7136,
                "IsDomainIP": -0.0521,
                "URLSimilarityIndex": 0.7444,
                "CharContinuationRate": -1.7048,
                "TLDLegitimateProb": -0.9215,
                "URLCharProb": 0.5071,
                "TLDLength": -1.2747,
                "NoOfSubDomain": 1.3898,
                "HasObfuscation": -0.0454,
                "NoOfObfuscatedChar": -0.0133,
                "ObfuscationRatio": -0.0363,
                "NoOfLettersInURL": 0.0196,
                "LetterRatioInURL": 0.4465,
                "NoOfDegitsInURL": -0.1582,
                "DegitRatioInURL": -0.4036,
                "NoOfEqualsInURL": -0.0666,
                "NoOfQMarkInURL": -0.1519,
                "NoOfAmpersandInURL": -0.0300,
                "NoOfOtherSpecialCharsInURL": 0.1870,
                "SpacialCharRatioInURL": 0.7005,
                "IsHTTPS": 0.5270,
                "LineOfCode": 0.7375,
                "LargestLineLength": -0.0218,
                "HasTitle": 0.4014,
                "DomainTitleMatchScore": -1.0092,
                "URLTitleMatchScore": -1.0508,
                "HasFavicon": 1.3282,
                "Robots": -0.6028,
                "IsResponsive": 0.7754,
                "NoOfURLRedirect": -0.3924,
                "NoOfSelfRedirect": -0.2044,
                "HasDescription": 1.1277,
                "NoOfPopup": -0.0573,
                "NoOfiFrame": -0.1021,
                "HasExternalFormSubmit": -0.2145,
                "HasSocialNet": 1.0910,
                "HasSubmitButton": 1.1890,
                "HasHiddenFields": 1.2833,
                "HasPasswordField": -0.3375,
                "Bank": -0.3816,
                "Pay": 1.7942,
                "Crypto": -0.1550,
                "HasCopyrightInfo": -0.9739,
                "NoOfImage": -0.1521,
                "NoOfCSS": -0.0579,
                "NoOfJS": -0.1130,
                "NoOfSelfRef": -0.3513,
                "NoOfEmptyRef": -0.1348,
                "NoOfExternalRef": -0.0762,
                "NoOfDotsInURL": 0.8051,
                "NoOfSpecialCharsInURL": 0.1130,
                "HasAtSymbol": -0.0802,
                "HasDoubleSlash": 0.0,
                "HasWWW": 0.5783,
                "HasSuspiciousTLD": -0.2003,
                "NoOfDotsInDomain": 1.3898,
                "HasHyphenInDomain": 2.1618,
                "TLD_FreqEnc": -0.9301
            },
            {
                "URLLength": 0.8575,
                "DomainLength": 1.1507,
                "IsDomainIP": -0.0521,
                "URLSimilarityIndex": -1.8098,
                "CharContinuationRate": -0.4409,
                "TLDLegitimateProb": 1.0431,
                "URLCharProb": -0.2256,
                "TLDLength": 0.3927,
                "NoOfSubDomain": -0.2742,
                "HasObfuscation": -0.0454,
                "NoOfObfuscatedChar": -0.0133,
                "ObfuscationRatio": -0.0363,
                "NoOfLettersInURL": 1.1197,
                "LetterRatioInURL": 1.8413,
                "NoOfDegitsInURL": 0.1783,
                "DegitRatioInURL": 0.4004,
                "NoOfEqualsInURL": -0.0666,
                "NoOfQMarkInURL": -0.1519,
                "NoOfAmpersandInURL": -0.0300,
                "NoOfOtherSpecialCharsInURL": 1.0375,
                "SpacialCharRatioInURL": 0.7005,
                "IsHTTPS": 0.5270,
                "LineOfCode": -0.3152,
                "LargestLineLength": -0.0830,
                "HasTitle": 0.4014,
                "DomainTitleMatchScore": -1.0092,
                "URLTitleMatchScore": -1.0508,
                "HasFavicon": -0.7529,
                "Robots": 1.6588,
                "IsResponsive": 0.7754,
                "NoOfURLRedirect": -0.3924,
                "NoOfSelfRedirect": -0.2044,
                "HasDescription": 1.1277,
                "NoOfPopup": -0.0573,
                "NoOfiFrame": -0.2757,
                "HasExternalFormSubmit": -0.2145,
                "HasSocialNet": -0.9166,
                "HasSubmitButton": -0.8410,
                "HasHiddenFields": -0.7792,
                "HasPasswordField": -0.3375,
                "Bank": -0.3816,
                "Pay": -0.5573,
                "Crypto": -0.1550,
                "HasCopyrightInfo": -0.9739,
                "NoOfImage": -0.3284,
                "NoOfCSS": -0.0579,
                "NoOfJS": -0.4716,
                "NoOfSelfRef": -0.3683,
                "NoOfEmptyRef": -0.1348,
                "NoOfExternalRef": -0.2997,
                "NoOfDotsInURL": -0.2787,
                "NoOfSpecialCharsInURL": 0.3801,
                "HasAtSymbol": -0.0802,
                "HasDoubleSlash": 0.0,
                "HasWWW": -1.7291,
                "HasSuspiciousTLD": -0.2003,
                "NoOfDotsInDomain": -0.2742,
                "HasHyphenInDomain": -0.4626,
                "TLD_FreqEnc": 1.0428
            }
        ]
    }
    resp = requests.post(f"{BASE_URL}/predict_batch", json=payload)
    print("\n=== /predict_batch (2 samples) ===")
    print(json.dumps(resp.json(), indent=2))


def predict_url(url: str):
    """Call /predict_url with a raw URL string."""
    resp = requests.post(f"{BASE_URL}/predict_url", json={"url": url})
    print(f"\n=== /predict_url ({url}) ===")
    print(json.dumps(resp.json(), indent=2))


def _set_base_url(url: str):
    global BASE_URL
    BASE_URL = url


def main():
    parser = argparse.ArgumentParser(description="Phishing Detection API Client")
    parser.add_argument("--url", type=str, default="", help="URL to test with /predict_url")
    parser.add_argument("--features", action="store_true", help="Test /predict with pre-scaled features")
    parser.add_argument("--batch", action="store_true", help="Test /predict_batch")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--base-url", type=str, default=BASE_URL, help="API base URL")
    args = parser.parse_args()

    base_url = args.base_url

    try:
        _set_base_url(base_url)
        health_check()
        get_info()

        if args.all or args.features:
            predict_single()

        if args.all or args.batch:
            predict_batch()

        if args.all or args.url:
            predict_url(args.url or "https://www.google.com")

    except requests.exceptions.ConnectionError:
        print(f"\n[ERROR] Could not connect to API at {base_url}")
        print("Make sure the API server is running: python app.py")
        sys.exit(1)


if __name__ == "__main__":
    main()
