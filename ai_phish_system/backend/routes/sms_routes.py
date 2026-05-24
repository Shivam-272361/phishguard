from flask import Blueprint, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from services.ml_integration_service import MLIntegrationService
from models.db_models import ScanModel
import os

sms_bp = Blueprint('sms', __name__)

@sms_bp.route('/webhook/twilio', methods=['POST'])
def twilio_webhook():
    from_number = request.form.get('From')
    message_body = request.form.get('Body')
    
    if not message_body:
        return str(MessagingResponse()), 200

    ml_service = MLIntegrationService()
    from services.email_monitor_service import EmailAnalyzer
    
    # Advanced analysis covering text + embedded URLs
    analysis = EmailAnalyzer.analyze_sms_content(from_number, message_body, ml_service)

    ScanModel.log_scan("SYSTEM_SMS_MONITOR", 'sms_monitor', from_number, analysis)

    resp = MessagingResponse()
    if analysis['is_phishing']:
        print(f"SMS PHISHING ALERT: From {from_number} - Score: {analysis['score']}")
    
    return str(resp)
