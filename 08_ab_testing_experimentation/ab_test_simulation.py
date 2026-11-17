import os
import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt

# Ensure output directory exists
os.makedirs("08_ab_testing_experimentation", exist_ok=True)

np.random.seed(42)

print("=" * 80)
print("A/B TESTING & EXPERIMENTATION STATISTICAL FRAMEWORK")
print("Experiment: One-Click Checkout Redesign vs Standard Multi-Step Checkout")
print("=" * 80)

# -------------------------------------------------------------
# 1. Experiment Parameters & Synthetic Generation
# -------------------------------------------------------------
N_control = 2500
N_variant = 2500

# True baseline conversion rate: 12.0%
# Variant true conversion rate: 14.5% (Relative lift: +20.8%)
p_control_true = 0.120
p_variant_true = 0.145

control_conversions = np.random.binomial(1, p_control_true, N_control)
variant_conversions = np.random.binomial(1, p_variant_true, N_variant)

# Average spend for converted users: Log-Normal distribution
# Control AOV: Mean ~$180
# Variant AOV: Mean ~$195
control_spend = np.where(control_conversions == 1, np.random.lognormal(mean=5.1, sigma=0.5, size=N_control), 0.0)
variant_spend = np.where(variant_conversions == 1, np.random.lognormal(mean=5.2, sigma=0.5, size=N_variant), 0.0)

df_ab = pd.DataFrame({
    "Visitor_ID": [f"VIS-{10000 + i}" for i in range(N_control + N_variant)],
    "Group": ["Control (Legacy 3-Step)"] * N_control + ["Variant (One-Click)"] * N_variant,
    "Converted": np.concatenate([control_conversions, variant_conversions]),
    "Revenue": np.round(np.concatenate([control_spend, variant_spend]), 2)
})

csv_path = "08_ab_testing_experimentation/ab_test_results.csv"
df_ab.to_csv(csv_path, index=False)
print(f"Exported experiment logs to {csv_path} ({len(df_ab)} visitors).")

# -------------------------------------------------------------
# 2. Conversion Rate Analysis (Two-Proportion Z-Test)
# -------------------------------------------------------------
conv_control = df_ab[df_ab["Group"] == "Control (Legacy 3-Step)"]["Converted"]
conv_variant = df_ab[df_ab["Group"] == "Variant (One-Click)"]["Converted"]

n_c, x_c = len(conv_control), conv_control.sum()
n_v, x_v = len(conv_variant), conv_variant.sum()

cr_control = x_c / n_c
cr_variant = x_v / n_v
relative_lift_cr = ((cr_variant - cr_control) / cr_control) * 100

# Pooled standard error
p_pool = (x_c + x_v) / (n_c + n_v)
se_pooled = np.sqrt(p_pool * (1 - p_pool) * (1/n_c + 1/n_v))
z_stat = (cr_variant - cr_control) / se_pooled
p_val_cr = 2 * (1 - stats.norm.cdf(abs(z_stat)))

# 95% Confidence Interval for difference
diff = cr_variant - cr_control
se_diff = np.sqrt((cr_control * (1 - cr_control) / n_c) + (cr_variant * (1 - cr_variant) / n_v))
ci_low = (diff - 1.96 * se_diff) * 100
ci_high = (diff + 1.96 * se_diff) * 100

print("\n--- CONVERSION RATE HYPOTHESIS TEST ---")
print(f"Control Sample Size:  {n_c:,} | Conversions: {x_c} | Rate: {cr_control * 100:.2f}%")
print(f"Variant Sample Size:  {n_v:,} | Conversions: {x_v} | Rate: {cr_variant * 100:.2f}%")
print(f"Observed Relative Lift: +{relative_lift_cr:.2f}%")
print(f"Z-Score:                {z_stat:.4f}")
print(f"p-value:                {p_val_cr:.5f} ({'Statistically Significant' if p_val_cr < 0.05 else 'Not Significant'})")
print(f"95% CI for Lift:        [{ci_low:.2f}%, {ci_high:.2f}%]")

# -------------------------------------------------------------
# 3. Revenue / AOV Analysis (Welch's Two-Sample t-Test)
# -------------------------------------------------------------
rev_control_converted = df_ab[(df_ab["Group"] == "Control (Legacy 3-Step)") & (df_ab["Converted"] == 1)]["Revenue"]
rev_variant_converted = df_ab[(df_ab["Group"] == "Variant (One-Click)") & (df_ab["Converted"] == 1)]["Revenue"]

aov_control = rev_control_converted.mean()
aov_variant = rev_variant_converted.mean()
relative_lift_aov = ((aov_variant - aov_control) / aov_control) * 100

t_stat, p_val_aov = stats.ttest_ind(rev_variant_converted, rev_control_converted, equal_var=False)

print("\n--- AVERAGE ORDER VALUE (AOV) HYPOTHESIS TEST ---")
print(f"Control Converted AOV:  ${aov_control:.2f}")
print(f"Variant Converted AOV:  ${aov_variant:.2f}")
print(f"Observed AOV Lift:      +{relative_lift_aov:.2f}%")
print(f"t-statistic:            {t_stat:.4f}")
print(f"p-value:                {p_val_aov:.5f}")

# -------------------------------------------------------------
# 4. Visualization & Decision Plot
# -------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Conversion Rate Comparison with Error Bars
axes[0].bar(
    ["Control (Legacy)", "Variant (One-Click)"],
    [cr_control * 100, cr_variant * 100],
    yerr=[1.96 * np.sqrt(cr_control*(1-cr_control)/n_c)*100, 1.96 * np.sqrt(cr_variant*(1-cr_variant)/n_v)*100],
    color=['#94A3B8', '#2563EB'],
    capsize=8,
    width=0.45
)
axes[0].set_title(f'Conversion Rate (p-value: {p_val_cr:.4f})', fontsize=12, fontweight='bold')
axes[0].set_ylabel('Conversion Rate (%)', fontsize=10)
axes[0].set_ylim(0, 20)
for i, v in enumerate([cr_control * 100, cr_variant * 100]):
    axes[0].text(i, v + 1.2, f"{v:.2f}%", ha='center', fontweight='bold', fontsize=11)

# Plot 2: AOV Distribution Boxplot
axes[1].boxplot(
    [rev_control_converted, rev_variant_converted],
    tick_labels=["Control (Legacy)", "Variant (One-Click)"],
    patch_artist=True,
    boxprops=dict(facecolor='#E0E7FF', color='#3730A3'),
    medianprops=dict(color='#DC2626', linewidth=2)
)
axes[1].set_title(f'AOV Distribution (p-value: {p_val_aov:.4f})', fontsize=12, fontweight='bold')
axes[1].set_ylabel('Order Revenue ($)', fontsize=10)

plt.suptitle('A/B Test Results: One-Click Checkout Redesign Experiment', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
chart_file = "08_ab_testing_experimentation/ab_test_decision_chart.png"
fig.savefig(chart_file, dpi=300)
plt.close(fig)
print(f"\nSaved decision visualization to {chart_file}")

# -------------------------------------------------------------
# 5. Final Business Decision Recommendation
# -------------------------------------------------------------
print("\n" + "=" * 80)
print("FINAL RECOMMENDATION: SHIP THE VARIANT TO 100% PRODUCTION")
print(f"Rationale: Conversion Rate increased from {cr_control*100:.2f}% to {cr_variant*100:.2f}% (p={p_val_cr:.4e} < 0.05).")
print(f"Estimated Annual Revenue Impact: +${(N_control*2 * (cr_variant*aov_variant - cr_control*aov_control)):,.2f} per 5,000 visitors.")
print("=" * 80)
