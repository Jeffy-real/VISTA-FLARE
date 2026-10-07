import { useState, useEffect } from 'react';
import {
  Sparkles,
  Brain,
  Compass,
  TrendingUp,
  Building2,
  Award,
  Layers,
  Menu,
  X,
} from 'lucide-react';
import { api } from './api/client';
import { LandingPage } from './pages/LandingPage';
import { SkillAnalyzerPage } from './pages/SkillAnalyzerPage';
import { CareerMatchesPage } from './pages/CareerMatchesPage';
import { SkillGapPage } from './pages/SkillGapPage';
import { JobMarketPage } from './pages/JobMarketPage';
import { CompanyDirectoryPage } from './pages/CompanyDirectoryPage';
import { DeepLearningLabPage } from './pages/DeepLearningLabPage';
import {
  SelectedSkill,
  ModelMetrics,
  Skill,
  Role,
  CareerRecommendation,
  HealthResponse,
} from './types';

type ViewMode = 'home' | 'skills' | 'matches' | 'skill-gap' | 'market' | 'companies' | 'lab';

export function App() {
  const [currentView, setCurrentView] = useState<ViewMode>('home');
  const [allSkills, setAllSkills] = useState<Skill[]>([]);
  const [allRoles, setAllRoles] = useState<Role[]>([]);
  const [selectedSkills, setSelectedSkills] = useState<SelectedSkill[]>([
    { name: 'Python', level: 'advanced' },
    { name: 'SQL', level: 'advanced' },
    { name: 'Pandas', level: 'intermediate' },
    { name: 'Machine Learning', level: 'intermediate' },
  ]);
  const [recommendations, setRecommendations] = useState<CareerRecommendation[]>([]);
  const [selectedRole, setSelectedRole] = useState<string>('Data Scientist');
  const [metrics, setMetrics] = useState<ModelMetrics | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [skillsData, rolesData, metricsData, healthData] = await Promise.all([
        api.getSkills(),
        api.getRoles(),
        api.getModelMetrics(),
        api.health(),
      ]);
      setAllSkills(skillsData);
      setAllRoles(rolesData);
      setMetrics(metricsData);
      setHealth(healthData);
    } catch (err) {
      console.error('Initial data load error:', err);
    }
  };

  const handlePredict = async () => {
    if (selectedSkills.length === 0) {
      setError('Please add at least one skill to run predictions.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await api.predict(selectedSkills);
      setRecommendations(res.recommendations);
      if (res.recommendations.length > 0) {
        setSelectedRole(res.recommendations[0].role);
      }
      setCurrentView('matches');
    } catch (err: any) {
      setError(err?.message || 'Prediction failed. Please ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectRoleForGap = (roleName: string) => {
    setSelectedRole(roleName);
    setCurrentView('skill-gap');
  };

  const handleExploreJobs = (roleName: string) => {
    setSelectedRole(roleName);
    setCurrentView('market');
  };

  const navItems: { id: ViewMode; label: string; icon: React.ElementType; badge?: string }[] = [
    { id: 'home', label: 'Home', icon: Sparkles },
    { id: 'skills', label: 'Skills & Profile', icon: Layers },
    {
      id: 'matches',
      label: 'Career Matches',
      icon: Award,
      badge: recommendations.length > 0 ? 'Top 3' : undefined,
    },
    { id: 'skill-gap', label: 'Skill Gap & Roadmap', icon: Compass },
    { id: 'market', label: 'Job Market', icon: TrendingUp },
    { id: 'companies', label: 'Companies', icon: Building2 },
    { id: 'lab', label: 'Deep Learning Lab', icon: Brain },
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      {/* Top Navbar */}
      <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          {/* Brand */}
          <div
            onClick={() => setCurrentView('home')}
            className="flex items-center gap-3 cursor-pointer select-none"
          >
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-primary-600 via-indigo-600 to-accent-600 flex items-center justify-center text-white shadow-md shadow-primary-500/20">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-slate-900 to-indigo-900 bg-clip-text text-transparent">
                Vista Flare
              </span>
              <span className="text-[10px] text-indigo-600 font-bold uppercase tracking-wider block -mt-1">
                AI Career Intelligence
              </span>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden lg:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentView === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setCurrentView(item.id)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all ${
                    isActive
                      ? 'bg-slate-900 text-white shadow-xs'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-indigo-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                  {item.badge && (
                    <span className="ml-0.5 px-1.5 py-0.2 rounded-full text-[9px] font-bold bg-indigo-500 text-white">
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* Right Status Badges & Mobile Menu Toggle */}
          <div className="flex items-center gap-3">
            {health && (
              <div className="hidden sm:flex items-center gap-2">
                <span
                  title={health.model_loaded ? 'ANN Model loaded in memory' : 'Model not ready'}
                  className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold border ${
                    health.model_loaded
                      ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                      : 'bg-amber-50 text-amber-700 border-amber-200'
                  }`}
                >
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${
                      health.model_loaded ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'
                    }`}
                  />
                  ANN Online
                </span>
              </div>
            )}

            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 rounded-xl text-slate-600 hover:bg-slate-100"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation Dropdown */}
        {mobileMenuOpen && (
          <div className="lg:hidden border-t border-slate-200 bg-white px-4 py-3 space-y-1 animate-fade-in shadow-lg">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentView === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setCurrentView(item.id);
                    setMobileMenuOpen(false);
                  }}
                  className={`w-full px-3 py-2.5 rounded-xl text-xs font-semibold flex items-center justify-between ${
                    isActive ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500 text-white">
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        )}
      </header>

      {/* Main View Area */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-6">
        {currentView === 'home' && (
          <LandingPage
            onNavigate={(view) => setCurrentView(view as ViewMode)}
            metrics={metrics}
            health={health}
          />
        )}

        {currentView === 'skills' && (
          <SkillAnalyzerPage
            availableSkills={allSkills}
            selectedSkills={selectedSkills}
            onChangeSkills={setSelectedSkills}
            onAnalyze={handlePredict}
            loading={loading}
            error={error}
          />
        )}

        {currentView === 'matches' && (
          <CareerMatchesPage
            recommendations={recommendations}
            selectedSkills={selectedSkills}
            onSelectRole={handleSelectRoleForGap}
            onExploreJobs={handleExploreJobs}
            onReset={() => setCurrentView('skills')}
          />
        )}

        {currentView === 'skill-gap' && (
          <SkillGapPage
            initialRole={selectedRole}
            allRoles={allRoles}
            selectedSkills={selectedSkills}
            onSelectRole={setSelectedRole}
            onExploreJobs={handleExploreJobs}
          />
        )}

        {currentView === 'market' && (
          <JobMarketPage
            initialRoleFilter={selectedRole}
            onSelectRole={handleSelectRoleForGap}
          />
        )}

        {currentView === 'companies' && (
          <CompanyDirectoryPage onExploreRole={handleSelectRoleForGap} />
        )}

        {currentView === 'lab' && <DeepLearningLabPage />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white mt-16 py-8">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-800">Vista Flare</span>
            <span>&bull;</span>
            <span>AI-Powered Career & Skill Matching Platform</span>
          </div>

          <div className="flex items-center gap-4 text-[11px]">
            <button onClick={() => setCurrentView('lab')} className="hover:text-slate-800 font-medium">
              Deep Learning Lab
            </button>
            <button onClick={() => setCurrentView('market')} className="hover:text-slate-800 font-medium">
              Job Market
            </button>
            <button onClick={() => setCurrentView('skills')} className="hover:text-slate-800 font-medium">
              Skill Classifier
            </button>
            <span>&bull;</span>
            <span>TensorFlow 2.18 / Keras 3</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
