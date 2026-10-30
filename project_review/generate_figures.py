import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

FIGURES_DIR = Path("project_review/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# 1. High-Quality Model Comparison Chart
def generate_comparison_chart():
    models = ['Deep ANN\n(Primary MLP)', '1D CNN\n(Convolutional)', 'LSTM\n(Recurrent)']
    accuracy = [68.27, 17.73, 47.52]
    top3_acc = [85.73, 32.27, 70.33]
    f1_score = [68.21, 17.08, 47.09]

    x = np.arange(len(models))
    width = 0.25

    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)

    rects1 = ax.bar(x - width, accuracy, width, label='Test Accuracy (%)', color='#2563eb', edgecolor='black', linewidth=0.5)
    rects2 = ax.bar(x, top3_acc, width, label='Top-3 Accuracy (%)', color='#059669', edgecolor='black', linewidth=0.5)
    rects3 = ax.bar(x + width, f1_score, width, label='Weighted F1 (%)', color='#7c3aed', edgecolor='black', linewidth=0.5)

    ax.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
    ax.set_title('Vista Flare — Deep Learning Model Performance Comparison (Test Split N=3,300)', fontsize=13, fontweight='bold', pad=14)
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=11, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.legend(loc='upper right', frameon=True, fontsize=10)

    # Attach labels above bars
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.2f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 4),  # 4 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, fontweight='bold')

    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "model_benchmark_comparison.png", dpi=300)
    plt.close(fig)
    print("Saved model_benchmark_comparison.png")

# 2. Complete Architecture Diagram
def generate_architecture_diagram():
    fig, ax = plt.subplots(figsize=(14, 7), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 7)

    # Title
    ax.text(7, 6.6, "Vista Flare — End-to-End System & Deep Learning Architecture", 
            ha='center', va='center', fontsize=15, fontweight='bold', color='#0f172a')

    # Sub-box 1: User & Frontend (Left)
    ax.add_patch(patches.FancyBboxPatch((0.4, 3.6), 2.5, 2.4, boxstyle="round,pad=0.15", facecolor='#f0fdf4', edgecolor='#16a34a', linewidth=2))
    ax.text(1.65, 5.7, "1. USER INTERACTION", ha='center', va='center', fontsize=10, fontweight='bold', color='#166534')
    ax.text(1.65, 4.8, "• Skill Analyzer UI\n• Skill Proficiency Rating\n  (Beginner - Expert)\n• Career Matches View\n• Learning Roadmaps", 
            ha='center', va='center', fontsize=9, color='#1e293b')

    # Sub-box 2: Preprocessing & Normalization (Center-Left)
    ax.add_patch(patches.FancyBboxPatch((3.4, 3.6), 2.7, 2.4, boxstyle="round,pad=0.15", facecolor='#eff6ff', edgecolor='#2563eb', linewidth=2))
    ax.text(4.75, 5.7, "2. NORMALIZATION & VECTOR", ha='center', va='center', fontsize=10, fontweight='bold', color='#1e40af')
    ax.text(4.75, 4.8, "• Alias Mapping (86 aliases)\n• Skill Canonicalization\n• Level Value Weights:\n  [0.0, 0.35, 0.65, 0.85, 1.0]\n• Dense Vector: 373 floats", 
            ha='center', va='center', fontsize=9, color='#1e293b')

    # Sub-box 3: Deep Learning Engine (Center-Right)
    ax.add_patch(patches.FancyBboxPatch((6.6, 3.2), 3.4, 3.1, boxstyle="round,pad=0.15", facecolor='#faf5ff', edgecolor='#7c3aed', linewidth=2))
    ax.text(8.3, 6.0, "3. DEEP LEARNING INFERENCE", ha='center', va='center', fontsize=10, fontweight='bold', color='#5b21b6')
    ax.text(8.3, 4.7, "Primary Model: Deep ANN (MLP)\n• Dense(128, ReLU) + Dropout(0.30)\n• Dense(64, ReLU) + Dropout(0.20)\n• Dense(32, ReLU)\n• Dense(85, Softmax) -> 85 Roles\n\nRuntime Fallback: Scikit-learn MLP\n(Guarantees zero-downtime serving)", 
            ha='center', va='center', fontsize=8.5, color='#1e293b')

    # Sub-box 4: Career Recommendation & Jobs (Right)
    ax.add_patch(patches.FancyBboxPatch((10.5, 3.6), 3.1, 2.4, boxstyle="round,pad=0.15", facecolor='#fff7ed', edgecolor='#ea580c', linewidth=2))
    ax.text(12.05, 5.7, "4. RECOMMENDATION & MARKET", ha='center', va='center', fontsize=10, fontweight='bold', color='#9a3412')
    ax.text(12.05, 4.7, "• Top-K Career Ranking\n• Skill-Gap Analysis Engine\n• Live Jobs Ingestion (192 jobs):\n  - Arbeitnow (10 live)\n  - Remotive (12 live)\n  - Seed Directory (170)", 
            ha='center', va='center', fontsize=8.5, color='#1e293b')

    # Arrows for flow 1->2->3->4
    ax.annotate('', xy=(3.4, 4.8), xytext=(2.9, 4.8), arrowprops=dict(arrowstyle="->", color='#2563eb', lw=2.5))
    ax.annotate('', xy=(6.6, 4.8), xytext=(6.1, 4.8), arrowprops=dict(arrowstyle="->", color='#7c3aed', lw=2.5))
    ax.annotate('', xy=(10.5, 4.8), xytext=(10.0, 4.8), arrowprops=dict(arrowstyle="->", color='#ea580c', lw=2.5))

    # Bottom Box: Training Pipeline (Offline)
    ax.add_patch(patches.FancyBboxPatch((0.4, 0.4), 13.2, 2.2, boxstyle="round,pad=0.15", facecolor='#f8fafc', edgecolor='#64748b', linewidth=1.5, linestyle='--'))
    ax.text(7.0, 2.2, "OFFLINE MODEL TRAINING & EVALUATION PIPELINE", ha='center', va='center', fontsize=10, fontweight='bold', color='#334155')
    
    # Steps inside bottom box
    step_y = 1.2
    ax.text(2.0, step_y, "Seed Roles & Skills\n(85 Roles, 373 Skills,\n508 Relations)", ha='center', va='center', fontsize=8.5, bbox=dict(boxstyle="square,pad=0.3", fc="#ffffff", ec="#94a3b8"))
    ax.text(5.0, step_y, "Synthetic Profile Gen\n(22,000 Profiles,\nStratified 70/15/15)", ha='center', va='center', fontsize=8.5, bbox=dict(boxstyle="square,pad=0.3", fc="#ffffff", ec="#94a3b8"))
    ax.text(8.5, step_y, "Multi-Model Benchmarking\n• ANN (61,013 params, 68.27% acc)\n• 1D CNN (16,469 params, 17.73% acc)\n• LSTM (32,501 params, 47.52% acc)", ha='center', va='center', fontsize=8, bbox=dict(boxstyle="square,pad=0.3", fc="#ffffff", ec="#94a3b8"))
    ax.text(12.0, step_y, "Evaluation & Persistence\n• Keras Artifact (ann_model.keras)\n• Sklearn Backup (sklearn_model.pkl)\n• Encoders & JSON Reports", ha='center', va='center', fontsize=8, bbox=dict(boxstyle="square,pad=0.3", fc="#ffffff", ec="#94a3b8"))

    ax.annotate('', xy=(3.5, step_y), xytext=(2.9, step_y), arrowprops=dict(arrowstyle="->", color='#64748b', lw=1.5))
    ax.annotate('', xy=(6.8, step_y), xytext=(6.1, step_y), arrowprops=dict(arrowstyle="->", color='#64748b', lw=1.5))
    ax.annotate('', xy=(10.3, step_y), xytext=(9.7, step_y), arrowprops=dict(arrowstyle="->", color='#64748b', lw=1.5))
    
    # Connecting offline pipeline to inference engine
    ax.annotate('', xy=(8.3, 3.2), xytext=(8.3, 2.4), arrowprops=dict(arrowstyle="->", color='#7c3aed', lw=2, linestyle=':'))
    ax.text(8.8, 2.7, "Deploy Artifacts", fontsize=8, color='#7c3aed', fontweight='bold')

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "system_architecture_diagram.png", dpi=300)
    plt.close(fig)
    print("Saved system_architecture_diagram.png")

if __name__ == "__main__":
    generate_comparison_chart()
    generate_architecture_diagram()

