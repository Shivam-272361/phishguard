from flask import jsonify
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models.db_models import SubscriptionModel
from datetime import datetime

def subscription_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        subscription = SubscriptionModel.get_subscription(user_id)
        
        if not subscription:
            return jsonify({"error": "No active subscription found", "code": "NO_SUBSCRIPTION"}), 403
            
        if subscription['status'] != 'active':
            return jsonify({"error": "Subscription is inactive", "code": "INACTIVE_SUBSCRIPTION"}), 403
            
        if subscription['expiry_date'] < datetime.utcnow():
            return jsonify({"error": "Subscription has expired", "code": "EXPIRED_SUBSCRIPTION"}), 403
            
        return f(*args, **kwargs)
    return decorated_function
