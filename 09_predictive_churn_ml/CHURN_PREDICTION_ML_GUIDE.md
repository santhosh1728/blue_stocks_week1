# Machine Learning for Data Analysts: Customer Churn Prediction Guide (Week 2)

Welcome to the **Machine Learning for Data Analysts Guide**. In modern business organizations, the boundary between a senior data analyst and a data scientist centers on predictive modeling—specifically, moving from **Descriptive Analytics** ("What happened?") to **Predictive Analytics** ("What will happen next?").

This project demonstrates an end-to-end customer churn prediction engine using both linear models (Logistic Regression) and non-linear ensemble models (Random Forest).

---

## Table of Contents
1. [The Business Problem: Customer Churn & Retention](#1-the-business-problem)
2. [Feature Engineering from Transaction Data](#2-feature-engineering)
3. [Logistic Regression vs Random Forest](#3-logistic-regression-vs-random-forest)
4. [Evaluating Classification Models](#4-evaluating-classification-models)
5. [The Precision vs Recall Business Trade-off](#5-precision-vs-recall-trade-off)
6. [Operationalizing ML: Churn Scoring in Production](#6-operationalizing-ml)

---

## 1. The Business Problem: Customer Churn & Retention

Customer churn occurs when a customer stops doing business with a company.
- **Economic Reality:** Acquiring a new customer costs **5x to 7x more** than retaining an existing customer.
- **Goal:** Identify high-risk customers 30 to 60 days *before* they churn, allowing marketing to trigger proactive retention offers (e.g., dedicated discount, account manager call).

---

## 2. Feature Engineering from Transaction Data

Predictive power comes from behavioral features aggregated at the customer level:
1. **Recency ($R$):** Days elapsed since the customer's last purchase.
2. **Frequency ($F$):** Total orders placed.
3. **Monetary ($M$):** Total dollars spent.
4. **Return Rate:** Percentage of orders refunded or cancelled (friction signal).
5. **Discount Sensitivity:** Average discount applied to purchases.
6. **Account Tenure (`Days_Active`):** Days since first registration.

---

## 3. Logistic Regression vs Random Forest

| Property | Logistic Regression | Random Forest |
| :--- | :--- | :--- |
| **Model Type** | Generalized Linear Model | Ensemble of Decision Trees (Bagging) |
| **Interpretability** | **High** (Coefficients translate directly to Odds Ratios) | Moderate (Feature importance plots) |
| **Non-linear Relationships** | Struggles without manual polynomial interaction terms | **Captures non-linearities and threshold interactions natively** |
| **Data Scaling** | **Requires scaling** (`StandardScaler`) | Immune to feature scale |
| **Best Used When** | Presenting to executives who demand clear causal coefficients | Maximum predictive accuracy is needed |

---

## 4. Evaluating Classification Models

Accuracy is a deceptive metric on imbalanced datasets! If 90% of customers don't churn, a naive model that predicts "Nobody churns" achieves 90% accuracy while failing 100% of the business objective.

### Key Metrics
- **Confusion Matrix:**
  - **True Positives (TP):** Churned customers correctly identified.
  - **False Positives (FP):** Retained customers wrongly flagged as churners (wasted promotional cost).
  - **False Negatives (FN):** Churned customers missed by the model (lost revenue).
- **Precision:** $\frac{TP}{TP + FP}$ — When the model says a customer will churn, how often is it right?
- **Recall (Sensitivity):** $\frac{TP}{TP + FN}$ — What percentage of all actual churners did the model catch?
- **F1-Score:** Harmonic mean of Precision and Recall.
- **ROC-AUC (Receiver Operating Characteristic - Area Under Curve):**
  Measures the model's ability to rank order high-risk users above low-risk users across all classification thresholds ($0.50 = \text{Random Guessing}, 1.00 = \text{Perfect}$).
  Our models achieve **AUC > 0.85**, indicating strong discriminatory power.

---

## 5. The Precision vs Recall Business Trade-off

Setting the probability threshold depends on the **cost of intervention**:
- **Scenario A (Expensive Intervention):** Calling each flagged customer with a \$100 gift card. You want **High Precision** ($>80\%$) to avoid handing out expensive cards to customers who had no intention of leaving.
- **Scenario B (Cheap Intervention):** Sending an automated personalized email reminder. You want **High Recall** ($>90\%$) because sending an extra email has virtually zero marginal cost, and missing a churner is far more costly.

---

## 6. Operationalizing ML: Churn Scoring in Production

1. **Daily Scoring Job:** A Python script runs nightly, pulls updated transaction records, calculates feature vectors, and computes `churn_probability` for all active accounts.
2. **CRM Integration:** Customers with `churn_probability >= 0.70` are tagged `At Risk` in Salesforce / HubSpot for immediate account team outreach.

