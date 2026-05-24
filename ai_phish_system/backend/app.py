import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from utils.db import init_db

def create_app():
    app = Flask(__name__)
    
    # 1. CORS Security - Restrict to Extension and Frontend
    allowed_origins = [
        os.getenv('CORS_ORIGIN_FRONTEND', 'http://localhost:5173'),
        os.getenv('CORS_ORIGIN_EXTENSION', 'chrome-extension://*')
    ]
    CORS(app, resources={r"/api/*": {"origins": allowed_origins}}, supports_credentials=True)

    # 2. Secure Headers & HTTPS redirection (Talisman)
    # force_https set to false for local development, true in production
    Talisman(app, 
             force_https=os.getenv('FLASK_ENV') == 'production', 
             content_security_policy=None,
             strict_transport_security=True)

    # 3. Rate Limiting
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
    )

    # App Config (Encrypted/Hardened)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'phishguard_default_secret_2026')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', app.config['SECRET_KEY'])
    app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/phishguard_db')
    
    # Secure JWT behavior
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600 # 1 hour
    app.config['JWT_ERROR_MESSAGE_KEY'] = 'error'

    # Initialize JWT
    jwt = JWTManager(app)

    # Initialize Database
    init_db(app)

    from routes.scan_routes import scan_bp
    from routes.auth_routes import auth_bp, sub_bp
    from routes.sms_routes import sms_bp
    from routes.admin_routes import admin_bp

    app.register_blueprint(scan_bp, url_prefix='/api/scan')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(sms_bp, url_prefix='/api/sms')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(sub_bp, url_prefix='/api/subscription')

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"success": False, "error": "Internal server error"}), 500

    @app.route('/')
    def index():
        return jsonify({"status": "AI PhishGuard API is running", "version": "2.0.0"})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5005, debug=True)
