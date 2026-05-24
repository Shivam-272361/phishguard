from flask import request, jsonify
from services.ml_integration_service import MLIntegrationService
from models.db_models import ScanModel
from flask_jwt_extended import get_jwt_identity
from middleware.auth_middleware import subscription_required
from utils.validators import UrlScanSchema
from marshmallow import ValidationError

@subscription_required
def check_url():
    # 1. Request Validation
    schema = UrlScanSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400

    url = data.get('url')
    user_id = get_jwt_identity()
    
    result = MLIntegrationService.predict_url(url)
    
    # Log scan to MongoDB
    ScanModel.log_scan(user_id, 'url', url, result)
        
    return jsonify({"success": True, "result": result})

def check_email():
    data = request.get_json()
    content = data.get('content')
    if not content:
        return jsonify({"success": False, "error": "Email content is required"}), 400
    
    result = MLIntegrationService.predict_email(content)
    return jsonify({"success": True, "result": result})

def check_sms():
    data = request.get_json()
    content = data.get('content')
    if not content:
        return jsonify({"success": False, "error": "SMS content is required"}), 400
    
    result = MLIntegrationService.predict_sms(content)
    return jsonify({"success": True, "result": result})
