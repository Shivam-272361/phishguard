import requests

urls = [
    'https://google.com',
    'https://openai.com',
    'https://github.com',
    'http://free-crypto-airdrop.tk',
    'http://paypa1-verify.tk/login',
    'http://free-gift.xyz/claim',
    'https://www.paypal.com',
    'https://192.168.1.1/login',
    'https://bit.ly/abc123',
    'http://login-secure-bank-verify.tk/update',
]

print('='*70)
print('PHISHING URL DETECTION API - FINAL TEST RESULTS')
print('='*70)
for url in urls:
    resp = requests.post('http://127.0.0.1:5000/predict_url', json={'url': url})
    data = resp.json()
    pred = data['prediction']
    print(f'\nURL: {url}')
    print(f"  -> {pred['predicted_class']} (score={pred['risk_score']}, prob={pred['phishing_probability']})")
    print(f"  -> Indicators: {pred['risk_indicators']}")
    if 'ml_prediction' in data:
        ml = data['ml_prediction']
        print(f"  -> ML fallback: {ml['predicted_class']} (prob={ml['phishing_probability']})")
