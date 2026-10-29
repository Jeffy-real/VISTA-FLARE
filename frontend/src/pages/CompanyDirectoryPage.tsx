import { useState, useEffect, useMemo } from 'react';
import {
  Building2,
  Search,
  MapPin,
  ExternalLink,
  Users,
  Loader2,
} from 'lucide-react';
import { api } from '../api/client';
import { Company } from '../types';

interface CompanyDirectoryPageProps {
  onExploreRole: (role: string) => void;
}

export const CompanyDirectoryPage: React.FC<CompanyDirectoryPageProps> = ({
  onExploreRole,
}) => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedIndustry, setSelectedIndustry] = useState('All');
  const [error, setError] = useState<string | null>(null);
  const [expandedCompany, setExpandedCompany] = useState<number | null>(null);
  const [companyJobs, setCompanyJobs] = useState<Record<number, Array<{ role?: string; title?: string }>>>({});

  useEffect(() => {
    loadCompanies();
  }, []);

  const loadCompanies = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getCompanies();
      setCompanies(data);
    } catch (err) {
      console.error('Failed to load companies:', err);
      setError('Company directory could not be loaded. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const industries = useMemo(() => {
    const set = new Set(companies.map((c) => c.industry));
    return ['All', ...Array.from(set).sort()];
  }, [companies]);

  const filteredCompanies = useMemo(() => {
    return companies.filter((c) => {
      const matchesSearch =
        c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.city.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.country.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesInd = selectedIndustry === 'All' || c.industry === selectedIndustry;
      return matchesSearch && matchesInd;
    });
  }, [companies, searchTerm, selectedIndustry]);

  return (
    <main className="page-shell max-w-5xl mx-auto space-y-6 py-2 animate-fade-in">
      {/* Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold">
          <Building2 className="w-3.5 h-3.5 text-indigo-600" />
          Hiring Organizations Directory
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          Explore Partner Companies
        </h1>
         <p className="text-slate-600 text-sm max-w-xl">
          Browse monitored tech organizations hiring across the 85 standardized roles with industry
          classifications and headquarters locations.
         </p>
         <p className="provenance-note">Directory data comes from the available catalog. Hiring status and role counts may change.</p>
      </div>

      {/* Filter Bar */}
      <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
           <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
             placeholder="Search company name, city, or country..."
             aria-label="Search companies"
            className="w-full pl-10 pr-4 py-2.5 bg-slate-50 hover:bg-white focus:bg-white border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
          />
        </div>

         <select
           aria-label="Filter companies by industry"
          value={selectedIndustry}
          onChange={(e) => setSelectedIndustry(e.target.value)}
          className="px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
        >
          {industries.map((ind) => (
            <option key={ind} value={ind}>
              {ind}
            </option>
          ))}
        </select>
      </div>

      {/* Companies Grid */}
      {loading ? (
        <div className="py-16 flex flex-col items-center justify-center text-slate-400 space-y-2">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
          <span className="text-xs">Loading companies...</span>
        </div>
      ) : error ? (
        <div role="alert" className="bg-rose-50 border border-rose-200 rounded-2xl p-5 flex items-center justify-between text-sm text-rose-800">
          <span>{error}</span><button onClick={loadCompanies} className="font-semibold underline">Retry</button>
        </div>
      ) : filteredCompanies.length === 0 ? (
        <div className="py-16 text-center text-slate-500 text-sm bg-white rounded-2xl border border-slate-200">
          No companies found matching your search.
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredCompanies.map((c) => (
            <div
              key={c.id}
              className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm hover:shadow-md hover:border-slate-300 transition-all flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-bold text-base text-slate-900">{c.name}</h3>
                    <span className="text-[11px] font-semibold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">
                      {c.industry}
                    </span>
                  </div>
                  <span className="text-xs text-slate-500 bg-slate-100 px-2 py-1 rounded-lg">
                    {c.job_count} open jobs
                  </span>
                </div>

                <div className="space-y-1.5 text-xs text-slate-500">
                  <p className="flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    {c.city}, {c.country}
                  </p>
                  <p className="flex items-center gap-1.5">
                    <Users className="w-3.5 h-3.5 text-slate-400" />
                    {c.size} employees
                  </p>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-100 mt-4 flex items-center justify-between text-xs">
                <a
                  href={c.website}
                  target="_blank"
                  rel="noreferrer"
                  className="text-slate-500 hover:text-slate-800 inline-flex items-center gap-1 font-medium"
                >
                  Careers Page
                  <ExternalLink className="w-3 h-3" />
                </a>

                  <button
                    type="button"
                    aria-expanded={expandedCompany === c.id}
                    aria-controls={`company-roles-${c.id}`}
                   onClick={async () => {
                     if (expandedCompany === c.id) { setExpandedCompany(null); return; }
                     setExpandedCompany(c.id);
                     if (!companyJobs[c.id]) {
                       try {
                         const response = await fetch(`/api/companies/${c.id}`);
                         if (!response.ok) throw new Error('Unable to load roles');
                         const detail = await response.json();
                         setCompanyJobs((current) => ({ ...current, [c.id]: detail.jobs || [] }));
                       } catch (err) { console.error(err); }
                     }
                   }}
                  className="font-semibold text-primary-600 hover:text-primary-700"
                >
                   {expandedCompany === c.id ? 'Hide roles' : 'View roles'} &rarr;
                 </button>
               </div>
               {expandedCompany === c.id && (
                  <div id={`company-roles-${c.id}`} className="pt-3 mt-3 border-t border-slate-100" aria-live="polite">
                   <p className="text-[11px] font-semibold text-slate-500 mb-2">Associated roles</p>
                   {(companyJobs[c.id] || []).length ? companyJobs[c.id].map((job, index) => (
                     <button key={`${job.role}-${index}`} onClick={() => job.role && onExploreRole(job.role)} className="block text-left text-xs text-primary-600 hover:underline py-1">
                       {job.title || job.role}
                     </button>
                   )) : <p className="text-xs text-slate-500">Loading roles or no roles listed.</p>}
                 </div>
               )}
            </div>
          ))}
        </div>
      )}
    </main>
  );
};
