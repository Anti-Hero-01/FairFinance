"""
Fairness metrics computation using Fairlearn/AIF360
Generates comprehensive fairness report
"""

import pandas as pd
import numpy as np
import json
import os
from sklearn.metrics import confusion_matrix

class FairnessPipeline:
    def __init__(self, config_path='configs/bias_groups_config.json'):
        self.config_path = config_path
        self.config = self._load_config()
        self.protected_attributes = self.config.get('protected_attributes', {})
        self.thresholds = self.config.get('thresholds', {})
    
    def _load_config(self):
        """Load bias groups configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def compute_confusion_matrix_metrics(self, y_true, y_pred, group_mask):
        """Compute confusion matrix metrics for a group"""
        group_y_true = y_true[group_mask]
        group_y_pred = y_pred[group_mask]
        
        if len(group_y_true) == 0:
            return {
                'tp': 0, 'tn': 0, 'fp': 0, 'fn': 0,
                'tpr': 0, 'tnr': 0, 'fpr': 0, 'fnr': 0
            }
        
        tn, fp, fn, tp = confusion_matrix(group_y_true, group_y_pred).ravel()
        
        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0  # True Positive Rate (Recall)
        tnr = tn / (tn + fp) if (tn + fp) > 0 else 0  # True Negative Rate
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0  # False Positive Rate
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0  # False Negative Rate
        
        return {
            'tp': int(tp), 'tn': int(tn), 'fp': int(fp), 'fn': int(fn),
            'tpr': tpr, 'tnr': tnr, 'fpr': fpr, 'fnr': fnr
        }
    
    def demographic_parity_difference(self, y_pred, protected_attr, groups):
        """Compute demographic parity difference"""
        metrics = {}
        approval_rates = {}
        
        for group in groups:
            group_mask = protected_attr == group
            if group_mask.sum() > 0:
                approval_rate = y_pred[group_mask].mean()
                approval_rates[group] = approval_rate
        
        if len(approval_rates) >= 2:
            rates = list(approval_rates.values())
            dp_diff = max(rates) - min(rates)
            metrics['demographic_parity_difference'] = dp_diff
            metrics['approval_rates'] = approval_rates
        
        return metrics
    
    def equal_opportunity_difference(self, y_true, y_pred, protected_attr, groups):
        """Compute equal opportunity difference (TPR difference)"""
        metrics = {}
        tprs = {}
        
        for group in groups:
            group_mask = protected_attr == group
            group_metrics = self.compute_confusion_matrix_metrics(y_true, y_pred, group_mask)
            tprs[group] = group_metrics['tpr']
        
        if len(tprs) >= 2:
            tpr_values = list(tprs.values())
            eod = max(tpr_values) - min(tpr_values)
            metrics['equal_opportunity_difference'] = eod
            metrics['true_positive_rates'] = tprs
        
        return metrics
    
    def disparate_impact_ratio(self, y_pred, protected_attr, groups):
        """Compute disparate impact ratio"""
        metrics = {}
        approval_rates = {}
        
        for group in groups:
            group_mask = protected_attr == group
            if group_mask.sum() > 0:
                approval_rate = y_pred[group_mask].mean()
                approval_rates[group] = approval_rate
        
        if len(approval_rates) >= 2:
            rates = list(approval_rates.values())
            min_rate = min(rates)
            max_rate = max(rates)
            dir_value = min_rate / max_rate if max_rate > 0 else 0
            metrics['disparate_impact_ratio'] = dir_value
            metrics['approval_rates'] = approval_rates
        
        return metrics
    
    def compute_fairness_metrics(self, y_true, y_pred, df, protected_attr_name):
        """Compute all fairness metrics for a protected attribute"""
        if protected_attr_name not in df.columns:
            return {}
        
        protected_attr = df[protected_attr_name]
        groups = self.protected_attributes.get(protected_attr_name, [])
        
        if len(groups) == 0:
            groups = protected_attr.unique().tolist()
        
        metrics = {}
        
        # Demographic Parity
        dp_metrics = self.demographic_parity_difference(y_pred, protected_attr, groups)
        metrics.update(dp_metrics)
        
        # Equal Opportunity
        eod_metrics = self.equal_opportunity_difference(y_true, y_pred, protected_attr, groups)
        metrics.update(eod_metrics)
        
        # Disparate Impact
        dir_metrics = self.disparate_impact_ratio(y_pred, protected_attr, groups)
        metrics.update(dir_metrics)
        
        # Group-wise confusion matrix metrics
        group_metrics = {}
        for group in groups:
            group_mask = protected_attr == group
            group_metrics[group] = self.compute_confusion_matrix_metrics(y_true, y_pred, group_mask)
        metrics['group_metrics'] = group_metrics
        
        return metrics
    
    def compute_all_fairness_metrics(self, y_true, y_pred, df):
        """Compute fairness metrics for all protected attributes"""
        all_metrics = {}
        
        for attr_name in self.protected_attributes.keys():
            if attr_name in df.columns:
                attr_metrics = self.compute_fairness_metrics(y_true, y_pred, df, attr_name)
                all_metrics[attr_name] = attr_metrics
        
        return all_metrics
    
    def check_fairness_thresholds(self, metrics):
        """Check if metrics violate fairness thresholds"""
        violations = []
        
        for attr_name, attr_metrics in metrics.items():
            # Check demographic parity
            if 'demographic_parity_difference' in attr_metrics:
                threshold = self.thresholds.get('demographic_parity_difference', 0.1)
                if attr_metrics['demographic_parity_difference'] > threshold:
                    violations.append({
                        'attribute': attr_name,
                        'metric': 'demographic_parity_difference',
                        'value': attr_metrics['demographic_parity_difference'],
                        'threshold': threshold
                    })
            
            # Check equal opportunity
            if 'equal_opportunity_difference' in attr_metrics:
                threshold = self.thresholds.get('equal_opportunity_difference', 0.1)
                if attr_metrics['equal_opportunity_difference'] > threshold:
                    violations.append({
                        'attribute': attr_name,
                        'metric': 'equal_opportunity_difference',
                        'value': attr_metrics['equal_opportunity_difference'],
                        'threshold': threshold
                    })
            
            # Check disparate impact
            if 'disparate_impact_ratio' in attr_metrics:
                threshold = self.thresholds.get('disparate_impact_ratio', 0.8)
                if attr_metrics['disparate_impact_ratio'] < threshold:
                    violations.append({
                        'attribute': attr_name,
                        'metric': 'disparate_impact_ratio',
                        'value': attr_metrics['disparate_impact_ratio'],
                        'threshold': threshold
                    })
        
        return violations
    
    def generate_fairness_report(self, y_true, y_pred, df, output_path='docs/fairness_report.md'):
        """Generate comprehensive fairness report"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Compute all metrics
        all_metrics = self.compute_all_fairness_metrics(y_true, y_pred, df)
        
        # Check violations
        violations = self.check_fairness_thresholds(all_metrics)
        
        # Generate report
        report_lines = [
            "# Fairness Report",
            "\n## Executive Summary",
            f"\nThis report analyzes fairness metrics across {len(self.protected_attributes)} protected attributes.",
            f"Total violations detected: {len(violations)}",
            "\n## Protected Attributes",
            ""
        ]
        
        for attr_name in self.protected_attributes.keys():
            report_lines.append(f"\n### {attr_name.capitalize()}")
            if attr_name in all_metrics:
                attr_metrics = all_metrics[attr_name]
                
                if 'demographic_parity_difference' in attr_metrics:
                    dpd = attr_metrics['demographic_parity_difference']
                    threshold = self.thresholds.get('demographic_parity_difference', 0.1)
                    status = "⚠️ VIOLATION" if dpd > threshold else "✅ PASS"
                    report_lines.append(f"\n- **Demographic Parity Difference**: {dpd:.4f} (threshold: {threshold}) {status}")
                    if 'approval_rates' in attr_metrics:
                        for group, rate in attr_metrics['approval_rates'].items():
                            report_lines.append(f"  - {group}: {rate:.4f}")
                
                if 'equal_opportunity_difference' in attr_metrics:
                    eod = attr_metrics['equal_opportunity_difference']
                    threshold = self.thresholds.get('equal_opportunity_difference', 0.1)
                    status = "⚠️ VIOLATION" if eod > threshold else "✅ PASS"
                    report_lines.append(f"\n- **Equal Opportunity Difference**: {eod:.4f} (threshold: {threshold}) {status}")
                
                if 'disparate_impact_ratio' in attr_metrics:
                    dir_val = attr_metrics['disparate_impact_ratio']
                    threshold = self.thresholds.get('disparate_impact_ratio', 0.8)
                    status = "⚠️ VIOLATION" if dir_val < threshold else "✅ PASS"
                    report_lines.append(f"\n- **Disparate Impact Ratio**: {dir_val:.4f} (threshold: {threshold}) {status}")
        
        if violations:
            report_lines.append("\n## ⚠️ Fairness Violations Detected")
            for violation in violations:
                report_lines.append(
                    f"\n- **{violation['attribute']}** - {violation['metric']}: "
                    f"{violation['value']:.4f} (exceeds threshold {violation['threshold']})"
                )
        else:
            report_lines.append("\n## ✅ No Fairness Violations Detected")
        
        report_lines.append("\n## Recommendations")
        report_lines.append("\n1. Review model training data for representation balance")
        report_lines.append("2. Consider post-processing techniques to mitigate bias")
        report_lines.append("3. Monitor fairness metrics in production")
        report_lines.append("4. Implement bias mitigation strategies if violations persist")
        
        report_content = "\n".join(report_lines)
        
        with open(output_path, 'w') as f:
            f.write(report_content)
        
        print(f"Fairness report saved to {output_path}")
        
        return {
            'metrics': all_metrics,
            'violations': violations,
            'report_path': output_path
        }

if __name__ == '__main__':
    # Test fairness pipeline
    np.random.seed(42)
    n_samples = 1000
    
    # Create synthetic data with bias
    df = pd.DataFrame({
        'gender': np.random.choice(['male', 'female'], n_samples),
        'region': np.random.choice(['urban', 'rural'], n_samples),
        'age_group': np.random.choice(['18-25', '26-40', '40+'], n_samples)
    })
    
    # Create biased predictions
    y_true = np.random.choice([0, 1], n_samples, p=[0.3, 0.7])
    y_pred = y_true.copy()
    
    # Inject bias in predictions
    female_mask = df['gender'] == 'female'
    y_pred[female_mask] = np.where(
        np.random.random(female_mask.sum()) < 0.15,
        0,
        y_pred[female_mask]
    )
    
    # Compute fairness metrics
    pipeline = FairnessPipeline()
    report = pipeline.generate_fairness_report(y_true, y_pred, df)
    
    print("\nFairness analysis completed!")

