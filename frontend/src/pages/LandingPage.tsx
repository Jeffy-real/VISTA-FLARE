import {
  Sparkles,
  ArrowRight,
  Brain,
  Compass,
  Briefcase,
  TrendingUp,
  Award,
} from 'lucide-react';
import { ModelMetrics, HealthResponse } from '../types';

interface LandingPageProps {
  onNavigate: (view: string) => void;
  metrics: ModelMetrics | null;
  health: HealthResponse | null;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onNavigate, metrics, health }) => {
  const annReady = health?.model_type === 'tensorflow';
  const modelLabel = annReady ? 'ANN model ready' : health?.model_loaded ? 'Fallback model ready' : 'Model unavailable';
  return (
    <main className="page-shell space-y-16 py-4 animate-fade-in">
      {/* Hero Section */}
      <section className="text-center space-y-6 max-w-4xl mx-auto pt-6">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary-50 border border-primary-200 text-primary-700 text-xs font-semibold uppercase tracking-wider">
          <Sparkles className="w-3.5 h-3.5" />
          Powered by Deep Learning & Market Intelligence
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold text-slate-900 tracking-tight leading-tight">
          See Your Skills. <br />
          <span className="bg-gradient-to-r from-primary-600 via-indigo-600 to-accent-600 bg-clip-text text-transparent">
            Find Your Direction.
          </span>
        </h1>

        <p className="text-lg sm:text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
           Vista Flare uses a trained deep-learning model and a local job-market catalog to connect your
          skills with the careers, companies, and learning paths that fit your future.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
          <button
            id="hero-discover-btn"
            onClick={() => onNavigate('skills')}
            className="inline-flex items-center gap-2 px-7 py-3.5 bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-700 hover:to-indigo-700 text-white font-semibold rounded-xl shadow-lg shadow-primary-500/25 transition-all transform hover:-translate-y-0.5"
          >
            Discover My Career
            <ArrowRight className="w-4 h-4" />
          </button>

          <button
            id="hero-market-btn"
            onClick={() => onNavigate('market')}
            className="inline-flex items-center gap-2 px-6 py-3.5 bg-white hover:bg-slate-50 text-slate-700 font-semibold rounded-xl border border-slate-200 shadow-sm transition-all"
          >
            <TrendingUp className="w-4 h-4 text-slate-500" />
            Explore Job Market
          </button>

          <button
            id="hero-lab-btn"
            onClick={() => onNavigate('lab')}
            className="inline-flex items-center gap-2 px-6 py-3.5 bg-slate-900 hover:bg-slate-800 text-white font-semibold rounded-xl shadow-sm transition-all"
          >
            <Brain className="w-4 h-4 text-indigo-400" />
            Deep Learning Lab
          </button>
        </div>

        {/* Live System Health Badge */}
        <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 pt-4 text-xs text-slate-500" aria-label="System status">
          <span className="inline-flex items-center gap-1.5">
             <span role="status" aria-label={modelLabel}
               className={`w-2 h-2 rounded-full ${
                 annReady ? 'bg-emerald-500' : health?.model_loaded ? 'bg-amber-500' : 'bg-rose-500'
               }`}
             />
             {modelLabel}
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span role="status" aria-label={health?.database_connected ? 'Database connected' : 'Database offline'}
              className={`w-2 h-2 rounded-full ${
                health?.database_connected ? 'bg-emerald-500' : 'bg-rose-500'
              }`}
            />
            {health?.database_connected ? 'Database Connected (85 Roles)' : 'DB Offline'}
          </span>
          {metrics && (
            <span className="inline-flex items-center gap-1.5 text-slate-600 font-medium">
              <Award className="w-3.5 h-3.5 text-indigo-500" />
             ANN evaluation Top-3: {(metrics.top_3_accuracy * 100).toFixed(1)}%
            </span>
          )}
        </div>
      </section>

      {/* Feature Grid */}
      <section className="grid md:grid-cols-3 gap-6 max-w-6xl mx-auto px-4">
        <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm hover:shadow-md transition-shadow">
          <div className="w-11 h-11 rounded-xl bg-primary-50 text-primary-600 flex items-center justify-center mb-4">
            <Brain className="w-6 h-6" />
          </div>
           <h2 className="text-lg font-bold text-slate-900 mb-2">Deep Learning Matching</h2>
          <p className="text-sm text-slate-600 leading-relaxed mb-4">
            Trained multi-class Artificial Neural Network (MLP) analyzing 373 normalized skill
            features to predict your top 3 career pathways with Softmax probability confidence.
          </p>
          <button
            onClick={() => onNavigate('lab')}
            className="text-xs font-semibold text-primary-600 hover:text-primary-700 inline-flex items-center gap-1"
          >
            Inspect Model Architecture &rarr;
          </button>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm hover:shadow-md transition-shadow">
          <div className="w-11 h-11 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-4">
            <Compass className="w-6 h-6" />
          </div>
           <h2 className="text-lg font-bold text-slate-900 mb-2">Skill Gap & Roadmap</h2>
          <p className="text-sm text-slate-600 leading-relaxed mb-4">
            Deterministic gap analysis breaking down Strong, Developing, and Missing skills with a
            5-stage personalized roadmap and curated courses.
          </p>
          <button
            onClick={() => onNavigate('skills')}
            className="text-xs font-semibold text-emerald-600 hover:text-emerald-700 inline-flex items-center gap-1"
          >
            Analyze Your Skill Gap &rarr;
          </button>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm hover:shadow-md transition-shadow">
          <div className="w-11 h-11 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center mb-4">
            <Briefcase className="w-6 h-6" />
          </div>
           <h2 className="text-lg font-bold text-slate-900 mb-2">Job Market Fit</h2>
          <p className="text-sm text-slate-600 leading-relaxed mb-4">
             Explore catalogued job postings, company skill alignment scores, salary disclosures,
             and demand trends. Availability is not guaranteed to be live.
          </p>
          <button
             onClick={() => onNavigate('market')}
            className="text-xs font-semibold text-purple-600 hover:text-purple-700 inline-flex items-center gap-1"
          >
             Browse Catalogued Roles &rarr;
          </button>
        </div>
      </section>

      {/* Model Performance Snapshot */}
      {metrics && (
        <section className="bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 rounded-3xl p-8 sm:p-12 text-white max-w-6xl mx-auto shadow-xl">
          <div className="grid md:grid-cols-2 gap-8 items-center">
            <div className="space-y-4">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 text-indigo-300 text-xs font-medium">
                 Model Report Provenance
              </div>
              <h2 className="text-2xl sm:text-3xl font-bold tracking-tight">
                 Available Deep Learning Results
              </h2>
              <p className="text-slate-300 text-sm leading-relaxed">
                 Metrics and charts are presented from the available model report artifacts. We provide
                 confusion matrices, accuracy/loss plots, and model comparisons when those artifacts exist.
              </p>
              <div className="flex gap-4 pt-2">
                <button
                  onClick={() => onNavigate('lab')}
                  className="px-5 py-2.5 bg-indigo-500 hover:bg-indigo-600 text-white font-medium rounded-xl text-sm transition-colors"
                >
                  View Complete Evaluation
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-5 border border-white/10">
                <span className="text-xs text-indigo-300 font-medium">Top-1 Accuracy</span>
                <p className="text-3xl font-extrabold text-white mt-1">
                  {(metrics.accuracy * 100).toFixed(1)}%
                </p>
                <span className="text-[11px] text-slate-400 mt-1 block">85 Class Output</span>
              </div>

              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-5 border border-white/10">
                <span className="text-xs text-indigo-300 font-medium">Top-3 Accuracy</span>
                <p className="text-3xl font-extrabold text-emerald-400 mt-1">
                  {(metrics.top_3_accuracy * 100).toFixed(1)}%
                </p>
                <span className="text-[11px] text-slate-400 mt-1 block">Career Triad Match</span>
              </div>

              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-5 border border-white/10">
                <span className="text-xs text-indigo-300 font-medium">Weighted F1</span>
                <p className="text-3xl font-extrabold text-purple-300 mt-1">
                  {(metrics.f1_weighted * 100).toFixed(1)}%
                </p>
                <span className="text-[11px] text-slate-400 mt-1 block">Precision & Recall Balance</span>
              </div>

              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-5 border border-white/10">
                <span className="text-xs text-indigo-300 font-medium">Training Samples</span>
                <p className="text-3xl font-extrabold text-amber-300 mt-1">
                  {(metrics.training_samples / 1000).toFixed(0)}k
                </p>
                <span className="text-[11px] text-slate-400 mt-1 block">373 Skill Dimensions</span>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Demonstration Steps */}
      <section className="max-w-4xl mx-auto px-4 text-center space-y-8">
        <h2 className="text-2xl font-bold text-slate-900">How Vista Flare Works</h2>
        <div className="grid sm:grid-cols-4 gap-4 text-left">
          <div className="p-4 bg-white rounded-xl border border-slate-200">
            <span className="w-7 h-7 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center font-bold text-xs mb-3">
              1
            </span>
            <h4 className="font-semibold text-sm text-slate-900 mb-1">Input Skills</h4>
            <p className="text-xs text-slate-600">Select your technologies and proficiency levels.</p>
          </div>

          <div className="p-4 bg-white rounded-xl border border-slate-200">
            <span className="w-7 h-7 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center font-bold text-xs mb-3">
              2
            </span>
            <h4 className="font-semibold text-sm text-slate-900 mb-1">ANN Prediction</h4>
            <p className="text-xs text-slate-600">Dense neural network calculates Softmax match scores.</p>
          </div>

          <div className="p-4 bg-white rounded-xl border border-slate-200">
            <span className="w-7 h-7 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center font-bold text-xs mb-3">
              3
            </span>
            <h4 className="font-semibold text-sm text-slate-900 mb-1">Skill Gap Analysis</h4>
            <p className="text-xs text-slate-600">Identifies strong, developing, and missing competencies.</p>
          </div>

          <div className="p-4 bg-white rounded-xl border border-slate-200">
            <span className="w-7 h-7 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center font-bold text-xs mb-3">
              4
            </span>
            <h4 className="font-semibold text-sm text-slate-900 mb-1">Jobs & Roadmap</h4>
            <p className="text-xs text-slate-600">Connect to open jobs and a personalized learning journey.</p>
          </div>
        </div>
      </section>
    </main>
  );
};
