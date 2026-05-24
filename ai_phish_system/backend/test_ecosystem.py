import requests
import json
import time

BASE_URL = "http://localhost:5005/api"
TOKEN = None

def test_auth():
    global TOKEN
    print("\n--- Testing Authentication ---")
    # Signup
    signup_payload = {
        "email": "testuser@phishguard.ai",
        "password": "SecurePassword123",
        "name": "QA Tester"
    }
    r = requests.post(f"{BASE_URL}/auth/signup", json=signup_payload)
    print(f"Signup: {r.status_code} - {r.json().get('message', r.json().get('error'))}")
    
    # Login (Assuming already verified for test purposes)
    login_payload = {
        "email": "testuser@phishguard.ai",
        "password": "SecurePassword123"
    }
    r = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    if r.status_code == 200:
        TOKEN = r.json().get('token')
        print("Login: SUCCESS")
    else:
        print(f"Login: FAILED - {r.json().get('error')}")

def test_url_scanning():
    print("\n--- Testing URL Scanning ---")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    urls = [
        {"url": "http://paypal-security-update.com", "expected": "Phishing"},
        {"url": "https://google.com", "expected": "Safe"}
    ]
    
    for item in urls:
        r = requests.post(f"{BASE_URL}/scan/url", json={"url": item['url']}, headers=headers)
        res = r.json()
        status = "HIT" if res.get('result', {}).get('is_phishing') else "MISS"
        print(f"URL: {item['url']} | Expected: {item['expected']} | Result: {status} | Score: {res.get('result', {}).get('score')}%")

def test_sms_scanning():
    print("\n--- Testing SMS Scanning ---")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    texts = [
        {"text": "URGENT: Your account is locked. Click here: http://bit.ly/fake", "expected": "Phishing"},
        {"text": "Hey, are we still meeting for lunch at 1pm?", "expected": "Safe"}
    ]
    
    for item in texts:
        r = requests.post(f"{BASE_URL}/scan/sms", json={"text": item['text']}, headers=headers)
        res = r.json()
        status = "Phishing" if res.get('is_phishing') else "Safe"
        print(f"SMS: {item['text'][:30]}... | Result: {status}")

def test_subscription_validation():
    print("\n--- Testing Subscription Gates ---")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    r = requests.get(f"{BASE_URL}/subscription/status", headers=headers)
    print(f"Subscription Status: {r.json().get('plan')} ({r.json().get('status')})")

if __name__ == "__main__":
    try:
        test_auth()
        if TOKEN:
            test_url_scanning()
            test_sms_scanning()
            test_subscription_validation()
    except Exception as e:
        print(f"Test Execution Error: {e}")
