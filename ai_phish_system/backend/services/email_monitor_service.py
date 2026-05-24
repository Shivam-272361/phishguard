import re
from bs4 import BeautifulSoup
import requests
import os

class EmailAnalyzer:
    @staticmethod
    def extract_urls(text):
        # Robust URL extraction regex
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return list(set(re.findall(url_pattern, text)))

    @staticmethod
    def clean_html(html_content):
        if not html_content:
            return ""
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text(separator=' ')

    @staticmethod
    def analyze_sms_content(sender, body, ml_service):
        # 1. Text Analysis using SMS Model
        prediction = ml_service.predict_sms(body)
        
        # 2. Extract URLs
        urls = EmailAnalyzer.extract_urls(body)
        url_results = []
        max_url_score = 0
        
        for url in urls:
            url_pred = ml_service.predict_url(url)
            url_results.append({
                "url": url,
                "score": url_pred.get('score', 0)
            })
            max_url_score = max(max_url_score, url_pred.get('score', 0))

        # 3. Decision Fusion
        is_phishing = prediction.get('label') == 'spam' or max_url_score > 75
        
        return {
            "sender": sender,
            "content": body,
            "is_phishing": is_phishing,
            "score": max(prediction.get('score', 0), max_url_score),
            "urls_detected": len(urls)
        }

class PhishingCoordinator:
    @staticmethod
    def analyze_email_full(sender, subject, body, ml_service):
        # 1. Analyze Email Text via Port 5002 ML
        email_prediction = ml_service.predict_sms(body) # Reusing the SMS/Email classifier
        
        # 2. Extract and Analyze URLs via Port 5001 ML
        urls = EmailAnalyzer.extract_urls(body)
        url_results = []
        max_url_score = 0
        
        for url in urls:
            url_pred = ml_service.predict_url(url)
            url_results.append({
                "url": url,
                "is_phishing": url_pred.get('is_phishing', False),
                "score": url_pred.get('score', 0)
            })
            max_url_score = max(max_url_score, url_pred.get('score', 0))

        # 3. Fusion Logic
        is_suspicious = email_prediction.get('label') == 'spam' or max_url_score > 70
        
        final_report = {
            "metadata": {
                "sender": sender,
                "subject": subject
            },
            "analysis": {
                "email_score": email_prediction.get('score', 0),
                "max_url_score": max_url_score,
                "urls_found": len(urls),
                "is_phishing": is_suspicious
            },
            "details": {
                "url_breakdown": url_results
            }
        }
        
        return final_report
