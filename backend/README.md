# PhishGuard Backend

Express API for SMS, email, and URL phishing detection.

## Run

```bash
npm install
npm run dev
```

The server runs on `http://localhost:5000` by default.

## Endpoints

- `POST /scan-sms` with `{ "text": "message text" }`
- `POST /scan-email` with `{ "content": "email text", "mode": "content" }`
- `POST /scan-email` with `{ "content": "sender@example.com", "mode": "address" }`
- `POST /scan-url` with `{ "url": "https://example.com" }`
- `POST /check_reputation` with `{ "url": "https://example.com" }` (ML + VirusTotal + optional Google Safe Browsing)
