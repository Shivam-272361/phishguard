from flask import Blueprint, request, jsonify
from controllers.scan_controller import check_url, check_email, check_sms

scan_bp = Blueprint('scan', __name__)

@scan_bp.route('/url', methods=['POST'])
def url_route():
    return check_url()

@scan_bp.route('/email', methods=['POST'])
def email_route():
    return check_email()

@scan_bp.route('/sms', methods=['POST'])
def sms_route():
    return check_sms()
