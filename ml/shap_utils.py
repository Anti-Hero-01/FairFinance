"""
SHAP explainability utilities
Provides feature importance and local/global explanations
"""

import numpy as np
import pandas as pd
import pickle
import os
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    print("Warning: SHAP not available. Install with: pip install shap")

class SHAPExplainer:
    def __init__(self, model, feature_names=None):
        self.model = model
        self.feature_names = feature_names
        self.explainer = None
        self.shap_values = None
        
    def create_explainer(self, X_train, explainer_type='tree'):
        """Create SHAP explainer"""
        if not SHAP_AVAILABLE:
            return None
        
        try:
            if explainer_type == 'tree' and hasattr(self.model, 'predict_proba'):
                self.explainer = shap.TreeExplainer(self.model)
            elif explainer_type == 'linear' and hasattr(self.model, 'coef_'):
                self.explainer = shap.LinearExplainer(self.model, X_train)
            else:
                # Use KernelExplainer as fallback
                self.explainer = shap.KernelExplainer(
                    self.model.predict_proba if hasattr(self.model, 'predict_proba') else self.model.predict,
                    X_train[:100]  # Sample for faster computation
                )
            return self.explainer
        except Exception as e:
            print(f"Error creating SHAP explainer: {e}")
            return None
    
    def compute_shap_values(self, X, max_evals=100):
        """Compute SHAP values for given data"""
        if self.explainer is None:
            return None
        
        try:
            if isinstance(self.explainer, shap.KernelExplainer):
                self.shap_values = self.explainer.shap_values(X, nsamples=max_evals)
            else:
                self.shap_values = self.explainer.shap_values(X)
            
            # Handle multi-class output
            if isinstance(self.shap_values, list):
                self.shap_values = self.shap_values[1]  # Use positive class
            
            return self.shap_values
        except Exception as e:
            print(f"Error computing SHAP values: {e}")
            return None
    
    def get_feature_importance(self, shap_values=None):
        """Get global feature importance from SHAP values"""
        if shap_values is None:
            shap_values = self.shap_values
        
        if shap_values is None:
            return None
        
        # Mean absolute SHAP values
        importance = np.abs(shap_values).mean(axis=0)
        
        if self.feature_names is not None:
            importance_df = pd.DataFrame({
                'feature': self.feature_names,
                'importance': importance
            }).sort_values('importance', ascending=False)
            return importance_df
        else:
            return importance
    
    def explain_instance(self, instance, shap_values=None):
        """Explain a single prediction instance"""
        if shap_values is None:
            shap_values = self.shap_values
        
        if shap_values is None or len(shap_values.shape) == 1:
            return None
        
        # Get SHAP values for this instance
        if isinstance(instance, int):
            instance_shap = shap_values[instance]
        else:
            # Find matching instance
            instance_shap = shap_values[0]  # Default to first
        
        if self.feature_names is not None:
            explanation = pd.DataFrame({
                'feature': self.feature_names,
                'shap_value': instance_shap
            }).sort_values('shap_value', key=abs, ascending=False)
            return explanation
        else:
            return instance_shap
    
    def get_top_features(self, instance_idx, top_n=5, shap_values=None):
        """Get top N features contributing to a prediction"""
        explanation = self.explain_instance(instance_idx, shap_values)
        
        if explanation is None:
            return None
        
        top_positive = explanation.nlargest(top_n, 'shap_value')
        top_negative = explanation.nsmallest(top_n, 'shap_value')
        
        return {
            'top_positive': top_positive.to_dict('records'),
            'top_negative': top_negative.to_dict('records')
        }
    
    def save_explainer(self, filepath='ml/shap_explainer.pkl'):
        """Save SHAP explainer"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump({
                'explainer': self.explainer,
                'feature_names': self.feature_names
            }, f)
    
    @classmethod
    def load_explainer(cls, model, filepath='ml/shap_explainer.pkl'):
        """Load SHAP explainer"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        explainer = cls(model, data['feature_names'])
        explainer.explainer = data['explainer']
        return explainer

def create_shap_explainer(model, X_train, feature_names=None, explainer_type='auto'):
    """Convenience function to create SHAP explainer"""
    explainer = SHAPExplainer(model, feature_names)
    
    if explainer_type == 'auto':
        # Auto-detect explainer type
        if hasattr(model, 'tree_') or hasattr(model, 'get_booster'):
            explainer_type = 'tree'
        elif hasattr(model, 'coef_'):
            explainer_type = 'linear'
        else:
            explainer_type = 'kernel'
    
    explainer.create_explainer(X_train, explainer_type)
    return explainer

if __name__ == '__main__':
    # Test SHAP explainer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import make_classification
    
    # Create sample data
    X, y = make_classification(n_samples=100, n_features=10, random_state=42)
    feature_names = [f'feature_{i}' for i in range(10)]
    
    # Train model
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    
    # Create SHAP explainer
    shap_explainer = create_shap_explainer(model, X, feature_names)
    
    # Compute SHAP values
    shap_values = shap_explainer.compute_shap_values(X[:10])
    
    if shap_values is not None:
        # Get feature importance
        importance = shap_explainer.get_feature_importance()
        print("Feature Importance:")
        print(importance)
        
        # Explain instance
        explanation = shap_explainer.explain_instance(0)
        print("\nInstance Explanation:")
        print(explanation)
        
        # Get top features
        top_features = shap_explainer.get_top_features(0, top_n=3)
        print("\nTop Features:")
        print(top_features)

