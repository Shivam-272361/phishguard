from flask import Blueprint, jsonify
from models.db_models import UserModel, ScanModel, SubscriptionModel
from flask_jwt_extended import jwt_required, get_jwt_identity

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/stats', methods=['GET'])
# @jwt_required() # Add admin check logic here in production
def get_stats():
    total_scans = 1250 # Placeholder for aggregation count
    phishing_detected = 342
    active_users = 450
    premium_users = 120
    
    return jsonify({
        "totalScans": total_scans,
        "phishingDetected": phishing_detected,
        "activeUsers": active_users,
        "premiumUsers": premium_users
    }), 200

@admin_bp.route('/recent-threats', methods=['GET'])
def get_recent_threats():
    # In reality, query ScanModel where result.is_phishing == True
    threats = [
        {"target": "paypal-login.security-check.ru", "type": "url", "score": 98, "timestamp": "2026-05-16T10:30:00Z"},
        {"target": "URGENT: Win $1000 gift card...", "type": "sms", "score": 92, "timestamp": "2026-05-16T11:15:00Z"},
        {"target": "microsoft.update-365.com", "type": "url", "score": 87, "timestamp": "2026-05-16T12:00:00Z"}
    ]
    return jsonify(threats), 200

@admin_bp.route('/users', methods=['GET'])
def get_users_admin():
    users = [
        {"email": "user1@example.com", "plan": "Premium", "status": "active"},
        {"email": "user2@example.com", "plan": "Free Trial", "status": "active"},
        {"email": "user3@example.com", "plan": "Premium", "status": "expired"}
    ]
    return jsonify(users), 200
