import time
import threading
from services.gmail_monitor import GmailMonitor
from models.db_models import SubscriptionModel
from utils.db import DatabaseService

class MonitoringOrchestrator:
    _monitors = {} # user_id -> thread

    @classmethod
    def start_user_monitoring(cls, user_id):
        if user_id in cls._monitors and cls._monitors[user_id].is_alive():
            return True, "Monitoring already active"

        # Check subscription status
        subscription = SubscriptionModel.get_subscription(user_id)
        if not subscription or subscription['status'] != 'active':
            return False, "Active subscription required for background monitoring"

        # Start Gmail Monitor in background thread
        try:
            monitor = GmailMonitor(user_id)
            thread = threading.Thread(target=monitor.start_monitoring, daemon=True)
            thread.start()
            cls._monitors[user_id] = thread
            return True, "Background monitoring started"
        except Exception as e:
            return False, str(e)

    @classmethod
    def stop_all_expired(cls):
        # Background maintenance task to kill threads for expired users
        # In a production distributed system, this would be handled by a worker fleet
        pass
