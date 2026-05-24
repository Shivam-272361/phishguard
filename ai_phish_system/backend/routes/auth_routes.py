from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers.auth_controller import signup, login, verify_otp, logout
from controllers.subscription_controller import get_status, upgrade_premium, check_feature_access
from services.monitor_orchestrator import MonitoringOrchestrator

auth_bp = Blueprint('auth', __name__)
sub_bp = Blueprint('subscription', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup_route():
    return signup()

@auth_bp.route('/verify-email', methods=['POST'])
def verify_email_route():
    return verify_otp()

@auth_bp.route('/login', methods=['POST'])
def login_route():
    return login()

@auth_bp.route('/logout', methods=['POST'])
def logout_route():
    return logout()

@sub_bp.route('/status', methods=['GET'])
def status_route():
    return get_status()

@sub_bp.route('/upgrade', methods=['POST'])
def upgrade_route():
    return upgrade_premium()

@sub_bp.route('/check-access', methods=['GET'])
def check_access_route():
    return check_feature_access()

@sub_bp.route('/monitor/email/start', methods=['POST'])
@jwt_required()
def start_email_monitor():
    user_id = get_jwt_identity()
    success, message = MonitoringOrchestrator.start_user_monitoring(user_id)
    return jsonify({
        "success": success, 
        "message": message
    }), 200 if success else 400

