from __future__ import annotations

import numpy as np
import pandas as pd

from ml_utils import (
    ensure_ml_dirs,
    kmeans,
    load_customers,
    markdown_table,
    standardize_fit,
    write_json,
    write_markdown,
)


def segment_name(row: pd.Series) -> str:
    if row["total_spent"] == row["total_spent"].max():
        return "High Value Loyalists"
    return "Customer Segment"


def main() -> None:
    paths = ensure_ml_dirs()
    customers = load_customers()

    numeric_cols = [
        "total_orders",
        "total_spent",
        "avg_review_score",
        "avg_delay",
        "late_delivery_rate",
        "payment_installments",
    ]

    cluster_df = customers[numeric_cols].copy()
    for col in numeric_cols:
        cluster_df[col] = cluster_df[col].fillna(cluster_df[col].median())

    x_scaled, means, stds = standardize_fit(cluster_df.to_numpy(dtype=float))

    elbow_rows = []
    best_k = 4
    for k in range(2, 7):
        _, _, inertia = kmeans(x_scaled, n_clusters=k, random_state=42)
        elbow_rows.append({"k": k, "inertia": round(inertia, 4)})
    elbow_df = pd.DataFrame(elbow_rows)

    labels, centroids, inertia = kmeans(x_scaled, n_clusters=best_k, random_state=42)
    segmented = customers.copy()
    segmented["cluster_id"] = labels

    cluster_profile = (
        segmented.groupby("cluster_id", as_index=False)
        .agg(
            customer_count=("customer_id", "count"),
            avg_total_orders=("total_orders", "mean"),
            avg_total_spent=("total_spent", "mean"),
            avg_review_score=("avg_review_score", "mean"),
            avg_delay=("avg_delay", "mean"),
            avg_late_delivery_rate=("late_delivery_rate", "mean"),
            avg_payment_installments=("payment_installments", "mean"),
        )
        .round(2)
        .sort_values("avg_total_spent", ascending=False)
        .reset_index(drop=True)
    )

    segment_names = [
        "High Value Loyalists",
        "Stable Everyday Buyers",
        "At-Risk Delay Hit Customers",
        "Low Value Occasional Buyers",
    ]
    cluster_profile["segment_name"] = segment_names[: len(cluster_profile)]

    label_map = dict(zip(cluster_profile["cluster_id"], cluster_profile["segment_name"]))
    segmented["segment_name"] = segmented["cluster_id"].map(label_map)

    city_summary = (
        segmented.groupby(["segment_name", "customer_state"], as_index=False)
        .size()
        .rename(columns={"size": "customer_count"})
        .sort_values(["segment_name", "customer_count"], ascending=[True, False])
    )

    cluster_profile.to_csv(paths["customer_segmentation"] / "cluster_profiles.csv", index=False)
    segmented.to_csv(
        paths["customer_segmentation"] / "customer_segments.csv",
        index=False,
    )
    elbow_df.to_csv(paths["customer_segmentation"] / "elbow_scores.csv", index=False)
    city_summary.head(50).to_csv(
        paths["customer_segmentation"] / "segment_state_distribution.csv", index=False
    )

    payload = {
        "selected_k": best_k,
        "final_inertia": inertia,
        "feature_means": means,
        "feature_stds": stds,
        "segment_distribution": segmented["segment_name"].value_counts().to_dict(),
    }
    write_json(payload, paths["customer_segmentation"] / "metrics.json")

    summary_lines = [
        "# Customer Segmentation",
        "",
        "## Clustering Summary",
        "",
        f"- Customers used: {len(segmented)}",
        f"- Selected number of clusters: {best_k}",
        f"- Final inertia: {inertia:.4f}",
        "",
        "## Cluster Profiles",
        "",
        markdown_table(
            cluster_profile[
                [
                    "segment_name",
                    "customer_count",
                    "avg_total_orders",
                    "avg_total_spent",
                    "avg_review_score",
                    "avg_delay",
                    "avg_late_delivery_rate",
                    "avg_payment_installments",
                ]
            ]
        ),
        "",
        "## Business Use",
        "",
        "- High Value Loyalists: protect with premium service and fast logistics.",
        "- Stable Everyday Buyers: target with cross-sell and repeat-purchase nudges.",
        "- At-Risk Delay Hit Customers: use service recovery and delay prevention campaigns.",
        "- Low Value Occasional Buyers: use lightweight offers and onboarding flows.",
    ]
    write_markdown(summary_lines, paths["customer_segmentation"] / "summary.md")

    print("Customer segmentation outputs written to:", paths["customer_segmentation"])


if __name__ == "__main__":
    main()
