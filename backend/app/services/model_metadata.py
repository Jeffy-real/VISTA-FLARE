"""Read-only metadata assembled from model artifacts, reports, and training code."""
from __future__ import annotations

import csv
import json
import pickle
from pathlib import Path
from typing import Any

from backend.app.core.config import PROJECT_ROOT

REPORTS_DIR = PROJECT_ROOT / "reports"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
MODELS_DIR = PROJECT_ROOT / "models"

MODEL_PATHS = {
    "ann": MODELS_DIR / "ann_model.keras",
    "cnn": MODELS_DIR / "cnn" / "cnn_model.keras",
    "lstm": MODELS_DIR / "lstm" / "lstm_model.keras",
}

# Fallback details are transcribed from the repository's build_* functions and
# are used only when the artifact cannot be introspected at runtime.
SOURCE_ARCHITECTURES: dict[str, dict[str, Any]] = {
    "ann": {
        "name": "Vista Flare ANN / MLP", "purpose": "Primary career classifier", "script": "scripts/train_ann.py",
        "input_interpretation": "A single scaled, 373-feature skill vector; this is tabular data, not a sequence.",
        "layers": [
            {"name": "skill_vector", "kind": "Input", "shape": "(373,)", "description": "Encoded numerical skill vector"},
            {"name": "dense_128_relu", "kind": "Dense", "units": 128, "activation": "relu"},
            {"name": "dropout_30", "kind": "Dropout", "rate": 0.30},
            {"name": "dense_64_relu", "kind": "Dense", "units": 64, "activation": "relu"},
            {"name": "dropout_20", "kind": "Dropout", "rate": 0.20},
            {"name": "dense_32_relu", "kind": "Dense", "units": 32, "activation": "relu"},
            {"name": "career_softmax", "kind": "Dense", "units": 85, "activation": "softmax", "description": "Career-class scores"},
        ],
        "callbacks": ["EarlyStopping(val_loss, patience=8)", "ModelCheckpoint(val_loss, save_best_only=True)", "ReduceLROnPlateau(val_loss, factor=0.5, patience=4)"],
    },
    "cnn": {
        "name": "Vista Flare 1D CNN", "purpose": "Comparative experiment", "script": "scripts/train_cnn.py",
        "input_interpretation": "The same static skill vector reshaped to (373, 1). Adjacent feature positions are not a natural sequence.",
        "layers": [
            {"name": "skill_sequence", "kind": "Input", "shape": "(373, 1)"},
            {"name": "conv1d_32", "kind": "Conv1D", "filters": 32, "kernel_size": 5, "activation": "relu", "padding": "same"},
            {"name": "batchnorm_1", "kind": "BatchNormalization"},
            {"name": "pool_1", "kind": "MaxPooling1D", "pool_size": 2},
            {"name": "conv1d_64", "kind": "Conv1D", "filters": 64, "kernel_size": 3, "activation": "relu", "padding": "same"},
            {"name": "batchnorm_2", "kind": "BatchNormalization"},
            {"name": "global_avg_pool", "kind": "GlobalAveragePooling1D"},
            {"name": "dense_64_relu", "kind": "Dense", "units": 64, "activation": "relu"},
            {"name": "dropout_30", "kind": "Dropout", "rate": 0.30},
            {"name": "career_softmax", "kind": "Dense", "units": 85, "activation": "softmax"},
        ],
        "callbacks": ["EarlyStopping(val_loss, patience=6)", "ModelCheckpoint(val_loss, save_best_only=True)", "ReduceLROnPlateau(val_loss, factor=0.5, patience=3)"],
    },
    "lstm": {
        "name": "Vista Flare LSTM", "purpose": "Comparative experiment", "script": "scripts/train_lstm.py",
        "input_interpretation": "The static vector is reshaped to (373, 1), then projected by strided Conv1D before the LSTM. It is not a temporal user-skill history.",
        "layers": [
            {"name": "skill_sequence", "kind": "Input", "shape": "(373, 1)"},
            {"name": "seq_projection", "kind": "Conv1D", "filters": 32, "kernel_size": 7, "strides": 4, "activation": "relu", "padding": "same"},
            {"name": "batchnorm_seq", "kind": "BatchNormalization"},
            {"name": "lstm_layer", "kind": "LSTM", "units": 64, "dropout": 0.20, "return_sequences": False},
            {"name": "dense_48_relu", "kind": "Dense", "units": 48, "activation": "relu"},
            {"name": "dropout_20", "kind": "Dropout", "rate": 0.20},
            {"name": "career_softmax", "kind": "Dense", "units": 85, "activation": "softmax"},
        ],
        "callbacks": ["EarlyStopping(val_loss, patience=5)", "ModelCheckpoint(val_loss, save_best_only=True)", "ReduceLROnPlateau(val_loss, factor=0.5, patience=3)"],
    },
}


def _model_key(model: str) -> str:
    key = model.lower().strip()
    return key if key in MODEL_PATHS else "ann"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _runtime_layers(path: Path) -> tuple[list[dict[str, Any]], int | None] | None:
    """Introspect a saved Keras artifact only when TensorFlow can load it."""
    if not path.exists():
        return None
    try:
        from tensorflow import keras
        model = keras.models.load_model(path, compile=False)
        layers = []
        for layer in model.layers:
            config = layer.get_config()
            shape = getattr(layer, "output", None)
            output_shape = tuple(shape.shape.as_list()) if getattr(shape, "shape", None) else None
            details: dict[str, Any] = {
                "name": layer.name, "kind": layer.__class__.__name__, "output_shape": str(output_shape) if output_shape else None,
                "parameter_count": int(layer.count_params()),
            }
            for source, target in (("units", "units"), ("filters", "filters"), ("kernel_size", "kernel_size"),
                                   ("pool_size", "pool_size"), ("strides", "strides"), ("rate", "rate"),
                                   ("dropout", "dropout"), ("return_sequences", "return_sequences"), ("padding", "padding")):
                if source in config:
                    details[target] = config[source]
            activation = config.get("activation")
            if activation and activation != "linear":
                details["activation"] = activation
            layers.append(details)
        return layers, int(model.count_params())
    except Exception:
        return None


def _history(model: str) -> list[dict[str, float | int]]:
    path = REPORTS_DIR / f"{model}_training_history.csv"
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        result = []
        for index, row in enumerate(csv.DictReader(handle), start=1):
            item: dict[str, float | int] = {"epoch": index}
            for name in ("accuracy", "val_accuracy", "loss", "val_loss", "top_3_accuracy", "val_top_3_accuracy"):
                if row.get(name) not in (None, ""):
                    item[name] = float(row[name])
            result.append(item)
        return result


def _labels() -> list[str]:
    path = ARTIFACTS_DIR / "label_encoder.pkl"
    try:
        with path.open("rb") as handle:
            value = pickle.load(handle)
        return list(value.get("roles", [])) if isinstance(value, dict) else []
    except (OSError, pickle.PickleError, AttributeError):
        return []


def get_model_metadata(model: str) -> dict[str, Any]:
    key = _model_key(model)
    source = SOURCE_ARCHITECTURES[key]
    metrics = _read_json(REPORTS_DIR / f"{key}_metrics.json")
    runtime = _runtime_layers(MODEL_PATHS[key])
    layers = runtime[0] if runtime else source["layers"]
    return {
        "key": key,
        "name": source["name"],
        "purpose": source["purpose"],
        "artifact_path": str(MODEL_PATHS[key].relative_to(PROJECT_ROOT)),
        "artifact_available": MODEL_PATHS[key].exists(),
        "architecture_source": "saved Keras artifact" if runtime else "verified training definition",
        "training_script": source["script"],
        "input_interpretation": source["input_interpretation"],
        "layers": layers,
        "total_parameters": runtime[1] if runtime else metrics.get("total_parameters"),
        "metrics": metrics,
        "training": {
            "dataset": metrics.get("dataset_version"), "framework": metrics.get("framework_version"),
            "split": "70% train / 15% validation / 15% test (stratified; verified in training script)",
            "training_samples": metrics.get("training_samples"), "validation_samples": metrics.get("validation_samples"),
            "test_samples": metrics.get("test_samples"), "batch_size": metrics.get("batch_size"),
            "epochs_ran": metrics.get("epochs_ran"), "optimizer": f"Adam (learning_rate={metrics.get('learning_rate')})" if metrics.get("learning_rate") is not None else "Not recorded",
            "loss": "Sparse categorical crossentropy", "callbacks": source["callbacks"],
        },
        "history": _history(key), "class_labels": _labels(),
    }


def get_comparison() -> list[dict[str, Any]]:
    content = _read_json(REPORTS_DIR / "model_comparison.json")
    return content if isinstance(content, list) else []


def get_confusion_row(model: str, class_name: str | None = None) -> dict[str, Any]:
    key = _model_key(model)
    labels = _labels()
    path = REPORTS_DIR / "confusion_matrices" / f"{key}_confusion_matrix_full.csv"
    if not path.exists():
        return {"model": key, "available": False, "labels": labels, "selected": None, "values": []}
    with path.open(newline="", encoding="utf-8") as handle:
        matrix = [[int(float(cell)) for cell in row] for row in csv.reader(handle) if row]
    if not matrix:
        return {"model": key, "available": False, "labels": labels, "selected": None, "values": []}
    selected_index = labels.index(class_name) if class_name in labels else 0
    return {
        "model": key, "available": True, "labels": labels, "selected": labels[selected_index] if labels else str(selected_index),
        "values": matrix[selected_index], "matrix_shape": [len(matrix), len(matrix[0])],
    }
