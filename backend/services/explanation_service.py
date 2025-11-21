"""
Explanation service using templates and SHAP
"""

import json
import random
from typing import Dict, Any, List
from backend.config.settings import settings
from backend.services.ml_service import ml_service

class ExplanationService:
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load explanation templates"""
        try:
            with open(settings.EXPLANATION_TEMPLATES_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading templates: {e}")
            return {
                "loan_denied": ["Your loan was denied due to risk factors."],
                "loan_approved": ["Your loan was approved."],
                "profile_explanation": ["Your profile analysis."]
            }
    
    def generate_explanation(self, prediction: bool, probability: float, 
                            explanation_data: Dict[str, Any]) -> str:
        """Generate human-readable explanation"""
        template_key = "loan_approved" if prediction else "loan_denied"
        templates = self.templates.get(template_key, [f"Loan {'approved' if prediction else 'denied'}."])
        
        # Get top features
        top_features = explanation_data.get('top_features') or {}
        if isinstance(top_features, list):
            top_positive = top_features
            top_negative = []
        else:
            top_positive = top_features.get('top_positive', [])
            top_negative = top_features.get('top_negative', [])
        
        # Format feature names
        if prediction:
            feature_list = [f.get('feature', '') for f in top_positive[:3]]
        else:
            feature_list = [f.get('feature', '') for f in top_negative[:3]]
        
        # Select random template
        template = random.choice(templates)
        
        # Format template
        if prediction:
            explanation = template.format(
                top_positive_features=", ".join(feature_list) if feature_list else "strong financial indicators"
            )
        else:
            explanation = template.format(
                top_negative_features=", ".join(feature_list) if feature_list else "risk factors"
            )
        
        return explanation
    
    def generate_profile_explanation(self, user_applications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate profile-level explanation"""
        if not user_applications:
            return {
                'risk_category': 'unknown',
                'top_global_features': [],
                'improvement_suggestions': [],
                'explanation_text': 'No application history found.'
            }
        
        # Aggregate features across applications
        all_features = {}
        for app in user_applications:
            explanation = app.get('explanation', {}) or {}
            if not isinstance(explanation, dict):
                continue
            shap_exp = explanation.get('shap_explanation') or {}
            if not isinstance(shap_exp, dict):
                continue
            top_pos = shap_exp.get('top_positive', []) or []
            top_neg = shap_exp.get('top_negative', []) or []
            
            for feat in top_pos + top_neg:
                if not isinstance(feat, dict):
                    continue
                feat_name = feat.get('feature', '')
                if feat_name:
                    if feat_name not in all_features:
                        all_features[feat_name] = 0
                    all_features[feat_name] += abs(feat.get('contribution', 0))
        
        # Get top global features - use 'contribution' to match schema
        sorted_features = sorted(all_features.items(), key=lambda x: x[1], reverse=True)
        top_global = [{'feature': name, 'contribution': imp} for name, imp in sorted_features[:5]]
        
        # Determine risk category
        avg_probability = sum(app.get('probability', 0.5) for app in user_applications) / len(user_applications)
        if avg_probability > 0.7:
            risk_category = 'low'
        elif avg_probability > 0.4:
            risk_category = 'medium'
        else:
            risk_category = 'high'
        
        # Generate improvement suggestions
        negative_features = [f['feature'] for f in top_global if f.get('contribution', 0) < 0][:3]
        improvement_suggestions = negative_features if negative_features else ['credit_score', 'debt_to_income_ratio']
        
        # Generate explanation text
        template = random.choice(self.templates.get('profile_explanation', ['Your profile analysis.']))
        explanation_text = template.format(
            risk_category=risk_category,
            top_global_features=", ".join([f['feature'] for f in top_global[:3]])
        )
        
        return {
            'risk_category': risk_category,
            'top_global_features': top_global or [],
            'improvement_suggestions': improvement_suggestions or [],
            'explanation_text': explanation_text or 'Profile analysis completed.'
        }

# Global explanation service
explanation_service = ExplanationService()

