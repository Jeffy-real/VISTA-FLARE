import { Link, useSearchParams } from 'react-router-dom';
import { useEffect, useMemo, useState } from 'react';
import {
  UserRound,
  Bookmark,
  Compass,
  Briefcase,
  Layers,
  ArrowRight,
  Trash2,
  ExternalLink,
  Loader2,
} from 'lucide-react';
import { useAuth } from '../auth/AuthContext';
import { api } from '../api/client';
import type { Role, RoleDetail } from '../types';

export function ProfilePage() {
  const { user, logout, refresh } = useAuth();
  const [name, setName] = useState(user?.display_name || user?.name || '');
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);

  const importGuest = async () => {
    setLoading(true);
    const data = Object.fromEntries(
      Object.keys(localStorage)
        .filter((key) => key.startsWith('vista-journey-v1:'))
        .map((key) => [key.replace('vista-journey-v1:', ''), localStorage.getItem(key)])
    );
    try {
      await api.importJourney(data);
      setStatus('Guest journey imported to your account. Local storage retained.');
    } catch (err) {
      setStatus(err instanceof Error ? err.message : 'Import failed.');
    } finally {
      setLoading(false);
    }
  };

  const save = async () => {
    setLoading(true);
    try {
      await api.updateProfile({ display_name: name });
      await refresh();
      setStatus('Profile updated successfully.');
    } catch (err) {
      setStatus(err instanceof Error ? err.message : 'Could not save profile.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page-shell max-w-2xl mx-auto space-y-6 py-2 animate-fade-in">
      <div className="space-y-1">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold">
          <UserRound className="w-3.5 h-3.5 text-indigo-600" />
          Account Center
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Your Profile</h1>
        <p className="text-slate-600 text-sm">
          Manage your account credentials, preferences, and data synchronization.
        </p>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-5">
        <div>
          <label htmlFor="profile-display-name" className="block text-xs font-bold text-slate-900 mb-1">
            Display Name
          </label>
          <input
            id="profile-display-name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full rounded-xl border border-slate-200 p-3 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
          />
        </div>

        <div>
          <span className="block text-xs font-bold text-slate-900 mb-1">Email Address</span>
          <p className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-600 font-mono">
            {user?.email}
          </p>
        </div>

        <div className="flex items-center gap-3 pt-2">
          <button
            type="button"
            onClick={() => void save()}
            disabled={loading}
            className="rounded-xl bg-slate-900 hover:bg-slate-800 text-white px-5 py-2.5 text-xs font-semibold transition-colors disabled:opacity-50"
          >
            Save Profile
          </button>
          <button
            type="button"
            onClick={() => void logout()}
            className="rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-700 px-5 py-2.5 text-xs font-semibold transition-colors"
          >
            Sign Out
          </button>
        </div>

        {status && (
          <p role="status" className="text-xs p-3 rounded-xl bg-slate-50 text-slate-700 font-semibold">
            {status}
          </p>
        )}
      </div>

      <div className="rounded-2xl border border-indigo-200 bg-indigo-50/60 p-6 space-y-3">
        <h2 className="text-sm font-bold text-indigo-950">Guest Journey Synchronization</h2>
        <p className="text-xs text-slate-600 leading-relaxed">
          If you explored career recommendations or skill roadmaps before signing in, you can migrate those browser-cached records to your permanent account.
        </p>
        <button
          type="button"
          onClick={() => void importGuest()}
          disabled={loading}
          className="rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 text-xs font-semibold transition-colors disabled:opacity-50"
        >
          {loading ? 'Importing...' : 'Sync Local Journey to Account'}
        </button>
      </div>
    </main>
  );
}

export function SavedPage() {
  const [saved, setSaved] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await api.getSavedJobs();
      setSaved(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load saved jobs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  return (
    <main className="page-shell max-w-4xl mx-auto space-y-6 py-2 animate-fade-in">
      <div className="space-y-1">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold">
          <Bookmark className="w-3.5 h-3.5 text-indigo-600" />
          Bookmarked Listings
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Saved Jobs</h1>
        <p className="text-slate-600 text-sm">
          Job postings bookmarked for later review. Saved on your account and distinct from applications.
        </p>
      </div>

      {error && (
        <div role="alert" className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => void load()} className="underline font-semibold">Retry</button>
        </div>
      )}

      {loading ? (
        <div className="py-16 flex flex-col items-center justify-center text-slate-400 space-y-2 bg-white rounded-2xl border border-slate-200">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
          <span className="text-xs">Loading saved bookmarks...</span>
        </div>
      ) : saved.length ? (
        <div className="grid gap-3">
          {saved.map((item) => (
            <article
              key={item.id}
              className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm hover:border-slate-300 transition-all flex flex-col sm:flex-row justify-between gap-4"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <h2 className="font-bold text-base text-slate-900">{item.job?.title || `Job #${item.job_id}`}</h2>
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                    item.job?.stale ? 'bg-amber-50 text-amber-800' : 'bg-emerald-50 text-emerald-700'
                  }`}>
                    {item.job?.stale ? 'Stale' : 'Active'}
                  </span>
                </div>
                <p className="text-xs text-slate-600">{item.job?.company || 'Company details unavailable'}</p>
                <div className="flex items-center gap-3 text-xs text-slate-400 pt-1">
                  <span>{item.job?.location || 'Location unavailable'}</span>
                  {item.job?.source && <span>&bull; Source: {item.job.source}</span>}
                </div>
              </div>

              <div className="flex items-center gap-3">
                {item.job?.source_url && (
                  <a
                    href={item.job.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-800"
                  >
                    Open Source
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                )}
                <button
                  type="button"
                  onClick={async () => {
                    await api.deleteSavedJob(item.job_id);
                    await load();
                  }}
                  className="inline-flex items-center gap-1 text-xs font-semibold text-rose-600 hover:text-rose-800"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  Remove
                </button>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center text-slate-400 space-y-2">
          <Bookmark className="w-8 h-8 mx-auto text-slate-300" />
          <p className="text-sm font-semibold text-slate-700">No saved jobs yet</p>
          <p className="text-xs">Browse the Job Market and bookmark listings that match your goals.</p>
        </div>
      )}
    </main>
  );
}

export function ApplicationsPage() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await api.getApplications();
      setItems(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load applications.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  return (
    <main className="page-shell max-w-4xl mx-auto space-y-6 py-2 animate-fade-in">
      <div className="space-y-1">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold">
          <Briefcase className="w-3.5 h-3.5 text-indigo-600" />
          Pipeline Tracker
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Application Tracker</h1>
        <p className="text-slate-600 text-sm">
          Track interview rounds, submissions, and status across your active job search.
        </p>
      </div>

      {error && (
        <div role="alert" className="p-4 rounded-xl bg-rose-50 text-rose-800 text-xs">
          {error}
        </div>
      )}

      {loading ? (
        <div className="py-16 flex flex-col items-center justify-center text-slate-400 space-y-2 bg-white rounded-2xl border border-slate-200">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
          <span className="text-xs">Loading application pipeline...</span>
        </div>
      ) : items.length ? (
        <div className="grid md:grid-cols-2 gap-4">
          {items.map((item) => (
            <article key={item.id} className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="font-bold text-base text-slate-900">{item.job?.title || `Job #${item.job_id}`}</h2>
                  <p className="text-xs text-slate-500">{item.job?.company || 'Company details unavailable'}</p>
                </div>
                <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 uppercase tracking-wider">
                  {item.status}
                </span>
              </div>

              <div>
                <label htmlFor={`app-status-${item.id}`} className="block text-xs font-bold text-slate-700 mb-1">
                  Update Stage
                </label>
                <select
                  id={`app-status-${item.id}`}
                  value={item.status}
                  onChange={async (e) => {
                    await api.updateApplication(item.id, e.target.value, item.notes);
                    await load();
                  }}
                  className="w-full border border-slate-200 rounded-xl p-2 text-xs bg-slate-50 text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                >
                  <option>Interested</option>
                  <option>Applied</option>
                  <option>Interview</option>
                  <option>Offer</option>
                  <option>Rejected</option>
                  <option>Withdrawn</option>
                </select>
              </div>

              <div>
                <span className="block text-[11px] font-semibold text-slate-500 mb-1">Notes</span>
                <p className="text-xs text-slate-600 p-2.5 bg-slate-50 border border-slate-100 rounded-xl">
                  {item.notes || 'No candidate notes recorded for this application.'}
                </p>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center text-slate-400 space-y-2">
          <Briefcase className="w-8 h-8 mx-auto text-slate-300" />
          <p className="text-sm font-semibold text-slate-700">No applications recorded yet</p>
          <p className="text-xs">Find openings in the Job Market to track applications through every hiring stage.</p>
        </div>
      )}
    </main>
  );
}

export function RoadmapPage() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    api.getRoadmaps()
      .then(setItems)
      .catch((err) => setError(err instanceof Error ? err.message : 'Could not load roadmaps.'))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="page-shell max-w-4xl mx-auto space-y-6 py-2 animate-fade-in">
      <div className="space-y-1">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold">
          <Compass className="w-3.5 h-3.5 text-indigo-600" />
          Personal Pathways
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Saved Career Roadmaps</h1>
        <p className="text-slate-600 text-sm">
          Structured 5-stage learning progressions saved to your verified account.
        </p>
      </div>

      {error && <div role="alert" className="p-4 rounded-xl bg-rose-50 text-rose-800 text-xs">{error}</div>}

      {loading ? (
        <div className="py-16 flex flex-col items-center justify-center text-slate-400 space-y-2 bg-white rounded-2xl border border-slate-200">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
          <span className="text-xs">Loading roadmap archives...</span>
        </div>
      ) : items.length ? (
        <div className="grid gap-4">
          {items.map((item) => (
            <article key={item.id} className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="font-bold text-lg text-slate-900">{item.target_role}</h2>
                  <p className="text-xs text-slate-500">Roadmap ID #{item.id}</p>
                </div>
                <Link
                  to={`/skill-gap?role=${encodeURIComponent(item.target_role)}`}
                  className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-800"
                >
                  Open in Skill Gap Engine
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center text-slate-400 space-y-2">
          <Compass className="w-8 h-8 mx-auto text-slate-300" />
          <p className="text-sm font-semibold text-slate-700">No saved roadmaps yet</p>
          <p className="text-xs">
            Analyze any target role in the Skill Gap analyzer to generate and save a personalized roadmap.
          </p>
        </div>
      )}
    </main>
  );
}

export function ComparisonPage() {
  const [params, setParams] = useSearchParams();
  const [roles, setRoles] = useState<Role[]>([]);
  const selectedRolesParam = params.get('roles') || '';
  const selected = useMemo(
    () => selectedRolesParam.split(',').filter(Boolean).slice(0, 3),
    [selectedRolesParam]
  );
  const [details, setDetails] = useState<RoleDetail[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    void api.getRoles().then(setRoles).catch(() => setRoles([]));
  }, []);

  useEffect(() => {
    if (selected.length > 0) {
      setLoading(true);
      Promise.all(selected.map((id) => api.getRole(Number(id))))
        .then(setDetails)
        .catch(() => setDetails([]))
        .finally(() => setLoading(false));
    } else {
      setDetails([]);
    }
  }, [selected]);

  const toggle = (id: string) => {
    const next = selected.includes(id)
      ? selected.filter((x) => x !== id)
      : selected.length < 3
      ? [...selected, id]
      : selected;
    setParams(next.length ? { roles: next.join(',') } : {});
  };

  const category = useMemo(
    () => roles.filter((role) => selected.includes(String(role.id))),
    [roles, selected]
  );

  return (
    <main className="page-shell max-w-6xl mx-auto space-y-6 py-2 animate-fade-in">
      <div className="space-y-1">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold">
          <Layers className="w-3.5 h-3.5 text-indigo-600" />
          Role Analytics
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Career Comparison Studio</h1>
        <p className="text-slate-600 text-sm max-w-2xl">
          Side-by-side evaluation of requirements, market posting counts, and salary bands across catalogued roles.
        </p>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <label htmlFor="compare-role-select" className="text-xs font-bold text-slate-900">
            Add roles
          </label>
          <select
            id="compare-role-select"
            onChange={(e) => {
              if (e.target.value) toggle(e.target.value);
            }}
            value=""
            className="border border-slate-200 rounded-xl p-2 text-xs bg-slate-50 text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
          >
            <option value="">Select a career role...</option>
            {roles
              .filter((r) => !selected.includes(String(r.id)))
              .map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name} ({r.category})
                </option>
              ))}
          </select>
        </div>

        <div className="flex flex-wrap gap-2 pt-2 border-t border-slate-100">
          {category.map((r) => (
            <button
              key={r.id}
              onClick={() => toggle(String(r.id))}
              className="inline-flex items-center gap-1.5 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 px-3 py-1 text-xs font-semibold hover:bg-indigo-100 transition-colors"
            >
              {r.name} &times;
            </button>
          ))}
          {category.length === 0 && (
            <span className="text-xs text-slate-400">No roles selected for comparison.</span>
          )}
        </div>
      </div>

      {selected.length < 2 ? (
        <div className="rounded-2xl bg-amber-50 border border-amber-200 p-6 text-center text-xs text-amber-800">
          Select at least two distinct career roles to view their side-by-side competency requirements and market statistics.
        </div>
      ) : loading ? (
        <div className="py-16 flex flex-col items-center justify-center text-slate-400 space-y-2 bg-white rounded-2xl border border-slate-200">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
          <span className="text-xs">Loading comparison details...</span>
        </div>
      ) : (
        <div className="grid md:grid-cols-3 gap-5">
          {details.map((role) => (
            <article key={role.id} className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex flex-col justify-between">
              <div className="space-y-4">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">
                    {role.category}
                  </span>
                  <h2 className="font-bold text-lg text-slate-900 mt-1">{role.name}</h2>
                </div>

                <dl className="space-y-3 text-xs">
                  <div>
                    <dt className="font-bold text-slate-500 mb-1">Standardized Role Competencies</dt>
                    <dd className="flex flex-wrap gap-1">
                      {role.skills.length
                        ? role.skills.slice(0, 8).map((skill) => (
                            <span key={skill.skill} className="rounded bg-slate-50 border border-slate-200 px-2 py-0.5 text-[11px] text-slate-700">
                              {skill.skill}
                            </span>
                          ))
                        : 'No specific competencies recorded'}
                    </dd>
                  </div>

                  <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                    <dt className="text-slate-500">Catalogued Job Postings</dt>
                    <dd className="font-bold text-slate-900">{role.job_count}</dd>
                  </div>

                  <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                    <dt className="text-slate-500">Average Salary Range</dt>
                    <dd className="font-bold text-emerald-700">
                      {role.avg_salary_min != null && role.avg_salary_max != null
                        ? `$${Math.round(role.avg_salary_min).toLocaleString()} – $${Math.round(role.avg_salary_max).toLocaleString()}`
                        : 'Not disclosed'}
                    </dd>
                  </div>
                </dl>
              </div>

              <div className="pt-4 mt-4 border-t border-slate-100">
                <Link
                  className="w-full inline-flex items-center justify-center gap-1.5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-semibold transition-colors"
                  to={`/skill-gap?role=${encodeURIComponent(role.name)}`}
                >
                  Analyze Skill Gap
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </article>
          ))}
        </div>
      )}
    </main>
  );
}
