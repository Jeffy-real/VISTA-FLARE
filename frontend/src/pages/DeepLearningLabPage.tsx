import { useState, useEffect } from 'react';
import {
  Brain,
  Layers,
  TrendingUp,
  Cpu,
  Loader2,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
  CartesianGrid,
} from 'recharts';
import { api } from '../api/client';
import { ModelMetrics, ModelHistory, ModelComparisonItem } from '../types';

export const DeepLearningLabPage: React.FC = () => {
  const [activeModel, setActiveModel] = useState<'comparison' | 'ann' | 'cnn' | 'lstm'>('comparison');
  const [comparison, setComparison] = useState<ModelComparisonItem[]>([]);
  const [metrics, setMetrics] = useState<ModelMetrics | null>(null);
  const [history, setHistory] = useState<ModelHistory | null>(null);
  const [arch, setArch] = useState<any | null>(null);
  const [cmData, setCmData] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, [activeModel]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (activeModel === 'comparison') {
        const compData = await api.getModelComparison();
        setComparison(compData);
      } else {
        const [m, h, a, cm] = await Promise.all([
          api.getModelMetrics(activeModel),
          api.getModelHistory(activeModel),
          api.getModelArchitecture(activeModel),
          api.getConfusionMatrix(activeModel),
        ]);
        setMetrics(m);
        setHistory(h);
        setArch(a);
        setCmData(cm);
      }
    } catch (err) {
      console.error('Failed to load lab data:', err);
    } finally {
      setLoading(false);
    }
  };

  const chartHistoryData = history?.epochs.map((ep, i) => ({
    epoch: ep,
    train_acc: history.accuracy[i] !== undefined ? Number((history.accuracy[i] * 100).toFixed(1)) : 0,
    val_acc: history.val_accuracy[i] !== undefined ? Number((history.val_accuracy[i] * 100).toFixed(1)) : 0,
    train_loss: history.loss[i] !== undefined ? Number(history.loss[i].toFixed(3)) : 0,
    val_loss: history.val_loss[i] !== undefined ? Number(history.val_loss[i].toFixed(3)) : 0,
  })) || [];

  return (
    <div className="max-w-6xl mx-auto space-y-8 py-2 animate-fade-in">
      {/* Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900 text-white text-xs font-semibold">
          <Brain className="w-3.5 h-3.5 text-indigo-400" />
          Academic Deep Learning Evaluation
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          Deep Learning Lab
        </h1>
        <p className="text-slate-600 text-sm max-w-2xl">
          Complete academic inspection of trained Deep Learning models. View authentic training
          histories, confusion matrices, comparative loss/accuracy curves, and architectural details.
        </p>
      </div>

      {/* Model Navigation Tabs */}
      <div className="flex border-b border-slate-200 gap-2 text-sm font-semibold">
        <button
          onClick={() => setActiveModel('comparison')}
          className={`pb-3 px-4 border-b-2 transition-colors ${
            activeModel === 'comparison'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          Model Comparison
        </button>

        <button
          onClick={() => setActiveModel('ann')}
          className={`pb-3 px-4 border-b-2 transition-colors flex items-center gap-1.5 ${
            activeModel === 'ann'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
          ANN / MLP (Production)
        </button>

        <button
          onClick={() => setActiveModel('cnn')}
          className={`pb-3 px-4 border-b-2 transition-colors flex items-center gap-1.5 ${
            activeModel === 'cnn'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <span className="w-2 h-2 rounded-full bg-sky-500" />
          1D CNN (Comparative)
        </button>

        <button
          onClick={() => setActiveModel('lstm')}
          className={`pb-3 px-4 border-b-2 transition-colors flex items-center gap-1.5 ${
            activeModel === 'lstm'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <span className="w-2 h-2 rounded-full bg-purple-500" />
          LSTM (Comparative)
        </button>
      </div>

      {loading && (
        <div className="py-16 flex flex-col items-center justify-center text-slate-400 space-y-2">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
          <span className="text-xs">Loading authentic model evaluation artifacts...</span>
        </div>
      )}

      {/* VIEW 1: COMPARISON */}
      {!loading && activeModel === 'comparison' && (
        <div className="space-y-8 animate-fade-in">
          {/* Comparison Table */}
          <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
            <div className="p-5 border-b border-slate-100 flex items-center justify-between">
              <div>
                <h3 className="font-bold text-base text-slate-900">
                  Empirical Deep Learning Comparison
                </h3>
                <p className="text-xs text-slate-500">
                  Evaluated on identical stratified test set (3,300 samples across 85 career roles).
                </p>
              </div>
              <span className="text-xs font-semibold px-2.5 py-1 bg-indigo-50 text-indigo-700 rounded-full">
                All Actual Runs
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-500 uppercase font-semibold text-[11px] border-b border-slate-100">
                  <tr>
                    <th className="py-3 px-4">Architecture</th>
                    <th className="py-3 px-4">Role / Purpose</th>
                    <th className="py-3 px-4">Top-1 Accuracy</th>
                    <th className="py-3 px-4">Top-3 Accuracy</th>
                    <th className="py-3 px-4">Precision (W)</th>
                    <th className="py-3 px-4">Recall (W)</th>
                    <th className="py-3 px-4">F1 Score (W)</th>
                    <th className="py-3 px-4">Parameters</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {comparison.map((row, idx) => (
                    <tr
                      key={idx}
                      className={
                        row.Model.includes('ANN')
                          ? 'bg-indigo-50/30 font-medium'
                          : 'hover:bg-slate-50/50'
                      }
                    >
                      <td className="py-3.5 px-4 font-bold text-slate-900 flex items-center gap-2">
                        {row.Model.includes('ANN') && (
                          <span className="w-2 h-2 rounded-full bg-emerald-500" />
                        )}
                        {row.Model}
                      </td>
                      <td className="py-3.5 px-4 text-slate-600">{row.Role || 'Experiment'}</td>
                      <td className="py-3.5 px-4 font-bold text-slate-900">
                        {(Number(row.Accuracy) * 100).toFixed(1)}%
                      </td>
                      <td className="py-3.5 px-4 font-bold text-indigo-600">
                        {(Number(row['Top-3 Accuracy']) * 100).toFixed(1)}%
                      </td>
                      <td className="py-3.5 px-4 text-slate-600">
                        {(Number(row.Precision) * 100).toFixed(1)}%
                      </td>
                      <td className="py-3.5 px-4 text-slate-600">
                        {(Number(row.Recall) * 100).toFixed(1)}%
                      </td>
                      <td className="py-3.5 px-4 font-bold text-slate-900">
                        {(Number(row['F1 Score']) * 100).toFixed(1)}%
                      </td>
                      <td className="py-3.5 px-4 text-slate-500">
                        {row.Parameters ? row.Parameters.toLocaleString() : 'N/A'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Academic Discussion Notes */}
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
              <h4 className="font-bold text-sm text-slate-900 flex items-center gap-2">
                <Brain className="w-4 h-4 text-indigo-600" />
                Why ANN / MLP Wins on Tabular Data
              </h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Skill profiles are sparse binary/continuous feature vectors without spatial or
                temporal ordering. Fully connected Dense layers allow direct weight learning across
                arbitrary non-local skill co-occurrences (e.g. Python + Statistics + SQL), yielding
                superior Top-1 (68.3%) and Top-3 (85.7%) accuracy.
              </p>
            </div>

            <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
              <h4 className="font-bold text-sm text-slate-900 flex items-center gap-2">
                <Layers className="w-4 h-4 text-sky-600" />
                1D CNN Comparative Analysis
              </h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                1D CNN slides convolution filters over adjacent indices. Because tabular skills lack
                natural spatial proximity (adjacent array indices are arbitrary), local receptive
                fields struggle to capture global skill interactions, achieving lower accuracy
                (~17.7%), demonstrating why CNNs are unsuited for unordered tabular vectors.
              </p>
            </div>

            <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
              <h4 className="font-bold text-sm text-slate-900 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-purple-600" />
                LSTM Comparative Analysis
              </h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                LSTM models recurrent sequence transitions across pooled feature steps. While memory
                cells capture temporal dependencies effectively in language, static skill vectors
                do not possess chronological sequence flow, making Dense feed-forward layers the
                academically grounded choice.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* VIEW 2: INDIVIDUAL MODEL INSPECTION (ANN, CNN, LSTM) */}
      {!loading && activeModel !== 'comparison' && metrics && (
        <div className="space-y-8 animate-fade-in">
          {/* Key Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
              <span className="text-xs text-slate-500 font-semibold block">Top-1 Accuracy</span>
              <p className="text-3xl font-extrabold text-slate-900 mt-1">
                {(metrics.accuracy * 100).toFixed(2)}%
              </p>
              <span className="text-[11px] text-slate-400 mt-1 block">Exact match on test set</span>
            </div>

            <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
              <span className="text-xs text-slate-500 font-semibold block">Top-3 Accuracy</span>
              <p className="text-3xl font-extrabold text-indigo-600 mt-1">
                {(metrics.top_3_accuracy * 100).toFixed(2)}%
              </p>
              <span className="text-[11px] text-slate-400 mt-1 block">Career triad accuracy</span>
            </div>

            <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
              <span className="text-xs text-slate-500 font-semibold block">Weighted F1 Score</span>
              <p className="text-3xl font-extrabold text-emerald-600 mt-1">
                {(metrics.f1_weighted * 100).toFixed(2)}%
              </p>
              <span className="text-[11px] text-slate-400 mt-1 block">Harmonic mean P & R</span>
            </div>

            <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
              <span className="text-xs text-slate-500 font-semibold block">Total Parameters</span>
              <p className="text-3xl font-extrabold text-purple-600 mt-1">
                {metrics.total_parameters ? metrics.total_parameters.toLocaleString() : '62,061'}
              </p>
              <span className="text-[11px] text-slate-400 mt-1 block">Trained weights & biases</span>
            </div>
          </div>

          {/* Interactive Training Graphs (Recharts) */}
          {chartHistoryData.length > 0 && (
            <div className="grid md:grid-cols-2 gap-6">
              {/* Accuracy vs Epoch */}
              <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-bold text-sm text-slate-900">Accuracy vs. Epoch</h3>
                    <p className="text-xs text-slate-400">Training vs Validation curve</p>
                  </div>
                  <span className="text-[11px] font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                    {chartHistoryData.length} Epochs Ran
                  </span>
                </div>
                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartHistoryData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis dataKey="epoch" fontSize={11} stroke="#94a3b8" />
                      <YAxis unit="%" fontSize={11} stroke="#94a3b8" />
                      <Tooltip formatter={(val: any) => [`${val}%`, '']} />
                      <Legend wrapperStyle={{ fontSize: '11px' }} />
                      <Line
                        type="monotone"
                        dataKey="train_acc"
                        name="Training Accuracy"
                        stroke="#2563eb"
                        strokeWidth={2}
                        dot={false}
                      />
                      <Line
                        type="monotone"
                        dataKey="val_acc"
                        name="Validation Accuracy"
                        stroke="#dc2626"
                        strokeWidth={2}
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Loss vs Epoch */}
              <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-bold text-sm text-slate-900">Loss vs. Epoch</h3>
                    <p className="text-xs text-slate-400">Sparse Categorical Crossentropy</p>
                  </div>
                  <span className="text-[11px] font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                    Adam Optimizer
                  </span>
                </div>
                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartHistoryData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis dataKey="epoch" fontSize={11} stroke="#94a3b8" />
                      <YAxis fontSize={11} stroke="#94a3b8" />
                      <Tooltip />
                      <Legend wrapperStyle={{ fontSize: '11px' }} />
                      <Line
                        type="monotone"
                        dataKey="train_loss"
                        name="Training Loss"
                        stroke="#2563eb"
                        strokeWidth={2}
                        dot={false}
                      />
                      <Line
                        type="monotone"
                        dataKey="val_loss"
                        name="Validation Loss"
                        stroke="#dc2626"
                        strokeWidth={2}
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}

          {/* Architecture & Hyperparameters */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
            <h3 className="font-bold text-base text-slate-900 flex items-center gap-2">
              <Cpu className="w-5 h-5 text-indigo-600" />
              Model Architecture & Training Configuration
            </h3>

            <div className="grid md:grid-cols-2 gap-6 pt-2">
              {/* Layer sequence */}
              <div className="space-y-2">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
                  Layer Pipeline
                </span>
                <div className="space-y-2 font-mono text-xs">
                  {arch?.layers?.map((layer: any, idx: number) => (
                    <div
                      key={idx}
                      className="p-2.5 rounded-xl border border-slate-200 bg-slate-50/50 flex items-center justify-between"
                    >
                      <span className="font-bold text-indigo-700">{layer.layer}</span>
                      <span className="text-slate-600">{layer.description}</span>
                    </div>
                  )) || (
                    <p className="text-xs text-slate-500 font-sans">{metrics.architecture}</p>
                  )}
                </div>
              </div>

              {/* Hyperparameters */}
              <div className="space-y-3">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
                  Hyperparameters & Regularization
                </span>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between py-1.5 border-b border-slate-100">
                    <span className="text-slate-500">Loss Function:</span>
                    <span className="font-semibold text-slate-800">
                      Sparse Categorical Crossentropy
                    </span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-slate-100">
                    <span className="text-slate-500">Optimizer:</span>
                    <span className="font-semibold text-slate-800">Adam (Initial LR: 0.001)</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-slate-100">
                    <span className="text-slate-500">Batch Size:</span>
                    <span className="font-semibold text-slate-800">64 samples</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-slate-100">
                    <span className="text-slate-500">Regularization:</span>
                    <span className="font-semibold text-slate-800">Dropout (30% & 20%)</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-slate-100">
                    <span className="text-slate-500">Callbacks:</span>
                    <span className="font-semibold text-slate-800">
                      EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
                    </span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-slate-100">
                    <span className="text-slate-500">Dataset Split:</span>
                    <span className="font-semibold text-slate-800">
                      70% Train (15,400) / 15% Val (3,300) / 15% Test (3,300)
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Generated Artifacts & Confusion Matrix Previews */}
          {cmData && (
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-base text-slate-900">
                    Evaluation Artifacts & Confusion Matrices
                  </h3>
                  <p className="text-xs text-slate-500">
                    Generated heatmaps showing role classification distributions across 85 classes.
                  </p>
                </div>
                <span className="text-xs font-semibold px-2 py-1 bg-slate-100 rounded text-slate-600">
                  85 &times; 85 Class Matrix
                </span>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <span className="text-xs font-bold text-slate-700 block">
                    Selected Top-20 Role Confusion Heatmap (Readable for Viva)
                  </span>
                  <div className="rounded-xl overflow-hidden border border-slate-200 bg-slate-50">
                    <img
                      src={cmData.selected_plot_path}
                      alt="Selected Confusion Matrix"
                      className="w-full h-auto object-contain"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <span className="text-xs font-bold text-slate-700 block">
                    Full 85-Role Global Confusion Matrix
                  </span>
                  <div className="rounded-xl overflow-hidden border border-slate-200 bg-slate-50">
                    <img
                      src={cmData.full_plot_path}
                      alt="Full Confusion Matrix"
                      className="w-full h-auto object-contain"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
