# Statistics for Data Analysts: Complete Conceptual & Practical Guide

Welcome to the **Statistics for Data Analysts Master Guide**. This guide translates mathematical and statistical theory into daily analytical decision-making, using examples from our real-world retail dataset (`data/cleaned_sales_data.csv`).

---

## Table of Contents
1. [Measures of Central Tendency (Mean, Median, Mode)](#1-measures-of-central-tendency)
2. [Measures of Dispersion & Spread (Variance, Standard Deviation, IQR)](#2-measures-of-dispersion)
3. [Correlation vs Causation & Confounding Variables](#3-correlation-vs-causation)
4. [Probability Fundamentals & Bayes' Rule](#4-probability-fundamentals)
5. [Probability Distributions in Business](#5-probability-distributions)
6. [Hypothesis Testing & p-Values](#6-hypothesis-testing)
7. [Introduction to Linear Regression & OLS](#7-introduction-to-linear-regression)
8. [Python & SQL Statistical Implementations](#8-python--sql-statistical-implementations)

---

## 1. Measures of Central Tendency

Central tendency identifies the single central value that best summarizes an entire distribution.

### 1.1 The Three Core Measures
- **Mean ($\mu$ or $\bar{X}$):** Arithmetic average.
  $$\bar{X} = \frac{\sum_{i=1}^n X_i}{n}$$
  *Strength:* Uses every data point.  
  *Weakness:* Severely distorted by extreme outliers and skewed data.
- **Median ($M$ or $Q_2$):** The exact midpoint value when observations are sorted.
  *Strength:* **Robust against outliers**.  
  *Rule of Thumb:* Use median whenever data represents income, housing prices, transaction values, or web session durations.
- **Mode:** The most frequently occurring value in the dataset.
  *Application:* Most popular product size, most common delivery method (`"Standard Class"`).

### 1.2 Skewness & The Relationship Between Mean and Median
In our sales dataset:
- **Mean Transaction:** **\$1,459.20**
- **Median Transaction:** **\$741.00**
- **Mode Transaction:** **\$899.00** (Google Pixel 8 Pro standard order)

```
Positively Skewed Distribution (Right-Skewed):
Mode ($899)  <  Median ($741)  <  Mean ($1,459)
       ^             |                  \
     [Peak]     [50% Split]         [Pulled right by enterprise outliers]
```
> [!IMPORTANT]
> Because **Mean > Median**, the distribution has a **positive (right) skew**. Reporting only the mean would mislead management into thinking the average customer spends \$1,459, when in reality 50% of orders spend \$741 or less!

---

## 2. Measures of Dispersion

Dispersion measures how spread out the observations are around the center.

### 2.1 Variance ($\sigma^2$ or $s^2$)
The average of squared deviations from the mean:
$$s^2 = \frac{\sum_{i=1}^n (X_i - \bar{X})^2}{n - 1}$$
*(Note: We divide by $n - 1$ for sample variance to correct for Bessel's bias).*

### 2.2 Standard Deviation ($\sigma$ or $s$)
The square root of variance, returning the spread metric back into the original units of measurement (e.g., dollars):
$$s = \sqrt{s^2}$$
In our sales dataset:
$$s = \$2,064.60$$
Because the standard deviation (\$2,064) exceeds the mean (\$1,459), we have high dispersion and high revenue volatility between small retail orders and enterprise bulk orders.

### 2.3 Interquartile Range (IQR)
The distance between the 75th percentile ($Q_3$) and 25th percentile ($Q_1$):
$$\text{IQR} = Q_3 - Q_1$$
Unlike standard deviation, the IQR is **completely immune to extreme outliers**.

---

## 3. Correlation vs Causation

Correlation quantifies the strength and direction of a linear relationship between two continuous variables.

### 3.1 Pearson Correlation Coefficient ($r$)
$$r = \frac{\sum (X - \bar{X})(Y - \bar{Y})}{\sqrt{\sum (X - \bar{X})^2 \sum (Y - \bar{Y})^2}}$$
- $r = +1.0$: Perfect positive linear correlation.
- $r = 0.0$: No linear relationship.
- $r = -1.0$: Perfect negative linear correlation.

### Empirical Findings from our Dataset:
| Variable Pair | Pearson $r$ | Interpretation |
| :--- | :--- | :--- |
| **Sales Amount $\leftrightarrow$ Net Profit** | **+0.939** | Strong positive correlation (Higher volume = Higher gross profit) |
| **Discount Rate $\leftrightarrow$ Margin %** | **-0.600** | Strong negative correlation (Discounts destroy percentage profitability) |
| **Order Quantity $\leftrightarrow$ Discount Rate** | **+0.023** | Zero correlation (Discounts do not induce larger order sizes) |

### 3.2 Correlation Does NOT Imply Causation
1. **Confounding Variables (Third-Cause Fallacy):**
   - Ice cream sales and drowning rates both spike in July. Ice cream does not cause drowning; the confounding variable is **Summer Heat**.
2. **Simpson's Paradox:**
   - A trend appears in several different groups of data but disappears or reverses when the groups are aggregated. Always slice data by segments (e.g., Corporate vs Consumer) before drawing overarching conclusions.

---

## 4. Probability Fundamentals

### 4.1 Basic Definitions
- **Sample Space ($S$):** The set of all possible outcomes.
- **Event ($A$):** A subset of the sample space.
- **Probability:** $P(A) = \frac{\text{favorable outcomes}}{\text{total outcomes}}$.

### 4.2 Addition and Multiplication Rules
- **Union (OR):**
  $$P(A \cup B) = P(A) + P(B) - P(A \cap B)$$
- **Independent Multiplication (AND):**
  $$P(A \cap B) = P(A) \times P(B)$$

### 4.3 Conditional Probability & Bayes' Theorem
The probability of event $A$ occurring given that event $B$ has already occurred:
$$P(A \mid B) = \frac{P(A \cap B)}{P(B)}$$

**Bayes' Theorem Formula:**
$$P(A \mid B) = \frac{P(B \mid A) \cdot P(A)}{P(B)}$$

*Business Application:* What is the probability that a transaction will be refunded ($A$) given that it was shipped via Standard Class ($B$)?
$$P(\text{Refund} \mid \text{Standard Class}) = \frac{P(\text{Standard Class} \mid \text{Refund}) \cdot P(\text{Refund})}{P(\text{Standard Class})}$$

---

## 5. Probability Distributions in Business

### 5.1 The Normal (Gaussian) Distribution
- Symmetric, bell-shaped curve characterized by Mean ($\mu$) and Standard Deviation ($\sigma$).
- **The Empirical 68–95–99.7 Rule:**
  - $68.2\%$ of values fall within $\mu \pm 1\sigma$
  - $95.4\%$ of values fall within $\mu \pm 2\sigma$
  - $99.7\%$ of values fall within $\mu \pm 3\sigma$
- **Central Limit Theorem (CLT):**
  As sample size $n$ increases ($n \ge 30$), the sampling distribution of the sample mean approaches a Normal Distribution, **regardless** of the shape of the underlying population distribution!

### 5.2 Poisson Distribution
Models the number of discrete events occurring within a fixed interval of time:
$$P(X = k) = \frac{\lambda^k e^{-\lambda}}{k!}$$
*Use-case:* Modeling incoming customer service calls per hour or website visits per minute.

---

## 6. Hypothesis Testing & p-Values

Hypothesis testing allows data analysts to determine whether a pattern in the data is statistically significant or merely random noise.

### 6.1 The 5-Step Hypothesis Framework
1. **State the Null Hypothesis ($H_0$):** There is NO difference or NO effect.
   - Example: *"Offering a 10% discount does NOT change customer conversion rate."*
2. **State the Alternative Hypothesis ($H_1$):** There IS a significant difference.
   - Example: *"Offering a 10% discount increases customer conversion rate."*
3. **Choose Significance Level ($\alpha$):** Standard threshold is $\alpha = 0.05$ (5% risk of false positive).
4. **Calculate Test Statistic & p-value:**
   - **p-value:** The probability of observing results at least as extreme as the sample data, assuming $H_0$ is true.
5. **Decision Rule:**
   - If **$p < \alpha$ (i.e., $p < 0.05$)**: **Reject $H_0$** (Statistically significant finding).
   - If **$p \ge \alpha$**: **Fail to reject $H_0$** (Insufficient evidence of effect).

### 6.2 Decision Matrix: Type I vs Type II Errors
| Reality | Decision: Reject $H_0$ | Decision: Fail to Reject $H_0$ |
| :--- | :--- | :--- |
| **$H_0$ is TRUE** | **Type I Error ($\alpha$)** (False Positive) | Correct Decision ($1 - \alpha$) |
| **$H_0$ is FALSE** | Correct Decision ($1 - \beta$, Power) | **Type II Error ($\beta$)** (False Negative) |

---

## 7. Introduction to Linear Regression & OLS

Regression models the mathematical relationship between an independent variable ($X$, feature) and a dependent variable ($Y$, target).

### 7.1 Simple Linear Regression Equation
$$Y = \beta_0 + \beta_1 X + \epsilon$$
- $Y$: Dependent variable (e.g., `Net Profit`)
- $X$: Independent variable (e.g., `Sales Amount`)
- $\beta_0$: $Y$-intercept (the expected value of $Y$ when $X = 0$)
- $\beta_1$: Slope coefficient (change in $Y$ for every 1-unit increase in $X$)
- $\epsilon$: Random error term (residuals)

### 7.2 Ordinary Least Squares (OLS)
OLS finds the unique line that minimizes the **Sum of Squared Residuals (SSR)**:
$$\min \sum (Y_i - \hat{Y}_i)^2$$

### 7.3 Evaluating Regression Quality
- **$R^2$ (Coefficient of Determination):**
  The proportion of variance in $Y$ explained by $X$ ($0 \le R^2 \le 1$).
  In our model ($Y = \text{Profit}$, $X = \text{Sales}$), $R^2 = 0.882$, meaning **88.2% of the variance in Net Profit is explained by Sales Volume alone**.
- **Residual Analysis:** Residuals should be normally distributed around zero with constant variance (Homoscedasticity).

---

## 8. Python & SQL Statistical Implementations

### Python Implementation (`scipy.stats` & `statsmodels`)
```python
import numpy as np
import pandas as pd
from scipy import stats

df = pd.read_csv("data/cleaned_sales_data.csv")

# 1. Two-sample t-test: Do Corporate orders spend significantly more than Consumer orders?
corp_sales = df[df['Customer_Segment'] == 'Corporate']['Sales_Amount']
cons_sales = df[df['Customer_Segment'] == 'Consumer']['Sales_Amount']

t_stat, p_val = stats.ttest_ind(corp_sales, cons_sales, equal_var=False)
print(f"t-statistic: {t_stat:.4f}, p-value: {p_val:.4e}")
# Result: p-value < 0.001 -> Statistically significant difference!

# 2. Linear Regression (OLS)
slope, intercept, r_val, p_val, std_err = stats.linregress(df['Sales_Amount'], df['Profit'])
print(f"Profit = {intercept:.2f} + {slope:.4f} * Sales")
print(f"R-squared: {r_val**2:.4f}")
```

### SQL Implementation
```sql
-- Calculating Sample Standard Deviation & Variance in SQL
SELECT 
    ROUND(AVG(sales_amount), 2) AS Mean_Sales,
    ROUND(
        SQRT(
            SUM((sales_amount - sub.avg_sales) * (sales_amount - sub.avg_sales)) / (COUNT(*) - 1)
        ), 2
    ) AS Sample_Std_Dev
FROM order_items
CROSS JOIN (SELECT AVG(sales_amount) AS avg_sales FROM order_items) sub;
```

