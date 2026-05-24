import requests
import os

class MLIntegrationService:
    # Reusing existing ML API ports as designed in previous steps
    URL_API = os.getenv('URL_ML_URL', 'http://localhost:5001')
    SMS_EMAIL_API = os.getenv('SMS_ML_URL', 'http://localhost:5002')

    @classmethod
    def predict_url(cls, url):
        try:
            # Reusing the mature URL prediction endpoint
            response = requests.post(f"{cls.URL_API}/predict", json={"url": url}, timeout=5)
            return response.json()
        except Exception as e:
            return {"error": f"URL ML API connection failed: {str(e)}", "risk_score": 50}

    @classmethod
    def predict_email(cls, text):
        try:
            # Reusing the SMS/Content prediction endpoint for email text
            response = requests.post(f"{cls.SMS_EMAIL_API}/predict", json={"message": text}, timeout=5)
            data = response.json()
            # Combine with local heuristic logic if necessary (Architectural Placeholder)
            return data
        except Exception as e:
            return {"error": f"Content ML API connection failed: {str(e)}", "risk_score": 50}

    @classmethod
    def predict_sms(cls, text):
        try:
            response = requests.post(f"{cls.SMS_EMAIL_API}/predict", json={"message": text}, timeout=5)
            return response.json()
        except Exception as e:
            return {"error": f"SMS ML API connection failed: {str(e)}", "risk_score": 50}
