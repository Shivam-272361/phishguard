from utils.db import DatabaseService
from datetime import datetime, timedelta
import bcrypt

class UserModel:
    @staticmethod
    def create_user(email, password, name):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user_data = {
            "email": email,
            "password": hashed_password,
            "name": name,
            "verified": False,
            "otp": None,
            "otp_expiry": None,
            "created_at": datetime.utcnow(),
            "last_login": None
        }
        return DatabaseService.get_users_collection().insert_one(user_data)

    @staticmethod
    def find_by_email(email):
        return DatabaseService.get_users_collection().find_one({"email": email})

    @staticmethod
    def update_otp(email, otp, expiry):
        return DatabaseService.get_users_collection().update_one(
            {"email": email},
            {"$set": {"otp": otp, "otp_expiry": expiry}}
        )

    @staticmethod
    def verify_user(email):
        return DatabaseService.get_users_collection().update_one(
            {"email": email},
            {"$set": {"verified": True, "otp": None, "otp_expiry": None}}
        )

class SubscriptionModel:
    @staticmethod
    def activate_trial(user_id):
        start_date = datetime.utcnow()
        expiry_date = start_date + timedelta(days=14) # 14-day free trial
        sub_data = {
            "user_id": user_id,
            "plan": "free_trial",
            "status": "active",
            "start_date": start_date,
            "expiry_date": expiry_date,
            "auto_renew": False,
            "features": ["url_scan", "email_monitor_limited"]
        }
        return DatabaseService.get_subscriptions_collection().update_one(
            {"user_id": user_id},
            {"$set": sub_data},
            upsert=True
        )

    @staticmethod
    def upgrade_to_premium(user_id, months=1):
        start_date = datetime.utcnow()
        expiry_date = start_date + timedelta(days=30 * months)
        sub_data = {
            "user_id": user_id,
            "plan": "premium",
            "status": "active",
            "start_date": start_date,
            "expiry_date": expiry_date,
            "auto_renew": True,
            "features": ["url_scan", "email_monitor_full", "sms_monitor", "priority_support"]
        }
        return DatabaseService.get_subscriptions_collection().update_one(
            {"user_id": user_id},
            {"$set": sub_data},
            upsert=True
        )

    @staticmethod
    def get_subscription(user_id):
        subscription = DatabaseService.get_subscriptions_collection().find_one({"user_id": user_id})
        if subscription and subscription['status'] == 'active':
            # Auto-expire check
            if subscription['expiry_date'] < datetime.utcnow():
                DatabaseService.get_subscriptions_collection().update_one(
                    {"user_id": user_id},
                    {"$set": {"status": "expired"}}
                )
                subscription['status'] = 'expired'
        return subscription

class ScanModel:
    @staticmethod
    def log_scan(user_id, scan_type, target, result):
        log_data = {
            "user_id": user_id,
            "type": scan_type, # url, email, sms
            "target": target,
            "result": result,
            "timestamp": datetime.utcnow()
        }
        return DatabaseService.get_scan_history_collection().insert_one(log_data)
