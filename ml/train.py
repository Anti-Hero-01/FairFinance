"""
Train ML models: Logistic Regression and XGBoost
Saves trained models for inference
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import xgboost as xgb
from preprocessing import CreditDataPreprocessor
from synthetic_data import SyntheticBiasGenerator

class ModelTrainer:
    def __init__(self):
        self.models = {}
        self.preprocessor = None
        self.feature_names = None
        
    def load_and_prepare_data(self):
        """Load and prepare data with synthetic bias"""
        # Load and preprocess
        preprocessor = CreditDataPreprocessor()
        processed = preprocessor.process()
        
        # Add synthetic bias to original data
        generator = SyntheticBiasGenerator()
        original_df = preprocessor.load_data()
        synthetic_df = generator.generate_synthetic_dataset(original_df)
        
        # Re-process with synthetic data
        preprocessor_synthetic = CreditDataPreprocessor()
        preprocessor_synthetic.data_path = None  # Will use synthetic_df directly
        
        # Manually process synthetic data
        df_clean = preprocessor_synthetic.clean_data(synthetic_df)
        df_features = preprocessor_synthetic.engineer_features(df_clean)
        X, y = preprocessor_synthetic.prepare_features(df_features)
        
        # Split
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y if len(y.unique()) > 1 else None
        )
        
        # Scale
        X_train_scaled, X_test_scaled = preprocessor_synthetic.scale_features(X_train, X_test)
        
        self.preprocessor = preprocessor_synthetic
        self.feature_names = preprocessor_synthetic.feature_names
        
        return X_train_scaled, X_test_scaled, y_train, y_test
    
    def train_logistic_regression(self, X_train, y_train):
        """Train Logistic Regression model"""
        print("Training Logistic Regression...")
        lr_model = LogisticRegression(
            max_iter=1000,
            random_state=42,
            solver='lbfgs',
            class_weight='balanced'
        )
        lr_model.fit(X_train, y_train)
        self.models['logistic_regression'] = lr_model
        return lr_model
    
    def train_xgboost(self, X_train, y_train):
        """Train XGBoost model"""
        print("Training XGBoost...")
        xgb_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
            eval_metric='logloss',
            use_label_encoder=False
        )
        xgb_model.fit(X_train, y_train)
        self.models['xgboost'] = xgb_model
        return xgb_model
    
    def evaluate_model(self, model, X_test, y_test, model_name):
        """Evaluate model performance"""
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else y_pred
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1': f1_score(y_test, y_pred, zero_division=0),
        }
        
        try:
            metrics['roc_auc'] = roc_auc_score(y_test, y_pred_proba)
        except:
            metrics['roc_auc'] = 0.0
        
        print(f"\n{model_name} Metrics:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value:.4f}")
        
        return metrics
    
    def train_all_models(self):
        """Train all models"""
        # Load and prepare data
        X_train, X_test, y_train, y_test = self.load_and_prepare_data()
        
        # Train models
        lr_model = self.train_logistic_regression(X_train, y_train)
        xgb_model = self.train_xgboost(X_train, y_train)
        
        # Evaluate models
        lr_metrics = self.evaluate_model(lr_model, X_test, y_test, 'Logistic Regression')
        xgb_metrics = self.evaluate_model(xgb_model, X_test, y_test, 'XGBoost')
        
        # Select best model (based on F1 score)
        if xgb_metrics['f1'] > lr_metrics['f1']:
            self.best_model = xgb_model
            self.best_model_name = 'xgboost'
        else:
            self.best_model = lr_model
            self.best_model_name = 'logistic_regression'
        
        print(f"\nBest model: {self.best_model_name}")
        
        return {
            'X_test': X_test,
            'y_test': y_test,
            'models': self.models,
            'best_model': self.best_model,
            'best_model_name': self.best_model_name,
            'metrics': {
                'logistic_regression': lr_metrics,
                'xgboost': xgb_metrics
            }
        }
    
    def save_models(self, output_dir='ml'):
        """Save trained models"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save all models
        for model_name, model in self.models.items():
            model_path = os.path.join(output_dir, f'{model_name}.pkl')
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            print(f"Saved {model_name} to {model_path}")
        
        # Save best model as model.pkl
        best_model_path = os.path.join(output_dir, 'model.pkl')
        with open(best_model_path, 'wb') as f:
            pickle.dump(self.best_model, f)
        print(f"Saved best model to {best_model_path}")
        
        # Save preprocessor
        if self.preprocessor:
            self.preprocessor.save(os.path.join(output_dir, 'preprocessor.pkl'))
        
        # Save feature names
        feature_names_path = os.path.join(output_dir, 'feature_names.pkl')
        with open(feature_names_path, 'wb') as f:
            pickle.dump(self.feature_names, f)
        print(f"Saved feature names to {feature_names_path}")

if __name__ == '__main__':
    trainer = ModelTrainer()
    results = trainer.train_all_models()
    trainer.save_models()
    
    print("\nTraining completed successfully!")

