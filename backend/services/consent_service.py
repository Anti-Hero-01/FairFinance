"""
Consent management service
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from backend.config.settings import settings
from backend.models.database import ConsentRecord, User
from backend.schemas.consent import ConsentStatus, ConsentAlert

class ConsentService:
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load consent configuration"""
        try:
            with open(settings.CONSENT_CONFIG_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading consent config: {e}")
            return {}
    
    def get_consent_config(self) -> Dict:
        """Get consent configuration"""
        return self.config
    
    def update_consent(self, db: Session, user_id: int, data_category: str, consent_given: bool) -> ConsentRecord:
        """Update user consent for a data category"""
        # Check if record exists
        consent_record = db.query(ConsentRecord).filter(
            ConsentRecord.user_id == user_id,
            ConsentRecord.data_category == data_category
        ).first()
        
        if consent_record:
            consent_record.consent_given = consent_given
            consent_record.last_updated = datetime.utcnow()
        else:
            consent_record = ConsentRecord(
                user_id=user_id,
                data_category=data_category,
                consent_given=consent_given
            )
            db.add(consent_record)
        
        db.commit()
        db.refresh(consent_record)
        return consent_record
    
    def get_user_consents(self, db: Session, user_id: int) -> List[ConsentStatus]:
        """Get all consents for a user"""
        consent_records = db.query(ConsentRecord).filter(
            ConsentRecord.user_id == user_id
        ).all()
        
        # Get data categories from config
        data_categories = self.config.get('data_categories', {})
        
        consents = []
        for category, config in data_categories.items():
            # Find existing record
            record = next((r for r in consent_records if r.data_category == category), None)
            
            consent_status = ConsentStatus(
                data_category=category,
                description=config.get('description', ''),
                consent_given=record.consent_given if record else config.get('default', False),
                required_for=config.get('required_for', []),
                last_updated=record.last_updated if record else datetime.utcnow()
            )
            consents.append(consent_status)
        
        return consents
    
    def check_consent(self, db: Session, user_id: int, action: str) -> bool:
        """Check if user has consent for a specific action"""
        consents = self.get_user_consents(db, user_id)
        data_categories = self.config.get('data_categories', {})
        
        # Find required categories for action
        required_categories = []
        for category, config in data_categories.items():
            if action in config.get('required_for', []):
                required_categories.append(category)
        
        # Check if all required consents are given
        for category in required_categories:
            consent = next((c for c in consents if c.data_category == category), None)
            if not consent or not consent.consent_given:
                return False
        
        return True
    
    def generate_alert(self, action: str, consent_changed: bool = False) -> ConsentAlert:
        """Generate consent alert"""
        alert_messages = self.config.get('alert_messages', {})
        
        if consent_changed:
            message = alert_messages.get('consent_change', 'Your consent preferences have been updated.')
        else:
            message = alert_messages.get('data_usage', 'Your data was used for {action}.').format(action=action)
        
        return ConsentAlert(
            message=message,
            timestamp=datetime.utcnow(),
            action=action
        )

# Global consent service
consent_service = ConsentService()

