#!/usr/bin/env python
"""Train the Vista Flare ANN/MLP career recommendation model."""
from __future__ import annotations

import json
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import tensorflow as tf
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow import keras
from tensorflow.keras import layers

from scripts.common import (
    ARTIFACTS_DIR,
    CLASSIFICATION_DIR,
    CONFUSION_DIR,
    MODELS_DIR,
    PLOTS_DIR,
    PROCESSED_DIR,
    RANDOM_SEED,
    REPORTS_DIR,
    ensure_directories,
    load_processed_training,
    save_json,
    set_global_seed,
)

MODEL_NAME = "ann"
MODEL_VERSION = "ANN-v1"
EPOCHS = 35
BATCH_SIZE = 64
LEARNING_RATE = 0.001


def build_ann(input_dim: int, num_classes: int) -> keras.Model:
    model = keras.Sequential(
        [
            layers.Input(shape=(input_dim,), name="skill_vector"),
            layers.Dense(128, activation="relu", name="dense_128_relu"),
            layers.Dropout(0.30, name="dropout_30"),
            layers.Dense(64, activation="relu", name="dense_64_relu"),
            layers.Dropout(0.20, name="dropout_20"),
            layers.Dense(32, activation="relu", name="dense_32_relu"),
            layers.Dense(num_classes, activation="softmax", name="career_softmax"),
        ],
        name="vista_flare_ann",
    )
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy", keras.metrics.SparseTopKCategoricalAccuracy(k=3, name="top_3_accuracy")],
    )
    return model


def plot_history(history: keras.callbacks.History) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    colors = {"train": "#2563eb", "val": "#dc2626"}

    epochs = range(1, len(history.history["accuracy"]) + 1)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(epochs, history.history["accuracy"], label="Training Accuracy", color=colors["train"], linewidth=2.2)
    ax.plot(epochs, history.history["val_accuracy"], label="Validation Accuracy", color=colors["val"], linewidth=2.2)
    ax.set_title("Vista Flare ANN Accuracy", fontsize=16, fontweight="bold")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Accuracy")
    ax.legend()
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "ann_accuracy.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(epochs, history.history["loss"], label="Training Loss", color=colors["train"], linewidth=2.2)
    ax.plot(epochs, history.history["val_loss"], label="Validation Loss", color=colors["val"], linewidth=2.2)
    ax.set_title("Vista Flare ANN Loss", fontsize=16, fontweight="bold")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Sparse Categorical Crossentropy")
    ax.legend()
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "ann_loss.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def save_confusion_matrices(y_true: np.ndarray, y_pred: np.ndarray, role_names: list[str]) -> None:
    cm = confusion_matrix(y_true, y_pred)
    np.savetxt(CONFUSION_DIR / "ann_confusion_matrix_full.csv", cm, delimiter=",", fmt="%d")

    # Full heatmap with labels suppressed for readability on 85 classes.
    fig, ax = plt.subplots(figsize=(18, 16))
    sns.heatmap(cm, cmap="Blues", cbar=True, ax=ax, xticklabels=False, yticklabels=False)
    ax.set_title("Vista Flare ANN Full Confusion Matrix (85 Roles)", fontsize=16, fontweight="bold")
    ax.set_xlabel("Predicted Role")
    ax.set_ylabel("Actual Role")
    fig.tight_layout()
    fig.savefig(CONFUSION_DIR / "ann_confusion_matrix_full.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    # Selected top-supported classes for readable viva display.
    counts = np.bincount(y_true, minlength=len(role_names))
    top_indices = np.argsort(counts)[-20:]
    selected_cm = cm[np.ix_(top_indices, top_indices)]
    selected_labels = [role_names[i] for i in top_indices]
    fig, ax = plt.subplots(figsize=(16, 13))
    sns.heatmap(selected_cm, cmap="Blues", annot=True, fmt="d", cbar=True, ax=ax,
                xticklabels=selected_labels, yticklabels=selected_labels, linewidths=0.5)
    ax.set_title("Vista Flare ANN Selected Confusion Matrix", fontsize=16, fontweight="bold")
    ax.set_xlabel("Predicted Role")
    ax.set_ylabel("Actual Role")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=8)
    plt.setp(ax.get_yticklabels(), rotation=0, fontsize=8)
    fig.tight_layout()
    fig.savefig(CONFUSION_DIR / "ann_confusion_matrix_selected.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def evaluate(model: keras.Model, X_test: np.ndarray, y_test: np.ndarray, role_names: list[str]) -> dict:
    loss, accuracy, top3 = model.evaluate(X_test, y_test, verbose=0)
    probabilities = model.predict(X_test, verbose=0)
    y_pred = np.argmax(probabilities, axis=1)

    precision_macro = precision_score(y_test, y_pred, average="macro", zero_division=0)
    recall_macro = recall_score(y_test, y_pred, average="macro", zero_division=0)
    f1_macro = f1_score(y_test, y_pred, average="macro", zero_division=0)
    precision_weighted = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    recall_weighted = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1_weighted = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    report = classification_report(y_test, y_pred, target_names=role_names, zero_division=0)
    (CLASSIFICATION_DIR / "ann_classification_report.txt").write_text(report, encoding="utf-8")

    report_dict = classification_report(y_test, y_pred, target_names=role_names, zero_division=0, output_dict=True)
    pd.DataFrame(report_dict).transpose().to_csv(CLASSIFICATION_DIR / "ann_classification_report.csv")

    save_confusion_matrices(y_test, y_pred, role_names)

    return {
        "model": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "loss": float(loss),
        "accuracy": float(accuracy),
        "top_3_accuracy": float(top3),
        "precision_macro": float(precision_macro),
        "recall_macro": float(recall_macro),
        "f1_macro": float(f1_macro),
        "precision_weighted": float(precision_weighted),
        "recall_weighted": float(recall_weighted),
        "f1_weighted": float(f1_weighted),
    }


def main() -> None:
    print("=" * 60)
    print("Vista Flare - ANN Training")
    print("=" * 60)

    ensure_directories()
    set_global_seed(RANDOM_SEED)

    print("\n[1/8] Loading processed training data...")
    X, y, skill_names, role_names, df = load_processed_training()
    print(f"  - X shape: {X.shape}")
    print(f"  - y shape: {y.shape}")
    print(f"  - Skills: {len(skill_names)}")
    print(f"  - Classes: {len(role_names)}")

    print("\n[2/8] Splitting train/validation/test data...")
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, random_state=RANDOM_SEED, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=RANDOM_SEED, stratify=y_temp
    )
    print(f"  - Train: {len(X_train)}")
    print(f"  - Validation: {len(X_val)}")
    print(f"  - Test: {len(X_test)}")

    print("\n[3/8] Scaling features...")
    scaler = StandardScaler(with_mean=False)
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    with open(ARTIFACTS_DIR / "scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    with open(ARTIFACTS_DIR / "skill_encoder.pkl", "wb") as f:
        pickle.dump({"skills": skill_names, "skill_to_index": {s: i for i, s in enumerate(skill_names)}}, f)
    with open(ARTIFACTS_DIR / "label_encoder.pkl", "wb") as f:
        pickle.dump({"roles": role_names, "role_to_index": {r: i for i, r in enumerate(role_names)}}, f)

    print("\n[4/8] Building ANN model...")
    model = build_ann(input_dim=X.shape[1], num_classes=len(role_names))
    model.summary(print_fn=lambda line: print("  " + line))

    print("\n[5/8] Training ANN model...")
    checkpoint_path = MODELS_DIR / "ann_model.keras"
    callbacks = [
        keras.callbacks.EarlyStopping(monitor="val_loss", patience=8, restore_best_weights=True),
        keras.callbacks.ModelCheckpoint(filepath=checkpoint_path, monitor="val_loss", save_best_only=True),
        keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=4, min_lr=1e-5),
    ]
    history = model.fit(
        X_train_scaled,
        y_train,
        validation_data=(X_val_scaled, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=callbacks,
        verbose=1,
    )

    print("\n[6/8] Saving history and plots...")
    pd.DataFrame(history.history).to_csv(REPORTS_DIR / "ann_training_history.csv", index=False)
    plot_history(history)

    print("\n[7/8] Evaluating test set...")
    best_model = keras.models.load_model(checkpoint_path)
    metrics = evaluate(best_model, X_test_scaled, y_test, role_names)
    metrics.update({
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "dataset_version": "synthetic-role-skills-v1",
        "framework_version": f"tensorflow-{tf.__version__}",
        "num_skills": len(skill_names),
        "num_classes": len(role_names),
        "training_samples": int(len(X_train)),
        "validation_samples": int(len(X_val)),
        "test_samples": int(len(X_test)),
        "epochs_ran": int(len(history.history["loss"])),
        "batch_size": BATCH_SIZE,
        "learning_rate": LEARNING_RATE,
        "architecture": "Dense(128 ReLU) -> Dropout(0.30) -> Dense(64 ReLU) -> Dropout(0.20) -> Dense(32 ReLU) -> Dense(N Softmax)",
    })
    save_json(REPORTS_DIR / "ann_metrics.json", metrics)

    comparison_path = REPORTS_DIR / "model_comparison.csv"
    pd.DataFrame([
        {
            "model": "ANN",
            "accuracy": metrics["accuracy"],
            "top_3_accuracy": metrics["top_3_accuracy"],
            "precision": metrics["precision_weighted"],
            "recall": metrics["recall_weighted"],
            "f1": metrics["f1_weighted"],
        }
    ]).to_csv(comparison_path, index=False)

    print("\n[8/8] Training complete!")
    print("=" * 60)
    print(f"Accuracy:       {metrics['accuracy']:.4f}")
    print(f"Top-3 Accuracy: {metrics['top_3_accuracy']:.4f}")
    print(f"Precision:      {metrics['precision_weighted']:.4f}")
    print(f"Recall:         {metrics['recall_weighted']:.4f}")
    print(f"F1:             {metrics['f1_weighted']:.4f}")
    print(f"Model saved:    {checkpoint_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
