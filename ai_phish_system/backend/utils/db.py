from flask_pymongo import PyMongo
from flask import current_app

# Global mongo instance
mongo = PyMongo()

def init_db(app):
    """
    Initializes the MongoDB connection with the Flask app.
    Uses the MONGO_URI from config.
    """
    try:
        mongo.init_app(app)
        # Verify connection
        with app.app_context():
            mongo.db.command('ping')
            print("Successfully connected to MongoDB Docker container!")
            
            # Create collections if they don't exist implicitly by using them
            # users, subscriptions, scan_history, phishing_reports
    except Exception as e:
        print(f"Failed to connect to MongoDB: {str(e)}")
        raise e

class DatabaseService:
    @staticmethod
    def get_users_collection():
        return mongo.db.users

    @staticmethod
    def get_subscriptions_collection():
        return mongo.db.subscriptions

    @staticmethod
    def get_scan_history_collection():
        return mongo.db.scan_history

    @staticmethod
    def get_reports_collection():
        return mongo.db.phishing_reports
