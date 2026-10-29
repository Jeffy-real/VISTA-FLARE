import { useState, useEffect } from 'react';
import {
  FileText,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Save,
  Bell,
  Settings,
  Loader2,
  Sparkles,
} from 'lucide-react';
import { api } from '../api/client';
import { useAuth } from '../auth/AuthContext';
import { Role, Job } from '../types';

export function ResumeCoachPage() {
  const [resumeText, setResumeText] = useState('');
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<any | null>(null);

  useEffect(() => {
    void api.getJobs().then(setJobs).catch(() => setJobs([]));
  }, []);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resumeText.trim()) {
      setError('Please paste or type your resume content to extract skills.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const jobId = selectedJobId ? Number(selectedJobId) : undefined;
      const data = await api.analyzeResume({ resume_text: resumeText, job_id: jobId });
      setAnalysisResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not analyze resume.');
    } finally {
      setLoading(false);
    }
  };

  const detectedSkills = analysisResult?.skills || [];
  const comparison = analysisResult?.job_comparison;

  return (
    <main className="page-shell max-w-5xl mx-auto space-y-6 py-2 animate-fade-in">
      <div className="space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold">
          <FileText className="w-3.5 h-3.5 text-indigo-600" />
          Skill Extraction &amp; Alignment
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          Resume &amp; Job Matching Coach
        </h1>
        <p className="text-slate-600 text-sm max-w-2xl">
          Paste your resume text to detect technical capabilities against our 373 canonical skill dictionary and compare alignment against target job descriptions.
        </p>
        <p className="provenance-note">
          Security disclosure: Resume text analysis is ephemeral. Text is parsed in memory and discarded; nothing is permanently stored.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Left: Input Form */}
        <form onSubmit={handleAnalyze} className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div>
            <label htmlFor="resume-text-input" className="block text-xs font-bold text-slate-900 mb-1">
              Resume Text Content
            </label>
            <textarea
              id="resume-text-input"
              rows={12}
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              placeholder="Paste your resume work experience, skills summary, or project descriptions here..."
              className="w-full p-3.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-mono text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
            />
          </div>

          <div>
            <label htmlFor="compare-job-select" className="block text-xs font-bold text-slate-900 mb-1">
              Compare Against Catalog Job (Optional)
            </label>
            <select
              id="compare-job-select"
              value={selectedJobId}
              onChange={(e) => setSelectedJobId(e.target.value)}
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
            >
              <option value="">No specific job (skill extraction only)</option>
              {jobs.slice(0, 50).map((j) => (
                <option key={j.id} value={j.id}>
                  {j.title} — {j.company} ({j.role})
                </option>
              ))}
            </select>
          </div>

          {error && (
            <div role="alert" className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-slate-900 hover:bg-slate-800 text-white font-semibold rounded-xl text-xs transition-colors disabled:opacity-60 flex items-center justify-center gap-2"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4 text-indigo-400" />}
            Analyze Resume &amp; Match Skills
          </button>
        </form>

        {/* Right: Analysis Results */}
        <div className="space-y-4">
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
            <h2 className="text-base font-bold text-slate-900">Extracted Skills</h2>
            <p className="text-xs text-slate-500">
              Matched using multi-word alias normalization across standardized technical competencies.
            </p>

            {detectedSkills.length > 0 ? (
              <div className="flex flex-wrap gap-2 pt-2">
                {detectedSkills.map((sk: string) => (
                  <span
                    key={sk}
                    className="px-2.5 py-1 bg-indigo-50 text-indigo-700 border border-indigo-100 rounded-lg text-xs font-semibold"
                  >
                    {sk}
                  </span>
                ))}
              </div>
            ) : (
              <div className="py-8 text-center text-slate-400 text-xs">
                {loading ? 'Scanning document...' : 'No skills extracted yet. Submit your resume text to begin.'}
              </div>
            )}
          </div>

          {comparison && (
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4 animate-fade-in">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-slate-900">Target Job Alignment</h3>
                  <p className="text-xs text-slate-500">{comparison.job_title} at {comparison.company}</p>
                </div>
                <span className="px-3 py-1 bg-emerald-50 text-emerald-700 font-extrabold text-sm rounded-full border border-emerald-200">
                  {Math.round((comparison.matched_skills.length / Math.max(comparison.required_skills.length, 1)) * 100)}% Match
                </span>
              </div>

              <div className="space-y-3 pt-2">
                <div>
                  <p className="text-xs font-bold text-slate-700 mb-1.5 flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    Covered Requirements ({comparison.matched_skills.length})
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {comparison.matched_skills.map((s: string) => (
                      <span key={s} className="px-2 py-0.5 bg-emerald-50 text-emerald-700 rounded text-[11px] font-medium">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <p className="text-xs font-bold text-slate-700 mb-1.5 flex items-center gap-1.5">
                    <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
                    Missing Requirements ({comparison.missing_skills.length})
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {comparison.missing_skills.map((s: string) => (
                      <span key={s} className="px-2 py-0.5 bg-amber-50 text-amber-800 rounded text-[11px] font-medium">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

export function InterviewPrepPage() {
  const { user } = useAuth();
  const [roles, setRoles] = useState<Role[]>([]);
  const [selectedRoleId, setSelectedRoleId] = useState<number>(1);
  const [coachData, setCoachData] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notes, setNotes] = useState('');
  const [completedQuestions, setCompletedQuestions] = useState<string[]>([]);
  const [saveStatus, setSaveStatus] = useState<string | null>(null);

  useEffect(() => {
    void api.getRoles().then((data) => {
      setRoles(data);
      if (data.length) setSelectedRoleId(data[0].id);
    }).catch(() => setRoles([]));
  }, []);

  const loadCoach = async (roleId: number) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getInterviewCoach(roleId);
      setCoachData(data);
      setNotes(data.progress?.notes || '');
      setCompletedQuestions(data.progress?.completed_questions || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load interview preparation.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedRoleId) {
      void loadCoach(selectedRoleId);
    }
  }, [selectedRoleId]);

  const toggleQuestion = (q: string) => {
    setCompletedQuestions((prev) =>
      prev.includes(q) ? prev.filter((item) => item !== q) : [...prev, q]
    );
  };

  const handleSaveProgress = async () => {
    if (!user) {
      setSaveStatus('Please sign in to save your personal interview progress.');
      return;
    }
    setSaveStatus('Saving progress...');
    try {
      await api.saveInterviewProgress(selectedRoleId, notes, completedQuestions);
      setSaveStatus('Interview progress saved to your account.');
    } catch (err) {
      setSaveStatus(err instanceof Error ? err.message : 'Could not save progress.');
    }
  };

  const technical = coachData?.technical_questions || [];
  const behavioral = coachData?.behavioral_questions || [];

  return (
    <main className="page-shell max-w-5xl mx-auto space-y-6 py-2 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold">
            <HelpCircle className="w-3.5 h-3.5 text-indigo-600" />
            Interview Preparation
          </div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
            Role-Specific Interview Coach
          </h1>
          <p className="text-slate-600 text-sm max-w-2xl">
            Domain-specific technical and behavioral questions tailored to your target career role.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <label htmlFor="interview-role-select" className="text-xs font-bold text-slate-600 whitespace-nowrap">
            Select Role:
          </label>
          <select
            id="interview-role-select"
            value={selectedRoleId}
            onChange={(e) => setSelectedRoleId(Number(e.target.value))}
            className="px-3 py-2 bg-white border border-slate-200 rounded-xl text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
          >
            {roles.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="py-16 flex flex-col items-center justify-center text-slate-400 space-y-2 bg-white rounded-2xl border border-slate-200">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
          <span className="text-xs">Generating role-specific questions...</span>
        </div>
      ) : error ? (
        <div role="alert" className="p-4 rounded-xl bg-rose-50 text-rose-800 text-sm flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => void loadCoach(selectedRoleId)} className="font-semibold underline">Retry</button>
        </div>
      ) : (
        <div className="grid md:grid-cols-3 gap-6">
          <div className="md:col-span-2 space-y-6">
            {/* Technical Questions */}
            <section className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <h2 className="text-base font-bold text-slate-900">Technical Deep-Dive Questions</h2>
                <span className="text-xs text-slate-500">
                  {completedQuestions.length} completed
                </span>
              </div>

              <div className="space-y-3">
                {technical.length > 0 ? technical.map((q: string, idx: number) => {
                  const done = completedQuestions.includes(q);
                  return (
                    <label
                      key={idx}
                      className={`flex items-start gap-3 p-3.5 rounded-xl border transition-colors cursor-pointer ${
                        done ? 'bg-indigo-50/50 border-indigo-200' : 'bg-slate-50 border-slate-200 hover:bg-white'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={done}
                        onChange={() => toggleQuestion(q)}
                        className="mt-0.5 rounded text-indigo-600 focus:ring-indigo-500"
                      />
                      <span className={`text-xs ${done ? 'text-indigo-900 font-semibold line-through decoration-indigo-300' : 'text-slate-800'}`}>
                        {q}
                      </span>
                    </label>
                  );
                }) : (
                  <p className="text-xs text-slate-400">No questions mapped for this specific role yet.</p>
                )}
              </div>
            </section>

            {/* Behavioral Questions */}
            <section className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
              <h2 className="text-base font-bold text-slate-900 border-b border-slate-100 pb-3">
                Behavioral &amp; Situational Questions
              </h2>
              <div className="space-y-3">
                {behavioral.length > 0 ? behavioral.map((q: string, idx: number) => {
                  const done = completedQuestions.includes(q);
                  return (
                    <label
                      key={idx}
                      className={`flex items-start gap-3 p-3.5 rounded-xl border transition-colors cursor-pointer ${
                        done ? 'bg-indigo-50/50 border-indigo-200' : 'bg-slate-50 border-slate-200 hover:bg-white'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={done}
                        onChange={() => toggleQuestion(q)}
                        className="mt-0.5 rounded text-indigo-600 focus:ring-indigo-500"
                      />
                      <span className={`text-xs ${done ? 'text-indigo-900 font-semibold line-through decoration-indigo-300' : 'text-slate-800'}`}>
                        {q}
                      </span>
                    </label>
                  );
                }) : (
                  <p className="text-xs text-slate-400">Standard behavioral questions loaded.</p>
                )}
              </div>
            </section>
          </div>

          {/* Right: Notes & Progress Saver */}
          <div className="space-y-4">
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
              <h2 className="text-base font-bold text-slate-900">Preparation Notes</h2>
              <p className="text-xs text-slate-500">Record your STAR bullet points, project references, or talking points.</p>
              <textarea
                rows={10}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Write your personal answers or discussion frameworks here..."
                className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
              />
              <button
                type="button"
                onClick={() => void handleSaveProgress()}
                className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
              >
                <Save className="w-3.5 h-3.5" />
                Save Notes &amp; Progress
              </button>
              {saveStatus && (
                <p role="status" className="text-xs text-center text-slate-600 pt-1 font-medium">
                  {saveStatus}
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

export function SettingsPage() {
  const { user } = useAuth();
  const [preferences, setPreferences] = useState<any>({
    enabled: true,
    target_roles: [],
    skills: [],
    saved_jobs: true,
  });
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [rolesInput, setRolesInput] = useState('');
  const [skillsInput, setSkillsInput] = useState('');

  useEffect(() => {
    if (user) {
      setLoading(true);
      void api.getAlertPreferences().then((data) => {
        setPreferences(data);
        setRolesInput(data.target_roles?.join(', ') || '');
        setSkillsInput(data.skills?.join(', ') || '');
      }).catch(() => {
        // Default guest preferences
      }).finally(() => setLoading(false));
    }
  }, [user]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) {
      setStatus('Please sign in to persist your notification and alert settings.');
      return;
    }
    setStatus('Saving preferences...');
    try {
      const payload = {
        enabled: preferences.enabled,
        saved_jobs: preferences.saved_jobs,
        target_roles: rolesInput.split(',').map((s) => s.trim()).filter(Boolean),
        skills: skillsInput.split(',').map((s) => s.trim()).filter(Boolean),
      };
      await api.updateAlertPreferences(payload);
      setStatus('Preferences saved successfully.');
    } catch (err) {
      setStatus(err instanceof Error ? err.message : 'Could not save preferences.');
    }
  };

  return (
    <main className="page-shell max-w-3xl mx-auto space-y-6 py-2 animate-fade-in">
      <div className="space-y-1">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold">
          <Settings className="w-3.5 h-3.5 text-indigo-600" />
          System Preferences
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          Alert &amp; Account Settings
        </h1>
        <p className="text-slate-600 text-sm">
          Customize notifications for new job postings, salary updates, and saved career pathways.
        </p>
      </div>

      <form onSubmit={handleSave} className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100">
            <div>
              <p className="text-sm font-bold text-slate-900">Career Intelligence Alerts</p>
              <p className="text-xs text-slate-500">Receive alerts when new matching jobs are ingested.</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={preferences.enabled}
                onChange={(e) => setPreferences({ ...preferences, enabled: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between pb-4 border-b border-slate-100">
            <div>
              <p className="text-sm font-bold text-slate-900">Saved Job Status Tracking</p>
              <p className="text-xs text-slate-500">Alert me when saved listings become stale or close.</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={preferences.saved_jobs}
                onChange={(e) => setPreferences({ ...preferences, saved_jobs: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
            </label>
          </div>

          <div>
            <label htmlFor="settings-target-roles" className="block text-xs font-bold text-slate-900 mb-1">
              Target Career Roles (comma separated)
            </label>
            <input
              id="settings-target-roles"
              type="text"
              value={rolesInput}
              onChange={(e) => setRolesInput(e.target.value)}
              placeholder="e.g. Data Scientist, Cloud Engineer, MLOps Engineer"
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
            />
          </div>

          <div>
            <label htmlFor="settings-focus-skills" className="block text-xs font-bold text-slate-900 mb-1">
              Priority Focus Skills (comma separated)
            </label>
            <input
              id="settings-focus-skills"
              type="text"
              value={skillsInput}
              onChange={(e) => setSkillsInput(e.target.value)}
              placeholder="e.g. Python, Kubernetes, TensorFlow, SQL"
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
            />
          </div>
        </div>

        {status && (
          <p role="status" className="text-xs p-3 rounded-xl bg-slate-50 text-slate-700 font-semibold">
            {status}
          </p>
        )}

        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-semibold transition-colors disabled:opacity-50"
        >
          {loading ? 'Saving Preferences...' : 'Save Preferences'}
        </button>
      </form>
    </main>
  );
}

export function NotificationsPage() {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [unreadOnly, setUnreadOnly] = useState(false);

  useEffect(() => {
    if (!user) return;
    let active = true;
    setLoading(true);
    setError(null);
    api.getNotifications(unreadOnly)
      .then((data) => {
        if (active) setNotifications(data);
      })
      .catch((err) => {
        if (active) setError(err instanceof Error ? err.message : 'Could not load notifications.');
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [user, unreadOnly]);

  const markAsRead = async (id: number) => {
    try {
      await api.markNotificationRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, read_at: new Date().toISOString() } : n))
      );
    } catch (err) {
      console.error('Could not mark as read:', err);
    }
  };

  if (!user) {
    return (
      <main className="page-shell max-w-3xl mx-auto py-8">
        <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center space-y-3">
          <Bell className="w-8 h-8 mx-auto text-indigo-600" />
          <h1 className="text-xl font-bold text-slate-900">Sign in to view notifications</h1>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            Stay updated with real-time job market alerts and application updates.
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className="page-shell max-w-3xl mx-auto space-y-6 py-2 animate-fade-in">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold">
            <Bell className="w-3.5 h-3.5 text-indigo-600" />
            Inbox
          </div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Notifications</h1>
        </div>

        <label className="flex items-center gap-2 text-xs font-semibold text-slate-700 cursor-pointer">
          <input
            type="checkbox"
            checked={unreadOnly}
            onChange={(e) => setUnreadOnly(e.target.checked)}
            className="rounded text-indigo-600 focus:ring-indigo-500"
          />
          Unread only
        </label>
      </div>

      {loading ? (
        <div className="py-16 flex flex-col items-center justify-center text-slate-400 space-y-2 bg-white rounded-2xl border border-slate-200">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
          <span className="text-xs">Loading notifications...</span>
        </div>
      ) : error ? (
        <div role="alert" className="p-4 rounded-xl bg-rose-50 text-rose-800 text-sm">
          {error}
        </div>
      ) : notifications.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-400 space-y-2">
          <Bell className="w-8 h-8 mx-auto text-slate-300" />
          <p className="text-sm font-semibold text-slate-700">No notifications to display</p>
          <p className="text-xs">You are all caught up with your market alerts.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {notifications.map((n) => (
            <article
              key={n.id}
              className={`p-4 rounded-2xl border transition-all ${
                n.read_at ? 'bg-white border-slate-200' : 'bg-indigo-50/40 border-indigo-200'
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-600 bg-white border border-indigo-100 px-2 py-0.5 rounded">
                      {n.type || 'Alert'}
                    </span>
                    <span className="text-[11px] text-slate-400">
                      {new Date(n.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <h2 className="text-sm font-bold text-slate-900">{n.title}</h2>
                  <p className="text-xs text-slate-600">{n.message}</p>
                </div>

                {!n.read_at && (
                  <button
                    type="button"
                    onClick={() => void markAsRead(n.id)}
                    className="text-[11px] font-semibold text-indigo-600 hover:underline whitespace-nowrap"
                  >
                    Mark as read
                  </button>
                )}
              </div>
            </article>
          ))}
        </div>
      )}
    </main>
  );
}
