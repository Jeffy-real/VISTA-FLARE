import { Link } from 'react-router-dom';
import { Compass, Sparkles, TrendingUp, ArrowLeft } from 'lucide-react';
import { VistaFlareLogo } from '../components/VistaFlareLogo';

export function NotFoundPage() {
  return (
    <main className="page-shell max-w-2xl mx-auto py-16 text-center space-y-6" aria-labelledby="not-found-title">
      <div className="flex justify-center mb-2">
        <VistaFlareLogo variant="icon" size={48} />
      </div>
      <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold">
        <Compass className="w-3.5 h-3.5 text-indigo-600" />
        Destination Not Found
      </div>
      <h1 id="not-found-title" className="text-6xl font-black text-slate-900 tracking-tight">404</h1>
      <h2 className="text-lg font-bold text-slate-800">This destination or resource does not exist</h2>
      <p className="text-slate-500 text-sm max-w-md mx-auto">That career path does not exist.</p>
      <p className="text-xs text-slate-400 max-w-md mx-auto">
        The link you followed may be outdated, or the catalog item has moved. Choose a verified starting point below:
      </p>

      <div className="grid sm:grid-cols-3 gap-3 pt-4 text-left">
        <Link
          to="/"
          className="p-4 bg-white border border-slate-200 rounded-2xl hover:border-indigo-300 hover:shadow-sm transition-all group"
        >
          <Sparkles className="w-5 h-5 text-indigo-600 mb-2" />
          <h3 className="text-xs font-bold text-slate-900 group-hover:text-indigo-600">Overview Dashboard</h3>
          <p className="text-[11px] text-slate-500 mt-1">Platform metrics &amp; starting points</p>
        </Link>

        <Link
          to="/skills"
          className="p-4 bg-white border border-slate-200 rounded-2xl hover:border-indigo-300 hover:shadow-sm transition-all group"
        >
          <Compass className="w-5 h-5 text-emerald-600 mb-2" />
          <h3 className="text-xs font-bold text-slate-900 group-hover:text-emerald-600">Skills &amp; Profile</h3>
          <p className="text-[11px] text-slate-500 mt-1">Select competencies &amp; predict roles</p>
        </Link>

        <Link
          to="/market"
          className="p-4 bg-white border border-slate-200 rounded-2xl hover:border-indigo-300 hover:shadow-sm transition-all group"
        >
          <TrendingUp className="w-5 h-5 text-purple-600 mb-2" />
          <h3 className="text-xs font-bold text-slate-900 group-hover:text-purple-600">Job Market</h3>
          <p className="text-[11px] text-slate-500 mt-1">Explore openings &amp; salaries</p>
        </Link>
      </div>

      <div className="pt-4">
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-semibold transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Return to Dashboard
        </Link>
      </div>
    </main>
  );
}
