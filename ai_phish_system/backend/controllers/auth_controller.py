import random
import string
from datetime import datetime, timedelta
import bcrypt
from flask import request, jsonify
from flask_jwt_extended import create_access_token
from models.db_models import UserModel, SubscriptionModel
from utils.validators import UserSignupSchema, UserLoginSchema, OtpVerificationSchema
from marshmallow import ValidationError

def signup():
    # 1. Request Validation
    schema = UserSignupSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400

    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if UserModel.find_by_email(email):
        return jsonify({"error": "User already exists"}), 409

    UserModel.create_user(email, password, name)
    
    # Generate OTP for email verification
    otp = ''.join(random.choices(string.digits, k=6))
    expiry = datetime.utcnow() + timedelta(minutes=10)
    UserModel.update_otp(email, otp, expiry)

    # In a real app, send OTP via email service here
    print(f"DEBUG: OTP for {email} is {otp}")

    return jsonify({
        "success": True, 
        "message": "User registered. Please verify your email with the OTP sent.",
        "debug_otp": otp
    }), 201

def verify_otp():
    # 1. Request Validation
    schema = OtpVerificationSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400

    email = data.get('email')
    otp = data.get('otp')

    user = UserModel.find_by_email(email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.get('otp') != otp:
        return jsonify({"error": "Invalid OTP"}), 401

    if user.get('otp_expiry') < datetime.utcnow():
        return jsonify({"error": "OTP expired"}), 401

    # Mark user as verified
    UserModel.verify_user(email)
    
    # Automatically activate trial
    SubscriptionModel.activate_trial(str(user['_id']))

    return jsonify({"success": True, "message": "Email verified and 14-day trial activated"}), 200

def login():
    # 1. Request Validation
    schema = UserLoginSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400

    email = data.get('email')
    password = data.get('password')

    user = UserModel.find_by_email(email)
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.get('verified'):
        return jsonify({"error": "Email not verified", "code": "NOT_VERIFIED"}), 403

    access_token = create_access_token(identity=str(user['_id']), expires_delta=timedelta(days=1))

    return jsonify({
        "success": True,
        "token": access_token,
        "user": {
            "name": user['name'],
            "email": user['email']
        }
    }), 200

def logout():
    return jsonify({"success": True, "message": "Logged out successfully"}), 200

