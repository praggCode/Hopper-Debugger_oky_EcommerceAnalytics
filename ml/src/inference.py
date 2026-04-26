from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd

from ml_utils import (
    kmeans,
    load_customers,
    load_orders,
    sigmoid,
    standardize_apply,
    standardize_fit,
    train_test_split,
)


ORDER_FEATURE_COLS = [
    "total_items",
    "total_price",
    "total_freight",
    "payment_installments",
    "product_weight_g",
    "total_order_value",
    "order_month",
    "order_year",
    "customer_state",
    "seller_state",
    "payment_type",
    "product_category_name_english",
]

ORDER_NUMERIC_COLS = [
    "total_items",
    "total_price",
    "total_freight",
    "payment_installments",
    "product_weight_g",
    "total_order_value",
    "order_year",
]

ORDER_CATEGORICAL_COLS = [
    "order_month",
    "customer_state",
    "seller_state",
    "payment_type",
    "product_category_name_english",
]

SEGMENT_FEATURE_COLS = [
    "total_orders",
    "total_spent",
    "avg_review_score",
    "avg_delay",
    "late_delivery_rate",
    "payment_installments",
]


def fit_logistic_regression(
    x_train: np.ndarray,
    y_train: np.ndarray,
    learning_rate: float = 0.05,
    epochs: int = 700,
) -> np.ndarray:
    weights = np.zeros(x_train.shape[1], dtype=float)
    positive_rate = y_train.mean()
    class_weight_pos = 0.5 / max(positive_rate, 1e-12)
    class_weight_neg = 0.5 / max(1 - positive_rate, 1e-12)

    for _ in range(epochs):
        preds = sigmoid(x_train @ weights)
        sample_weights = np.where(y_train == 1, class_weight_pos, class_weight_neg)
        gradient = (x_train.T @ ((preds - y_train) * sample_weights)) / len(y_train)
        weights -= learning_rate * gradient

    return weights


def _prepare_orders_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, dict]:
    ml_df = df[ORDER_FEATURE_COLS + ["is_late_delivery"]].copy()
    ml_df["order_month"] = ml_df["order_month"].fillna("unknown").astype(str)
    ml_df["order_year"] = ml_df["order_year"].fillna(int(df["order_year"].median()))

    medians = {}
    for col in ORDER_NUMERIC_COLS:
        median_value = float(ml_df[col].median())
        medians[col] = median_value
        ml_df[col] = ml_df[col].fillna(median_value)

    top_values = {}
    for col in ["customer_state", "seller_state", "product_category_name_english"]:
        ml_df[col] = ml_df[col].fillna("unknown").astype(str)
        top = ml_df[col].value_counts().head(12).index.tolist()
        top_values[col] = top
        ml_df[col] = np.where(ml_df[col].isin(top), ml_df[col], "other")

    ml_df["payment_type"] = ml_df["payment_type"].fillna("unknown").astype(str)

    x = pd.get_dummies(
        ml_df.drop(columns=["is_late_delivery"]),
        columns=ORDER_CATEGORICAL_COLS,
        drop_first=False,
        dtype=float,
    )
    y = ml_df["is_late_delivery"].astype(int)

    preprocess = {
        "medians": medians,
        "top_values": top_values,
        "feature_columns": list(x.columns),
    }
    return x, y, preprocess


def _encode_order_input(payload: dict, preprocess: dict) -> pd.DataFrame:
    row = {
        "total_items": float(payload.get("totalItems", 1)),
        "total_price": float(payload.get("totalOrderValue", 0)),
        "total_freight": float(payload.get("totalFreight", 0)),
        "payment_installments": float(payload.get("paymentInstallments", 1)),
        "product_weight_g": float(payload.get("productWeightG", 0)),
        "total_order_value": float(payload.get("totalOrderValue", 0)),
        "order_month": str(payload.get("orderMonth", "unknown")),
        "order_year": int(str(payload.get("orderMonth", "2018-01")).split("-")[0]),
        "customer_state": str(payload.get("customerState", "unknown")),
        "seller_state": str(payload.get("sellerState", "unknown")),
        "payment_type": str(payload.get("paymentType", "unknown")),
        "product_category_name_english": str(
            payload.get("productCategory", "bed_bath_table")
        ),
    }

    for col, values in preprocess["top_values"].items():
        if row[col] not in values:
            row[col] = "other"

    df = pd.DataFrame([row])
    encoded = pd.get_dummies(df, columns=ORDER_CATEGORICAL_COLS, drop_first=False, dtype=float)
    encoded = encoded.reindex(columns=preprocess["feature_columns"], fill_value=0.0)
    return encoded


def _build_driver_list(encoded_row: np.ndarray, feature_columns: list[str], weights: np.ndarray) -> list[dict]:
    feature_weights = weights[1:]
    contributions = encoded_row * feature_weights
    drivers = []
    for feature, contribution in zip(feature_columns, contributions):
        if abs(contribution) < 1e-9:
            continue
        drivers.append(
            {
                "label": feature.replace("_", " "),
                "impact": float(round(contribution, 4)),
            }
        )
    drivers.sort(key=lambda item: abs(item["impact"]), reverse=True)
    return drivers[:5]


@lru_cache(maxsize=1)
def get_late_delivery_artifacts() -> dict:
    orders = load_orders()
    x, y, preprocess = _prepare_orders_dataset(orders)

    model_df = x.copy()
    model_df["target"] = y
    train_df, test_df = train_test_split(model_df, test_size=0.2, random_state=42)

    x_train = train_df.drop(columns=["target"])
    x_test = test_df.drop(columns=["target"])
    y_train = train_df["target"].to_numpy(dtype=float)
    y_test = test_df["target"].to_numpy(dtype=float)

    x_test = x_test.reindex(columns=x_train.columns, fill_value=0.0)
    x_train_matrix, means, stds = standardize_fit(x_train.to_numpy(dtype=float))
    x_test_matrix = standardize_apply(x_test.to_numpy(dtype=float), means, stds)

    x_train_matrix = np.column_stack([np.ones(len(x_train_matrix)), x_train_matrix])
    x_test_matrix = np.column_stack([np.ones(len(x_test_matrix)), x_test_matrix])

    weights = fit_logistic_regression(x_train_matrix, y_train)
    test_probs = sigmoid(x_test_matrix @ weights)

    best_threshold = 0.5
    best_f1 = -1.0
    for threshold in np.arange(0.15, 0.61, 0.05):
        preds = (test_probs >= threshold).astype(int)
        tp = np.sum((y_test == 1) & (preds == 1))
        fp = np.sum((y_test == 0) & (preds == 1))
        fn = np.sum((y_test == 1) & (preds == 0))
        precision = tp / max(1, tp + fp)
        recall = tp / max(1, tp + fn)
        f1 = 2 * precision * recall / max(1e-12, precision + recall)
        if f1 > best_f1:
            best_f1 = float(f1)
            best_threshold = float(round(threshold, 2))

    return {
        "weights": weights,
        "means": means,
        "stds": stds,
        "threshold": best_threshold,
        "feature_columns": list(x_train.columns),
        "preprocess": preprocess,
    }


def predict_late_delivery(payload: dict) -> dict:
    artifacts = get_late_delivery_artifacts()
    encoded = _encode_order_input(payload, artifacts["preprocess"])
    standardized = standardize_apply(
        encoded.to_numpy(dtype=float),
        artifacts["means"],
        artifacts["stds"],
    )
    model_input = np.column_stack([np.ones(len(standardized)), standardized])
    probability = float(sigmoid(model_input @ artifacts["weights"])[0])

    if probability >= artifacts["threshold"]:
        label = "High Risk"
    elif probability >= artifacts["threshold"] * 0.7:
        label = "Medium Risk"
    else:
        label = "Low Risk"

    drivers = _build_driver_list(
        standardized[0],
        artifacts["feature_columns"],
        artifacts["weights"],
    )

    return {
        "probability": round(probability, 4),
        "label": label,
        "drivers": drivers,
    }


@lru_cache(maxsize=1)
def get_customer_segmentation_artifacts() -> dict:
    customers = load_customers()
    cluster_df = customers[SEGMENT_FEATURE_COLS].copy()
    medians = {}
    for col in SEGMENT_FEATURE_COLS:
        median_value = float(cluster_df[col].median())
        medians[col] = median_value
        cluster_df[col] = cluster_df[col].fillna(median_value)

    x_scaled, means, stds = standardize_fit(cluster_df.to_numpy(dtype=float))
    labels, centroids, _ = kmeans(x_scaled, n_clusters=4, random_state=42)

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
    actions = {
        "High Value Loyalists": "Protect with premium support and faster service.",
        "Stable Everyday Buyers": "Target with repeat purchase and cross-sell offers.",
        "At-Risk Delay Hit Customers": "Use service recovery and delay prevention support.",
        "Low Value Occasional Buyers": "Use simple onboarding and lightweight offers.",
    }
    colors = {
        "High Value Loyalists": "#1f9d84",
        "Stable Everyday Buyers": "#295fd6",
        "At-Risk Delay Hit Customers": "#d94b5a",
        "Low Value Occasional Buyers": "#7a56d8",
    }
    cluster_profile["segment_name"] = segment_names[: len(cluster_profile)]

    label_map = dict(zip(cluster_profile["cluster_id"], cluster_profile["segment_name"]))
    profile_map = {}
    for row in cluster_profile.to_dict(orient="records"):
        name = label_map[row["cluster_id"]]
        profile_map[row["cluster_id"]] = {
            "name": name,
            "action": actions[name],
            "color": colors[name],
            "avgSpent": float(row["avg_total_spent"]),
            "avgReview": float(row["avg_review_score"]),
            "avgDelay": float(row["avg_delay"]),
            "customers": int(row["customer_count"]),
        }

    return {
        "means": means,
        "stds": stds,
        "centroids": centroids,
        "medians": medians,
        "profiles": profile_map,
    }


def predict_customer_segment(payload: dict) -> dict:
    artifacts = get_customer_segmentation_artifacts()
    row = np.array(
        [
            float(payload.get("totalOrders", artifacts["medians"]["total_orders"])),
            float(payload.get("totalSpent", artifacts["medians"]["total_spent"])),
            float(payload.get("avgReviewScore", artifacts["medians"]["avg_review_score"])),
            float(payload.get("avgDelay", artifacts["medians"]["avg_delay"])),
            float(payload.get("lateDeliveryRate", artifacts["medians"]["late_delivery_rate"])),
            float(payload.get("paymentInstallments", artifacts["medians"]["payment_installments"])),
        ],
        dtype=float,
    ).reshape(1, -1)

    scaled = standardize_apply(row, artifacts["means"], artifacts["stds"])
    distances = np.sqrt(((artifacts["centroids"] - scaled[0]) ** 2).sum(axis=1))
    cluster_id = int(distances.argmin())
    return artifacts["profiles"][cluster_id]
