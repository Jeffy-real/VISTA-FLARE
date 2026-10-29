import { useState, useEffect, useRef } from 'react';
import {
  Compass,
  CheckCircle2,
  Clock,
  AlertCircle,
  ExternalLink,
  Sparkles,
  Loader2,
} from 'lucide-react';
import { api } from '../api/client';
import { RoadmapProgress } from '../components/RoadmapProgress';
import { useAuth } from '../auth/AuthContext';
import {
  SelectedSkill,
  SkillAnalysisResponse,
  Role,
} from '../types';

interface SkillGapPageProps {
  initialRole: string;
  allRoles: Role[];
  selectedSkills: SelectedSkill[];
  onSelectRole: (role: string) => void;
  onExploreJobs: (role: string) => void;
}

export const SkillGapPage: React.FC<SkillGapPageProps> = ({
  initialRole,
  allRoles,
  selectedSkills,
  onSelectRole,
  onExploreJobs,
}) => {
  const { user } = useAuth();
  const [currentRole, setCurrentRole] = useState(initialRole || 'Data Scientist');
  const [analysis, setAnalysis] = useState<SkillAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'gap' | 'roadmap' | 'learning' | 'companies'>('gap');
  const [error, setError] = useState<string | null>(null);
  const [saveStatus, setSaveStatus] = useState<string | null>(null);
  const requestId = useRef(0);

  const loadAnalysis = async (roleName: string, skills: SelectedSkill[]) => {
    const requestRole = roleName;
    const requestSkills = JSON.stringify(skills);
    const id = ++requestId.current;
    setLoading(true);
    setError(null);
    try {
      const data = await api.analyzeSkills(roleName, skills);
      if (id !== requestId.current || requestRole !== currentRole || requestSkills !== JSON.stringify(skills)) return;
      setAnalysis(data);
    } catch (err) {
      if (id === requestId.current && requestRole === currentRole && requestSkills === JSON.stringify(skills)) {
        setError(err instanceof Error ? err.message : 'Skill analysis failed.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (currentRole) {
      void loadAnalysis(currentRole, selectedSkills);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentRole, selectedSkills]);

  const handleRoleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const roleName = e.target.value;
    setCurrentRole(roleName);
    onSelectRole(roleName);
  };

  const saveRoadmap = async () => {
    if (!analysis || !user) return;
    setSaveStatus('Saving roadmap…');
    try {
      await api.createRoadmap(currentRole, JSON.stringify(analysis.roadmap));
      setSaveStatus('Roadmap saved to your account.');
    } catch (err) {
      setSaveStatus(err instanceof Error ? err.message : 'Roadmap could not be saved.');
    }
  };

  return (
    <main className="page-shell max-w-5xl mx-auto space-y-6 py-2 animate-fade-in">
      {/* Top Bar with Role Switcher */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-600 text-xs font-semibold">
            {analysis?.role_category || 'Technology'}
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">{currentRole}</h1>
           <p className="text-xs text-slate-500">
             Comprehensive skill gap analysis, personalized roadmap, and market matching.
           </p>
           <p className="provenance-note mt-2">Analysis is generated from your selected skills and the catalogued role requirements. Results can change as source data changes.</p>
        </div>

        {/* Change Role Selector */}
        <div className="flex items-center gap-2">
          <label className="text-xs font-medium text-slate-500 whitespace-nowrap">Switch Role:</label>
          <select
            value={currentRole}
            onChange={handleRoleChange}
            className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
          >
            {allRoles.map((r) => (
              <option key={r.id} value={r.name}>
                {r.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Dual Scores Banner */}
      {analysis && (
        <div className="grid sm:grid-cols-2 gap-4">
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Deep Learning Model Match
              </span>
              <p className="text-2xl font-extrabold text-indigo-600 mt-1">
                {analysis.ai_match_score !== null && analysis.ai_match_score !== undefined
                  ? analysis.ai_match_score >= 0.995
                    ? '99.9%+'
                    : analysis.ai_match_score >= 0.01
                      ? `${(analysis.ai_match_score * 100).toFixed(1)}%`
                      : '<0.1%'
                  : 'Evaluating...'}
              </p>
              <span className="text-[11px] text-slate-400">
                Single-class Softmax probability across 85 roles
              </span>
            </div>
            <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
              <Sparkles className="w-6 h-6" />
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Deterministic Skill Fit
              </span>
              <p className="text-2xl font-extrabold text-emerald-600 mt-1">
                {Math.round(analysis.skill_match_score * 100)}%
              </p>
              <span className="text-[11px] text-slate-400">
                Weighted competency overlap calculation
              </span>
            </div>
            <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <Compass className="w-6 h-6" />
            </div>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
       <div className="tab-list border-b border-slate-200 text-sm font-semibold" role="tablist" aria-label="Skill analysis views">
        <button
           onClick={() => setActiveTab('gap')}
           role="tab" aria-selected={activeTab === 'gap'}
          className={`pb-3 px-3 transition-colors border-b-2 ${
            activeTab === 'gap'
              ? 'border-primary-600 text-primary-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          Skill Gap Analysis
        </button>

        <button
           onClick={() => setActiveTab('roadmap')}
           role="tab" aria-selected={activeTab === 'roadmap'}
          className={`pb-3 px-3 transition-colors border-b-2 ${
            activeTab === 'roadmap'
              ? 'border-primary-600 text-primary-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          Personalized Career Roadmap
        </button>

        <button
           onClick={() => setActiveTab('learning')}
           role="tab" aria-selected={activeTab === 'learning'}
          className={`pb-3 px-3 transition-colors border-b-2 ${
            activeTab === 'learning'
              ? 'border-primary-600 text-primary-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
           Learning Resources ({analysis?.learning_resources.length || 0})
        </button>

        <button
           onClick={() => setActiveTab('companies')}
           role="tab" aria-selected={activeTab === 'companies'}
          className={`pb-3 px-3 transition-colors border-b-2 ${
            activeTab === 'companies'
              ? 'border-primary-600 text-primary-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          Matching Companies ({analysis?.company_matches.length || 0})
        </button>
      </div>

      {loading && (
        <div className="py-12 flex flex-col items-center justify-center text-slate-400 space-y-2">
          <Loader2 className="w-6 h-6 animate-spin text-primary-500" />
          <span className="text-xs">Analyzing skill gaps and generating roadmap...</span>
        </div>
      )}

      {!loading && error && (
        <div role="alert" className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 flex items-center justify-between">
          <span>{error}</span>
          <button type="button" onClick={() => void loadAnalysis(currentRole, selectedSkills)} className="font-semibold underline">Retry</button>
        </div>
      )}

      {!loading && analysis && (
        <>
          {/* TAB 1: Skill Gap Analysis */}
          {activeTab === 'gap' && (
            <div className="space-y-6 animate-fade-in">
              {/* Strong Skills */}
              <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    Strong Competencies ({analysis.strong_skills.length})
                  </h3>
                  <span className="text-xs text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full font-medium">
                    Meets or exceeds requirement
                  </span>
                </div>

                <div className="grid sm:grid-cols-2 gap-2.5">
                  {analysis.strong_skills.map((s) => (
                    <div
                      key={s.skill}
                      className="p-3 rounded-xl border border-emerald-100 bg-emerald-50/30 space-y-1"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-slate-900">{s.skill}</span>
                        <span className="text-[10px] font-semibold text-emerald-700 bg-emerald-100 px-1.5 py-0.5 rounded">
                          {s.user_level}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-500">{s.explanation}</p>
                    </div>
                  ))}
                  {analysis.strong_skills.length === 0 && (
                    <p className="text-xs text-slate-400 italic col-span-2 py-2">
                      No strong skill overlap yet. Review developing and missing skills below.
                    </p>
                  )}
                </div>
              </div>

              {/* Developing Skills */}
              <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                    <Clock className="w-4 h-4 text-amber-500" />
                    Developing Competencies ({analysis.developing_skills.length})
                  </h3>
                  <span className="text-xs text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full font-medium">
                    Partial exposure &mdash; Advance proficiency
                  </span>
                </div>

                <div className="grid sm:grid-cols-2 gap-2.5">
                  {analysis.developing_skills.map((s) => (
                    <div
                      key={s.skill}
                      className="p-3 rounded-xl border border-amber-100 bg-amber-50/30 space-y-1"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-slate-900">{s.skill}</span>
                        <span className="text-[10px] font-semibold text-amber-700 bg-amber-100 px-1.5 py-0.5 rounded">
                          Current: {s.user_level} &rarr; Target: {s.required_level}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-500">{s.explanation}</p>
                    </div>
                  ))}
                  {analysis.developing_skills.length === 0 && (
                    <p className="text-xs text-slate-400 italic col-span-2 py-2">
                      None identified in developing category.
                    </p>
                  )}
                </div>
              </div>

              {/* Missing Skills */}
              <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-rose-500" />
                    Critical Missing Competencies ({analysis.missing_skills.length})
                  </h3>
                  <span className="text-xs text-rose-700 bg-rose-50 px-2 py-0.5 rounded-full font-medium">
                    Priority skill gaps to acquire
                  </span>
                </div>

                <div className="grid sm:grid-cols-2 gap-2.5">
                  {analysis.missing_skills.map((s) => (
                    <div
                      key={s.skill}
                      className="p-3 rounded-xl border border-rose-100 bg-rose-50/30 space-y-1"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-slate-900">{s.skill}</span>
                        <span className="text-[10px] font-semibold text-rose-700 bg-rose-100 px-1.5 py-0.5 rounded">
                          Priority: {s.importance.toFixed(1)}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-500">{s.explanation}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: Personalized Career Roadmap */}
          {activeTab === 'roadmap' && (
            <div className="space-y-4 animate-fade-in">
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600 flex items-center justify-between">
                <span>
                  Roadmap generated specifically for <strong>{currentRole}</strong> to bridge your{' '}
                  {analysis.missing_skills.length} missing and {analysis.developing_skills.length}{' '}
                  developing skills.
                </span>
                <span className="font-bold text-slate-900 whitespace-nowrap">
                </span>
                {user && <button type="button" onClick={() => void saveRoadmap()} className="rounded-lg bg-indigo-600 px-3 py-2 text-xs font-semibold text-white">Save to account</button>}
              </div>
              {saveStatus && <p role="status" className="text-xs text-slate-600">{saveStatus}</p>}

              <div className="space-y-4">
                {analysis.roadmap.map((stage) => (
                  <div
                    key={stage.stage_number}
                    className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4 hover:border-indigo-200 transition-all"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <span className="w-8 h-8 rounded-xl bg-indigo-50 text-indigo-700 font-bold text-sm flex items-center justify-center flex-shrink-0">
                          {stage.stage_number}
                        </span>
                        <div>
                          <h4 className="text-base font-bold text-slate-900">{stage.stage_name}</h4>
                          <p className="text-xs text-slate-500">{stage.description}</p>
                        </div>
                      </div>
                      <span className="text-xs font-semibold text-slate-500 bg-slate-100 px-2.5 py-1 rounded-full whitespace-nowrap">
                        ~{stage.estimated_weeks} Weeks
                      </span>
                    </div>

                    <div className="space-y-2 pt-2 border-t border-slate-100">
                      <span className="text-xs font-semibold text-slate-700 block">Focus Skills:</span>
                      <div className="flex flex-wrap gap-1.5">
                        {stage.skills.map((sk) => (
                          <span
                            key={sk}
                            className="px-2.5 py-1 rounded-lg bg-indigo-50/70 border border-indigo-100 text-indigo-800 text-xs font-medium"
                          >
                            {sk}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="space-y-1.5 pt-1">
                      <span className="text-xs font-semibold text-slate-700 block">Milestone Projects:</span>
                      <ul className="space-y-1 text-xs text-slate-600">
                        {stage.suggested_projects.map((proj, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-indigo-500 mt-0.5">&bull;</span>
                            <span>{proj}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
              <RoadmapProgress role={currentRole} stages={analysis.roadmap} />
            </div>
          )}

           {/* TAB 3: Learning Resources */}
          {activeTab === 'learning' && (
            <div className="space-y-4 animate-fade-in">
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600">
                 Resources returned by the backend for your competency gaps in {currentRole}; availability and quality may change.
              </div>
              <div className="grid sm:grid-cols-2 gap-4">
                {analysis.learning_resources.map((res) => (
                  <div
                    key={res.id}
                    className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between"
                  >
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">
                          {res.skill}
                        </span>
                        <span className="text-[11px] font-semibold text-slate-500">
                          {res.platform}
                        </span>
                      </div>

                      <h4 className="text-sm font-bold text-slate-900 leading-snug">
                        {res.title}
                      </h4>
                      <p className="text-xs text-slate-500 line-clamp-2">{res.description}</p>
                    </div>

                    <div className="pt-4 border-t border-slate-100 mt-4 flex items-center justify-between text-xs">
                      <span className="text-slate-500">
                        {res.provider} &bull; {res.free_or_paid}
                      </span>
                      <a
                        href={res.url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 font-semibold text-primary-600 hover:text-primary-700"
                      >
                        Start Learning
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 4: Matching Companies */}
          {activeTab === 'companies' && (
            <div className="space-y-4 animate-fade-in">
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600">
                Top companies actively hiring for {currentRole} or related tech roles with alignment
                scores based on your skill vector.
              </div>

              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {analysis.company_matches.map((comp) => (
                  <div
                    key={comp.company_id}
                    className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between"
                  >
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <h4 className="font-bold text-sm text-slate-900">{comp.company_name}</h4>
                        <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">
                          {Math.round(comp.match_score * 100)}% Fit
                        </span>
                      </div>
                      <p className="text-xs text-slate-500">{comp.industry}</p>
                      <p className="text-xs text-slate-400">{comp.location}</p>

                      <div className="pt-2">
                        <span className="text-[11px] text-slate-500 block mb-1">
                          Matched Skills:
                        </span>
                        <div className="flex flex-wrap gap-1">
                          {comp.matched_skills.map((s) => (
                            <span
                              key={s}
                              className="px-2 py-0.5 rounded bg-slate-100 text-[10px] text-slate-600"
                            >
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>

                    <div className="pt-4 border-t border-slate-100 mt-4 flex items-center justify-between">
                      <span className="text-xs text-slate-500">
                        {comp.open_jobs_count} open jobs
                      </span>
                      <button
                        onClick={() => onExploreJobs(currentRole)}
                        className="text-xs font-semibold text-primary-600 hover:text-primary-700"
                      >
                        View Openings &rarr;
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </main>
  );
};
