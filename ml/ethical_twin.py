"""
Ethical Twin: Interpretable surrogate model (Decision Tree)
Provides human-readable explanations for black-box models
"""

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree
import pickle
import os
import matplotlib.pyplot as plt

class EthicalTwin:
    def __init__(self, max_depth=5, min_samples_split=20, min_samples_leaf=10):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.model = DecisionTreeClassifier(
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=42
        )
        self.feature_names = None
        
    def train(self, X_train, y_train, feature_names=None):
        """Train ethical twin surrogate model"""
        self.feature_names = feature_names
        self.model.fit(X_train, y_train)
        return self.model
    
    def predict(self, X):
        """Make predictions using ethical twin"""
        return self.model.predict(X)
    
    def predict_proba(self, X):
        """Get prediction probabilities"""
        return self.model.predict_proba(X)
    
    def explain_decision(self, instance, feature_names=None):
        """Explain a single decision using tree path"""
        if feature_names is None:
            feature_names = self.feature_names or [f'feature_{i}' for i in range(len(instance))]
        
        # Get decision path
        decision_path = self.model.decision_path([instance])
        node_indicator = decision_path.toarray()[0]
        
        # Get leaf node
        leaf_id = self.model.apply([instance])[0]
        
        # Get path to leaf
        path_nodes = []
        for node_id in range(decision_path.shape[1]):
            if node_indicator[node_id] == 1:
                path_nodes.append(node_id)
        
        # Extract rules
        rules = []
        tree = self.model.tree_
        
        for node_id in path_nodes[:-1]:  # Exclude leaf node
            feature_idx = tree.feature[node_id]
            threshold = tree.threshold[node_id]
            
            if feature_idx >= 0 and feature_idx < len(feature_names):
                feature_name = feature_names[feature_idx]
                feature_value = instance[feature_idx]
                
                if feature_value <= threshold:
                    rules.append(f"{feature_name} <= {threshold:.2f} (actual: {feature_value:.2f})")
                else:
                    rules.append(f"{feature_name} > {threshold:.2f} (actual: {feature_value:.2f})")
        
        # Get prediction
        prediction = self.model.predict([instance])[0]
        proba = self.model.predict_proba([instance])[0]
        
        return {
            'prediction': int(prediction),
            'probability': float(proba[1] if len(proba) > 1 else proba[0]),
            'rules': rules,
            'leaf_node': int(leaf_id)
        }
    
    def get_global_explanation(self, feature_names=None):
        """Get global explanation of the model"""
        if feature_names is None:
            feature_names = self.feature_names or [f'feature_{i}' for i in range(self.model.n_features_in_)]
        
        # Get feature importances
        importances = self.model.feature_importances_
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        # Get tree structure as text
        tree_rules = export_text(
            self.model,
            feature_names=feature_names,
            max_depth=self.max_depth
        )
        
        return {
            'feature_importances': importance_df.to_dict('records'),
            'tree_rules': tree_rules,
            'max_depth': self.max_depth,
            'n_nodes': self.model.tree_.node_count
        }
    
    def visualize_tree(self, feature_names=None, output_path='docs/ethical_twin_tree.png'):
        """Visualize decision tree"""
        if feature_names is None:
            feature_names = self.feature_names or [f'feature_{i}' for i in range(self.model.n_features_in_)]
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        plt.figure(figsize=(20, 10))
        plot_tree(
            self.model,
            feature_names=feature_names,
            filled=True,
            rounded=True,
            fontsize=10
        )
        plt.title('Ethical Twin Decision Tree', fontsize=16)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Tree visualization saved to {output_path}")
    
    def save(self, filepath='ml/ethical_twin.pkl'):
        """Save ethical twin model"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'feature_names': self.feature_names,
                'max_depth': self.max_depth
            }, f)
    
    @classmethod
    def load(cls, filepath='ml/ethical_twin.pkl'):
        """Load ethical twin model"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        twin = cls(max_depth=data['max_depth'])
        twin.model = data['model']
        twin.feature_names = data['feature_names']
        return twin

def train_ethical_twin(black_box_model, X_train, y_train, feature_names=None, max_depth=5):
    """Train ethical twin to mimic black box model"""
    # Get predictions from black box model
    if hasattr(black_box_model, 'predict_proba'):
        y_surrogate = black_box_model.predict(X_train)
    else:
        y_surrogate = black_box_model.predict(X_train)
    
    # Train ethical twin
    twin = EthicalTwin(max_depth=max_depth)
    twin.train(X_train, y_surrogate, feature_names)
    
    return twin

if __name__ == '__main__':
    # Test ethical twin
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import make_classification
    
    # Create sample data
    X, y = make_classification(n_samples=200, n_features=5, random_state=42)
    feature_names = [f'feature_{i}' for i in range(5)]
    
    # Train black box model
    black_box = RandomForestClassifier(n_estimators=10, random_state=42)
    black_box.fit(X, y)
    
    # Train ethical twin
    twin = train_ethical_twin(black_box, X, y, feature_names, max_depth=3)
    
    # Explain a decision
    explanation = twin.explain_decision(X[0], feature_names)
    print("Decision Explanation:")
    print(explanation)
    
    # Get global explanation
    global_exp = twin.get_global_explanation(feature_names)
    print("\nFeature Importances:")
    for item in global_exp['feature_importances'][:3]:
        print(f"  {item['feature']}: {item['importance']:.4f}")

