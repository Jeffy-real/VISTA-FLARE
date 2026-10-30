# Vista Flare — Deep Learning Technical Verification Report
**Date:** 2026-10-29  
**Review Type:** Deep Learning Project Review-2 Audit  
**Author/Auditor:** Senior Deep Learning Engineer & Software Auditor (Antigravity)  
**Target Repository:** Vista Flare (`c:\Users\Jeffy\OneDrive\Documents\VISTA FLARE`)  

---

## 1. Executive Verification Summary

This audit independently inspects, executes, and verifies the full codebase, dataset files, model artifacts, training scripts, evaluation reports, and runtime services of Vista Flare. No metrics or architectural parameters were fabricated.

### Key Audit Findings

| Component | Verified Fact | Evidence Location | Status |
|---|---|---|---|
| **Total Career Classes** | 85 discrete professional roles | `data/seed/roles.csv`, `artifacts/role_mapping.json` | **VERIFIED** |
| **Skill Vocabulary Size** | 373 canonical skills | `data/seed/skills.csv`, `artifacts/skill_mapping.json` | **VERIFIED** |
| **Training Dataset Size** | 22,000 synthetic skill profiles | `data/processed/training_examples.csv` | **VERIFIED** |
| **Dataset Columns** | 3 (`role_id`, `role_name`, `skills_json`) | `data/processed/training_examples.csv` (line 1) | **VERIFIED** |
| **Empty Skill Profiles** | Exactly 23 empty profiles (0 skills) | Audited via pandas parse of `skills_json` | **VERIFIED** |
| **Dataset Split** | 70% Train (15,400) / 15% Val (3,300) / 15% Test (3,300) | `reports/ann_metrics.json`, `scripts/train_ann.py` | **VERIFIED** |
| **ANN Architecture** | Dense(128, ReLU) -> Dropout(0.30) -> Dense(64, ReLU) -> Dropout(0.20) -> Dense(32, ReLU) -> Dense(85, Softmax) | `scripts/train_ann.py` (lines 46-58) | **VERIFIED** |
| **ANN Parameters** | Exactly 61,013 trainable parameters | Calculated analytically and verified via `reports/model_comparison.json` | **VERIFIED** |
| **ANN Test Metrics** | Accuracy: 68.27%, Top-3 Accuracy: 85.73%, Weighted F1: 68.21% | `reports/ann_metrics.json`, `reports/model_comparison.json` | **VERIFIED** |
| **1D CNN Architecture** | Conv1D(32, k=5) -> BatchNorm -> MaxPool(2) -> Conv1D(64, k=3) -> BatchNorm -> GlobalAvgPool -> Dense(64) -> Dropout(0.3) -> Dense(85) | `scripts/train_cnn.py` (lines 59-75) | **VERIFIED** |
| **1D CNN Parameters** | 16,469 trainable parameters | `reports/cnn_metrics.json` | **VERIFIED** |
| **1D CNN Test Metrics** | Accuracy: 17.73%, Top-3 Accuracy: 32.27%, Weighted F1: 17.08% | `reports/cnn_metrics.json`, `reports/model_comparison.json` | **VERIFIED** |
| **LSTM Architecture** | Conv1D(32, k=7, s=4) -> BatchNorm -> LSTM(64) -> Dense(48) -> Dropout(0.20) -> Dense(85) | `scripts/train_lstm.py` (lines 59-76) | **VERIFIED** |
| **LSTM Parameters** | 32,501 trainable parameters | `reports/lstm_metrics.json` | **VERIFIED** |
| **LSTM Test Metrics** | Accuracy: 47.52%, Top-3 Accuracy: 70.33%, Weighted F1: 47.09% | `reports/lstm_metrics.json`, `reports/model_comparison.json` | **VERIFIED** |
| **Runtime Model Serving** | Scikit-learn MLPClassifier (`models/sklearn_model.pkl`) fallback active when Keras/TensorFlow C-backend is unavailable | `backend/app/services/predictor.py` (tested live) | **VERIFIED** |
| **SQLite Database** | 192 total jobs (170 seed + 22 external from Arbeitnow & Remotive) | `data/vista_flare.db` audited via SQLite query | **VERIFIED** |

---

## 2. In-Depth Model Comparison Table

All values verified against `reports/model_comparison.json`, `reports/ann_metrics.json`, `reports/cnn_metrics.json`, and `reports/lstm_metrics.json`:

| Model Metric / Attribute | Deep ANN / MLP | 1D CNN | Recurrent LSTM |
|---|---|---|---|
| **Architectural Role** | Primary Production Model | Comparative Experiment | Comparative Experiment |
| **Input Shape** | `(373,)` continuous vector | `(373, 1)` reshaped 1D | `(373, 1)` reshaped 1D |
| **Input Representation** | Continuous skill proficiencies | Arbitrary ordered 1D sequence | Projected 46-step sequence |
| **Trainable Parameters** | **61,013** | **16,469** | **32,501** |
| **Epochs Ran** | 28 (EarlyStopped at 35) | 25 | 18 (EarlyStopped at 25) |
| **Batch Size & Optimizer** | 64, Adam ($lr=0.001$) | 64, Adam ($lr=0.001$) | 64, Adam ($lr=0.001$) |
| **Test Accuracy** | **68.27%** | **17.73%** | **47.52%** |
| **Top-3 Accuracy** | **85.73%** | **32.27%** | **70.33%** |
| **Weighted Precision** | **69.70%** | **23.72%** | **50.81%** |
| **Weighted Recall** | **68.27%** | **17.73%** | **47.52%** |
| **Weighted F1-Score** | **68.21%** | **17.08%** | **47.09%** |
| **Test Cross-Entropy Loss** | **1.2261** | **3.4166** | **1.9848** |
| **Inference Latency** | **0.336 ms / sample** | **0.289 ms / sample** | **1.206 ms / sample** |
| **Training Time** | ~110 s | 146.57 s | 348.57 s |

---

## 3. Mathematical Parameter Verification of ANN (MLP)

The ANN architecture defined in `scripts/train_ann.py` has input dimension $D_{in} = 373$ and output classes $C = 85$:
1. **Layer 1 — Dense(128, ReLU):**  
   $\text{Weights} = 373 \times 128 = 47,744$  
   $\text{Biases} = 128$  
   $\text{Subtotal} = 47,872$
2. **Layer 2 — Dropout(0.30):**  
   $\text{Parameters} = 0$
3. **Layer 3 — Dense(64, ReLU):**  
   $\text{Weights} = 128 \times 64 = 8,192$  
   $\text{Biases} = 64$  
   $\text{Subtotal} = 8,256$
4. **Layer 4 — Dropout(0.20):**  
   $\text{Parameters} = 0$
5. **Layer 5 — Dense(32, ReLU):**  
   $\text{Weights} = 64 \times 32 = 2,048$  
   $\text{Biases} = 32$  
   $\text{Subtotal} = 2,080$
6. **Layer 6 — Dense(85, Softmax):**  
   $\text{Weights} = 32 \times 85 = 2,720$  
   $\text{Biases} = 85$  
   $\text{Subtotal} = 2,805$

$$\text{Total Parameters} = 47,872 + 8,256 + 2,080 + 2,805 = \mathbf{61,013}$$
*Analytical calculation perfectly matches the saved report value of 61,013.*

---

## 4. Methodological Analysis: Why ANN Outperformed CNN and LSTM

1. **Lack of Spatial Invariance (Why CNN failed with 17.73%):**
   - Convolutional 1D kernels assume local spatial continuity (i.e. feature $i$ is physically adjacent to feature $i+1$, like adjacent pixels or speech samples).
   - In Vista Flare's skill vector, the 373 skills are arranged in alphabetical or arbitrary index order. Kernel sizes of 5 or 3 slide across unrelated skills (e.g., "Angular" next to "Apache Spark"), generating meaningless local filter activations.
   - GlobalAveragePooling1D then averages these meaningless activations, destroying discriminative power across 85 fine-grained role classes.
2. **Artificial Sequential Inductive Bias (Why LSTM achieved 47.52%):**
   - LSTMs are engineered for temporally ordered token streams (e.g. natural language, speech, time series).
   - Candidate skill profiles are non-sequential sets (a "bag-of-skills").
   - To feed the 373-dimensional vector into an LSTM, `scripts/train_lstm.py` used a strided 1D convolution (`filters=32, kernel_size=7, strides=4`) to project the vector into an artificial 46-step sequence. While the recurrent gating captured broader feature co-occurrences than CNN, the temporal ordering is artificial, leading to suboptimal hidden state transitions.
3. **Superiority of Feed-Forward MLP (Why ANN achieved 68.27%):**
   - Dense layers compute fully connected inner products between all input features and hidden neurons. Every skill interacts directly with every other skill without positional or temporal bias.
   - Non-linear ReLU activations and dropout regularization allow the network to discover non-linear combinations of core skills and complementary skills, reflecting the true nature of career requirements.

---

## 5. Deployment vs. Runtime Model Execution Audit

The prompt requires verifying the exact runtime prediction path.
- **Experimental Best Model:** TensorFlow/Keras ANN (`models/ann_model.keras`), achieving 68.27% accuracy and 85.73% top-3 accuracy.
- **Intended Deployment Model:** `models/ann_model.keras` loaded by `PredictionService` in `backend/app/services/predictor.py`.
- **Actual Runtime Path:**
  - `backend/app/services/predictor.py` wraps model loading in a `try...except` block.
  - When TensorFlow C-extensions are missing or version mismatches occur, it catches `Exception` and logs:
    `"TensorFlow ANN unavailable: ModuleNotFoundError: No module named 'tensorflow.python'"`.
  - It then executes `self._load_sklearn_fallback(sklearn_path)`, which loads `models/sklearn_model.pkl` (an `sklearn.neural_network._multilayer_perceptron.MLPClassifier`).
  - Runtime live test returned valid career role predictions (`Python Developer`, score: $0.999994$) with sub-millisecond execution.
  - Both models share the exact same 373-feature input vector and 85-role target space!

---

## 6. SQLite Database Audit

Audited via `project_review/audit_db.py` on `data/vista_flare.db`:
- Total Career Roles: 85
- Total Skills: 373
- Role-Skill Associations: 508
- Skill Aliases: 86
- Companies: 30
- Total Jobs: 192
  - `vista_flare_seed`: 170
  - `Arbeitnow` (live external API ingestion): 10
  - `Remotive` (live external API ingestion): 12
- Learning Resources: 62
- Users: 82
- User Sessions: 79
- Inference Traces: 13
- Ingestion Runs: 3
- Provider Health: 2

