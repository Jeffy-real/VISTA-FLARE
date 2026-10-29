# Vista Flare

**AI-Powered Career & Skill Matching Platform**

> See Your Skills. Find Your Direction. Build Your Future.

Vista Flare uses Deep Learning and job-market intelligence to connect your skills with careers, companies, and learning paths aligned with your future.

## Overview

Vista Flare analyzes a user's skills and provides:

- Top 3 career-role recommendations powered by Deep Learning
- AI match scores with skill alignment explanations
- Skill-gap analysis for target roles
- Company and job matching
- Job-market information and salary insights
- Learning resources and career roadmaps

## Architecture

```
vista-flare/
├── backend/          # FastAPI backend with trained ANN model
├── frontend/         # React frontend
├── data/            # Datasets (raw, processed, seed)
├── models/          # Trained model artifacts
├── artifacts/       # Encoders and preprocessing pipelines
├── scripts/         # Training and data processing scripts
├── reports/         # Training metrics, plots, confusion matrices
├── docs/            # Documentation and viva guide
└── tests/           # Test suites
```

## Technology Stack

### Backend
- Python 3.12
- FastAPI
- TensorFlow/Keras (Deep Learning)
- SQLite
- Pandas, NumPy, Scikit-learn

### Frontend
- React
- TypeScript
- Tailwind CSS
- Recharts

### Deep Learning Models
- ANN/MLP (Primary production model)
- 1D CNN (Comparative experiment)
- LSTM (Comparative experiment)

## Installation

### Prerequisites
- Python 3.12+
- Node.js 18+

### Backend Setup

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

## Running the Application

### Start Backend

```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```

### Start Frontend

```bash
cd frontend
npm run dev
```

## Model Training

### Generate Training Data

```bash
python scripts/generate_training_data.py
```

### Train ANN

```bash
python scripts/train_ann.py
```

### Train CNN (Optional)

```bash
python scripts/train_cnn.py
```

### Train LSTM (Optional)

```bash
python scripts/train_lstm.py
```

### Evaluate Models

```bash
python scripts/evaluate_models.py
```

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/predict` - Get career predictions
- `GET /api/skills` - List all skills
- `GET /api/roles` - List all roles
- `GET /api/companies` - List companies
- `GET /api/jobs` - List jobs
- `GET /api/learning` - List learning resources
- `GET /api/model/metrics` - Model performance metrics

The frontend stores the current skill profile, recommendations, saved career
roles, and roadmap task statuses in versioned browser-local storage. This is
not account-backed synchronization; clearing browser storage removes that
local journey data.

`GET /api/health` reports `degraded` when the TensorFlow ANN cannot be loaded,
even when the existing scikit-learn fallback can serve predictions. The
fallback is labeled in the UI rather than presented as the TensorFlow model.

## Dataset

The project uses multiple datasets:

1. **Global Job Market Dataset** - Job postings with skills, salaries, locations
2. **Role-Skill Dataset** - Skills required for each career role (85 roles)
3. **Skill Taxonomy** - Standardized skill vocabulary (200+ skills)
4. **Learning Resource Dataset** - Educational resources for skill development

Training data is synthetically generated from role-skill relationships to create diverse user profiles.

## Deep Learning Approach

### Why ANN/MLP?

The user's profile is represented as a structured numerical skill vector. An MLP/ANN is suitable for learning nonlinear relationships between combinations of skills and career-role classes.

### Architecture

```
Input (skill features)
    ↓
Dense(128, ReLU)
    ↓
Dropout(0.30)
    ↓
Dense(64, ReLU)
    ↓
Dropout(0.20)
    ↓
Dense(32, ReLU)
    ↓
Dense(N, Softmax)
```

Where N = number of career role classes (~85)

### Evaluation Metrics (Authentic Test Set Results)

Evaluated on 3,300 stratified test samples across 85 career roles:

| Metric | ANN / MLP (Production) | 1D CNN (Comparative) | LSTM (Comparative) |
| :--- | :---: | :---: | :---: |
| **Top-1 Accuracy** | **68.27%** | 17.73% | 47.52% |
| **Top-3 Accuracy** | **85.73%** | 32.27% | 70.33% |
| **Weighted Precision** | **69.70%** | 23.72% | 50.81% |
| **Weighted Recall** | **68.27%** | 17.73% | 47.52% |
| **Weighted F1 Score** | **68.21%** | 17.08% | 47.09% |
| **Test Loss** | **1.2261** | 3.4166 | 1.9848 |
| **Parameters** | **61,013** | 16,469 | 32,501 |
| **Inference Latency** | **0.221 ms / sample** | 0.278 ms / sample | 0.747 ms / sample |

### Automated Testing

Run full backend test suite:
```bash
python -m pytest backend/tests -v
```

Build frontend production bundle:
```bash
cd frontend
npm run build
```

Detailed college examination notes and viva preparation questions are documented in [docs/viva.md](docs/viva.md).

## Limitations

- Job-market data is periodically refreshed, not real-time
- Salary information varies by region and source
- Training data is synthetically generated
- Model predictions are career recommendations, not employment guarantees

## License

MIT License

## Author

Vista Flare Project
