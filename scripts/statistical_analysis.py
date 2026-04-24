from __future__ import annotations

import pandas as pd

from analysis_utils import (
    ensure_output_dirs,
    linear_regression_summary,
    load_master_dataset,
    markdown_table,
    one_way_anova,
    pearson_with_pvalue,
    welch_t_test,
    write_csv,
    write_json,
)


def main() -> None:
    paths = ensure_output_dirs()
    df = load_master_dataset()

    late_reviews = df.loc[df["delivery_status"] == "Late", "review_score"]
    nonlate_reviews = df.loc[df["delivery_status"] != "Late", "review_score"]
    t_test_late = welch_t_test(late_reviews, nonlate_reviews)

    repeat_values = df.loc[df["customer_repeat_flag"] == True, "total_order_value"]
    onetime_values = df.loc[df["customer_repeat_flag"] == False, "total_order_value"]
    t_test_repeat = welch_t_test(repeat_values, onetime_values)

    anova_state_review = one_way_anova(df, "customer_state", "review_score")

    correlation_rows = []
    for feature in [
        "total_order_value",
        "delivery_time_days",
        "delivery_delay_days",
        "payment_installments",
        "total_items",
    ]:
        result = pearson_with_pvalue(df[feature], df["review_score"])
        correlation_rows.append(
            {
                "feature": feature,
                "target": "review_score",
                "pearson_r": round(result["r"], 4),
                "p_value_approx": result["p_value_approx"],
                "sample_size": result["n"],
            }
        )
    correlations = pd.DataFrame(correlation_rows)

    coefficients, regression_metrics = linear_regression_summary(
        df,
        [
            "delivery_delay_days",
            "delivery_time_days",
            "total_order_value",
            "payment_installments",
            "total_items",
        ],
        "review_score",
    )
    coefficients["coefficient"] = coefficients["coefficient"].round(4)

    value_segments = df.copy()
    value_segments["value_segment"] = pd.qcut(
        value_segments["total_order_value"],
        q=3,
        labels=["Low Value", "Mid Value", "High Value"],
    )
    segment_summary = (
        value_segments.groupby("value_segment", observed=True, as_index=False)
        .agg(
            order_count=("order_id", "count"),
            avg_order_value_brl=("total_order_value", "mean"),
            avg_review_score=("review_score", "mean"),
            avg_delivery_days=("delivery_time_days", "mean"),
            repeat_rate=("customer_repeat_flag", "mean"),
        )
        .assign(
            avg_order_value_brl=lambda x: x["avg_order_value_brl"].round(2),
            avg_review_score=lambda x: x["avg_review_score"].round(2),
            avg_delivery_days=lambda x: x["avg_delivery_days"].round(2),
            repeat_rate_pct=lambda x: (x["repeat_rate"] * 100).round(2),
        )
        .drop(columns=["repeat_rate"])
    )

    distribution_rows = []
    for column in [
        "total_order_value",
        "delivery_time_days",
        "delivery_delay_days",
        "review_score",
    ]:
        series = df[column].dropna()
        distribution_rows.append(
            {
                "column": column,
                "mean": round(series.mean(), 2),
                "median": round(series.median(), 2),
                "std_dev": round(series.std(), 2),
                "skewness": round(series.skew(), 2),
                "kurtosis": round(series.kurtosis(), 2),
            }
        )
    distributions = pd.DataFrame(distribution_rows)

    hypothesis_tests = pd.DataFrame(
        [
            {
                "test_name": "late_vs_nonlate_review_score",
                "metric": "review_score",
                "group_a": "Late",
                "group_b": "Non-Late",
                "group_a_mean": round(t_test_late["group_a_mean"], 4),
                "group_b_mean": round(t_test_late["group_b_mean"], 4),
                "difference_a_minus_b": round(t_test_late["difference_a_minus_b"], 4),
                "test_statistic": round(t_test_late["t_statistic"], 4),
                "p_value_approx": t_test_late["p_value_approx"],
                "significant_alpha_0_05": t_test_late["p_value_approx"] < 0.05,
            },
            {
                "test_name": "repeat_vs_onetime_order_value",
                "metric": "total_order_value",
                "group_a": "Repeat",
                "group_b": "One-time",
                "group_a_mean": round(t_test_repeat["group_a_mean"], 4),
                "group_b_mean": round(t_test_repeat["group_b_mean"], 4),
                "difference_a_minus_b": round(t_test_repeat["difference_a_minus_b"], 4),
                "test_statistic": round(t_test_repeat["t_statistic"], 4),
                "p_value_approx": t_test_repeat["p_value_approx"],
                "significant_alpha_0_05": t_test_repeat["p_value_approx"] < 0.05,
            },
            {
                "test_name": "anova_review_score_by_state",
                "metric": "review_score",
                "group_a": "customer_state",
                "group_b": "all_states",
                "group_a_mean": None,
                "group_b_mean": None,
                "difference_a_minus_b": None,
                "test_statistic": round(anova_state_review["f_statistic"], 4),
                "p_value_approx": None,
                "significant_alpha_0_05": anova_state_review["significant_flag"] == "Yes",
            },
        ]
    )

    write_csv(hypothesis_tests, paths["statistics"] / "hypothesis_tests.csv")
    write_csv(correlations, paths["statistics"] / "correlations.csv")
    write_csv(coefficients, paths["statistics"] / "regression_coefficients.csv")
    write_csv(segment_summary, paths["statistics"] / "customer_value_segments.csv")
    write_csv(distributions, paths["statistics"] / "distribution_summary.csv")

    metrics_payload = {
        "regression_metrics": regression_metrics,
        "anova_review_by_state": anova_state_review,
        "notes": {
            "t_tests": "Welch-style large-sample approximation implemented with numpy.",
            "anova": "F-statistic and eta-squared effect size computed without external statistics packages.",
            "regression": "Ordinary least squares solved with numpy.linalg.lstsq.",
        },
    }
    write_json(metrics_payload, paths["statistics"] / "statistical_metrics.json")

    summary_md = [
        "# Statistical Analysis Output",
        "",
        "## Hypothesis Tests",
        "",
        markdown_table(hypothesis_tests),
        "",
        "## Correlations Against Review Score",
        "",
        markdown_table(correlations),
        "",
        "## Regression Coefficients",
        "",
        markdown_table(coefficients),
        "",
        "## Customer Value Segments",
        "",
        markdown_table(segment_summary),
        "",
    ]
    (paths["statistics"] / "statistical_summary.md").write_text("\n".join(summary_md))

    print("Statistical outputs written to:", paths["statistics"])


if __name__ == "__main__":
    main()
