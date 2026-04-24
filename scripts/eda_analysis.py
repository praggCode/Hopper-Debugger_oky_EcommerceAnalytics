from __future__ import annotations

from pathlib import Path

import pandas as pd

from analysis_utils import (
    ensure_output_dirs,
    format_currency,
    load_master_dataset,
    markdown_table,
    top_revenue_share,
    write_csv,
    write_json,
)


def build_kpi_summary(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            ("total_revenue_brl", round(df["total_order_value"].sum(), 2)),
            ("total_orders", int(len(df))),
            ("unique_customers", int(df["customer_unique_id"].nunique())),
            ("average_order_value_brl", round(df["total_order_value"].mean(), 2)),
            ("median_order_value_brl", round(df["total_order_value"].median(), 2)),
            ("average_delivery_time_days", round(df["delivery_time_days"].mean(), 2)),
            ("late_delivery_rate_pct", round(df["delivery_status"].eq("Late").mean() * 100, 2)),
            (
                "repeat_customer_rate_pct",
                round(df["customer_repeat_flag"].mean() * 100, 2),
            ),
            ("average_review_score", round(df["review_score"].mean(), 2)),
            ("top_10pct_revenue_share_pct", round(top_revenue_share(df["total_order_value"], 0.90) * 100, 2)),
            ("top_20pct_revenue_share_pct", round(top_revenue_share(df["total_order_value"], 0.80) * 100, 2)),
        ],
        columns=["metric", "value"],
    )


def main() -> None:
    paths = ensure_output_dirs()
    df = load_master_dataset()

    kpi_summary = build_kpi_summary(df)

    monthly_revenue = (
        df.groupby("month_year", as_index=False)["total_order_value"]
        .sum()
        .rename(columns={"total_order_value": "revenue_brl"})
        .sort_values("month_year")
    )

    delivery_status = (
        df["delivery_status"]
        .value_counts(normalize=True)
        .rename_axis("delivery_status")
        .reset_index(name="share")
    )
    delivery_status["share_pct"] = (delivery_status["share"] * 100).round(2)

    retention_profile = (
        df.groupby("customer_repeat_flag", as_index=False)
        .agg(
            orders=("order_id", "count"),
            unique_customers=("customer_unique_id", "nunique"),
            avg_order_value_brl=("total_order_value", "mean"),
            avg_review_score=("review_score", "mean"),
            late_delivery_rate=("is_late_delivery", "mean"),
        )
        .assign(
            customer_type=lambda x: x["customer_repeat_flag"].map(
                {False: "One-time", True: "Repeat"}
            ),
            avg_order_value_brl=lambda x: x["avg_order_value_brl"].round(2),
            avg_review_score=lambda x: x["avg_review_score"].round(2),
            late_delivery_rate_pct=lambda x: (x["late_delivery_rate"] * 100).round(2),
        )
        .drop(columns=["late_delivery_rate", "customer_repeat_flag"])
    )

    state_performance = (
        df.groupby("customer_state", as_index=False)
        .agg(
            order_count=("order_id", "count"),
            revenue_brl=("total_order_value", "sum"),
            avg_order_value_brl=("total_order_value", "mean"),
            avg_review_score=("review_score", "mean"),
            late_delivery_rate=("is_late_delivery", "mean"),
        )
        .assign(
            revenue_brl=lambda x: x["revenue_brl"].round(2),
            avg_order_value_brl=lambda x: x["avg_order_value_brl"].round(2),
            avg_review_score=lambda x: x["avg_review_score"].round(2),
            late_delivery_rate_pct=lambda x: (x["late_delivery_rate"] * 100).round(2),
        )
        .drop(columns=["late_delivery_rate"])
        .sort_values("revenue_brl", ascending=False)
    )

    category_performance = (
        df.groupby("product_category_name_english", as_index=False)
        .agg(
            order_count=("order_id", "count"),
            revenue_brl=("total_order_value", "sum"),
            avg_review_score=("review_score", "mean"),
            avg_delivery_days=("delivery_time_days", "mean"),
        )
        .assign(
            revenue_brl=lambda x: x["revenue_brl"].round(2),
            avg_review_score=lambda x: x["avg_review_score"].round(2),
            avg_delivery_days=lambda x: x["avg_delivery_days"].round(2),
        )
        .sort_values("revenue_brl", ascending=False)
    )

    payment_mix = (
        df["payment_type"]
        .value_counts(normalize=True)
        .rename_axis("payment_type")
        .reset_index(name="share")
    )
    payment_mix["share_pct"] = (payment_mix["share"] * 100).round(2)

    review_distribution = (
        df["review_score"]
        .value_counts()
        .sort_index()
        .rename_axis("review_score")
        .reset_index(name="order_count")
    )

    write_csv(kpi_summary, paths["eda"] / "kpi_summary.csv")
    write_csv(monthly_revenue, paths["eda"] / "monthly_revenue.csv")
    write_csv(delivery_status, paths["eda"] / "delivery_status_distribution.csv")
    write_csv(retention_profile, paths["eda"] / "customer_retention_profile.csv")
    write_csv(state_performance, paths["eda"] / "state_performance.csv")
    write_csv(category_performance, paths["eda"] / "category_performance.csv")
    write_csv(payment_mix, paths["eda"] / "payment_mix.csv")
    write_csv(review_distribution, paths["eda"] / "review_distribution.csv")

    headline_summary = {
        "dataset_rows": int(len(df)),
        "dataset_columns": int(df.shape[1]),
        "total_revenue": format_currency(df["total_order_value"].sum()),
        "average_order_value": round(df["total_order_value"].mean(), 2),
        "best_revenue_month": monthly_revenue.sort_values("revenue_brl", ascending=False)
        .head(1)
        .to_dict(orient="records")[0],
        "top_revenue_state": state_performance.head(1).to_dict(orient="records")[0],
        "worst_late_state_min_500_orders": state_performance[state_performance["order_count"] >= 500]
        .sort_values("late_delivery_rate_pct", ascending=False)
        .head(1)
        .to_dict(orient="records")[0],
    }
    write_json(headline_summary, paths["eda"] / "headline_summary.json")

    summary_md = [
        "# EDA Output",
        "",
        "## KPI Snapshot",
        "",
        markdown_table(kpi_summary),
        "",
        "## Top 5 States By Revenue",
        "",
        markdown_table(state_performance.head(5)),
        "",
        "## Highest Late-Delivery States (min 500 orders)",
        "",
        markdown_table(
            state_performance[state_performance["order_count"] >= 500]
            .sort_values("late_delivery_rate_pct", ascending=False)
            .head(5)
        ),
        "",
        "## Top 5 Categories By Revenue",
        "",
        markdown_table(category_performance.head(5)),
        "",
    ]
    (paths["eda"] / "eda_summary.md").write_text("\n".join(summary_md))

    print("EDA outputs written to:", paths["eda"])


if __name__ == "__main__":
    main()
