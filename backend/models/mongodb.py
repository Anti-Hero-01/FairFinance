"""
MongoDB models for immutable decision logs
"""

from pymongo import MongoClient
from datetime import datetime
from typing import Dict, Any, Optional
from backend.config.settings import settings
import json

class MongoDBClient:
    def __init__(self):
        try:
            self.client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=2000)
            self.db = self.client[settings.MONGODB_DB]
            self.decision_logs = self.db.decision_logs
            self.audit_trails = self.db.audit_trails
            # Test connection
            self.client.admin.command('ping')
            self.available = True
        except Exception as e:
            print(f"MongoDB not available: {e}. Using in-memory storage.")
            self.available = False
            self._memory_logs = []
            self._memory_audits = []
    
    def insert_decision_log(self, log_data: Dict[str, Any]) -> str:
        """Insert immutable decision log"""
        log_data['timestamp'] = datetime.utcnow()
        log_data['_id'] = f"{log_data.get('application_id')}_{int(datetime.utcnow().timestamp())}"
        if self.available:
            result = self.decision_logs.insert_one(log_data)
            return str(result.inserted_id)
        else:
            self._memory_logs.append(log_data)
            return log_data['_id']
    
    def get_decision_logs(self, user_id: Optional[int] = None, limit: int = 100):
        """Get decision logs, optionally filtered by user_id"""
        if self.available:
            query = {}
            if user_id:
                query['user_id'] = user_id
            logs = self.decision_logs.find(query).sort('timestamp', -1).limit(limit)
            return list(logs)
        else:
            logs = self._memory_logs
            if user_id:
                logs = [log for log in logs if log.get('user_id') == user_id]
            return sorted(logs, key=lambda x: x.get('timestamp', datetime.utcnow()), reverse=True)[:limit]
    
    def get_decision_log(self, application_id: int):
        """Get decision log for specific application"""
        if self.available:
            log = self.decision_logs.find_one({'application_id': application_id})
            return log
        else:
            for log in self._memory_logs:
                if log.get('application_id') == application_id:
                    return log
            return None
    
    def insert_audit_trail(self, audit_data: Dict[str, Any]) -> str:
        """Insert audit trail entry"""
        audit_data['timestamp'] = datetime.utcnow()
        if self.available:
            result = self.audit_trails.insert_one(audit_data)
            return str(result.inserted_id)
        else:
            audit_data['_id'] = f"audit_{int(datetime.utcnow().timestamp())}"
            self._memory_audits.append(audit_data)
            return audit_data['_id']
    
    def get_audit_trails(self, user_id: Optional[int] = None, limit: int = 100):
        """Get audit trails"""
        if self.available:
            query = {}
            if user_id:
                query['user_id'] = user_id
            trails = self.audit_trails.find(query).sort('timestamp', -1).limit(limit)
            return list(trails)
        else:
            trails = self._memory_audits
            if user_id:
                trails = [trail for trail in trails if trail.get('user_id') == user_id]
            return sorted(trails, key=lambda x: x.get('timestamp', datetime.utcnow()), reverse=True)[:limit]

# Global MongoDB client instance
mongodb_client = MongoDBClient()

