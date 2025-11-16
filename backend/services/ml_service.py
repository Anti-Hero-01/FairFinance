"""
ML model service for predictions and explanations
"""

import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List
from backend.config.settings import settings
from ml.shap_utils import SHAPExplainer
from ml.ethical_twin import EthicalTwin

class MLService:
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.ethical_twin = None
        self.shap_explainer = None
        self.feature_names = None
        self.load_models()
    
    def load_models(self):
        """Load all ML models and components"""
        try:
            # Load main model
            with open(settings.MODEL_PATH, 'rb') as f:
                self.model = pickle.load(f)
            
            # Load preprocessor
            try:
                with open(settings.PREPROCESSOR_PATH, 'rb') as f:
                    preprocessor_data = pickle.load(f)
                    self.preprocessor = preprocessor_data
            except:
                print("Preprocessor not found, using default")
            
            # Load feature names
            try:
                with open(settings.FEATURE_NAMES_PATH, 'rb') as f:
                    self.feature_names = pickle.load(f)
            except:
                print("Feature names not found")
            
            # Load ethical twin
            try:
                self.ethical_twin = EthicalTwin.load(settings.ETHICAL_TWIN_PATH)
            except:
                print("Ethical twin not found")
            
            # Load SHAP explainer
            try:
                self.shap_explainer = SHAPExplainer.load_explainer(
                    self.model,
                    settings.SHAP_EXPLAINER_PATH
                )
            except:
                print("SHAP explainer not found")
            
            print("ML models loaded successfully")
        except Exception as e:
            print(f"Error loading models: {e}")
            self.model = None
    
    def prepare_features(self, application_data: Dict[str, Any]) -> np.ndarray:
        """Prepare features for prediction"""
        # Create feature vector
        feature_dict = {
            'age': application_data.get('age', 0),
            'income': application_data.get('income', 0),
            'credit_score': application_data.get('credit_score', 0),
            'loan_amount': application_data.get('loan_amount', 0),
            'employment_years': application_data.get('employment_years', 0),
            'debt_to_income': application_data.get('debt_to_income', 0),
            'credit_history_length': application_data.get('credit_history_length', 0),
            'number_of_accounts': application_data.get('number_of_accounts', 0),
            'defaults': application_data.get('defaults', 0),
        }
        
        # Add derived features if needed
        if 'age' in feature_dict and 'income' in feature_dict:
            feature_dict['age_income_ratio'] = feature_dict['age'] / (feature_dict['income'] + 1)
        
        if 'loan_amount' in feature_dict and 'income' in feature_dict:
            feature_dict['loan_to_income'] = feature_dict['loan_amount'] / (feature_dict['income'] + 1)
        
        # Create DataFrame
        if self.feature_names:
            # Ensure all features are present
            for feat in self.feature_names:
                if feat not in feature_dict:
                    feature_dict[feat] = 0
            
            # Order by feature names
            feature_array = np.array([feature_dict.get(feat, 0) for feat in self.feature_names])
        else:
            feature_array = np.array(list(feature_dict.values()))
        
        # Reshape for single prediction
        feature_array = feature_array.reshape(1, -1)
        
        # Scale if preprocessor available
        if self.preprocessor and hasattr(self.preprocessor, 'scaler'):
            feature_array = self.preprocessor['scaler'].transform(feature_array)
        
        return feature_array
    
    def predict(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make prediction"""
        if self.model is None:
            raise Exception("Model not loaded")
        
        # Prepare features
        features = self.prepare_features(application_data)
        
        # Predict
        prediction = self.model.predict(features)[0]
        probability = self.model.predict_proba(features)[0][1] if hasattr(self.model, 'predict_proba') else float(prediction)
        
        return {
            'prediction': bool(prediction),
            'probability': float(probability),
            'features': features
        }
    
    def explain_prediction(self, application_data: Dict[str, Any], features: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Explain prediction using SHAP and Ethical Twin"""
        explanation = {
            'shap_explanation': None,
            'ethical_twin_explanation': None,
            'top_features': []
        }
        
        if features is None:
            features = self.prepare_features(application_data)
        
        # SHAP explanation
        if self.shap_explainer:
            try:
                shap_values = self.shap_explainer.compute_shap_values(features)
                if shap_values is not None:
                    top_features = self.shap_explainer.get_top_features(0, top_n=5, shap_values=shap_values)
                    explanation['shap_explanation'] = {
                        'top_positive': top_features.get('top_positive', []),
                        'top_negative': top_features.get('top_negative', [])
                    }
                    explanation['top_features'] = top_features
            except Exception as e:
                print(f"SHAP explanation error: {e}")
        
        # Ethical Twin explanation
        if self.ethical_twin:
            try:
                ethical_explanation = self.ethical_twin.explain_decision(
                    features[0],
                    self.feature_names
                )
                explanation['ethical_twin_explanation'] = ethical_explanation
            except Exception as e:
                print(f"Ethical twin explanation error: {e}")
        
        return explanation

# Global ML service instance
ml_service = MLService()

