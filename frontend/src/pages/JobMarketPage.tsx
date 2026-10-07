import { useState, useEffect, useMemo } from 'react';
import {
  TrendingUp,
  Search,
  MapPin,
  DollarSign,
  Clock,
  Briefcase,
  Loader2,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { api } from '../api/client';
import { Job, MarketOverview } from '../types';

interface JobMarketPageProps {
  initialRoleFilter?: string;
  onSelectRole: (role: string) => void;
}

export const JobMarketPage: React.FC<JobMarketPageProps> = ({
  initialRoleFilter,
  onSelectRole,
}) => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [overview, setOverview] = useState<MarketOverview | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRole, setSelectedRole] = useState(initialRoleFilter || 'All');
  const [selectedWorkMode, setSelectedWorkMode] = useState<string>('All');
  const [selectedExp, setSelectedExp] = useState<string>('All');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [jobsData, overviewData] = await Promise.all([
        api.getJobs(),
        api.getMarketOverview(),
      ]);
      setJobs(jobsData);
      setOverview(overviewData);
    } catch (err) {
      console.error('Failed to load job market data:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredJobs = useMemo(() => {
    return jobs.filter((job) => {
      const matchesSearch =
        job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.location.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.skills.some((s) => s.toLowerCase().includes(searchTerm.toLowerCase()));

      const matchesRole =
        selectedRole === 'All' ||
        job.role.toLowerCase() === selectedRole.toLowerCase();

      const matchesWorkMode =
        selectedWorkMode === 'All' ||
        job.work_mode.toLowerCase() === selectedWorkMode.toLowerCase();

      const matchesExp =
        selectedExp === 'All' ||
        job.experience_level.toLowerCase() === selectedExp.toLowerCase();

      return matchesSearch && matchesRole && matchesWorkMode && matchesExp;
    });
  }, [jobs, searchTerm, selectedRole, selectedWorkMode, selectedExp]);

  const uniqueRoles = useMemo(() => {
    const roles = new Set(jobs.map((j) => j.role));
    return ['All', ...Array.from(roles).sort()];
  }, [jobs]);

  return (
    <div className="max-w-6xl mx-auto space-y-8 py-2 animate-fade-in">
      {/* Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold">
          <TrendingUp className="w-3.5 h-3.5 text-primary-600" />
          Job Market Intelligence & Verified Openings
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          Tech Job Market Analytics
        </h1>
        <p className="text-slate-600 text-sm max-w-2xl">
          Aggregated openings across 85 standardized roles with verified salary disclosures,
          remote/hybrid work modes, and competency requirements.
        </p>
      </div>

      {/* KPI Cards */}
      {overview && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
            <span className="text-xs font-semibold text-slate-500 block">Total Active Jobs</span>
            <p className="text-2xl font-extrabold text-slate-900 mt-1">
              {overview.total_jobs.toLocaleString()}
            </p>
            <span className="text-[11px] text-slate-400 mt-1 block">Across 85 roles</span>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
            <span className="text-xs font-semibold text-slate-500 block">Hiring Companies</span>
            <p className="text-2xl font-extrabold text-indigo-600 mt-1">
              {overview.total_companies}
            </p>
            <span className="text-[11px] text-slate-400 mt-1 block">Global tech enterprises</span>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
            <span className="text-xs font-semibold text-slate-500 block">Average Tech Salary</span>
            <p className="text-2xl font-extrabold text-emerald-600 mt-1">
              ${(overview.avg_salary / 1000).toFixed(0)}k/yr
            </p>
            <span className="text-[11px] text-slate-400 mt-1 block">Disclosed ranges</span>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
            <span className="text-xs font-semibold text-slate-500 block">Remote / Hybrid Share</span>
            <p className="text-2xl font-extrabold text-purple-600 mt-1">
              {Math.round(
                (((overview.work_mode_distribution['Remote'] || 0) +
                  (overview.work_mode_distribution['Hybrid'] || 0)) /
                  Math.max(overview.total_jobs, 1)) *
                  100
              )}
              %
            </p>
            <span className="text-[11px] text-slate-400 mt-1 block">Flexible work options</span>
          </div>
        </div>
      )}

      {/* Analytics Charts */}
      {overview && (
        <div className="grid md:grid-cols-2 gap-6">
          {/* Top In-Demand Roles */}
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-900">Most Demanded Roles</h3>
              <span className="text-xs text-slate-400">By active listings</span>
            </div>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={overview.top_demanded_roles.slice(0, 7)}
                  layout="vertical"
                  margin={{ top: 5, right: 20, left: 40, bottom: 5 }}
                >
                  <XAxis type="number" fontSize={11} stroke="#94a3b8" />
                  <YAxis
                    type="category"
                    dataKey="role"
                    fontSize={11}
                    width={110}
                    stroke="#475569"
                  />
                  <Tooltip
                    formatter={(val: any) => [`${val} jobs`, 'Openings']}
                    contentStyle={{ borderRadius: '8px', fontSize: '12px' }}
                  />
                  <Bar dataKey="count" fill="#4f46e5" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Top In-Demand Skills */}
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-900">Highest In-Demand Skills</h3>
              <span className="text-xs text-slate-400">Requirement frequency</span>
            </div>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={overview.top_in_demand_skills.slice(0, 8)}
                  margin={{ top: 5, right: 10, left: 10, bottom: 25 }}
                >
                  <XAxis
                    dataKey="skill"
                    angle={-30}
                    textAnchor="end"
                    interval={0}
                    fontSize={10}
                    stroke="#475569"
                  />
                  <YAxis fontSize={11} stroke="#94a3b8" />
                  <Tooltip
                    formatter={(val: any) => [`${val} postings`, 'Frequency']}
                    contentStyle={{ borderRadius: '8px', fontSize: '12px' }}
                  />
                  <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* Filter & Search Bar */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row gap-3">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by job title, company, location, or skill..."
              className="w-full pl-10 pr-4 py-2.5 bg-slate-50 hover:bg-white focus:bg-white border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
            />
          </div>

          {/* Role Filter */}
          <select
            value={selectedRole}
            onChange={(e) => setSelectedRole(e.target.value)}
            className="px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
          >
            <option value="All">All Roles ({jobs.length})</option>
            {uniqueRoles.filter((r) => r !== 'All').map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>

          {/* Work Mode */}
          <select
            value={selectedWorkMode}
            onChange={(e) => setSelectedWorkMode(e.target.value)}
            className="px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
          >
            <option value="All">All Work Modes</option>
            <option value="Remote">Remote</option>
            <option value="Hybrid">Hybrid</option>
            <option value="On-site">On-site</option>
          </select>

          {/* Experience */}
          <select
            value={selectedExp}
            onChange={(e) => setSelectedExp(e.target.value)}
            className="px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
          >
            <option value="All">All Levels</option>
            <option value="Junior">Junior</option>
            <option value="Mid">Mid</option>
            <option value="Senior">Senior</option>
            <option value="Lead">Lead</option>
          </select>
        </div>

        <div className="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-100">
          <span>Showing {filteredJobs.length} job postings</span>
          {(searchTerm || selectedRole !== 'All' || selectedWorkMode !== 'All' || selectedExp !== 'All') && (
            <button
              onClick={() => {
                setSearchTerm('');
                setSelectedRole('All');
                setSelectedWorkMode('All');
                setSelectedExp('All');
              }}
              className="text-primary-600 hover:text-primary-700 font-semibold"
            >
              Reset Filters
            </button>
          )}
        </div>
      </div>

      {/* Job Postings Grid */}
      <div className="space-y-3">
        {loading ? (
          <div className="py-16 flex flex-col items-center justify-center text-slate-400 space-y-2 bg-white rounded-2xl border border-slate-200">
            <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
            <span className="text-xs">Loading job postings and market intelligence...</span>
          </div>
        ) : (
          <>
            {filteredJobs.map((job) => (
              <div
                key={job.id}
                className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm hover:border-slate-300 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="space-y-2 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-bold text-sm text-slate-900">{job.title}</span>
                    <span className="text-xs text-slate-600">&bull; {job.company}</span>
                    <span
                      className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                        job.work_mode === 'Remote'
                          ? 'bg-purple-50 text-purple-700'
                          : job.work_mode === 'Hybrid'
                          ? 'bg-blue-50 text-blue-700'
                          : 'bg-slate-100 text-slate-700'
                      }`}
                    >
                      {job.work_mode}
                    </span>
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
                      {job.experience_level}
                    </span>
                  </div>

                  <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500">
                    <span className="inline-flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5 text-slate-400" />
                      {job.location}
                    </span>
                    <span className="inline-flex items-center gap-1 font-semibold text-slate-700">
                      <DollarSign className="w-3.5 h-3.5 text-emerald-600" />
                      {job.salary_min && job.salary_max
                        ? `$${job.salary_min.toLocaleString()} - $${job.salary_max.toLocaleString()} USD`
                        : 'Salary not disclosed'}
                    </span>
                    <span className="inline-flex items-center gap-1 text-[11px] text-slate-400">
                      <Clock className="w-3 h-3 text-slate-400" />
                      Posted {job.posting_date}
                    </span>
                  </div>

                  {/* Required Skills */}
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {job.skills.map((sk) => (
                      <span
                        key={sk}
                        className="px-2 py-0.5 rounded bg-slate-50 border border-slate-200 text-[10px] text-slate-600 font-medium"
                      >
                        {sk}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Quick Actions */}
                <div className="flex md:flex-col items-center gap-2">
                  <button
                    onClick={() => onSelectRole(job.role)}
                    className="w-full px-3 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-semibold whitespace-nowrap transition-colors"
                  >
                    Analyze Skill Fit
                  </button>
                </div>
              </div>
            ))}

            {filteredJobs.length === 0 && (
              <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center space-y-2 text-slate-400">
                <Briefcase className="w-8 h-8 mx-auto text-slate-300" />
                <p className="text-sm font-semibold text-slate-700">No jobs match your filter</p>
                <p className="text-xs">Try selecting a different role or resetting your search criteria.</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};
