"""
Fairness metrics and reporting service
"""

import json
from typing import Dict, List, Any
from datetime import datetime
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
from backend.config.settings import settings
from backend.models.database import LoanApplication
from ml.fairness_pipeline import FairnessPipeline

class FairnessService:
    def __init__(self):
        self.pipeline = FairnessPipeline(settings.BIAS_GROUPS_CONFIG_PATH)
    
    def compute_fairness_metrics(self, db: Session) -> Dict[str, Any]:
        """Compute fairness metrics from recent applications"""
        # Get recent applications with predictions
        applications = db.query(LoanApplication).filter(
            LoanApplication.prediction.isnot(None)
        ).all()
        
        if len(applications) < 10:
            return {
                'error': 'Insufficient data for fairness analysis',
                'applications_count': len(applications)
            }
        
        # Prepare data
        data = []
        y_true = []
        y_pred = []
        
        for app in applications:
            row = {
                'gender': app.gender,
                'region': app.region,
                'age_group': app.age_group
            }
            data.append(row)
            # Use prediction as ground truth for now (in production, use actual outcomes)
            y_true.append(int(app.prediction))
            y_pred.append(int(app.prediction))
        
        df = pd.DataFrame(data)
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        
        # Compute fairness metrics
        all_metrics = self.pipeline.compute_all_fairness_metrics(y_true, y_pred, df)
        violations = self.pipeline.check_fairness_thresholds(all_metrics)
        
        return {
            'metrics': all_metrics,
            'violations': violations,
            'applications_analyzed': len(applications),
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def generate_fairness_report(self, db: Session, output_path: str = None) -> Dict[str, Any]:
        """Generate comprehensive fairness report"""
        if output_path is None:
            output_path = settings.BIAS_GROUPS_CONFIG_PATH.replace('bias_groups_config.json', '../docs/fairness_report.md')
        
        # Get applications
        applications = db.query(LoanApplication).filter(
            LoanApplication.prediction.isnot(None)
        ).all()
        
        if len(applications) < 10:
            return {
                'error': 'Insufficient data for fairness analysis'
            }
        
        # Prepare data
        data = []
        y_true = []
        y_pred = []
        
        for app in applications:
            row = {
                'gender': app.gender,
                'region': app.region,
                'age_group': app.age_group
            }
            data.append(row)
            y_true.append(int(app.prediction))
            y_pred.append(int(app.prediction))
        
        df = pd.DataFrame(data)
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        
        # Generate report
        report = self.pipeline.generate_fairness_report(y_true, y_pred, df, output_path)
        
        return {
            'report_id': f"report_{int(datetime.utcnow().timestamp())}",
            'generated_at': datetime.utcnow().isoformat(),
            'metrics': report['metrics'],
            'violations': report['violations'],
            'report_path': report['report_path']
        }

# Global fairness service
fairness_service = FairnessService()

