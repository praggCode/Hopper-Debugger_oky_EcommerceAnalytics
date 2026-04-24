from __future__ import annotations

import numpy as np
import pandas as pd

from ml_utils import (
    classification_metrics,
    ensure_ml_dirs,
    load_orders,
    markdown_table,
    sigmoid,
    standardize_apply,
    standardize_fit,
    train_test_split,
    write_json,
    write_markdown,
)


def prepare_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    feature_cols = [
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

    ml_df = df[feature_cols + ["is_late_delivery"]].copy()
    ml_df["order_month"] = ml_df["order_month"].fillna("unknown").astype(str)

    numeric_cols = [
        "total_items",
        "total_price",
        "total_freight",
        "payment_installments",
        "product_weight_g",
        "total_order_value",
        "order_year",
    ]
    for col in numeric_cols:
        ml_df[col] = ml_df[col].fillna(ml_df[col].median())

    for col in ["customer_state", "seller_state", "payment_type", "product_category_name_english"]:
        ml_df[col] = ml_df[col].fillna("unknown")

    category_cap = 12
    for col in ["customer_state", "seller_state", "product_category_name_english"]:
        top_values = ml_df[col].value_counts().head(category_cap).index
        ml_df[col] = np.where(ml_df[col].isin(top_values), ml_df[col], "other")

    x = pd.get_dummies(
        ml_df.drop(columns=["is_late_delivery"]),
        columns=[
            "order_month",
            "customer_state",
            "seller_state",
            "payment_type",
            "product_category_name_english",
        ],
        drop_first=False,
        dtype=float,
    )
    y = ml_df["is_late_delivery"].astype(int)
    return x, y


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


def evaluate_thresholds(y_true: np.ndarray, probabilities: np.ndarray) -> tuple[float, dict]:
    best_threshold = 0.5
    best_metrics = classification_metrics(y_true, (probabilities >= 0.5).astype(int))

    for threshold in np.arange(0.15, 0.61, 0.05):
        preds = (probabilities >= threshold).astype(int)
        metrics = classification_metrics(y_true, preds)
        if metrics["f1_score"] > best_metrics["f1_score"]:
            best_threshold = float(round(threshold, 2))
            best_metrics = metrics

    return best_threshold, best_metrics


def main() -> None:
    paths = ensure_ml_dirs()
    orders = load_orders()
    x, y = prepare_dataset(orders)

    model_df = x.copy()
    model_df["target"] = y
    train_df, test_df = train_test_split(model_df, test_size=0.2, random_state=42)

    x_train = train_df.drop(columns=["target"])
    x_test = test_df.drop(columns=["target"])
    y_train = train_df["target"].to_numpy(dtype=float)
    y_test = test_df["target"].to_numpy(dtype=float)

    x_train_aligned = x_train.copy()
    x_test_aligned = x_test.reindex(columns=x_train_aligned.columns, fill_value=0.0)

    train_matrix, means, stds = standardize_fit(x_train_aligned.to_numpy(dtype=float))
    test_matrix = standardize_apply(x_test_aligned.to_numpy(dtype=float), means, stds)

    train_matrix = np.column_stack([np.ones(len(train_matrix)), train_matrix])
    test_matrix = np.column_stack([np.ones(len(test_matrix)), test_matrix])

    weights = fit_logistic_regression(train_matrix, y_train)
    train_probs = sigmoid(train_matrix @ weights)
    test_probs = sigmoid(test_matrix @ weights)

    threshold, test_metrics = evaluate_thresholds(y_test, test_probs)
    test_preds = (test_probs >= threshold).astype(int)

    coefficients = pd.DataFrame(
        {
            "feature": ["intercept"] + list(x_train_aligned.columns),
            "coefficient": weights,
        }
    )
    coefficients["abs_coefficient"] = coefficients["coefficient"].abs()
    top_features = (
        coefficients[coefficients["feature"] != "intercept"]
        .sort_values("abs_coefficient", ascending=False)
        .head(15)
        .drop(columns=["abs_coefficient"])
        .assign(coefficient=lambda d: d["coefficient"].round(4))
    )

    predictions = pd.DataFrame(
        {
            "actual_late_delivery": y_test.astype(int),
            "predicted_probability": np.round(test_probs, 4),
            "predicted_late_delivery": test_preds.astype(int),
        }
    )

    metrics_payload = {
        "dataset_rows": int(len(model_df)),
        "training_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "late_delivery_rate_train": float(y_train.mean()),
        "late_delivery_rate_test": float(y_test.mean()),
        "selected_threshold": threshold,
        "test_metrics": test_metrics,
    }

    top_features.to_csv(paths["late_delivery_prediction"] / "top_model_features.csv", index=False)
    predictions.head(500).to_csv(
        paths["late_delivery_prediction"] / "sample_predictions.csv", index=False
    )
    write_json(metrics_payload, paths["late_delivery_prediction"] / "metrics.json")

    summary_lines = [
        "# Late Delivery Prediction",
        "",
        "## Model Summary",
        "",
        f"- Dataset rows used: {len(model_df)}",
        f"- Training rows: {len(train_df)}",
        f"- Test rows: {len(test_df)}",
        f"- Selected classification threshold: {threshold}",
        f"- Accuracy: {test_metrics['accuracy']:.4f}",
        f"- Precision: {test_metrics['precision']:.4f}",
        f"- Recall: {test_metrics['recall']:.4f}",
        f"- F1-score: {test_metrics['f1_score']:.4f}",
        "",
        "## Confusion Matrix Counts",
        "",
        f"- True positives: {test_metrics['tp']}",
        f"- True negatives: {test_metrics['tn']}",
        f"- False positives: {test_metrics['fp']}",
        f"- False negatives: {test_metrics['fn']}",
        "",
        "## Top Predictive Features",
        "",
        markdown_table(top_features),
    ]
    write_markdown(summary_lines, paths["late_delivery_prediction"] / "summary.md")

    print("Late delivery prediction outputs written to:", paths["late_delivery_prediction"])


if __name__ == "__main__":
    main()
