import { ModelMetrics } from '../types';
import { Activity, Layers, Brain, Target, Zap, TrendingUp } from 'lucide-react';

interface MetricsPanelProps {
  metrics: ModelMetrics;
}

export function MetricsPanel({ metrics }: MetricsPanelProps) {
  const cards = [
    {
      icon: Target,
      label: 'Top-1 Accuracy',
      value: `${(metrics.accuracy * 100).toFixed(2)}%`,
      color: 'text-green-600 bg-green-50',
    },
    {
      icon: TrendingUp,
      label: 'Top-3 Accuracy',
      value: `${(metrics.top_3_accuracy * 100).toFixed(2)}%`,
      color: 'text-blue-600 bg-blue-50',
    },
    {
      icon: Zap,
      label: 'F1 Score',
      value: `${(metrics.f1_weighted * 100).toFixed(2)}%`,
      color: 'text-purple-600 bg-purple-50',
    },
    {
      icon: Brain,
      label: 'Model',
      value: metrics.model_version,
      color: 'text-amber-600 bg-amber-50',
    },
    {
      icon: Layers,
      label: 'Architecture',
      value: metrics.architecture || 'ANN',
      color: 'text-pink-600 bg-pink-50',
    },
    {
      icon: Activity,
      label: 'Classes',
      value: metrics.num_classes.toString(),
      color: 'text-teal-600 bg-teal-50',
    },
  ];

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Model Performance</h2>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {cards.map((card, i) => (
          <div key={i} className="p-3 rounded-lg bg-gray-50">
            <div className="flex items-center gap-2 mb-1">
              <card.icon className={`h-4 w-4 p-0.5 rounded ${card.color}`} />
              <span className="text-xs text-gray-600">{card.label}</span>
            </div>
            <p className="text-lg font-semibold text-gray-900">{card.value}</p>
          </div>
        ))}
      </div>
      <p className="mt-4 text-xs text-gray-500">
        Trained on {metrics.training_samples.toLocaleString()} samples with {metrics.num_skills} skill features
      </p>
    </div>
  );
}
