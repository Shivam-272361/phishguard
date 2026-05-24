from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.db_models import SubscriptionModel
from datetime import datetime

@jwt_required()
def get_status():
    user_id = get_jwt_identity()
    subscription = SubscriptionModel.get_subscription(user_id)
    
    if not subscription:
        return jsonify({
            "has_subscription": False,
            "status": "none",
            "message": "No subscription found for this user."
        }), 200

    # Clean up MongoDB object for JSON
    subscription['_id'] = str(subscription['_id'])
    
    return jsonify({
        "has_subscription": True,
        "plan": subscription['plan'],
        "status": subscription['status'],
        "expiry_date": subscription['expiry_date'].isoformat(),
        "is_expired": subscription['expiry_date'] < datetime.utcnow(),
        "features": subscription.get('features', [])
    }), 200

@jwt_required()
def upgrade_premium():
    user_id = get_jwt_identity()
    # In a real app, verify payment token here
    
    SubscriptionModel.upgrade_to_premium(user_id)
    
    return jsonify({
        "success": True,
        "message": "Successfully upgraded to Premium!"
    }), 200

@jwt_required()
def check_feature_access():
    feature = request.args.get('feature')
    user_id = get_jwt_identity()
    
    subscription = SubscriptionModel.get_subscription(user_id)
    
    if not subscription or subscription['status'] != 'active':
        return jsonify({"access": False, "reason": "No active subscription"}), 200
        
    features = subscription.get('features', [])
    if feature in features:
        return jsonify({"access": True}), 200
    else:
        return jsonify({"access": False, "reason": "Feature not included in current plan"}), 200
