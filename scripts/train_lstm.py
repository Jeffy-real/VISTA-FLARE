#!/usr/bin/env python
"""Train the Vista Flare LSTM comparative career recommendation model."""
from __future__ import annotations

import json
import pickle
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import tensorflow as tf
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from tensorflow import keras
from tensorflow.keras import layers

from scripts.common import (
    ARTIFACTS_DIR,
    CLASSIFICATION_DIR,
    CONFUSION_DIR,
    MODELS_DIR,
    PLOTS_DIR,
    RANDOM_SEED,
    REPORTS_DIR,
    ensure_directories,
    load_processed_training,
    save_json,
    set_global_seed,
)

MODEL_NAME = "lstm"
MODEL_VERSION = "LSTM-Sequence-v1"
EPOCHS = 18
BATCH_SIZE = 64
LEARNING_RATE = 0.001


def build_lstm(input_dim: int, num_classes: int) -> keras.Model:
    """Build sequence-based LSTM model for skill vectors.

    Uses a strided feature projection layer to map the static 373-dimensional skill
    vector into a 46-step temporal sequence suitable for recurrent memory cell processing.
    """
    model = keras.Sequential(
        [
            layers.Input(shape=(input_dim, 1), name="skill_sequence"),
            layers.Conv1D(filters=32, kernel_size=7, strides=4, padding="same", activation="relu", name="seq_projection"),
            layers.BatchNormalization(name="batchnorm_seq"),
            layers.LSTM(64, return_sequences=False, dropout=0.20, name="lstm_layer"),
            layers.Dense(48, activation="relu", name="dense_48_relu"),
            layers.Dropout(0.20, name="dropout_20"),
            layers.Dense(num_classes, activation="softmax", name="career_softmax"),
        ],
        name="vista_flare_lstm",
    )
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy", keras.metrics.SparseTopKCategoricalAccuracy(k=3, name="top_3_accuracy")],
    )
    return model


def plot_history(history: keras.callbacks.History) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    colors = {"train": "#8b5cf6", "val": "#f59e0b"}
    epochs = range(1, len(history.history["accuracy"]) + 1)

    # Accuracy Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(epochs, history.history["accuracy"], label="Training Accuracy", color=colors["train"], linewidth=2.2)
    ax.plot(epochs, history.history["val_accuracy"], label="Validation Accuracy", color=colors["val"], linewidth=2.2)
    ax.set_title("Vista Flare LSTM Accuracy", fontsize=15, fontweight="bold")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Accuracy")
    ax.legend()
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "lstm_accuracy.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    # Loss Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(epochs, history.history["loss"], label="Training Loss", color=colors["train"], linewidth=2.2)
    ax.plot(epochs, history.history["val_loss"], label="Validation Loss", color=colors["val"], linewidth=2.2)
    ax.set_title("Vista Flare LSTM Loss", fontsize=15, fontweight="bold")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Sparse Categorical Crossentropy")
    ax.legend()
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "lstm_loss.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def save_confusion_matrices(y_true: np.ndarray, y_pred: np.ndarray, role_names: list[str]) -> None:
    cm = confusion_matrix(y_true, y_pred)
    np.savetxt(CONFUSION_DIR / "lstm_confusion_matrix_full.csv", cm, delimiter=",", fmt="%d")

    fig, ax = plt.subplots(figsize=(18, 16))
    sns.heatmap(cm, cmap="Blues", cbar=True, ax=ax, xticklabels=False, yticklabels=False)
    ax.set_title("Vista Flare LSTM Full Confusion Matrix (85 Roles)", fontsize=16, fontweight="bold")
    ax.set_xlabel("Predicted Role")
    ax.set_ylabel("Actual Role")
    fig.tight_layout()
    fig.savefig(CONFUSION_DIR / "lstm_confusion_matrix_full.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    counts = np.bincount(y_true, minlength=len(role_names))
    top_indices = np.argsort(counts)[-20:]
    selected_cm = cm[np.ix_(top_indices, top_indices)]
    selected_labels = [role_names[i] for i in top_indices]
    fig, ax = plt.subplots(figsize=(16, 13))
    sns.heatmap(
        selected_cm,
        cmap="Blues",
        annot=True,
        fmt="d",
        cbar=True,
        ax=ax,
        xticklabels=selected_labels,
        yticklabels=selected_labels,
        linewidths=0.5,
    )
    ax.set_title("Vista Flare LSTM Selected Confusion Matrix", fontsize=16, fontweight="bold")
    ax.set_xlabel("Predicted Role")
    ax.set_ylabel("Actual Role")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=8)
    plt.setp(ax.get_yticklabels(), rotation=0, fontsize=8)
    fig.tight_layout()
    fig.savefig(CONFUSION_DIR / "lstm_confusion_matrix_selected.png", dpi=160, bbox_inches="tight")
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
    (CLASSIFICATION_DIR / "lstm_classification_report.txt").write_text(report, encoding="utf-8")

    report_dict = classification_report(y_test, y_pred, target_names=role_names, zero_division=0, output_dict=True)
    pd.DataFrame(report_dict).transpose().to_csv(CLASSIFICATION_DIR / "lstm_classification_report.csv")

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


def main():
    print("=" * 60)
    print("Vista Flare - LSTM Training (Comparative Model)")
    print("=" * 60)

    ensure_directories()
    set_global_seed(RANDOM_SEED)

    print("\n[1/7] Loading processed training data...")
    X, y, skill_names, role_names, _ = load_processed_training()

    scaler_path = ARTIFACTS_DIR / "scaler.pkl"
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, random_state=RANDOM_SEED, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=RANDOM_SEED, stratify=y_temp
    )

    X_train_scaled = scaler.transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    X_train_lstm = np.expand_dims(X_train_scaled, axis=-1)
    X_val_lstm = np.expand_dims(X_val_scaled, axis=-1)
    X_test_lstm = np.expand_dims(X_test_scaled, axis=-1)

    print(f"  - Train shape: {X_train_lstm.shape}")
    print(f"  - Validation shape: {X_val_lstm.shape}")
    print(f"  - Test shape: {X_test_lstm.shape}")

    print("\n[2/7] Building LSTM model...")
    model = build_lstm(input_dim=X.shape[1], num_classes=len(role_names))
    model.summary(print_fn=lambda line: print("  " + line))
    param_count = model.count_params()

    lstm_model_dir = MODELS_DIR / "lstm"
    lstm_model_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = lstm_model_dir / "lstm_model.keras"

    callbacks = [
        keras.callbacks.EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True),
        keras.callbacks.ModelCheckpoint(filepath=checkpoint_path, monitor="val_loss", save_best_only=True),
        keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, min_lr=1e-5),
    ]

    print("\n[3/7] Training LSTM model...")
    start_time = time.time()
    history = model.fit(
        X_train_lstm,
        y_train,
        validation_data=(X_val_lstm, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=callbacks,
        verbose=2,
    )
    training_time = round(time.time() - start_time, 2)

    print(f"\n[4/7] Training finished in {training_time} seconds.")
    pd.DataFrame(history.history).to_csv(REPORTS_DIR / "lstm_training_history.csv", index=False)
    plot_history(history)

    print("\n[5/7] Evaluating test set...")
    best_model = keras.models.load_model(checkpoint_path)
    metrics = evaluate(best_model, X_test_lstm, y_test, role_names)
    metrics.update(
        {
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "training_time_seconds": training_time,
            "total_parameters": param_count,
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
            "architecture": "Conv1D(32, strides=4) -> BatchNorm -> LSTM(64) -> Dense(48) -> Dropout(0.20) -> Dense(N Softmax)",
        }
    )
    save_json(REPORTS_DIR / "lstm_metrics.json", metrics)

    print("\n[6/7] LSTM evaluation results:")
    print(f"  Accuracy:       {metrics['accuracy']:.4f}")
    print(f"  Top-3 Accuracy: {metrics['top_3_accuracy']:.4f}")
    print(f"  Precision:      {metrics['precision_weighted']:.4f}")
    print(f"  Recall:         {metrics['recall_weighted']:.4f}")
    print(f"  F1 Score:       {metrics['f1_weighted']:.4f}")
    print(f"  Saved model:    {checkpoint_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
