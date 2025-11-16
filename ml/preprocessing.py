"""
Data preprocessing pipeline for credit dataset
Handles cleaning, feature engineering, and preparation for ML models
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import pickle
import os

class CreditDataPreprocessor:
    def __init__(self, data_path='data/credit_dataset.csv.xls'):
        self.data_path = data_path
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = None
        
    def load_data(self):
        """Load the credit dataset"""
        try:
            # Try reading as Excel first
            if self.data_path.endswith('.xls') or self.data_path.endswith('.xlsx'):
                df = pd.read_excel(self.data_path)
            else:
                df = pd.read_csv(self.data_path)
            
            print(f"Loaded dataset with shape: {df.shape}")
            print(f"Columns: {df.columns.tolist()}")
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            # Create synthetic dataset if file can't be read
            return self._create_synthetic_dataset()
    
    def _create_synthetic_dataset(self):
        """Create synthetic credit dataset if file cannot be loaded"""
        np.random.seed(42)
        n_samples = 1000
        
        data = {
            'age': np.random.randint(18, 70, n_samples),
            'income': np.random.randint(20000, 200000, n_samples),
            'credit_score': np.random.randint(300, 850, n_samples),
            'loan_amount': np.random.randint(10000, 500000, n_samples),
            'employment_years': np.random.randint(0, 30, n_samples),
            'debt_to_income': np.random.uniform(0.1, 0.8, n_samples),
            'credit_history_length': np.random.randint(0, 20, n_samples),
            'number_of_accounts': np.random.randint(1, 10, n_samples),
            'defaults': np.random.randint(0, 3, n_samples),
            'loan_approved': np.random.choice([0, 1], n_samples, p=[0.3, 0.7])
        }
        
        return pd.DataFrame(data)
    
    def clean_data(self, df):
        """Clean and handle missing values"""
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().sum() > 0:
                df[col].fillna(df[col].median(), inplace=True)
        
        # Handle categorical columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if df[col].isnull().sum() > 0:
                df[col].fillna(df[col].mode()[0] if len(df[col].mode()) > 0 else 'Unknown', inplace=True)
        
        return df
    
    def engineer_features(self, df):
        """Create additional features"""
        # Ensure we have numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Create derived features if base columns exist
        if 'age' in df.columns and 'income' in df.columns:
            df['age_income_ratio'] = df['age'] / (df['income'] + 1)
        
        if 'loan_amount' in df.columns and 'income' in df.columns:
            df['loan_to_income'] = df['loan_amount'] / (df['income'] + 1)
        
        if 'credit_score' in df.columns:
            df['credit_score_category'] = pd.cut(
                df['credit_score'], 
                bins=[0, 580, 670, 740, 850],
                labels=['Poor', 'Fair', 'Good', 'Excellent']
            )
        
        return df
    
    def encode_categorical(self, df):
        """Encode categorical variables"""
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        for col in categorical_cols:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                df[col] = self.label_encoders[col].fit_transform(df[col].astype(str))
            else:
                # Handle unseen categories
                df[col] = df[col].astype(str)
                known_classes = set(self.label_encoders[col].classes_)
                df[col] = df[col].apply(lambda x: x if x in known_classes else 'Unknown')
                # Add Unknown if not in classes
                if 'Unknown' not in self.label_encoders[col].classes_:
                    self.label_encoders[col].classes_ = np.append(self.label_encoders[col].classes_, 'Unknown')
                df[col] = self.label_encoders[col].transform(df[col])
        
        return df
    
    def prepare_features(self, df, target_col='loan_approved'):
        """Prepare features and target"""
        # Identify target column
        if target_col not in df.columns:
            # Try to find a similar column
            possible_targets = [col for col in df.columns if 'approv' in col.lower() or 'target' in col.lower() or 'label' in col.lower()]
            if possible_targets:
                target_col = possible_targets[0]
            else:
                # Use last column as target
                target_col = df.columns[-1]
        
        # Separate features and target
        X = df.drop(columns=[target_col], errors='ignore')
        y = df[target_col] if target_col in df.columns else np.random.choice([0, 1], len(df))
        
        # Ensure all features are numeric
        X = self.encode_categorical(X)
        
        # Store feature names
        self.feature_names = X.columns.tolist()
        
        return X, y
    
    def scale_features(self, X_train, X_test=None):
        """Scale features using StandardScaler"""
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_train_df = pd.DataFrame(X_train_scaled, columns=self.feature_names, index=X_train.index)
        
        if X_test is not None:
            X_test_scaled = self.scaler.transform(X_test)
            X_test_df = pd.DataFrame(X_test_scaled, columns=self.feature_names, index=X_test.index)
            return X_train_df, X_test_df
        
        return X_train_df
    
    def process(self, test_size=0.2, random_state=42):
        """Complete preprocessing pipeline"""
        # Load data
        df = self.load_data()
        
        # Clean data
        df = self.clean_data(df)
        
        # Engineer features
        df = self.engineer_features(df)
        
        # Prepare features and target
        X, y = self.prepare_features(df)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y if len(y.unique()) > 1 else None
        )
        
        # Scale features
        X_train_scaled, X_test_scaled = self.scale_features(X_train, X_test)
        
        return {
            'X_train': X_train_scaled,
            'X_test': X_test_scaled,
            'y_train': y_train,
            'y_test': y_test,
            'feature_names': self.feature_names,
            'preprocessor': self
        }
    
    def save(self, filepath='ml/preprocessor.pkl'):
        """Save preprocessor"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump({
                'scaler': self.scaler,
                'label_encoders': self.label_encoders,
                'feature_names': self.feature_names
            }, f)
    
    @classmethod
    def load(cls, filepath='ml/preprocessor.pkl'):
        """Load preprocessor"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        preprocessor = cls()
        preprocessor.scaler = data['scaler']
        preprocessor.label_encoders = data['label_encoders']
        preprocessor.feature_names = data['feature_names']
        return preprocessor

if __name__ == '__main__':
    preprocessor = CreditDataPreprocessor()
    processed_data = preprocessor.process()
    preprocessor.save()
    
    print(f"Training set shape: {processed_data['X_train'].shape}")
    print(f"Test set shape: {processed_data['X_test'].shape}")
    print(f"Features: {processed_data['feature_names']}")

