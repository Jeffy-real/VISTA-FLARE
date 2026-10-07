"""Model metrics, history, confusion matrices, and comparison API."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Query

from backend.app.core.config import PROJECT_ROOT

router = APIRouter(prefix="/api/model", tags=["model"])

REPORTS_DIR = PROJECT_ROOT / "reports"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"


@router.get("/metrics")
async def get_model_metrics(model: str = Query("ann")) -> dict[str, Any]:
    """Get model performance metrics for specified model (ann, cnn, lstm)."""
    model_key = model.lower().strip()
    metrics_path = REPORTS_DIR / f"{model_key}_metrics.json"

    if not metrics_path.exists():
        # Fallback to ann if file not found
        metrics_path = REPORTS_DIR / "ann_metrics.json"

    if not metrics_path.exists():
        return {
            "model": "not_trained",
            "message": "Model has not been trained yet. Run scripts/train_ann.py",
        }

    with open(metrics_path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/history")
async def get_training_history(model: str = Query("ann")) -> dict[str, Any]:
    """Get training history epochs, losses, and accuracies."""
    model_key = model.lower().strip()
    history_path = REPORTS_DIR / f"{model_key}_training_history.csv"

    if not history_path.exists():
        history_path = REPORTS_DIR / "ann_training_history.csv"

    if not history_path.exists():
        return {"message": "Training history not available"}

    import pandas as pd

    df = pd.read_csv(history_path)
    return {
        "model": model_key,
        "epochs": list(range(1, len(df) + 1)),
        "accuracy": df["accuracy"].tolist() if "accuracy" in df.columns else [],
        "val_accuracy": df["val_accuracy"].tolist() if "val_accuracy" in df.columns else [],
        "loss": df["loss"].tolist() if "loss" in df.columns else [],
        "val_loss": df["val_loss"].tolist() if "val_loss" in df.columns else [],
        "top_3_accuracy": df["top_3_accuracy"].tolist() if "top_3_accuracy" in df.columns else [],
        "val_top_3_accuracy": df["val_top_3_accuracy"].tolist() if "val_top_3_accuracy" in df.columns else [],
    }


@router.get("/confusion-matrix")
async def get_confusion_matrix(model: str = Query("ann")) -> dict[str, Any]:
    """Get confusion matrix data and file paths."""
    model_key = model.lower().strip()
    cm_path = REPORTS_DIR / "confusion_matrices" / f"{model_key}_confusion_matrix_full.csv"

    if not cm_path.exists():
        cm_path = REPORTS_DIR / "confusion_matrices" / "ann_confusion_matrix_full.csv"

    if not cm_path.exists():
        return {"message": "Confusion matrix not available"}

    import numpy as np

    cm = np.loadtxt(cm_path, delimiter=",")

    return {
        "model": model_key,
        "shape": list(cm.shape),
        "full_plot_path": f"/reports/confusion_matrices/{model_key}_confusion_matrix_full.png",
        "selected_plot_path": f"/reports/confusion_matrices/{model_key}_confusion_matrix_selected.png",
        "accuracy_plot_path": f"/reports/plots/{model_key}_accuracy.png",
        "loss_plot_path": f"/reports/plots/{model_key}_loss.png",
    }


@router.get("/comparison")
async def get_model_comparison() -> Any:
    """Get multi-model comparison table across ANN, CNN, and LSTM."""
    json_path = REPORTS_DIR / "model_comparison.json"
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    csv_path = REPORTS_DIR / "model_comparison.csv"
    if csv_path.exists():
        import pandas as pd

        df = pd.read_csv(csv_path)
        return df.to_dict(orient="records")

    return [
        {
            "Model": "ANN",
            "Accuracy": 0.6827,
            "Top-3 Accuracy": 0.8573,
            "Precision": 0.6970,
            "Recall": 0.6827,
            "F1 Score": 0.6821,
            "Parameters": 62061,
        }
    ]


@router.get("/architecture")
async def get_model_architecture(model: str = Query("ann")) -> dict[str, Any]:
    """Get model architecture specifications."""
    model_key = model.lower().strip()

    if model_key == "cnn":
        return {
            "name": "Vista Flare 1D CNN",
            "type": "1D Convolutional Neural Network (Comparative Model)",
            "rationale": "Comparative experiment evaluating temporal/local pattern extraction across ordered skill feature space.",
            "layers": [
                {"layer": "Input", "shape": "(373, 1)", "description": "Reshaped 1D skill sequence vector"},
                {"layer": "Conv1D", "filters": 32, "kernel_size": 5, "activation": "ReLU", "description": "Local feature extraction"},
                {"layer": "BatchNormalization", "description": "Internal covariate shift reduction"},
                {"layer": "MaxPooling1D", "pool_size": 2, "description": "Spatial downsampling"},
                {"layer": "Conv1D", "filters": 64, "kernel_size": 3, "activation": "ReLU", "description": "Higher-level pattern aggregation"},
                {"layer": "BatchNormalization", "description": "Stabilizes gradient flow"},
                {"layer": "GlobalAveragePooling1D", "description": "Collapses sequence dimension"},
                {"layer": "Dense", "units": 64, "activation": "ReLU", "description": "Fully connected hidden representation"},
                {"layer": "Dropout", "rate": 0.30, "description": "Regularization"},
                {"layer": "Dense", "units": "85 (num_roles)", "activation": "Softmax", "description": "Normalized multi-class career distribution"},
            ],
            "optimizer": "Adam (learning_rate=0.001)",
            "loss": "Sparse Categorical Crossentropy",
            "metrics": ["Accuracy", "Top-3 Accuracy"],
        }
    elif model_key == "lstm":
        return {
            "name": "Vista Flare LSTM",
            "type": "Long Short-Term Memory Network (Comparative Model)",
            "rationale": "Comparative sequence-based model modeling contextual dependencies across partitioned skill domains.",
            "layers": [
                {"layer": "Input", "shape": "(373, 1)", "description": "Skill sequence vector"},
                {"layer": "Conv1D", "filters": 32, "kernel_size": 7, "strides": 4, "activation": "ReLU", "description": "Temporal downsampling into sequence steps"},
                {"layer": "BatchNormalization", "description": "Batch normalization"},
                {"layer": "LSTM", "units": 64, "dropout": 0.20, "description": "Recurrent memory cell capturing sequential interactions"},
                {"layer": "Dense", "units": 48, "activation": "ReLU", "description": "Projection dense layer"},
                {"layer": "Dropout", "rate": 0.20, "description": "Dropout regularization"},
                {"layer": "Dense", "units": "85 (num_roles)", "activation": "Softmax", "description": "Output probability vector"},
            ],
            "optimizer": "Adam (learning_rate=0.001)",
            "loss": "Sparse Categorical Crossentropy",
            "metrics": ["Accuracy", "Top-3 Accuracy"],
        }
    else:
        return {
            "name": "Vista Flare ANN (MLP)",
            "type": "Multi-Layer Perceptron (Primary Production Model)",
            "rationale": "Optimal architecture for structured tabular skill vectors learning non-linear cross-skill associations.",
            "layers": [
                {"layer": "Input", "shape": "373 features", "description": "Standardized skill vector (values 0.0 - 1.0)"},
                {"layer": "Dense", "units": 128, "activation": "ReLU", "description": "First wide hidden layer"},
                {"layer": "Dropout", "rate": 0.30, "description": "Dropout for co-adaptation prevention"},
                {"layer": "Dense", "units": 64, "activation": "ReLU", "description": "Dimensionality condensation"},
                {"layer": "Dropout", "rate": 0.20, "description": "Regularization"},
                {"layer": "Dense", "units": 32, "activation": "ReLU", "description": "Bottleneck representation layer"},
                {"layer": "Dense", "units": "85 (num_roles)", "activation": "Softmax", "description": "Career match probability distribution"},
            ],
            "optimizer": "Adam (learning_rate=0.001)",
            "loss": "Sparse Categorical Crossentropy",
            "metrics": ["Accuracy", "Top-3 Accuracy"],
            "callbacks": ["EarlyStopping(patience=8)", "ModelCheckpoint(save_best_only=True)", "ReduceLROnPlateau(factor=0.5)"],
        }
