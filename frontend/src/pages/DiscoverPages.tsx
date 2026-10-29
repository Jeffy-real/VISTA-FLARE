import { useState, useEffect, useMemo } from 'react';
import {
  BookOpen,
  Search,
  ExternalLink,
  Loader2,
  TrendingUp,
  DollarSign,
  Activity,
  Layers,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import { api } from '../api/client';
import { LearningResource } from '../types';

export function LearningResourcesPage() {
  const [resources, setResources] = useState<LearningResource[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('All');
  const [selectedCost, setSelectedCost] = useState('All');
  const [selectedType, setSelectedType] = useState('All');

  const loadResources = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getLearning();
      setResources(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load learning resources.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadResources();
  }, []);

  const filtered = useMemo(() => {
    return resources.filter((r) => {
      const matchesSearch =
        r.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        r.skill.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (r.platform && r.platform.toLowerCase().includes(searchTerm.toLowerCase()));
      const matchesDiff = selectedDifficulty === 'All' || r.difficulty === selectedDifficulty;
      const matchesCost = selectedCost === 'All' || r.free_or_paid === selectedCost;
      const matchesType = selectedType === 'All' || r.type === selectedType;
      return matchesSearch && matchesDiff && matchesCost && matchesType;
    });
  }, [resources, searchTerm, selectedDifficulty, selectedCost, selectedType]);

  const uniqueTypes = useMemo(() => {
    return ['All', ...Array.from(new Set(resources.map((r) => r.type).filter(Boolean))).sort()];
  }, [resources]);

  return (
    <main className="page-shell max-w-6xl mx-auto space-y-6 py-2 animate-fade-in">
      <div className="space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold">
          <BookOpen className="w-3.5 h-3.5 text-indigo-600" />
          Curated Skill Curriculum
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          Learning Resources &amp; Courses
        </h1>
        <p className="text-slate-600 text-sm max-w-2xl">
          Browse vetted courses, documentation, and certifications mapped to the 373 skills across our 85 career roles.
        </p>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm flex flex-col md:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by skill, title, or platform..."
            aria-label="Search learning resources"
            className="w-full pl-10 pr-4 py-2.5 bg-slate-50 hover:bg-white focus:bg-white border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <select
            value={selectedDifficulty}
            onChange={(e) => setSelectedDifficulty(e.target.value)}
            aria-label="Filter by difficulty"
            className="px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
          >
            <option value="All">All Difficulties</option>
            <option value="Beginner">Beginner</option>
            <option value="Intermediate">Intermediate</option>
            <option value="Advanced">Advanced</option>
          </select>

          <select
            value={selectedCost}
            onChange={(e) => setSelectedCost(e.target.value)}
            aria-label="Filter by cost"
            className="px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
          >
            <option value="All">All Pricing</option>
            <option value="Free">Free</option>
            <option value="Paid">Paid</option>
          </select>

          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            aria-label="Filter by format"
            className="px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
          >
            {uniqueTypes.map((t) => (
              <option key={t} value={t}>
                {t === 'All' ? 'All Formats' : t}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="py-16 flex flex-col items-center justify-center text-slate-400 space-y-2 bg-white rounded-2xl border border-slate-200">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
          <span className="text-xs">Loading educational catalog...</span>
        </div>
      ) : error ? (
        <div role="alert" className="bg-rose-50 border border-rose-200 rounded-2xl p-5 flex items-center justify-between text-sm text-rose-800">
          <span>{error}</span>
          <button onClick={() => void loadResources()} className="font-semibold underline">Retry</button>
        </div>
      ) : filtered.length === 0 ? (
        <div className="py-16 text-center text-slate-500 text-sm bg-white rounded-2xl border border-slate-200">
          No learning resources match your current search criteria.
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((item) => (
            <article
              key={item.id}
              className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm hover:shadow-md hover:border-slate-300 transition-all flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <span className="text-[11px] font-semibold text-indigo-700 bg-indigo-50 border border-indigo-100 px-2 py-0.5 rounded-full">
                    {item.skill}
                  </span>
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                    item.free_or_paid === 'Free' ? 'bg-emerald-50 text-emerald-700 border border-emerald-100' : 'bg-slate-100 text-slate-700'
                  }`}>
                    {item.free_or_paid}
                  </span>
                </div>

                <h2 className="font-bold text-base text-slate-900 leading-snug line-clamp-2">
                  {item.title}
                </h2>

                <p className="text-xs text-slate-500 line-clamp-2">
                  {item.description || 'Comprehensive learning resource focusing on core domain capabilities.'}
                </p>

                <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500 pt-2 border-t border-slate-100">
                  <span className="font-medium text-slate-700">{item.platform}</span>
                  {item.difficulty && (
                    <>
                      <span>&bull;</span>
                      <span>{item.difficulty}</span>
                    </>
                  )}
                  {item.duration && (
                    <>
                      <span>&bull;</span>
                      <span>{item.duration}</span>
                    </>
                  )}
                </div>
              </div>

              <div className="pt-4 mt-4 border-t border-slate-100 flex items-center justify-between">
                <span className="text-[11px] text-slate-400 capitalize">{item.type}</span>
                <a
                  href={item.url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-600 hover:text-indigo-800"
                >
                  Visit Resource
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>
            </article>
          ))}
        </div>
      )}
    </main>
  );
}

export function MarketTrendsPage() {
  const [trendsData, setTrendsData] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [roleFilter, setRoleFilter] = useState('');

  const loadTrends = async (role?: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getMarketTrends(role || undefined);
      setTrendsData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load market trends.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadTrends(roleFilter);
  }, [roleFilter]);

  const points = trendsData?.points || [];

  return (
    <main className="page-shell max-w-6xl mx-auto space-y-6 py-2 animate-fade-in">
      <div className="space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold">
          <TrendingUp className="w-3.5 h-3.5 text-indigo-600" />
          Job Market Observations
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          Market Trends &amp; Demand Tracking
        </h1>
        <p className="text-slate-600 text-sm max-w-2xl">
          Historical salary distributions and active posting volumes tracked from our persistent external provider snapshots.
        </p>
        <p className="provenance-note">
          Data source: {trendsData?.source || 'persisted job observations'}. Sample size: {trendsData?.sample_size ?? 0} observations across {trendsData?.source_metadata?.providers?.join(', ') || 'configured providers'}.
        </p>
      </div>

      {/* KPI Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
            <span>Observed Snapshots</span>
            <Activity className="w-4 h-4 text-indigo-600" />
          </div>
          <p className="text-2xl font-black text-slate-900">{trendsData?.sample_size ?? 0}</p>
          <span className="text-[11px] text-slate-400">Total job records</span>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
            <span>Trend Days</span>
            <TrendingUp className="w-4 h-4 text-emerald-600" />
          </div>
          <p className="text-2xl font-black text-slate-900">{points.length}</p>
          <span className="text-[11px] text-slate-400">Distinct time intervals</span>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
            <span>Active Listings</span>
            <DollarSign className="w-4 h-4 text-blue-600" />
          </div>
          <p className="text-2xl font-black text-slate-900">
            {points.reduce((acc: number, p: any) => acc + (p.active_jobs || 0), 0)}
          </p>
          <span className="text-[11px] text-slate-400">Active postings recorded</span>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
            <span>Providers Monitored</span>
            <Layers className="w-4 h-4 text-purple-600" />
          </div>
          <p className="text-2xl font-black text-slate-900">
            {trendsData?.source_metadata?.providers?.length || 3}
          </p>
          <span className="text-[11px] text-slate-400">Verified ingestion sources</span>
        </div>
      </div>

      {/* Role Filter & Chart */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-bold text-slate-900">Observation History &amp; Postings</h2>
            <p className="text-xs text-slate-500">Number of job observations and active listings per recorded date.</p>
          </div>
          <div className="w-full sm:w-64">
            <input
              type="text"
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              placeholder="Filter by role name (e.g. Data Scientist)..."
              aria-label="Filter trends by role"
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
            />
          </div>
        </div>

        {loading ? (
          <div className="h-64 flex flex-col items-center justify-center text-slate-400 space-y-2">
            <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
            <span className="text-xs">Loading market timeline...</span>
          </div>
        ) : error ? (
          <div role="alert" className="p-4 rounded-xl bg-rose-50 text-rose-800 text-sm">
            {error} <button onClick={() => void loadTrends(roleFilter)} className="underline font-semibold ml-2">Retry</button>
          </div>
        ) : points.length === 0 ? (
          <div className="py-12 text-center text-slate-500 text-sm">
            No historical trend points recorded yet for this criteria.
          </div>
        ) : (
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={points} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '0.75rem', fontSize: '12px' }}
                />
                <Line
                  type="monotone"
                  dataKey="observations"
                  name="Recorded Postings"
                  stroke="#4f46e5"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
                <Line
                  type="monotone"
                  dataKey="active_jobs"
                  name="Active Jobs"
                  stroke="#10b981"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </main>
  );
}

