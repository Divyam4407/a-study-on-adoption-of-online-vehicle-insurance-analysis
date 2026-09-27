from google.colab import drive
drive.mount('/content/drive')

!pip install openpyxl statsmodels

import os
import sys
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.stattools import durbin_watson




# 1. FILE CONFIGURATION & COLUMN MAPPING
EXCEL_FILE_PATH = "Survey on Adoption of Online Vehicle Insurance Responses (FINAL).xlsx"
SHEET_NAME = 0

# Core substrings mapped to research variable keys
SUBSTRING_COLUMN_MAP = {

    # Screening & Demographics
    "screen_qualify": "motorized vehicle in Bangalore",
    "age_group": "Your Age Group",
    "gender": "Gender",
    "occupation": "Primary Occupation",
    "income": "Monthly Household Income",

    # Vehicle & Channel Information
    "vehicle_type": "type of vehicle do you primarily purchase/renew",
    "policy_type": "type of policy cover do you currently hold",
    "recent_channel": "purchase or renew your vehicle insurance most recently",
    "tenure": "using digital channels for insurance renewals",
    "renewal_intent": "For my next vehicle insurance renewal, I intend to",

    # 14 Likert-Scale Items
    "PE1": "faster than offline agents",
    "PE2": "email/WhatsApp is highly convenient",
    "EE1": "understanding coverage options is easy",
    "EE2": "inspection photos/videos online during renewal",
    "PV1": "zero agent commission",
    "PV2": "Add-on covers (Zero Dep, Engine Protect)",
    "SI1": "Recommendations from colleagues/friends",
    "PR1": "lack of personal assistance during physical claim",
    "PR2": "secure entering my financial and vehicle details",
    "PT1": "trust digital-first insurers (e.g., Acko/Digit)",
    "PT2": "Automated digital claim processing",
    "UBI1": "Pay-As-You-Drive",
    "REG1": "Mandatory Digilocker integration",
    "UBI2": "sharing driving data via telematics",

}



LIKERT_TEXT_MAP = {
    "strongly disagree": 1,
    "disagree": 2,
    "neutral": 3,
    "agree": 4,
    "strongly agree": 5,
}



LIKERT_ITEMS = [
    "PE1", "PE2", "EE1", "EE2", "PV1", "PV2", "SI1",
    "PR1", "PR2", "PT1", "PT2", "UBI1", "REG1", "UBI2",
]



# 2. DATA INGESTION & VARIABLE TRANSFORMATION
def load_and_preprocess_data(file_path: str, substring_map: dict) -> pd.DataFrame:
    if not os.path.exists(file_path):

        raise FileNotFoundError(f"File not found: '{os.path.abspath(file_path)}'")

    df_raw = pd.read_excel(file_path, sheet_name=SHEET_NAME)
    print(f"Total raw observations loaded: {len(df_raw)}")



    # Robust matching: match standardized keys against survey column titles
    matched_cols = {}
    for col in df_raw.columns:
        col_clean = str(col).strip().lower()
        for key, pattern in substring_map.items():
            if pattern.lower() in col_clean:
                matched_cols[col] = key
                break
    df = df_raw.rename(columns=matched_cols).copy()



    # A. Screening Filter: Only retain respondents who own & maintain vehicle insurance
    if "screen_qualify" in df.columns:
        df = df[df["screen_qualify"].astype(str).str.strip().str.lower() == "yes"].copy()
        print(f"Screened validated sample size (N): {len(df)}")
    else:
        print("[!] Note: 'screen_qualify' column not found; running on all rows.")



    # B. Classification of Recent Purchase Channel: Digital vs Offline
    digital_keywords = ["bank", "upi", "portal", "app", "aggregator", "online"]

    def classify_channel(val):
        s = str(val).lower()
        if any(k in s for k in digital_keywords) and not any(
            k in s for k in ["dealer", "offline", "agent"]
        ):
            return "Digital"
        return "Offline"

    df["channel_binary"] = df["recent_channel"].apply(classify_channel)



    # C. Binary Intention for Logistic/OLS Modeling: 1 = Online, 0 = Offline
    def classify_intent(val):
        s = str(val).lower()
        if "online" in s or "switch" in s:
            return 1
        return 0

    df["digital_intent"] = df["renewal_intent"].apply(classify_intent)



    # D. Standardize text Likert responses to 1-5 integers
    for col in LIKERT_ITEMS:
        if col in df.columns:
            cleaned = df[col].astype(str).str.strip().str.lower()
            df[col] = cleaned.map(LIKERT_TEXT_MAP).fillna(pd.to_numeric(df[col], errors="coerce"))



    # E. Composite Construct Averages
    df["PE"] = df[["PE1", "PE2"]].mean(axis=1)
    df["EE"] = df[["EE1", "EE2"]].mean(axis=1)
    df["PV"] = df[["PV1", "PV2"]].mean(axis=1)
    df["SI"] = df["SI1"]
    df["PR"] = df["PR1"]
    df["PT"] = df[["PT1", "PT2", "PR2"]].mean(axis=1)
    df["UBI"] = df[["UBI1", "REG1", "UBI2"]].mean(axis=1)

    return df




# 3. STATISTICAL PROCEDURES & TESTS
def calculate_cochran_sample_size(
    confidence_level: float = 0.95, p: float = 0.50, margin_of_error: float = 0.065
) -> float:

    """Calculates theoretical sample size using Cochran's formula."""
    z_score = stats.norm.ppf(1 - (1 - confidence_level) / 2)
    n0 = (z_score**2 * p * (1 - p)) / (margin_of_error**2)
    print("\n" + "=" * 70)
    print("1. COCHRAN'S SAMPLE SIZE DETERMINATION")
    print("=" * 70)
    print(f"Confidence Level: {confidence_level * 100:.0f}% (Z-Score: {z_score:.4f})")
    print(f"Assumed Population Proportion (p): {p:.2f}")
    print(f"Margin of Error (e): ±{margin_of_error * 100:.1f}%")
    print(f"Calculated Sample Requirement (n0): {n0:.2f} -> Rounded: {int(np.ceil(n0))}")
    return n0



def calculate_cronbach_alpha(df: pd.DataFrame, item_cols: list) -> float:

    """Calculates Cronbach's alpha reliability metric for psychometric scale items."""
    items_df = df[item_cols].dropna()
    k = items_df.shape[1]
    item_variances = items_df.var(axis=0, ddof=1).sum()
    total_score_variance = items_df.sum(axis=1).var(ddof=1)

    alpha = (k / (k - 1)) * (1 - (item_variances / total_score_variance))

    print("\n" + "=" * 70)
    print("2. MEASUREMENT SCALE RELIABILITY (CRONBACH'S ALPHA)")
    print("=" * 70)
    print(f"Number of psychometric scale items (k): {k}")
    print(f"Complete cases evaluated: {len(items_df)}")
    print(f"Sum of individual item variances: {item_variances:.4f}")
    print(f"Composite total score variance: {total_score_variance:.4f}")
    print(f"Cronbach's Alpha (α): {alpha:.4f}")
    print(
        f"Internal Consistency: {'Satisfactory (α >= 0.70)' if alpha >= 0.70 else 'Insufficient (α < 0.70)'}"
    )
    return alpha



def generate_item_descriptive_statistics(df: pd.DataFrame, item_cols: list) -> pd.DataFrame:

    """Computes mean, standard deviation, median, and response distribution percentages."""
    print("\n" + "=" * 70)
    print(f"3. DESCRIPTIVE STATISTICS OF PSYCHOMETRIC SCALE ITEMS (N = {len(df)})")
    print("=" * 70)
    stats_list = []
    for col in item_cols:
        series = df[col].dropna()
        n = len(series)
        if n == 0:
            continue

        mean_val = series.mean()
        std_val = series.std(ddof=1)
        med_val = series.median()

        disagree_pct = ((series == 1) | (series == 2)).sum() / n * 100
        neutral_pct = (series == 3).sum() / n * 100
        agree_pct = ((series == 4) | (series == 5)).sum() / n * 100

        stats_list.append(
            {
                "Item": col,
                "Mean (μ)": f"{mean_val:.2f}",
                "Std Dev (σ)": f"{std_val:.2f}",
                "Median": f"{med_val:.1f}",
                "Disagree (1-2) %": f"{disagree_pct:.2f}%",
                "Neutral (3) %": f"{neutral_pct:.2f}%",
                "Agree (4-5) %": f"{agree_pct:.2f}%",
            }
        )

    summary_table = pd.DataFrame(stats_list)
    print(summary_table.to_string(index=False))
    return summary_table



def run_cross_tabulation_and_chi2(
    df: pd.DataFrame, row_var: str, col_var: str = "channel_binary", label: str = ""
):
    """Generates cross-tabulations and computes Pearson's Chi-Square Test of Independence."""
    print("\n" + "=" * 70)
    print(f"4. BIVARIATE CROSS-TABULATION & CHI-SQUARE: {label.upper()}")
    print("=" * 70)

    sub_df = df[[row_var, col_var]].dropna()
    observed = pd.crosstab(sub_df[row_var], sub_df[col_var], margins=True, margins_name="Total")
    obs_unmargined = pd.crosstab(sub_df[row_var], sub_df[col_var])

    chi2, p_val, dof, expected = stats.chi2_contingency(obs_unmargined)

    print("Observed Frequencies with Row Percentages:")
    row_pcts = (pd.crosstab(sub_df[row_var], sub_df[col_var], normalize="index") * 100).round(2)
    formatted_table = observed.copy().astype(str)
    for r in obs_unmargined.index:
        for c in obs_unmargined.columns:
            formatted_table.loc[r, c] = f"{observed.loc[r, c]} ({row_pcts.loc[r, c]:.2f}%)"

    print(formatted_table)
    print("\nChi-Square Test of Independence:")
    print(f"Pearson Chi-Square Statistic (χ²): {chi2:.4f}")
    print(f"Degrees of Freedom (df): {dof}")
    print(f"Asymptotic p-value: {p_val:.6f}")
    print(
        f"Inference (α = 0.05): {'Statistically Significant (Reject H0)' if p_val < 0.05 else 'Not Significant (Fail to Reject H0)'}"
    )

    exp_df = pd.DataFrame(
        expected,
        index=obs_unmargined.index,
        columns=[f"Exp_{c}" for c in obs_unmargined.columns],
    )
    print("\nExpected Cell Frequencies:")
    print(exp_df.round(2))
    return chi2, p_val



def run_binary_logistic_regression(df: pd.DataFrame, predictors: list, target: str = "digital_intent"):
    """Estimates Binary Logistic Regression via Maximum Likelihood Estimation."""
    print("\n" + "=" * 70)
    print("5. BINARY LOGISTIC REGRESSION MODEL (MLE)")
    print("=" * 70)

    df_reg = df[[target] + predictors].dropna()
    X = sm.add_constant(df_reg[predictors])
    y = df_reg[target]

    logit_model = sm.Logit(y, X).fit(disp=False)

    params = logit_model.params
    se = logit_model.bse
    z_stats = logit_model.tvalues
    p_vals = logit_model.pvalues
    odds_ratios = np.exp(params)
    conf = logit_model.conf_int()
    conf_or = np.exp(conf)

    results_df = pd.DataFrame(
        {
            "Coefficient (β)": params.round(4),
            "Std. Error": se.round(4),
            "z-statistic": z_stats.round(3),
            "p-value": p_vals.round(4),
            "Odds Ratio (OR)": odds_ratios.round(4),
            "95% CI Lower": conf_or[0].round(3),
            "95% CI Upper": conf_or[1].round(3),
        }
    )

    print(results_df.to_string())
    print("\nModel Fit Metrics:")
    print(f"Observations (N): {int(logit_model.nobs)}")
    print(f"Log-Likelihood: {logit_model.llf:.2f}")
    print(f"McFadden's Pseudo R²: {logit_model.prsquared:.4f}")
    print(f"LLR Chi-Square: {logit_model.llr:.2f}")
    print(f"LLR p-value: {logit_model.llr_pvalue:.4e}")
    return logit_model



def run_ols_regression(df: pd.DataFrame, predictors: list, target: str = "digital_intent"):
    """Estimates Ordinary Least Squares (OLS) Linear Regression for robustness testing."""
    print("\n" + "=" * 70)
    print("6. ORDINARY LEAST SQUARES (OLS) REGRESSION ROBUSTNESS MODEL")
    print("=" * 70)

    df_reg = df[[target] + predictors].dropna()
    X = sm.add_constant(df_reg[predictors])
    y = df_reg[target]

    ols_model = sm.OLS(y, X).fit()

    params = ols_model.params
    se = ols_model.bse
    t_stats = ols_model.tvalues
    p_vals = ols_model.pvalues
    conf = ols_model.conf_int()

    results_df = pd.DataFrame(
        {
            "Coefficient (β)": params.round(4),
            "Std. Error": se.round(4),
            "t-statistic": t_stats.round(3),
            "p-value": p_vals.round(4),
            "95% CI Lower": conf[0].round(3),
            "95% CI Upper": conf[1].round(3),
        }
    )

    dw_stat = durbin_watson(ols_model.resid)

    print(results_df.to_string())
    print("\nModel Diagnostics:")
    print(f"R-squared: {ols_model.rsquared:.4f}")
    print(f"Adjusted R-squared: {ols_model.rsquared_adj:.4f}")
    print(f"F-statistic: {ols_model.fvalue:.3f}")
    print(f"Prob (F-statistic): {ols_model.f_pvalue:.4e}")
    print(f"Durbin-Watson Statistic: {dw_stat:.3f}")
    return ols_model




# 4. EXECUTION PIPELINE
if __name__ == "__main__":
    try:
        data = load_and_preprocess_data(EXCEL_FILE_PATH, SUBSTRING_COLUMN_MAP)


        # A. Cochran Sample Size Verification
        calculate_cochran_sample_size(
            confidence_level=0.95, p=0.50, margin_of_error=0.065
        )

        # B. Scale Reliability
        calculate_cronbach_alpha(data, LIKERT_ITEMS)


        # C. Item-Level Descriptives
        generate_item_descriptive_statistics(data, LIKERT_ITEMS)


        # D. Chi-Square Hypothesis Testing
        if "age_group" in data.columns:
            run_cross_tabulation_and_chi2(
                data,
                row_var="age_group",
                col_var="channel_binary",
                label="H1: Age Group vs Channel Choice",
            )

        if "vehicle_type" in data.columns:
            run_cross_tabulation_and_chi2(
                data,
                row_var="vehicle_type",
                col_var="channel_binary",
                label="Vehicle Type vs Channel Choice",
            )

        # E. Multivariate Regression Models (H2 through H7)
        model_predictors = ["PE", "EE", "PV", "PR", "PT", "SI"]
        run_binary_logistic_regression(data, predictors=model_predictors)
        run_ols_regression(data, predictors=model_predictors)



    except FileNotFoundError as err:
        print(f"\n[!] Execution Aborted: {err}")
        print("Please check that the file is uploaded to the root working directory or Google Drive.")
