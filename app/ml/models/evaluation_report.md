# Model Evaluation & Comparison Report

This report presents the comparative metrics of all trained baseline models.

## 1. Suitability Score Regressors (Site Scoring)

| Model | MAE | RMSE | R² Score | Train Time (s) |
|---|---|---|---|---|
| Linear Regression | 2.7289 | 3.3436 | 0.915 | 0.017 |
| Decision Tree Regressor | 3.8237 | 4.8325 | 0.8225 | 0.0305 |
| Random Forest Regressor | 2.3063 | 2.8837 | 0.9368 | 2.1508 |
| Gradient Boosting Regressor | 1.3261 | 1.6952 | 0.9782 | 1.2443 |

## 2. Deployment Classifiers (Technology Recommendation)

| Model | Accuracy | Precision | Recall | F1-Score | Train Time (s) |
|---|---|---|---|---|---|
| Logistic Regression | 0.4775 | 0.3622 | 0.3497 | 0.3516 | 1.6699 |
| Decision Tree Classifier | 1.0 | 1.0 | 1.0 | 1.0 | 0.01 |
| Random Forest Classifier | 1.0 | 1.0 | 1.0 | 1.0 | 0.7383 |
| Gradient Boosting Classifier | 1.0 | 1.0 | 1.0 | 1.0 | 4.3176 |

## 3. Best Model Selection & Justification

### Selected Regressor: **Gradient Boosting Regressor**
- **R² Score**: 0.9782
- **Justification**: Exhibits highest variance explanation and lowest predictions error. Highly stable ensemble.

### Selected Classifier: **Decision Tree Classifier**
- **F1-Score**: 1.0000
- **Justification**: High accuracy and precision-recall trade-offs. Adapts to non-linear class distributions perfectly.
