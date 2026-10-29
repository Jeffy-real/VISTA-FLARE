import {
  Compass,
  Briefcase,
  Sparkles,
  Info,
  CheckCircle2,
  RotateCcw,
} from 'lucide-react';
import { CareerRecommendation, SelectedSkill } from '../types';

interface CareerMatchesPageProps {
  recommendations: CareerRecommendation[];
  selectedSkills: SelectedSkill[];
  model?: string | null;
  onSelectRole: (roleName: string) => void;
  onExploreJobs: (roleName: string) => void;
  onReset: () => void;
  savedRoles: string[];
  onToggleSavedRole: (role: string) => void;
}

const RANK_CONFIG = [
  {
    rank: 1,
    title: 'Top Recommendation',
    badge: 'Primary Pathway',
    border: 'border-slate-300 ring-1 ring-slate-200',
    headerBg: 'bg-slate-50',
    iconColor: 'text-indigo-600',
    barColor: 'from-indigo-600 to-blue-600',
  },
  {
    rank: 2,
    title: 'Second Match',
    badge: 'Secondary Pathway',
    border: 'border-slate-200 hover:border-slate-300',
    headerBg: 'bg-slate-50/60',
    iconColor: 'text-slate-600',
    barColor: 'from-slate-600 to-indigo-500',
  },
  {
    rank: 3,
    title: 'Third Match',
    badge: 'Alternative Pathway',
    border: 'border-slate-200 hover:border-slate-300',
    headerBg: 'bg-slate-50/40',
    iconColor: 'text-slate-500',
    barColor: 'from-slate-500 to-slate-700',
  },
];

function formatScoreDisplay(score: number): { display: string; raw: string; barWidth: number; note: string } {
  if (score >= 0.995) {
    return {
      display: score >= 1 ? '99.9%+' : `${(score * 100).toFixed(1)}%`,
      raw: score.toFixed(4),
      barWidth: 99,
      note: 'Dominant probability across 85 classified career roles',
    };
  }
  if (score >= 0.01) {
    return {
      display: `${(score * 100).toFixed(1)}%`,
      raw: score.toFixed(4),
      barWidth: Math.max(score * 100, 8),
      note: `Classifier confidence: ${(score * 100).toFixed(1)}%`,
    };
  }
  if (score > 0) {
    return {
      display: '<0.1%',
      raw: score < 0.0001 ? score.toExponential(2) : score.toFixed(4),
      barWidth: 4,
      note: 'Runner-up class in 85-way single-label classification',
    };
  }
  return {
    display: '<0.01%',
    raw: '0.0000',
    barWidth: 3,
    note: 'Ranked by relative output logit in Softmax distribution',
  };
}

export const CareerMatchesPage: React.FC<CareerMatchesPageProps> = ({
  recommendations,
  selectedSkills,
  model,
  onSelectRole,
  onExploreJobs,
  onReset,
  savedRoles,
  onToggleSavedRole,
}) => {
  const isAnn = model === 'tensorflow' || model === 'ann';
  const scoreLabel = isAnn ? 'ANN Softmax score' : model === 'sklearn' ? 'Fallback classifier score' : 'Model score';
  const scoreDescription = isAnn
    ? 'Scores are the ANN Softmax outputs for the ranked classes. They describe model output, not suitability or hiring likelihood.'
    : model === 'sklearn'
      ? 'Scores come from the configured scikit-learn fallback classifier. They describe classifier output, not suitability or hiring likelihood.'
      : 'Scores describe the configured model output, not suitability or hiring likelihood.';

  return (
    <main className="page-shell max-w-5xl mx-auto space-y-8 py-2 animate-fade-in">
      {/* Header */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
           Model recommendation results
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          Your Top 3 Career Recommendations
        </h1>
        <p className="text-slate-600 max-w-xl mx-auto text-sm">
           Ranked from the backend model using your {selectedSkills.length} selected skills. {scoreDescription}
        </p>
      </div>

      {/* Academic Disclosure Alert */}
      <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 text-slate-600 text-xs flex items-start gap-3">
        <Info className="w-4 h-4 text-primary-600 mt-0.5 flex-shrink-0" />
        <p>
          <strong className="text-slate-900 font-semibold">About Match Scores: </strong>
           {scoreDescription} A 100% display can be a valid highly concentrated classifier output; it is
           not an employment guarantee.
        </p>
      </div>

      {/* Exactly Top 3 Recommendation Cards */}
       {recommendations.length === 0 ? (
         <section className="state-panel" aria-live="polite">
           <h2 className="text-base font-bold text-slate-900">No recommendations yet</h2>
           <p className="text-sm text-slate-500 mt-1">Return to the skill analyzer to generate a ranked career match.</p>
         </section>
       ) : <div className="grid md:grid-cols-3 gap-6">
        {recommendations.slice(0, 3).map((rec, index) => {
          const cfg = RANK_CONFIG[index] || RANK_CONFIG[2];
          const scoreInfo = formatScoreDisplay(rec.score);

          return (
            <div
              key={rec.role}
              className={`bg-white rounded-2xl border ${cfg.border} shadow-sm hover:shadow-md transition-all flex flex-col justify-between overflow-hidden`}
            >
              {/* Card Header */}
              <div className={`p-5 ${cfg.headerBg} border-b border-slate-100 space-y-2`}>
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                    Rank #{rec.rank}
                  </span>
                  <span className="px-2 py-0.5 rounded-full bg-white text-[10px] font-semibold text-slate-600 shadow-xs border border-slate-200">
                    {cfg.badge}
                  </span>
                 </div>

                <h3 className="text-lg font-bold text-slate-900 leading-snug">{rec.role}</h3>
               </div>

              {/* Card Body */}
              <div className="p-5 space-y-5 flex-1 flex flex-col justify-between">
                {/* Score bar */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                     <span className="text-slate-500 font-medium">{scoreLabel}</span>
                    <span className="text-base font-extrabold text-slate-900">{scoreInfo.display}</span>
                  </div>
                  <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full bg-gradient-to-r ${cfg.barColor} rounded-full transition-all duration-700`}
                      style={{ width: `${scoreInfo.barWidth}%` }}
                    />
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-400">
                     <span>{scoreInfo.note}</span>
                     <span>Raw: {scoreInfo.raw}</span>
                  </div>
                </div>

                {/* Profile overlap summary */}
                <div className="text-xs text-slate-600 space-y-2 bg-slate-50/70 p-3 rounded-xl border border-slate-100">
                   <p className="font-semibold text-slate-800 flex items-center gap-1.5">
                     <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                     Skills considered
                  </p>
                  <p className="text-[11px] text-slate-500">
                    Your skills overlap with the core competencies expected for {rec.role}.
                  </p>
                </div>

                {/* Action buttons */}
                <div className="space-y-2 pt-2">
                  <button
                    onClick={() => onSelectRole(rec.role)}
                    className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-semibold shadow-xs transition-colors"
                  >
                    <Compass className="w-3.5 h-3.5" />
                    Explore Skill Gap & Roadmap
                  </button>
                  <button aria-pressed={savedRoles.includes(rec.role)} onClick={() => onToggleSavedRole(rec.role)} className="w-full px-4 py-2 text-xs font-semibold border border-slate-200 rounded-xl hover:bg-slate-50">
                    {savedRoles.includes(rec.role) ? 'Saved locally' : 'Save career locally'}
                  </button>

                  <button
                    onClick={() => onExploreJobs(rec.role)}
                    className="w-full inline-flex items-center justify-center gap-2 px-4 py-2 bg-white hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-semibold border border-slate-200 transition-colors"
                  >
                    <Briefcase className="w-3.5 h-3.5 text-slate-400" />
                    View Open Jobs
                  </button>
                </div>
              </div>
            </div>
          );
         })}
       </div>}

      {/* Bottom CTA bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-5 rounded-2xl bg-white border border-slate-200 shadow-sm">
        <div>
          <h4 className="text-sm font-bold text-slate-900">Want to test different competencies?</h4>
          <p className="text-xs text-slate-500">
            Adjust your proficiency levels or explore other skill combinations.
          </p>
        </div>
        <button
          onClick={onReset}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-300 hover:bg-slate-50 text-xs font-semibold text-slate-700 transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Edit Skills
        </button>
      </div>
    </main>
  );
};
