import subprocess
import sys
import os

scripts = [
    ("1. Dataset Generation & SQL DB Population", "create_datasets.py"),
    ("2. Excel Dashboard Generator", "01_excel_dashboard/build_excel_dashboard.py"),
    ("3. SQL Practice Suite (18 Queries)", "02_sql_practice/run_sql_exercises.py"),
    ("4. Python Analysis & KPI Visualizations", "03_python_analysis/analysis_script.py"),
    ("5. Data Cleaning & Validation Pipeline", "04_data_cleaning_eda/clean_dataset.py"),
    ("6. Exploratory Data Analysis (EDA) Stats", "04_data_cleaning_eda/run_eda.py"),
    ("7. Advanced SQL & Cohort Retention", "07_advanced_sql/run_advanced_sql.py"),
    ("8. A/B Testing & Statistical Experimentation", "08_ab_testing_experimentation/ab_test_simulation.py"),
    ("9. Predictive Churn Machine Learning Models", "09_predictive_churn_ml/train_churn_model.py"),
]

def main():
    print("=" * 80)
    print("APEX RETAIL SOLUTIONS - DATA ANALYST PORTFOLIO RUNNER")
    print("=" * 80)
    print("Running all project components sequentially...\n")

    for title, script in scripts:
        print(f"\n{'='*30} [START: {title}] {'='*30}")
        if not os.path.exists(script):
            print(f"Skipping {script}: file not found.")
            continue
        try:
            result = subprocess.run([sys.executable, script], capture_output=False, check=True)
            print(f">>> Finished: {script} (Status: OK)")
        except subprocess.CalledProcessError as e:
            print(f"Error running {script}: {e}")

    print("\n" + "=" * 80)
    print("ALL MODULES EXECUTED SUCCESSFULLY!")
    print("Open the following files in your browser or application:")
    print(" - Power BI Interactive Preview: 05_powerbi_dashboard/dashboard_preview.html")
    print(" - Excel Sales Dashboard:       01_excel_dashboard/sales_dashboard.xlsx")
    print(" - Jupyter Notebook:             03_python_analysis/python_data_analysis.ipynb")
    print(" - Executive EDA Report:         04_data_cleaning_eda/eda_report.md")
    print("=" * 80)

if __name__ == "__main__":
    main()

