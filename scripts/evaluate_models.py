#!/usr/bin/env python
"""Evaluate and compare all trained models (ANN, CNN, LSTM) on the test dataset."""
from __future__ import annotations

import json
import pickle
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from tensorflow import keras

from scripts.common import (
    ARTIFACTS_DIR,
    MODELS_DIR,
    PLOTS_DIR,
    RANDOM_SEED,
    REPORTS_DIR,
    ensure_directories,
    load_processed_training,
    save_json,
    set_global_seed,
)


def evaluate_all():
    print("=" * 60)
    print("Vista Flare - Multi-Model Evaluation & Comparison")
    print("=" * 60)

    ensure_directories()
    set_global_seed(RANDOM_SEED)

    # 1. Load data
    X, y, skill_names, role_names, _ = load_processed_training()

    scaler_path = ARTIFACTS_DIR / "scaler.pkl"
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)

    # Replicate identical split
    _, X_temp, _, y_temp = train_test_split(
        X, y, test_size=0.30, random_state=RANDOM_SEED, stratify=y
    )
    _, X_test, _, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=RANDOM_SEED, stratify=y_temp
    )

    X_test_scaled = scaler.transform(X_test)
    X_test_3d = np.expand_dims(X_test_scaled, axis=-1)

    models_config = [
        {
            "name": "ANN (MLP)",
            "key": "ann",
            "type": "Primary Production Model",
            "path": MODELS_DIR / "ann_model.keras",
            "input": X_test_scaled,
            "metrics_file": REPORTS_DIR / "ann_metrics.json",
        },
        {
            "name": "1D CNN",
            "key": "cnn",
            "type": "Comparative Experiment",
            "path": MODELS_DIR / "cnn" / "cnn_model.keras",
            "input": X_test_3d,
            "metrics_file": REPORTS_DIR / "cnn_metrics.json",
        },
        {
            "name": "LSTM",
            "key": "lstm",
            "type": "Comparative Experiment",
            "path": MODELS_DIR / "lstm" / "lstm_model.keras",
            "input": X_test_3d,
            "metrics_file": REPORTS_DIR / "lstm_metrics.json",
        },
    ]

    results = []

    for cfg in models_config:
        model_path = cfg["path"]
        print(f"\nChecking {cfg['name']} at {model_path}...")
        if not model_path.exists():
            print(f"  [-] Model file not found. Skipping.")
            continue

        try:
            model = keras.models.load_model(model_path)
            param_count = model.count_params()

            # Latency benchmark
            t0 = time.time()
            probs = model.predict(cfg["input"], verbose=0)
            latency_ms = round(((time.time() - t0) / len(cfg["input"])) * 1000, 3)

            eval_res = model.evaluate(cfg["input"], y_test, verbose=0)
            loss = float(eval_res[0])
            accuracy = float(eval_res[1])
            top3 = float(eval_res[2]) if len(eval_res) > 2 else 0.0

            y_pred = np.argmax(probs, axis=1)
            precision_w = float(precision_score(y_test, y_pred, average="weighted", zero_division=0))
            recall_w = float(recall_score(y_test, y_pred, average="weighted", zero_division=0))
            f1_w = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))

            # Retrieve training time if recorded
            train_time = "N/A"
            if cfg["metrics_file"].exists():
                with open(cfg["metrics_file"], "r", encoding="utf-8") as mf:
                    m_data = json.load(mf)
                    if "training_time_seconds" in m_data:
                        train_time = f"{m_data['training_time_seconds']}s"

            res = {
                "Model": cfg["name"],
                "Role": cfg["type"],
                "Accuracy": round(accuracy, 4),
                "Top-3 Accuracy": round(top3, 4),
                "Precision": round(precision_w, 4),
                "Recall": round(recall_w, 4),
                "F1 Score": round(f1_w, 4),
                "Loss": round(loss, 4),
                "Parameters": param_count,
                "Latency (ms/sample)": latency_ms,
                "Training Time": train_time,
            }
            results.append(res)
            print(f"  [OK] Accuracy: {accuracy:.4f} | Top-3: {top3:.4f} | F1: {f1_w:.4f} | Params: {param_count:,}")
        except Exception as e:
            print(f"  [-] Failed to evaluate {cfg['name']}: {e}")

    if not results:
        print("\nNo models could be evaluated.")
        return

    df_comp = pd.DataFrame(results)
    df_comp.to_csv(REPORTS_DIR / "model_comparison.csv", index=False)
    save_json(REPORTS_DIR / "model_comparison.json", results)
    print(f"\n[OK] Saved comparison table to reports/model_comparison.csv and reports/model_comparison.json")

    # Generate visual comparison chart
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(10, 6))

    models_names = [r["Model"] for r in results]
    acc_scores = [r["Accuracy"] for r in results]
    top3_scores = [r["Top-3 Accuracy"] for r in results]
    f1_scores = [r["F1 Score"] for r in results]

    x = np.arange(len(models_names))
    width = 0.25

    rects1 = ax.bar(x - width, acc_scores, width, label="Top-1 Accuracy", color="#3b82f6")
    rects2 = ax.bar(x, top3_scores, width, label="Top-3 Accuracy", color="#10b981")
    rects3 = ax.bar(x + width, f1_scores, width, label="Weighted F1", color="#8b5cf6")

    ax.set_title("Vista Flare - Deep Learning Model Comparison", fontsize=15, fontweight="bold")
    ax.set_ylabel("Score (0.0 - 1.0)")
    ax.set_xticks(x)
    ax.set_xticklabels(models_names, fontsize=11, fontweight="medium")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.25)

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(
                f"{height:.2f}",
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)

    fig.tight_layout()
    comp_plot_path = PLOTS_DIR / "model_comparison.png"
    fig.savefig(comp_plot_path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Saved comparison plot to {comp_plot_path}")

    print("\n" + "=" * 60)
    print("Model Comparison Summary:")
    print("=" * 60)
    print(df_comp[["Model", "Accuracy", "Top-3 Accuracy", "F1 Score", "Parameters"]].to_string(index=False))
    print("=" * 60)


if __name__ == "__main__":
    evaluate_all()
