# A/B Testing & Product Experimentation Master Guide (Week 2)

Welcome to the **A/B Testing & Product Experimentation Guide for Data Analysts**. This document covers end-to-end online experimentation, from power calculations to hypothesis formulation, metric selection, statistical tests, and decision-making.

---

## Table of Contents
1. [The Experimentation Lifecycle](#1-the-experimentation-lifecycle)
2. [Formulating Testable Hypotheses](#2-formulating-testable-hypotheses)
3. [Sample Size Determination & Statistical Power](#3-sample-size-determination)
4. [Statistical Tests: Proportions vs Continuous Metrics](#4-statistical-tests)
5. [Common Experimentation Pitfalls & How to Avoid Them](#5-common-experimentation-pitfalls)
6. [Case Study: One-Click Checkout Redesign](#6-case-study)

---

## 1. The Experimentation Lifecycle

Every product feature, pricing modification, and algorithm update in tech companies is validated through randomized controlled trials (A/B testing):

```
+-----------------------------------------------------------------------------------+
|                           THE 5-STAGE A/B TESTING ENGINE                          |
+-------------------+-------------------+-------------------+-----------------------+
|  1. Hypothesis    |  2. Power & Size  |  3. Randomization |  4. Statistical Test  |
|  Define Primary   |  Calculate sample |  Assign 50/50     |  Two-sample t-test    |
|  & Guardrail KPI  |  size with MDE    |  Control / Variant|  or 2-Proportion Z    |
+-------------------+-------------------+-------------------+-----------------------+
                                          │
                                          ▼
                         [ 5. Decision: Ship or Rollback ]
```

---

## 2. Formulating Testable Hypotheses

A rigorous hypothesis must specify the **Independent Variable**, the **Primary Metric**, the **Population**, and the **Business Mechanism**:

> **Hypothesis Statement:**  
> *"Replacing the legacy 3-step checkout with a 'One-Click Buy' interface will reduce checkout friction and cognitive load for registered desktop and mobile users, resulting in a minimum relative increase of +5% in Checkout Conversion Rate without increasing accidental cancellation or return rates."*

### Primary vs Secondary vs Guardrail Metrics
- **Primary (Decision) Metric:** Checkout Conversion Rate ($CR = \frac{\text{Orders}}{\text{Visitors}}$).
- **Secondary (Mechanistic) Metric:** Time-to-Checkout, Funnel Drop-off Rate at Payment step.
- **Guardrail (Safety) Metric:** Customer Return Rate, Support Ticket Rate, Margin %. (If conversion rises by 10% but returns surge by 50%, the variant is rejected!).

---

## 3. Sample Size Determination & Statistical Power

Before launching any test, the analyst must determine: *"How many visitors do we need per group to detect an effect?"*

### The 4 Variables of Power Analysis:
1. **Significance Level ($\alpha$):** Probability of a Type I error (False Positive). Industry standard: $\alpha = 0.05$ (5%).
2. **Statistical Power ($1 - \beta$):** Probability of detecting a true effect if one exists. Industry standard: $80\%$ ($0.80$).
3. **Baseline Conversion Rate ($p_1$):** Historical conversion rate (e.g., $12.0\%$).
4. **Minimum Detectable Effect (MDE):** The smallest relative lift the business cares about detecting (e.g., $10\%$ relative lift $\rightarrow 13.2\%$).

$$\text{Sample Size per Group } n \approx \frac{2 \cdot (Z_{\alpha/2} + Z_{\beta})^2 \cdot p(1 - p)}{\text{MDE}^2}$$

---

## 4. Statistical Tests: Proportions vs Continuous Metrics

### 4.1 Categorical / Discrete Metric (Conversion Rate)
- **Test:** Two-Proportion Z-Test or Chi-Square ($\chi^2$) Test of Independence.
- Null Hypothesis: $H_0: p_{\text{variant}} - p_{\text{control}} = 0$.
- Alternative Hypothesis: $H_1: p_{\text{variant}} - p_{\text{control}} \ne 0$.

### 4.2 Continuous Monetary Metric (Revenue per User / AOV)
- **Test:** Two-Sample Student's t-Test or **Welch's t-Test** (which does not assume equal variances between groups).
- Null Hypothesis: $H_0: \mu_{\text{variant}} = \mu_{\text{control}}$.

---

## 5. Common Experimentation Pitfalls

1. **The "Peeking Problem" (Continuous Monitoring):**
   - Checking p-values every morning and stopping the test as soon as $p < 0.05$ inflates the true False Positive Rate from 5% to over **30%**!
   - *Fix:* Fix sample size in advance and only evaluate p-values when target sample size is reached.
2. **Sample Ratio Mismatch (SRM):**
   - If a 50/50 test results in 5,500 Control and 4,500 Variant users, the randomization engine is broken (e.g., bots getting blocked on the new frontend).
   - Always run a Chi-Square goodness-of-fit test on sample allocations before analyzing results.
3. **Novelty Effect & Primacy Effect:**
   - Existing users may click the new button simply because it looks new, causing a temporary spike that decays after two weeks.

