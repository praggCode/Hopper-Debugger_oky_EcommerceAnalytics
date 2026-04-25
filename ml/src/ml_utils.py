from __future__ import annotations

from pathlib import Path
import json

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MASTER_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "olist_master_cleaned.csv"
CUSTOMER_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "tableau_customer_dataset.csv"
ML_ROOT = PROJECT_ROOT / "ml"
OUTPUT_ROOT = ML_ROOT / "outputs"


def ensure_ml_dirs() -> dict[str, Path]:
    late = OUTPUT_ROOT / "late_delivery_prediction"
    segmentation = OUTPUT_ROOT / "customer_segmentation"
    for path in [ML_ROOT, OUTPUT_ROOT, late, segmentation]:
        path.mkdir(parents=True, exist_ok=True)
    return {
        "root": OUTPUT_ROOT,
        "late_delivery_prediction": late,
        "customer_segmentation": segmentation,
    }


def load_orders() -> pd.DataFrame:
    return pd.read_csv(MASTER_DATA_PATH)


def load_customers() -> pd.DataFrame:
    return pd.read_csv(CUSTOMER_DATA_PATH)


def write_json(payload: dict, path: Path) -> None:
    path.write_text(json.dumps(payload, indent=2, default=_json_default))


def write_markdown(lines: list[str], path: Path) -> None:
    path.write_text("\n".join(lines))


def _json_default(obj):
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return str(obj)


def train_test_split(
    df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(random_state)
    mask = rng.random(len(df)) >= test_size
    return df.loc[mask].copy(), df.loc[~mask].copy()


def standardize_fit(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    means = x.mean(axis=0)
    stds = x.std(axis=0)
    stds[stds == 0] = 1.0
    transformed = (x - means) / stds
    return transformed, means, stds


def standardize_apply(x: np.ndarray, means: np.ndarray, stds: np.ndarray) -> np.ndarray:
    safe_stds = stds.copy()
    safe_stds[safe_stds == 0] = 1.0
    return (x - means) / safe_stds


def sigmoid(z: np.ndarray) -> np.ndarray:
    z = np.clip(z, -500, 500)
    return 1.0 / (1.0 + np.exp(-z))


def confusion_counts(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, int]:
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    return {"tp": tp, "tn": tn, "fp": fp, "fn": fn}


def classification_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    counts = confusion_counts(y_true, y_pred)
    tp = counts["tp"]
    tn = counts["tn"]
    fp = counts["fp"]
    fn = counts["fn"]

    accuracy = (tp + tn) / max(1, len(y_true))
    precision = tp / max(1, tp + fp)
    recall = tp / max(1, tp + fn)
    f1 = 2 * precision * recall / max(1e-12, precision + recall)

    return {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        **counts,
    }


def markdown_table(df: pd.DataFrame) -> str:
    header = "| " + " | ".join(df.columns.astype(str)) + " |"
    separator = "| " + " | ".join(["---"] * len(df.columns)) + " |"
    rows = [
        "| " + " | ".join(str(value) for value in row) + " |"
        for row in df.astype(object).itertuples(index=False, name=None)
    ]
    return "\n".join([header, separator] + rows)


def kmeans(
    x: np.ndarray, n_clusters: int, random_state: int = 42, max_iter: int = 100
) -> tuple[np.ndarray, np.ndarray, float]:
    rng = np.random.default_rng(random_state)
    initial_idx = rng.choice(len(x), size=n_clusters, replace=False)
    centroids = x[initial_idx].copy()

    for _ in range(max_iter):
        distances = np.sqrt(((x[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2))
        labels = distances.argmin(axis=1)

        new_centroids = centroids.copy()
        for cluster_id in range(n_clusters):
            cluster_points = x[labels == cluster_id]
            if len(cluster_points) > 0:
                new_centroids[cluster_id] = cluster_points.mean(axis=0)

        if np.allclose(new_centroids, centroids):
            centroids = new_centroids
            break
        centroids = new_centroids

    distances = np.sqrt(((x[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2))
    labels = distances.argmin(axis=1)
    inertia = float(np.sum((x - centroids[labels]) ** 2))
    return labels, centroids, inertia
