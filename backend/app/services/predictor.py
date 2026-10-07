"""ML prediction service for Vista Flare."""
from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any, Optional

import numpy as np
from sqlalchemy.orm import Session

from backend.app.core.config import PROJECT_ROOT

ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
MODELS_DIR = PROJECT_ROOT / "models"


class PredictionService:
    def __init__(self) -> None:
        self.model: Optional[Any] = None
        self.scaler: Optional[Any] = None
        self.skill_encoder: Optional[dict] = None
        self.label_encoder: Optional[dict] = None
        self.aliases: dict[str, str] = {}
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        # Load aliases
        aliases_path = PROJECT_ROOT / "data" / "seed" / "skill_aliases.csv"
        if aliases_path.exists():
            import pandas as pd

            df = pd.read_csv(aliases_path)
            for _, row in df.iterrows():
                alias = str(row["alias"]).strip().lower()
                normalized = self._normalize_skill_name(row["normalized_skill"])
                self.aliases[alias] = normalized
                self.aliases[alias.replace(".", "").replace(" ", "")] = normalized

        # Load skill encoder
        skill_encoder_path = ARTIFACTS_DIR / "skill_encoder.pkl"
        if skill_encoder_path.exists():
            with open(skill_encoder_path, "rb") as f:
                self.skill_encoder = pickle.load(f)

        # Load label encoder
        label_encoder_path = ARTIFACTS_DIR / "label_encoder.pkl"
        if label_encoder_path.exists():
            with open(label_encoder_path, "rb") as f:
                self.label_encoder = pickle.load(f)

        # Load scaler
        scaler_path = ARTIFACTS_DIR / "scaler.pkl"
        if scaler_path.exists():
            with open(scaler_path, "rb") as f:
                self.scaler = pickle.load(f)

        # Load TensorFlow model if available, otherwise scikit-learn fallback
        model_path = MODELS_DIR / "ann_model.keras"
        sklearn_path = MODELS_DIR / "sklearn_model.pkl"

        if model_path.exists():
            try:
                from tensorflow import keras

                self.model = keras.models.load_model(model_path)
                self.model_type = "tensorflow"
            except Exception:
                self._load_sklearn_fallback(sklearn_path)
        else:
            self._load_sklearn_fallback(sklearn_path)

    def _load_sklearn_fallback(self, path: Path) -> None:
        if path.exists():
            with open(path, "rb") as f:
                self.model = pickle.load(f)
            self.model_type = "sklearn"
        else:
            self.model = None
            self.model_type = None

    def _normalize_skill_name(self, name: str) -> str:
        if name is None:
            return ""
        cleaned = str(name).strip()
        if not cleaned:
            return ""
        special = {
            "c#": "C#",
            "c++": "C++",
            ".net": ".NET",
            "dbt": "dbt",
            "node.js": "Node.js",
            "next.js": "Next.js",
            "vue.js": "Vue",
            "react.js": "React",
            "powerbi": "Power BI",
            "power bi": "Power BI",
            "github actions": "GitHub Actions",
            "ci/cd": "CI/CD",
            "rest api": "REST API",
            "llms": "LLMs",
            "aws": "AWS",
            "sql": "SQL",
            "html": "HTML",
            "css": "CSS",
            "nlp": "NLP",
            "owasp": "OWASP",
            "soc": "SOC",
            "siem": "SIEM",
        }
        key = cleaned.lower().replace("_", " ").strip()
        if key in special:
            return special[key]
        return " ".join(word if word.isupper() else word.capitalize() for word in cleaned.replace("_", " ").split())

    def _canonicalize_skill(self, name: str) -> str:
        raw = str(name).strip()
        if not raw:
            return ""
        key = raw.lower()
        compact = key.replace(".", "").replace(" ", "")
        if key in self.aliases:
            return self.aliases[key]
        if compact in self.aliases:
            return self.aliases[compact]
        return self._normalize_skill_name(raw)

    def encode_profile(self, skills: list[dict[str, Any]]) -> np.ndarray:
        if not self.skill_encoder:
            raise RuntimeError("Skill encoder not loaded")

        skill_to_index = self.skill_encoder.get("skill_to_index", {})
        skills_list = self.skill_encoder.get("skills", [])

        level_values = {
            "missing": 0.0,
            "beginner": 0.35,
            "intermediate": 0.65,
            "advanced": 0.85,
            "expert": 1.0,
        }

        vector = np.zeros(len(skills_list), dtype=np.float32)

        for item in skills:
            if isinstance(item, str):
                name = item
                level_value = 0.75
            else:
                name = str(item.get("name", ""))
                raw_level = item.get("level", "intermediate")
                if isinstance(raw_level, (int, float)):
                    level_value = float(raw_level)
                else:
                    level_value = level_values.get(str(raw_level).lower(), 0.65)

            canonical = self._canonicalize_skill(name)
            idx = skill_to_index.get(canonical)
            if idx is not None:
                vector[idx] = max(vector[idx], max(0.0, min(1.0, level_value)))

        return vector

    def predict(self, skills: list[dict[str, Any]], top_k: int = 3) -> list[dict[str, Any]]:
        if self.model is None:
            raise RuntimeError("Model not loaded")

        if not skills:
            raise ValueError("Skills list cannot be empty")

        X = self.encode_profile(skills).reshape(1, -1)

        if self.scaler:
            X = self.scaler.transform(X)

        if self.model_type == "tensorflow":
            probabilities = self.model.predict(X, verbose=0)[0]
        else:
            # Scikit-learn fallback
            if hasattr(self.model, "predict_proba"):
                probabilities = self.model.predict_proba(X)[0]
            else:
                probabilities = np.zeros(len(self.label_encoder["roles"]))

        # Get top-k indices
        top_indices = np.argsort(probabilities)[-top_k:][::-1]

        role_names = self.label_encoder.get("roles", [])

        recommendations = []
        for rank, idx in enumerate(top_indices, start=1):
            if idx < len(role_names):
                role_name = role_names[idx]
            else:
                role_name = f"Role {idx}"
            score = float(probabilities[idx])
            recommendations.append(
                {
                    "rank": rank,
                    "role": role_name,
                    "score": round(score, 4),
                }
            )

        return recommendations

    def get_model_info(self) -> dict[str, Any]:
        return {
            "model_type": self.model_type or "not_loaded",
            "num_skills": len(self.skill_encoder.get("skills", [])) if self.skill_encoder else 0,
            "num_roles": len(self.label_encoder.get("roles", [])) if self.label_encoder else 0,
        }


# Global instance
_prediction_service: Optional[PredictionService] = None


def get_prediction_service() -> PredictionService:
    global _prediction_service
    if _prediction_service is None:
        _prediction_service = PredictionService()
    return _prediction_service
