# Exploratory Data Analysis (EDA) & Business Insights Report
**Organization:** Apex Retail Solutions  
**Analysis Period:** January 2024 – October 2025  
**Data Analyst Team:** Enterprise Analytics & BI Group  
**Dataset Reference:** [`cleaned_sales_data.csv`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/data/cleaned_sales_data.csv)

---

## Executive Summary

This report delivers a rigorous diagnostic evaluation of Apex Retail Solutions' global omni-channel performance across 1,209 validated customer orders. Over the 22-month analysis window, the company generated **\$1,764,170.20 in Gross Sales** and **\$537,291.20 in Net Profit**, delivering an aggregate gross margin of **30.45%**. 

While topline revenue has scaled steadily, our diagnostic audit reveals three critical operational opportunities:
1. **Severe Margin Erosion from Promotional Discounts:** Orders with discounts greater than 20% generate an average margin of just **16.95%**, compared to **40.36%** for zero-discount sales.
2. **Heavy Segment Concentration:** The **Corporate** segment drives **69.30%** of total revenue, representing significant enterprise client dependency.
3. **Category Volume vs. Margin Trade-off:** **Technology** hardware drives **56.3%** of all revenue but carries our lowest category margin (**25.90%**), whereas **Office Supplies** and **Furniture** deliver premium returns (**39.63%** and **36.42%** respectively).

```
+---------------------------------------------------------------------------------------------------------+
|                                    EXECUTIVE SCORECARD AT A GLANCE                                      |
+--------------------------+--------------------------+--------------------------+------------------------+
|       Gross Revenue      |        Net Profit        |       Gross Margin       |       Total Orders     |
|       $1,764,170.20      |       $537,291.20        |          30.45%          |          1,209         |
+--------------------------+--------------------------+--------------------------+------------------------+
|     Mean Transaction     |    Median Transaction    |   Corporate Rev Share    |      Refund Rate       |
|         $1,459.20        |         $741.00          |          69.30%          |         4.33%          |
+--------------------------+--------------------------+--------------------------+------------------------+
```

---

## 1. Data Quality & Data Cleaning Audit

The raw ingestion feed (`data/raw_sales_data.csv`) contained typical real-world transactional imperfections. The cleaning pipeline (`04_data_cleaning_eda/clean_dataset.py`) conducted a 6-stage remediation:

| Audit Stage | Anomaly Identified | Diagnostic Impact | Remediation Method | Cleaned Result |
| :--- | :--- | :--- | :--- | :--- |
| **Deduplication** | 21 exact duplicate rows | Inflated sales by \$32,450 | Hash-based row deduplication | 21 redundant records purged |
| **Whitespace & Case** | Mixed casing (`technology`, `FURNITURE `) | Fragmented pivot groupings | `.str.strip().str.title()` | Standardized to 4 pristine categories |
| **Missing Values** | 45 null emails, 20 null segments, 30 null discounts | Failed JOINs & missing slices | Mode imputation & zero-discount default | 100% column completeness |
| **Date Inconsistency** | Mixed `MM/DD/YYYY` and `YYYY-MM-DD` | Time-series parsing errors | Coerced to ISO-8601 `YYYY-MM-DD` | Unified chronological index |
| **Typographical Negatives** | 3 negative quantities (`-2`, `-4`) | Corrupted item totals | Absolute value correction `abs()` | Preserved valid transactions |
| **Extreme Outliers** | 2 revenue typo records ($>50\times$ unit price) | Distorted mean statistics | Recalculated from verified unit prices | Verified mathematical consistency |

---

## 2. Descriptive Statistical Analysis

The dataset contains both continuous monetary variables and discrete fulfillment indicators.

### 2.1 Univariate Summary Table
| Metric | Quantity | Discount Rate | Sales Amount ($) | Net Profit ($) | Profit Margin (%) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Count** | 1,209 | 1,209 | 1,209 | 1,209 | 1,209 |
| **Mean** | 2.59 | 0.060 (6.0%) | \$1,459.20 | \$444.41 | 36.14% |
| **Standard Deviation** | 1.86 | 0.076 (7.6%) | \$2,064.60 | \$577.15 | 9.52% |
| **Minimum** | 1.00 | 0.000 (0.0%) | \$14.40 | -\$212.10 | -5.32% |
| **25th Percentile ($Q_1$)** | 1.00 | 0.000 (0.0%) | \$266.00 | \$94.00 | 29.78% |
| **50th Percentile (Median)** | 2.00 | 0.050 (5.0%) | \$741.00 | \$267.00 | 36.76% |
| **75th Percentile ($Q_3$)** | 3.00 | 0.100 (10.0%)| \$1,798.20 | \$558.10 | 43.32% |
| **Maximum** | 10.00 | 0.300 (30.0%)| \$19,992.00 | \$5,592.00 | 55.56% |

### 2.2 Skewness & Kurtosis Assessment
- **`Sales_Amount` Skewness = +3.56 (High Positive Right Skew):**
  Because the mean (\$1,459.20) is nearly **double** the median (\$741.00), the sales distribution is heavily pulled to the right by high-ticket orders (such as multi-unit MacBook Pro and Standing Desk purchases).
  > **Analyst Directive:** For executive KPI reporting, the **Median** must be reported alongside the Mean to avoid misleading branch managers regarding typical ticket sizes.
- **`Sales_Amount` Kurtosis = 19.37 (Leptokurtic):**
  High kurtosis indicates a fat-tailed distribution with significant peak clustering around lower-cost office accessories and a thin tail of high-value bulk purchases.

---

## 3. Outlier Detection via Interquartile Range (IQR)

Using the standard Tukey boxplot rule:
$$\text{IQR} = Q_3 - Q_1 = \$1,798.20 - \$266.00 = \$1,532.20$$
$$\text{Upper Inner Fence} = Q_3 + (1.5 \times \text{IQR}) = \$1,798.20 + (1.5 \times \$1,532.20) = \$4,096.50$$
$$\text{Upper Outer Fence} = Q_3 + (3.0 \times \text{IQR}) = \$1,798.20 + (3.0 \times \$1,532.20) = \$6,394.80$$

```
Distribution of Transaction Value ($):
[Min: $14] --- [Q1: $266] ======= [Median: $741] ======= [Q3: $1,798] --- [Inner Fence: $4,096] ... * * * [Max: $19,992]
```
- **Findings:** 41 transactions fall beyond the outer fence of \$6,394.80.
- **Business Interpretation:** These outliers are **legitimate enterprise bulk procurements** (e.g., Corporate orders of 8–10 MacBook Pros or Herman Miller chairs). They represent real business revenue and should **not** be removed from production financial reporting, but should be partitioned into a separate "Enterprise Deals" reporting layer.

---

## 4. Correlation & Driver Analysis

Using the Pearson correlation coefficient ($r$):

| Variable Pair | Pearson $r$ | Statistical Interpretation | Business Implication |
| :--- | :--- | :--- | :--- |
| **Sales Amount $\leftrightarrow$ Profit** | **+0.939** | Extremely strong positive | Higher transaction volume directly drives absolute gross dollar profit. |
| **Discount Rate $\leftrightarrow$ Profit Margin %** | **-0.600** | Moderate to strong negative | Increasing discounts directly degrades unit profitability. |
| **Unit Price $\leftrightarrow$ Quantity** | **-0.025** | Near zero correlation | High-priced items are not purchased in significantly smaller counts by our Corporate buyers. |
| **Unit Price $\leftrightarrow$ Profit Margin %** | **-0.642** | Moderate negative | Lower-priced items (Stationery, Cables) carry higher gross percentage markups than high-ticket electronics. |

### Promotional Discount Erosion Curve
Our empirical breakdown of discount bands reveals a steep decay in margin:

```
Discount Band   | Transaction Count | Average Margin % | Realized Net Profit
----------------+-------------------+------------------+--------------------
0% (None)       |        586        |      40.36%      |      $309,400.00
1% - 10% (Low)  |        394        |      35.60%      |      $171,124.70
11% - 20% (Mid) |        191        |      28.12%      |      $ 53,268.40
> 20% (Steep)   |         38        |      16.95%      |      $  3,498.10
```
> [!WARNING]
> While $>20\%$ discount clearance promotions drove \$36,864 in sales volume, they contributed only **\$3,498.10** in total profit. The operational cost of shipping and fulfillment for these orders leaves the business operating near break-even.

---

## 5. Segment & Product Performance Breakdown

### 5.1 Customer Segment Distribution
- **Corporate (69.30% of Total Revenue, \$1,222,547.50):** Average order quantity of 3.8 units. The primary revenue engine.
- **Consumer (15.34% of Total Revenue, \$270,595.40):** Average order quantity of 1.4 units. Typically single-item purchases (iPhones, Headphones).
- **Home Office (15.36% of Total Revenue, \$271,027.30):** High proportion of ergonomic furniture and desk accessories.

### 5.2 Product Category Performance
```
Category         Revenue ($K)   Profit ($K)   Realized Margin %
Technology       $993.9K        $257.5K       25.90%
Furniture        $492.2K        $179.3K       36.42%
Smart Gadgets    $227.0K        $ 80.3K       35.38%
Office Supplies  $ 51.1K        $ 20.2K       39.63%
```

---

## 6. Strategic Business Recommendations

Based on the quantitative findings, we recommend the following strategic actions for leadership:

1. **Implement Hard Discount Guardrails:**
   - Cap discretionary sales discounts at **15%**. Any discount exceeding 15% must require VP approval. This policy change will prevent the margin collapse observed in the $>20\%$ tier and protect an estimated **\$25,000 to \$35,000 in annualized gross margin**.
2. **Bundle High-Margin Office Supplies with Technology Hardware:**
   - Technology carries a 25.9% margin, while Office Supplies carries a 39.6% margin. Create cross-sell checkout bundles (e.g., MacBook Pro + Ergonomic Stand + Premium Cables) to lift basket gross margins by 200–350 basis points.
3. **Establish a Dedicated B2B Account Management Tier:**
   - Because 69.3% of revenue originates from Corporate accounts, institutionalizing dedicated account managers and contract pricing will reduce enterprise churn risk.
4. **Fulfillment Speed Optimization:**
   - Order status analysis indicates a **4.33% return rate** and **1.67% cancellation rate**. The vast majority of cancellations occurred on standard 5–7 day delivery modes. Transitioning high-value orders ($>\$1,000$) to 2-day priority fulfillment will reduce cancellation churn.

