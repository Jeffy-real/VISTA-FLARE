# Vista Flare - Deep Learning Academic & Viva Examination Guide

> **Review 2 & College Viva Preparation Guide**  
> **Project:** Vista Flare (AI-Powered Career & Skill Matching Platform)  
> **Primary Model:** Artificial Neural Network / Multi-Layer Perceptron (ANN/MLP)  
> **Framework:** TensorFlow 2.18 / Keras 3 (Python 3.12, FastAPI, React + Vite)

---

## 1. Project Background & Problem Statement

### What problem does Vista Flare solve?
Traditional job portals require users to search by fixed job titles or keyword queries. However, college students and job seekers often possess an evolving mix of technical competencies (e.g., Python, SQL, Git, Pandas) and do not know which specific job role best matches their skill profile.

**Vista Flare** formulates this as a multi-class Deep Learning classification problem:
Given a user's multi-dimensional skill vector $\mathbf{x} \in \mathbb{R}^{373}$ (where each element indicates the presence and proficiency of a skill from $0.0$ to $1.0$), the model computes a calibrated probability distribution over $N = 85$ career roles:
$$\mathbf{y} = \text{Softmax}(\text{ANN}(\mathbf{x}))$$
The top-3 roles with the highest confidence scores are recommended to the user, followed by deterministic skill-gap analysis, company matching, and structured 5-stage learning roadmaps.

---

## 2. Dataset Architecture & Pipeline

### Dataset Dimensions & Classes
- **Total Training Dataset Size:** 22,000 synthetic skill-role profile samples.
- **Number of Features (Input Dimension):** 373 distinct standardized technical skills.
- **Number of Target Classes (Output Dimension):** 85 standardized technology career roles (e.g., Data Scientist, Machine Learning Engineer, Cloud Architect, Full Stack Developer, DevOps Engineer).
- **Dataset Split:**
  - **Training Set:** 15,400 samples (70%)
  - **Validation Set:** 3,300 samples (15%)
  - **Test Set:** 3,300 samples (15%)
  - **Stratification:** Stratified splitting (`stratify=y`) ensures all 85 career classes maintain identical proportional representation across train, validation, and test sets.

### Skill Normalization & Canonicalization
Users input skill names in many variations (e.g., `"react.js"`, `"React"`, `"powerbi"`, `"Power BI"`, `"aws"`, `"AWS"`).
- A seed dictionary (`data/seed/skill_aliases.csv`) contains 86 normalized alias mappings.
- The pipeline canonicalizes aliases to standardized vocabulary tokens before vectorization.

### Feature Encoding (Proficiency-Weighted Vector)
Rather than a crude binary one-hot encoding, Vista Flare encodes proficiency levels on a continuous scale $[0.0, 1.0]$:
- `missing` $\to 0.00$
- `beginner` $\to 0.35$
- `intermediate` $\to 0.65$
- `advanced` $\to 0.85$
- `expert` $\to 1.00$

Features are scaled using `StandardScaler(with_mean=False)` to preserve feature sparsity while standardizing feature variance for numerical gradient stability.

---

## 3. ANN Architecture & Hyperparameters

```
Input Vector (373 skills, scaled)
       ↓
Dense(128 units, ReLU activation)
       ↓
Dropout(rate = 0.30)
       ↓
Dense(64 units, ReLU activation)
       ↓
Dropout(rate = 0.20)
       ↓
Dense(32 units, ReLU activation)
       ↓
Dense(85 units, Softmax activation)
```

### Layer Breakdown & Parameter Count
1. **Input Layer (`shape=(373,)`):** Receives the standardized 373-dimensional skill vector.
2. **First Hidden Dense Layer (`128` units):**
   - Learns wide first-order non-linear combinations across skills.
   - Parameters: $(373 \times 128) + 128 = 47,872$ weights and biases.
3. **Dropout Layer (`0.30` rate):** Randomly zeroes 30% of activations during training to prevent co-adaptation.
4. **Second Hidden Dense Layer (`64` units):**
   - Compresses representation into higher-level abstract feature interactions.
   - Parameters: $(128 \times 64) + 64 = 8,256$.
5. **Dropout Layer (`0.20` rate):** Randomly drops 20% of activations.
6. **Third Hidden Dense Layer (`32` units):**
   - Bottleneck representation layer isolating core role features.
   - Parameters: $(64 \times 32) + 32 = 2,080$.
7. **Output Dense Layer (`85` units, Softmax):**
   - Computes multi-class probability distribution across all 85 target career roles.
   - Parameters: $(32 \times 85) + 85 = 2,805$.
- **Total Trainable Parameters:** **61,013** parameters.

---

## 4. Deep Learning Concepts Explained for Viva

### 1. Dense (Fully Connected) Layer
In a Dense layer, every neuron is connected to every neuron in the preceding layer:
$$z = \sum_{i=1}^n w_i x_i + b = \mathbf{W}\mathbf{x} + \mathbf{b}$$
This allows the network to learn global cross-skill patterns (e.g., detecting that Python + SQL + Machine Learning indicates Data Science, regardless of index positions).

### 2. ReLU Activation Function
**Rectified Linear Unit (ReLU)** is defined as:
$$f(z) = \max(0, z)$$
- **Why use ReLU?** It is computationally efficient, introduces non-linearity, and does not suffer from vanishing gradients for positive inputs (unlike Sigmoid or Tanh).

### 3. Dropout Regularization
During training, Dropout temporarily switches off a randomly selected fraction of neurons:
- At 0.30, 30% of hidden units are disabled in each forward pass.
- **Why?** It prevents the network from relying excessively on any single skill feature, forcing distributed representation and reducing **overfitting**.

### 4. Softmax Output Layer
Softmax converts an unnormalized logit vector $\mathbf{z} \in \mathbb{R}^{85}$ into a valid probability distribution:
$$\sigma(\mathbf{z})_i = \frac{e^{z_i}}{\sum_{j=1}^{85} e^{z_j}}$$
Properties:
- All output values lie strictly between $0$ and $1$.
- The sum of all 85 outputs equals exactly $1.00$ ($100\%$).
- Enables ranking to find the **Top-3** career recommendations.

### 5. Loss Function: Sparse Categorical Cross-Entropy
Since target roles are integer class indices ($y \in \{0, 1, \dots, 84\}$):
$$\mathcal{L} = -\sum_{k=1}^N \log(\hat{y}_{k, \text{true}})$$
Penalizes the model heavily when it assigns low probability to the actual ground-truth role.

### 6. Adam Optimizer
**Adam (Adaptive Moment Estimation)** computes individual adaptive learning rates for each parameter by combining:
- First moment (momentum / exponentially decaying average of past gradients).
- Second moment (RMSProp / uncentered variance of past gradients).
- Configured with initial learning rate $\alpha = 0.001$, $\beta_1 = 0.9$, $\beta_2 = 0.999$, $\epsilon = 10^{-7}$.

### 7. Forward Propagation vs. Backpropagation
- **Forward Propagation:** The input feature vector flows forward through Dense layers, applying weights, biases, and activation functions, culminating in the Softmax probability output.
- **Backpropagation:** The error gradient $\frac{\partial \mathcal{L}}{\partial \mathbf{W}}$ is calculated via the chain rule of calculus from the loss function back through the layers, updating weights via gradient descent:
$$\mathbf{W} \leftarrow \mathbf{W} - \alpha \nabla_{\mathbf{W}} \mathcal{L}$$

### 8. Epochs & Batch Size
- **Epoch:** One complete cycle through all 15,400 training samples.
- **Batch Size (64):** Mini-batch gradient descent processes 64 profiles per weight update step, providing balance between computational speed and gradient noise stability.

### 9. Overfitting, Validation & Early Stopping
- **Overfitting:** When a neural network memorizes training samples, performing well on training data but poorly on unseen test data.
- **EarlyStopping:** Monitored `val_loss` with `patience=8`. If validation loss failed to improve for 8 consecutive epochs, training terminated automatically, and `restore_best_weights=True` restored the model state with minimum validation loss.
- **ReduceLROnPlateau:** Halved learning rate (`factor=0.5`) if validation loss plateaued for 4 epochs, allowing fine-grained convergence.

---

## 5. Authentic Evaluation Results (Review 2 Deliverables)

All values below were empirically calculated on the 3,300-sample test set using `scripts/evaluate_models.py` and `scripts/train_ann.py`:

| Metric | ANN (MLP) Production | 1D CNN Comparative | LSTM Comparative |
| :--- | :---: | :---: | :---: |
| **Top-1 Accuracy** | **68.27%** (0.6827) | 17.73% (0.1773) | 47.52% (0.4752) |
| **Top-3 Accuracy** | **85.73%** (0.8573) | 32.27% (0.3227) | 70.33% (0.7033) |
| **Precision (Weighted)** | **69.70%** (0.6970) | 23.72% (0.2372) | 50.81% (0.5081) |
| **Recall (Weighted)** | **68.27%** (0.6827) | 17.73% (0.1773) | 47.52% (0.4752) |
| **F1 Score (Weighted)**| **68.21%** (0.6821) | 17.08% (0.1708) | 47.09% (0.4709) |
| **Test Loss** | **1.2261** | 3.4166 | 1.9848 |
| **Parameters** | 61,013 | 16,469 | 32,501 |
| **Inference Latency** | **0.221 ms / sample** | 0.278 ms / sample | 0.747 ms / sample |

### Why ANN Outperforms CNN and LSTM on Skill Data (Key Viva Question!)
- **Tabular / Unordered Feature Space:** Unlike images (where adjacent pixels represent edges) or audio/text (where words have sequential order), technical skill features have **no intrinsic spatial or sequential ordering**.
- **1D CNN Limitation:** 1D convolutions compute dot products over sliding local windows (e.g., indices $[i, i+1, i+2]$). Because the index order of skills is arbitrary, the CNN cannot capture global relationships between distant skills without massive pooling.
- **LSTM Limitation:** LSTMs are designed for sequential time-series where step $t$ depends on step $t-1$. Skill profiles are static snapshots, making recurrent state transitions non-optimal.
- **ANN Superiority:** Dense layers connect every skill directly to every hidden neuron, enabling the model to learn high-order non-local correlations directly.

---

## 6. Generated Visual Artifacts

The following generated plots and matrices are saved in the project and served by the API under `/reports`:

1. **Accuracy Curve:** `reports/plots/ann_accuracy.png` (Training vs. Validation Accuracy over epochs).
2. **Loss Curve:** `reports/plots/ann_loss.png` (Training vs. Validation Cross-Entropy Loss over epochs).
3. **Selected Confusion Matrix (Top 20 Roles):** `reports/confusion_matrices/ann_confusion_matrix_selected.png` (Annotated with counts and role labels for clear viva display).
4. **Full 85-Role Confusion Matrix:** `reports/confusion_matrices/ann_confusion_matrix_full.png` (Heatmap over the complete $85 \times 85$ test prediction matrix).
5. **Model Comparison Bar Chart:** `reports/plots/model_comparison.png` (Side-by-side Top-1, Top-3, and F1 comparison of ANN vs CNN vs LSTM).
6. **Classification Report:** `reports/classification_reports/ann_classification_report.csv` (Per-class precision, recall, f1-score, and support for all 85 career roles).

---

## 7. Viva Q&A Cheat Sheet

**Q1: Why is Top-3 Accuracy an important metric for this project?**  
*Answer:* In real-world career planning, a user's skill set frequently overlaps across adjacent career tracks (e.g., Data Scientist vs. Machine Learning Engineer vs. Data Analyst). While exact Top-1 match is 68.27%, the Top-3 accuracy is **85.73%**, meaning in ~86 out of 100 cases, the user's ideal career trajectory is included in the recommended triad.

**Q2: Does the backend retrain the model when a user submits skills?**  
*Answer:* No. The model is trained offline (`scripts/train_ann.py`) and saved as `models/ann_model.keras`. On application startup, `PredictionService` loads the pre-trained weights once into memory. Real-time inference takes only ~0.22 milliseconds per request.

**Q3: How are missing or unknown skills handled?**  
*Answer:* When a user enters a skill not present in the 373-skill dictionary, it is safely filtered out and does not disrupt the input vector. If empty or zero skills are passed, the API returns a graceful 400 validation response.

**Q4: How are skill-gap analysis and company matching related to the ANN?**  
*Answer:* They are decoupled by design. The ANN's responsibility is solely multi-class role classification and confidence scoring. Once the top role is established, deterministic domain logic performs set intersections against database role requirements (`RoleSkill` table) and job posting requirements (`Job` table) to produce strong/developing/missing skill categorizations and company rankings.
