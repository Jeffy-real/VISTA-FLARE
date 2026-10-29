import { FormEvent, useCallback, useEffect, useState } from 'react';
import { Briefcase, ExternalLink, Loader2, MapPin, RefreshCw, Search, Sparkles } from 'lucide-react';
import { api } from '../api/client';
import { useAuth } from '../auth/AuthContext';
import type { Job, JobSearchResponse } from '../types';

interface JobMarketPageProps {
  initialRoleFilter?: string;
  profileSkills?: string[];
  onSelectRole: (role: string) => void;
}

const freshnessClasses: Record<string, string> = {
  recently_refreshed: 'bg-emerald-50 text-emerald-700', cached: 'bg-amber-50 text-amber-800',
  stale: 'bg-rose-50 text-rose-700', seed_demo: 'bg-slate-100 text-slate-700',
};

function formatDate(value?: string | null) {
  if (!value) return 'Not recorded';
  const date = new Date(value);
  return Number.isNaN(date.valueOf()) ? value : date.toLocaleString();
}

function salary(job: Job) {
  if (job.salary_min == null && job.salary_max == null) return 'Salary not disclosed';
  const currency = job.currency || 'Currency not recorded';
  const range = [job.salary_min, job.salary_max].filter((v): v is number => typeof v === 'number').map((v) => v.toLocaleString()).join(' – ');
  return `${currency} ${range}${job.salary_period ? ` / ${job.salary_period}` : ''}`;
}

export const JobMarketPage: React.FC<JobMarketPageProps> = ({ initialRoleFilter, profileSkills = [], onSelectRole }) => {
  const { user } = useAuth();
  const [results, setResults] = useState<JobSearchResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');
  const [targetRole, setTargetRole] = useState(initialRoleFilter || '');
  const [workMode, setWorkMode] = useState('');
  const [experience, setExperience] = useState('');
  const [sourceKind, setSourceKind] = useState('all');
  const [sort, setSort] = useState('relevance');
  const [page, setPage] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [savedJobIds, setSavedJobIds] = useState<Set<number>>(new Set());
  const [trackedJobIds, setTrackedJobIds] = useState<Set<number>>(new Set());

  const load = useCallback(async (nextPage = page) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.searchJobs({
        q: query, target_role: targetRole, skills: profileSkills.join(','), work_mode: workMode,
        experience_level: experience, freshness: sourceKind, sort, page: nextPage, page_size: 12,
      });
      setResults(data);
      setPage(nextPage);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Job listings could not be loaded.');
    } finally {
      setLoading(false);
    }
  }, [experience, page, profileSkills, query, sort, sourceKind, targetRole, workMode]);

  useEffect(() => {
    void load(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  useEffect(() => { if (initialRoleFilter) setTargetRole(initialRoleFilter); }, [initialRoleFilter]);
  useEffect(() => {
    if (!user) { setSavedJobIds(new Set()); setTrackedJobIds(new Set()); return; }
    Promise.all([api.getSavedJobs(), api.getApplications()]).then(([saved, applications]) => {
      setSavedJobIds(new Set(saved.map((item: { job_id: number }) => item.job_id)));
      setTrackedJobIds(new Set(applications.map((item: { job_id: number }) => item.job_id)));
    }).catch(() => undefined);
  }, [user]);

  const apply = (event: FormEvent) => { event.preventDefault(); void load(1); };
  const announce = (message: string) => { setFeedback(message); window.setTimeout(() => setFeedback(null), 3500); };
  const toggleSaved = async (jobId: number) => {
    if (!user) return;
    try {
      if (savedJobIds.has(jobId)) {
        await api.deleteSavedJob(jobId);
        setSavedJobIds((current) => { const next = new Set(current); next.delete(jobId); return next; });
        announce('Removed from saved jobs.');
      } else {
        await api.saveJob(jobId);
        setSavedJobIds((current) => new Set(current).add(jobId));
        announce('Saved job to your account.');
      }
    } catch (err) { announce(err instanceof Error ? err.message : 'Could not update saved jobs.'); }
  };
  const track = async (jobId: number) => {
    if (!user || trackedJobIds.has(jobId)) return;
    try {
      await api.createApplication(jobId, 'saved');
      setTrackedJobIds((current) => new Set(current).add(jobId));
      announce('Added to the application tracker.');
    } catch (err) { announce(err instanceof Error ? err.message : 'Could not add this application.'); }
  };

  const totalPages = Math.max(1, Math.ceil((results?.total || 0) / (results?.page_size || 12)));
  return (
    <main className="page-shell max-w-6xl mx-auto space-y-6 py-2 animate-fade-in">
      <header className="space-y-2">
        <span className="page-eyebrow"><Briefcase className="w-3.5 h-3.5" /> Persisted job intelligence</span>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Job Market</h1>
        <p className="text-sm text-slate-600 max-w-3xl">Search cached and externally sourced listings. Freshness is based on the last successful backend refresh; this page does not make live provider calls.</p>
      </header>

      <form className="surface-card p-4 space-y-3" onSubmit={apply}>
        <div className="grid gap-3 md:grid-cols-[minmax(0,1.5fr)_repeat(3,minmax(0,1fr))]">
          <label className="relative"><span className="sr-only">Search jobs</span><Search className="absolute left-3 top-3 w-4 h-4 text-slate-400" /><input value={query} onChange={(e) => setQuery(e.target.value)} className="w-full rounded-xl border border-slate-200 bg-white py-2 pl-9 pr-3 text-sm" placeholder="Title, company, location, or skill" /></label>
          <label><span className="sr-only">Target career</span><input value={targetRole} onChange={(e) => setTargetRole(e.target.value)} className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" placeholder="Target career" /></label>
          <select aria-label="Work mode" value={workMode} onChange={(e) => setWorkMode(e.target.value)} className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm"><option value="">All work modes</option><option>Remote</option><option>Hybrid</option><option>On-site</option></select>
          <select aria-label="Listing type" value={sourceKind} onChange={(e) => setSourceKind(e.target.value)} className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm"><option value="all">All sources</option><option value="external">External sources</option><option value="seed">Seed/demo only</option></select>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <select aria-label="Experience level" value={experience} onChange={(e) => setExperience(e.target.value)} className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm"><option value="">All experience levels</option><option>Junior</option><option>Mid</option><option>Senior</option><option>Lead</option></select>
          <select aria-label="Sort jobs" value={sort} onChange={(e) => setSort(e.target.value)} className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm"><option value="relevance">Sort by relevance</option><option value="recent">Sort by most recently checked</option></select>
          <button type="submit" className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white"><Search className="w-4 h-4" /> Search</button>
          <button type="button" onClick={() => void load(1)} className="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-700"><RefreshCw className="w-4 h-4" /> Refresh view</button>
          {profileSkills.length > 0 && <span className="text-xs text-slate-500"><Sparkles className="mr-1 inline w-3.5 h-3.5" />Matching against {profileSkills.length} selected skills</span>}
        </div>
      </form>

      {results && <div className="flex flex-wrap items-center justify-between gap-2 text-sm text-slate-600"><span>{results.total.toLocaleString()} matching stored listings</span><span className="provenance-note">{results.score_explanation}</span></div>}
      {feedback && <p role="status" className="vf-banner vf-banner-info">{feedback}</p>}
      {error && <div role="alert" className="vf-banner vf-banner-danger"><span>{error}</span><button type="button" onClick={() => void load(page)} className="underline font-semibold">Retry</button></div>}
      {loading ? <div className="state-panel"><Loader2 className="mx-auto mb-2 w-6 h-6 animate-spin text-indigo-600" />Loading persisted listings…</div> : (
        <section aria-live="polite" className="space-y-3">
          {results?.items.map((job) => <article key={job.id} className="surface-card p-5 space-y-3">
            <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
              <div className="min-w-0 space-y-2"><div className="flex flex-wrap items-center gap-2"><h2 className="font-bold text-slate-900">{job.title}</h2><span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${freshnessClasses[job.freshness || 'cached'] || freshnessClasses.cached}`}>{job.freshness_label || 'Cached'}</span>{job.match_score != null && <span className="rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-semibold text-indigo-700">{job.match_score}% relevance</span>}</div><p className="text-sm text-slate-600">{job.company || 'Company not recorded'} · {job.employment_type || 'Type not recorded'} · {job.experience_level || 'Experience not recorded'}</p><div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-500"><span className="inline-flex items-center gap-1"><MapPin className="w-3.5 h-3.5" />{job.location || 'Location not recorded'}</span><span>{salary(job)}</span><span>Source: {job.source || job.provider_name || 'Not recorded'}</span><span>Last checked: {formatDate(job.last_checked)}</span></div></div>
              <div className="flex flex-wrap gap-2 md:max-w-48"><button type="button" onClick={() => onSelectRole(job.role)} className="rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-700">Analyze skill fit</button>{user && <button type="button" onClick={() => void toggleSaved(job.id)} className="rounded-lg border border-indigo-200 bg-indigo-50 px-3 py-2 text-xs font-semibold text-indigo-700">{savedJobIds.has(job.id) ? 'Saved' : 'Save job'}</button>}{user && <button type="button" disabled={trackedJobIds.has(job.id)} onClick={() => void track(job.id)} className="rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-700">{trackedJobIds.has(job.id) ? 'Tracked' : 'Track application'}</button>}</div>
            </div>
            {job.matched_skills && job.matched_skills.length > 0 && <p className="text-xs text-emerald-700">Matched skills: {job.matched_skills.join(', ')}</p>}
            {job.skills.length > 0 && <div className="flex flex-wrap gap-1.5">{job.skills.slice(0, 10).map((skill) => <span key={skill} className="rounded bg-slate-100 px-2 py-1 text-[11px] text-slate-600">{skill}</span>)}</div>}
            {job.source_url && <a className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-700 hover:underline" href={job.source_url} target="_blank" rel="noreferrer">View source listing <ExternalLink className="w-3.5 h-3.5" /></a>}
          </article>)}
          {results && results.items.length === 0 && <div className="state-panel"><Briefcase className="mx-auto mb-2 w-7 h-7 text-slate-400" /><p className="font-semibold text-slate-700">No stored jobs match these filters</p><p className="mt-1 text-sm text-slate-500">Adjust the filters or refresh configured providers from an authorized backend process.</p></div>}
        </section>
      )}
      {results && results.total > 0 && <nav aria-label="Job results pages" className="flex items-center justify-between"><button type="button" disabled={page <= 1 || loading} onClick={() => void load(page - 1)} className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-semibold">Previous</button><span className="text-sm text-slate-600">Page {page} of {totalPages}</span><button type="button" disabled={page >= totalPages || loading} onClick={() => void load(page + 1)} className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-semibold">Next</button></nav>}
    </main>
  );
};
