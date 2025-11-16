"""
Synthetic bias generation using bias_groups_config.json
Adds protected attributes and injects bias for fairness testing
"""

import pandas as pd
import numpy as np
import json
import os

class SyntheticBiasGenerator:
    def __init__(self, config_path='configs/bias_groups_config.json'):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self):
        """Load bias groups configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {
                "protected_attributes": {
                    "gender": ["male", "female"],
                    "region": ["urban", "rural"],
                    "age_group": ["18-25", "26-40", "40+"]
                }
            }
    
    def add_protected_attributes(self, df):
        """Add synthetic protected attributes to dataset"""
        np.random.seed(42)
        n_samples = len(df)
        
        # Add gender attribute
        if 'gender' not in df.columns:
            # Bias: females slightly lower approval rate
            gender = np.random.choice(['male', 'female'], n_samples, p=[0.5, 0.5])
            df['gender'] = gender
        
        # Add region attribute
        if 'region' not in df.columns:
            # Bias: rural areas slightly lower approval rate
            region = np.random.choice(['urban', 'rural'], n_samples, p=[0.6, 0.4])
            df['region'] = region
        
        # Add age_group attribute
        if 'age_group' not in df.columns and 'age' in df.columns:
            df['age_group'] = pd.cut(
                df['age'],
                bins=[0, 25, 40, 100],
                labels=['18-25', '26-40', '40+']
            ).astype(str)
        elif 'age_group' not in df.columns:
            age_group = np.random.choice(['18-25', '26-40', '40+'], n_samples, p=[0.2, 0.5, 0.3])
            df['age_group'] = age_group
        
        return df
    
    def inject_bias(self, df, target_col='loan_approved'):
        """Inject bias into loan approval decisions"""
        np.random.seed(42)
        
        # Ensure target column exists
        if target_col not in df.columns:
            df[target_col] = np.random.choice([0, 1], len(df), p=[0.3, 0.7])
        
        # Inject gender bias: females have 10% lower approval rate
        if 'gender' in df.columns:
            female_mask = df['gender'] == 'female'
            original_approval = df[target_col].copy()
            
            # Reduce approval probability for females
            female_indices = df[female_mask].index
            for idx in female_indices:
                if df.loc[idx, target_col] == 1:
                    # 15% chance of flipping approval to rejection
                    if np.random.random() < 0.15:
                        df.loc[idx, target_col] = 0
        
        # Inject region bias: rural areas have 8% lower approval rate
        if 'region' in df.columns:
            rural_mask = df['region'] == 'rural'
            rural_indices = df[rural_mask].index
            for idx in rural_indices:
                if df.loc[idx, target_col] == 1:
                    # 12% chance of flipping approval to rejection
                    if np.random.random() < 0.12:
                        df.loc[idx, target_col] = 0
        
        # Inject age bias: 18-25 age group has 5% lower approval rate
        if 'age_group' in df.columns:
            young_mask = df['age_group'] == '18-25'
            young_indices = df[young_mask].index
            for idx in young_indices:
                if df.loc[idx, target_col] == 1:
                    # 8% chance of flipping approval to rejection
                    if np.random.random() < 0.08:
                        df.loc[idx, target_col] = 0
        
        return df
    
    def generate_synthetic_dataset(self, base_df):
        """Generate complete synthetic dataset with bias"""
        # Add protected attributes
        df_with_attributes = self.add_protected_attributes(base_df.copy())
        
        # Inject bias
        df_with_bias = self.inject_bias(df_with_attributes)
        
        return df_with_bias
    
    def get_protected_attributes(self):
        """Get list of protected attributes from config"""
        return list(self.config.get('protected_attributes', {}).keys())
    
    def get_attribute_values(self, attribute):
        """Get possible values for a protected attribute"""
        return self.config.get('protected_attributes', {}).get(attribute, [])

if __name__ == '__main__':
    # Test synthetic data generation
    generator = SyntheticBiasGenerator()
    
    # Create sample dataframe
    np.random.seed(42)
    sample_df = pd.DataFrame({
        'age': np.random.randint(18, 70, 1000),
        'income': np.random.randint(20000, 200000, 1000),
        'credit_score': np.random.randint(300, 850, 1000),
        'loan_amount': np.random.randint(10000, 500000, 1000),
    })
    
    # Generate synthetic dataset with bias
    synthetic_df = generator.generate_synthetic_dataset(sample_df)
    
    print("Synthetic dataset generated:")
    print(synthetic_df.head())
    print(f"\nProtected attributes: {generator.get_protected_attributes()}")
    print(f"\nGender distribution:\n{synthetic_df['gender'].value_counts()}")
    print(f"\nRegion distribution:\n{synthetic_df['region'].value_counts()}")
    print(f"\nAge group distribution:\n{synthetic_df['age_group'].value_counts()}")

