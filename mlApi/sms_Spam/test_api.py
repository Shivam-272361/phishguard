

import json
import sys

import requests

BASE_URL = "http://127.0.0.1:5000"


def print_header(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_response(response):
    print(f"Status: {response.status_code}")
    try:
        body = response.json()
        print(json.dumps(body, indent=2, ensure_ascii=False))
    except Exception:
        print(response.text)


def test_health():
    print_header("TEST: GET /health")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        print_response(resp)
        return resp.status_code == 200
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Could not connect to {BASE_URL}")
        print("[HINT] Make sure the server is running: python run_server.py")
        return False


def test_info():
    print_header("TEST: GET /")
    resp = requests.get(f"{BASE_URL}/", timeout=5)
    print_response(resp)
    return resp.status_code == 200


def test_predict_ham():
    print_header("TEST: POST /predict (HAM message)")
    payload = {"message": "Hey, are we still meeting for lunch tomorrow at 1pm?"}
    resp = requests.post(
        f"{BASE_URL}/predict",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    print_response(resp)
    return resp.status_code == 200 and resp.json().get("prediction", {}).get("label") == "ham"


def test_predict_spam():
    print_header("TEST: POST /predict (SPAM message)")
    payload = {"message": "Congratulations! You've won a $1000 gift card. Call now to claim your prize!"}
    resp = requests.post(
        f"{BASE_URL}/predict",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    print_response(resp)
    return resp.status_code == 200 and resp.json().get("prediction", {}).get("label") == "spam"


def test_predict_empty():
    print_header("TEST: POST /predict (empty message - expect error)")
    payload = {"message": ""}
    resp = requests.post(
        f"{BASE_URL}/predict",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    print_response(resp)
    return resp.status_code == 400


def test_predict_missing_field():
    print_header("TEST: POST /predict (missing field - expect error)")
    payload = {"text": "This is wrong field name"}
    resp = requests.post(
        f"{BASE_URL}/predict",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    print_response(resp)
    return resp.status_code == 400


def test_predict_batch():
    print_header("TEST: POST /predict/batch")
    payload = {
        "messages": [
            "Hey, are we still meeting for lunch tomorrow at 1pm?",
            "Thanks for the ride home last night! Really appreciate it.",
            "Congratulations! You've won a $1000 gift card. Call now to claim your prize!",
            "URGENT: You have won a free iPhone. Click here to claim within 24 hours.",
            "Call me back when you get a chance, it's urgent but not an emergency."
        ]
    }
    resp = requests.post(
        f"{BASE_URL}/predict/batch",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    print_response(resp)
    data = resp.json()
    return resp.status_code == 200 and data.get("summary", {}).get("total") == 5


def main():
    print("SMS Spam Detection API - Test Client")
    print(f"Target: {BASE_URL}")

    # Check server connectivity first
    if not test_health():
        sys.exit(1)

    results = []

    results.append(("GET / (info)", test_info()))
    results.append(("POST /predict (ham)", test_predict_ham()))
    results.append(("POST /predict (spam)", test_predict_spam()))
    results.append(("POST /predict (empty)", test_predict_empty()))
    results.append(("POST /predict (missing field)", test_predict_missing_field()))
    results.append(("POST /predict/batch", test_predict_batch()))

    print_header("TEST SUMMARY")
    passed = 0
    failed = 0
    for name, ok in results:
        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1
        print(f"  [{status}] {name}")

    print(f"\nTotal: {passed + failed} | Passed: {passed} | Failed: {failed}")

    if failed == 0:
        print("\n[SUCCESS] All tests passed!")
    else:
        print(f"\n[WARNING] {failed} test(s) failed.")
        sys.exit(1)


if __name__ == '__main__':
    main()
