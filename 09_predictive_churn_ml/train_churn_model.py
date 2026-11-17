import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
    precision_score,
    recall_score,
    f1_score
)

# Ensure chart directory exists
os.makedirs("09_predictive_churn_ml/charts", exist_ok=True)
np.random.seed(42)

print("=" * 80)
print("WEEK 2: MACHINE LEARNING FOR DATA ANALYSTS")
print("Project: Predictive Customer Churn & Retention Modeling")
print("=" * 80)

# -------------------------------------------------------------
# 1. Feature Engineering & Dataset Construction
# -------------------------------------------------------------
# We simulate a rich customer behavioral dataset of 1,000 customers
N_customers = 1000

# Behavioral Features:
# - recency_days: 1 to 180 days
# - total_orders: 1 to 25 orders
# - lifetime_spend: $100 to $15,000
# - avg_discount: 0% to 30%
# - return_rate: 0% to 25%
# - days_since_signup: 30 to 730 days

recency = np.random.exponential(scale=35, size=N_customers) + 1
recency = np.clip(recency, 1, 180)

orders_count = np.random.poisson(lam=5, size=N_customers) + 1
lifetime_spend = orders_count * np.random.normal(loc=350, scale=80, size=N_customers)
lifetime_spend = np.clip(lifetime_spend, 50, 20000)

avg_discount = np.random.beta(a=2, b=10, size=N_customers) * 0.35
return_rate = np.random.beta(a=1, b=15, size=N_customers) * 0.25
days_active = np.random.randint(60, 730, size=N_customers)

# True underlying churn probability function
# High recency (inactivity) + high return rate + low orders -> high churn
log_odds = (
    -2.2
    + 0.045 * recency
    - 0.35 * orders_count
    - 0.00015 * lifetime_spend
    + 4.5 * return_rate
    + 2.8 * avg_discount
)
churn_prob = 1 / (1 + np.exp(-log_odds))
churn_label = np.random.binomial(1, churn_prob)

df_churn = pd.DataFrame({
    "Customer_ID": [f"CUST-{20000 + i}" for i in range(N_customers)],
    "Recency_Days": np.round(recency, 1),
    "Total_Orders": orders_count,
    "Lifetime_Spend": np.round(lifetime_spend, 2),
    "Avg_Discount_Rate": np.round(avg_discount, 3),
    "Return_Rate": np.round(return_rate, 3),
    "Days_Active": days_active,
    "Churned": churn_label
})

dataset_path = "09_predictive_churn_ml/customer_churn_dataset.csv"
df_churn.to_csv(dataset_path, index=False)
print(f"Generated {len(df_churn)} customer profiles in {dataset_path}.")
print(f"Overall Churn Rate: {df_churn['Churned'].mean() * 100:.2f}% ({df_churn['Churned'].sum()} churned customers)\n")

# -------------------------------------------------------------
# 2. Train / Test Split & Normalization
# -------------------------------------------------------------
feature_cols = ["Recency_Days", "Total_Orders", "Lifetime_Spend", "Avg_Discount_Rate", "Return_Rate", "Days_Active"]
X = df_churn[feature_cols]
y = df_churn["Churned"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
print(f"Training Set: {X_train.shape[0]} rows | Test Set: {X_test.shape[0]} rows")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# -------------------------------------------------------------
# 3. Model 1: Logistic Regression (Interpretable Linear Baseline)
# -------------------------------------------------------------
lr_model = LogisticRegression(random_state=42)
lr_model.fit(X_train_scaled, y_train)

y_pred_lr = lr_model.predict(X_test_scaled)
y_prob_lr = lr_model.predict_proba(X_test_scaled)[:, 1]
roc_auc_lr = roc_auc_score(y_test, y_prob_lr)

print("\n--- MODEL 1: LOGISTIC REGRESSION EVALUATION ---")
print(f"ROC-AUC Score: {roc_auc_lr:.4f}")
print(classification_report(y_test, y_pred_lr, target_names=["Retained", "Churned"]))

# Feature Importance from Logistic Regression Odds Coefficients
odds_ratios = pd.DataFrame({
    "Feature": feature_cols,
    "Coefficient": lr_model.coef_[0],
    "Odds_Ratio": np.exp(lr_model.coef_[0])
}).sort_values(by="Odds_Ratio", ascending=False)
print("Logistic Regression Feature Impact (Odds Ratios):")
print(odds_ratios.to_string(index=False))

# -------------------------------------------------------------
# 4. Model 2: Random Forest Classifier
# -------------------------------------------------------------
rf_model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
rf_model.fit(X_train, y_train)

y_pred_rf = rf_model.predict(X_test)
y_prob_rf = rf_model.predict_proba(X_test)[:, 1]
roc_auc_rf = roc_auc_score(y_test, y_prob_rf)

print("\n--- MODEL 2: RANDOM FOREST EVALUATION ---")
print(f"ROC-AUC Score: {roc_auc_rf:.4f}")
print(classification_report(y_test, y_pred_rf, target_names=["Retained", "Churned"]))

# -------------------------------------------------------------
# 5. Visualizations: Confusion Matrix & ROC Curve
# -------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Confusion Matrix for Random Forest
cm = confusion_matrix(y_test, y_pred_rf)
axes[0].imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
axes[0].set_title(f'Random Forest Confusion Matrix\n(Accuracy: {(cm[0,0]+cm[1,1])/cm.sum()*100:.1f}%)', fontsize=12, fontweight='bold')
tick_marks = np.arange(2)
axes[0].set_xticks(tick_marks)
axes[0].set_xticklabels(['Retained (0)', 'Churned (1)'])
axes[0].set_yticks(tick_marks)
axes[0].set_yticklabels(['Retained (0)', 'Churned (1)'])
thresh = cm.max() / 2.
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        axes[0].text(j, i, format(cm[i, j], 'd'),
                     ha="center", va="center",
                     color="white" if cm[i, j] > thresh else "black",
                     fontweight='bold', fontsize=13)
axes[0].set_ylabel('True Label')
axes[0].set_xlabel('Predicted Label')

# Plot 2: ROC Curve Comparison
fpr_lr, tpr_lr, _ = roc_curve(y_test, y_prob_lr)
fpr_rf, tpr_rf, _ = roc_curve(y_test, y_prob_rf)

axes[1].plot(fpr_rf, tpr_rf, color='#1E40AF', lw=2.5, label=f'Random Forest (AUC = {roc_auc_rf:.3f})')
axes[1].plot(fpr_lr, tpr_lr, color='#059669', lw=2, linestyle='--', label=f'Logistic Regression (AUC = {roc_auc_lr:.3f})')
axes[1].plot([0, 1], [0, 1], color='#94A3B8', lw=1.5, linestyle=':')
axes[1].set_xlim([0.0, 1.0])
axes[1].set_ylim([0.0, 1.05])
axes[1].set_xlabel('False Positive Rate (1 - Specificity)')
axes[1].set_ylabel('True Positive Rate (Recall / Sensitivity)')
axes[1].set_title('Receiver Operating Characteristic (ROC) Curve', fontsize=12, fontweight='bold')
axes[1].legend(loc="lower right", frameon=True, facecolor='white')
axes[1].grid(True, linestyle=':', alpha=0.6)

plt.tight_layout()
chart_path = "09_predictive_churn_ml/charts/churn_model_evaluation.png"
fig.savefig(chart_path, dpi=300)
plt.close(fig)
print(f"\nSaved model evaluation charts to {chart_path}")

print("\n" + "=" * 80)
print("CHURN MODEL TRAINING COMPLETE: Both Logistic Regression and Random Forest deployed!")
print("=" * 80)

