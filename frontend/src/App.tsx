import { useEffect, useRef, useState, type ElementType, type ReactNode } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Sparkles,
  Layers,
  Award,
  Compass,
  Map,
  TrendingUp,
  Bookmark,
  Briefcase,
  Building2,
  SlidersHorizontal,
  BookOpen,
  Activity,
  FileText,
  HelpCircle,
  Brain,
  UserRound,
  Settings,
  Bell,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Menu,
  X,
  ExternalLink,
  Loader2,
  Mail,
  Workflow,
  Layers3,
  GitBranch,
  Database,
} from 'lucide-react';
import { api } from './api/client';
import { LandingPage } from './pages/LandingPage';
import { SkillAnalyzerPage } from './pages/SkillAnalyzerPage';
import { CareerMatchesPage } from './pages/CareerMatchesPage';
import { SkillGapPage } from './pages/SkillGapPage';
import { JobMarketPage } from './pages/JobMarketPage';
import { CompanyDirectoryPage } from './pages/CompanyDirectoryPage';
import { DeepLearningLabPage } from './pages/DeepLearningLabPage';
import { AIModelWorkflowsPage } from './pages/AIModelWorkflowsPage';
import { LearningResourcesPage, MarketTrendsPage } from './pages/DiscoverPages';
import { ResumeCoachPage, InterviewPrepPage, SettingsPage, NotificationsPage } from './pages/CareerToolsPages';
import { ApplicationsPage, ComparisonPage, ProfilePage, RoadmapPage, SavedPage } from './pages/WorkspacePages';
import { LoginPage, RegisterPage } from './pages/AuthPages';
import { NotFoundPage } from './pages/NotFoundPage';
import { StatusBanner, StatusPill } from './components/ui';
import { VistaFlareLogo } from './components/VistaFlareLogo';
import { SelectedSkill, ModelMetrics, Skill, Role, CareerRecommendation, HealthResponse } from './types';
import { useLocalJourney, validHistory, validRecommendations, validSavedRoles, validSkills, type AnalysisHistory } from './localJourney';
import { useAuth } from './auth/AuthContext';

export interface NavItemConfig {
  id: string;
  path: string;
  label: string;
  icon: ElementType;
  badge?: string;
}

interface NavGroupConfig {
  label: string;
  items: NavItemConfig[];
}

const navGroups: NavGroupConfig[] = [
  {
    label: 'Workspace',
    items: [
      { id: 'home', path: '/', label: 'Overview', icon: Sparkles },
      { id: 'skills', path: '/skills', label: 'Skills & Profile', icon: Layers },
      { id: 'matches', path: '/matches', label: 'Career Matches', icon: Award },
      { id: 'skill-gap', path: '/skill-gap', label: 'Skill Gap Analysis', icon: Compass },
      { id: 'roadmap', path: '/roadmap', label: 'Career Roadmap', icon: Map },
    ],
  },
  {
    label: 'Discover',
    items: [
      { id: 'market', path: '/market', label: 'Job Market', icon: TrendingUp },
      { id: 'saved', path: '/saved', label: 'Saved Jobs', icon: Bookmark },
      { id: 'applications', path: '/applications', label: 'Applications', icon: Briefcase },
      { id: 'companies', path: '/companies', label: 'Companies', icon: Building2 },
      { id: 'compare', path: '/compare', label: 'Career Comparison', icon: SlidersHorizontal },
      { id: 'learning', path: '/learning', label: 'Learning Resources', icon: BookOpen },
      { id: 'trends', path: '/trends', label: 'Market Trends', icon: Activity },
    ],
  },
  {
    label: 'AI & Model Workflows',
    items: [
      { id: 'wf-system', path: '/ai-model-workflows?tab=system', label: 'System Workflow', icon: Workflow },
      { id: 'wf-architectures', path: '/ai-model-workflows?tab=architectures', label: 'Model Architectures', icon: Layers3 },
      { id: 'wf-training', path: '/ai-model-workflows?tab=training', label: 'Training Pipeline', icon: GitBranch },
      { id: 'wf-inference', path: '/ai-model-workflows?tab=inference', label: 'Live Inference', icon: Activity },
      { id: 'wf-evaluation', path: '/ai-model-workflows?tab=evaluation', label: 'Evaluation & Comparison', icon: Brain },
      { id: 'wf-data', path: '/ai-model-workflows?tab=data', label: 'Live Data Pipeline', icon: Database },
    ],
  },
  {
    label: 'Career Tools',
    items: [
      { id: 'resume', path: '/resume', label: 'Resume & Job Matching', icon: FileText },
      { id: 'interview', path: '/interview', label: 'Interview Preparation', icon: HelpCircle },
      { id: 'lab', path: '/lab', label: 'Deep Learning Lab', icon: Brain },
    ],
  },
  {
    label: 'Account',
    items: [
      { id: 'profile', path: '/profile', label: 'Profile', icon: UserRound },
      { id: 'settings', path: '/settings', label: 'Settings', icon: Settings },
      { id: 'notifications', path: '/notifications', label: 'Notifications', icon: Bell },
    ],
  },
];

const ROUTE_TITLES: Record<string, string> = {
  '/': 'Overview',
  '/skills': 'Skills & Profile',
  '/matches': 'Career Recommendations',
  '/skill-gap': 'Skill Gap Analysis & Roadmap',
  '/roadmap': 'Saved Career Roadmaps',
  '/market': 'Job Market Intelligence',
  '/saved': 'Saved Jobs',
  '/applications': 'Application Tracker',
  '/companies': 'Company Directory',
  '/compare': 'Career Comparison Studio',
  '/learning': 'Learning Resources',
  '/trends': 'Market Trends',
  '/resume': 'Resume & Job Matching',
  '/interview': 'Interview Preparation',
  '/lab': 'Deep Learning Lab',
  '/ai-model-workflows': 'AI & Model Workflows',
  '/profile': 'Account Profile',
  '/settings': 'Alert Preferences & Settings',
  '/notifications': 'Notifications',
  '/login': 'Sign In',
  '/register': 'Create Account',
};

export function App() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [allSkills, setAllSkills] = useState<Skill[]>([]);
  const [allRoles, setAllRoles] = useState<Role[]>([]);
  const [selectedSkills, setSelectedSkills, skillsStorageError] = useLocalJourney<SelectedSkill[]>('skills', [], validSkills);
  const [recommendations, setRecommendations, recommendationsStorageError] = useLocalJourney<CareerRecommendation[]>('recommendations', [], validRecommendations);
  const [selectedRole, setSelectedRole] = useLocalJourney<string>('selected-role', '', (v): v is string => typeof v === 'string' && v.length <= 300);
  const [savedRoles, setSavedRoles, savedRolesStorageError] = useLocalJourney<string[]>('saved-careers', [], validSavedRoles);
  const [history, setHistory, historyStorageError] = useLocalJourney<AnalysisHistory[]>('analysis-history', [], validHistory);
  const [metrics, setMetrics] = useState<ModelMetrics | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [predictionModel, setPredictionModel] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [initialLoadError, setInitialLoadError] = useState<string | null>(null);

  useEffect(() => {
    void loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setInitialLoadError(null);
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
      setInitialLoadError(err instanceof Error ? err.message : 'Could not load catalog data.');
    }
  };

  const handlePredict = async () => {
    if (!selectedSkills.length) {
      setError('Please add at least one skill to run predictions.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await api.predict(selectedSkills);
      setPredictionModel(res.model);
      setRecommendations(res.recommendations);
      setHistory([
        {
          at: new Date().toISOString(),
          skills: selectedSkills,
          recommendations: res.recommendations,
          model: res.model,
        },
        ...history,
      ].slice(0, 10));
      if (res.recommendations.length) setSelectedRole(res.recommendations[0].role);
      navigate('/matches');
    } catch (err: any) {
      setError(err?.message || 'Prediction failed. Please ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const storageNotice = [skillsStorageError, recommendationsStorageError, savedRolesStorageError, historyStorageError].find(Boolean);

  const handleSelectRoleForGap = (roleName: string) => {
    setSelectedRole(roleName);
    navigate('/skill-gap');
  };

  const handleExploreJobs = (roleName: string) => {
    setSelectedRole(roleName);
    navigate('/market');
  };

  // Dynamic document title
  const currentTitle = ROUTE_TITLES[location.pathname] ||
    (location.pathname.startsWith('/roles/') ? 'Career Role Details' :
     location.pathname.startsWith('/jobs/') ? 'Job Posting Details' : 'Page Not Found');

  useEffect(() => {
    document.title = `${currentTitle} — Vista Flare`;
  }, [currentTitle]);

  const renderContent = () => {
    const p = location.pathname;
    if (p === '/') {
      return <LandingPage onNavigate={(view) => navigate(view === 'home' ? '/' : `/${view}`)} metrics={metrics} health={health} />;
    }
    if (p === '/skills') {
      return <SkillAnalyzerPage availableSkills={allSkills} selectedSkills={selectedSkills} onChangeSkills={setSelectedSkills} onAnalyze={handlePredict} loading={loading} error={error} />;
    }
    if (p === '/matches') {
      return (
        <CareerMatchesPage
          recommendations={recommendations}
          selectedSkills={selectedSkills}
          model={predictionModel || history[0]?.model || health?.model_type || null}
          onSelectRole={handleSelectRoleForGap}
          onExploreJobs={handleExploreJobs}
          onReset={() => navigate('/skills')}
          savedRoles={savedRoles}
          onToggleSavedRole={(role) =>
            setSavedRoles(savedRoles.includes(role) ? savedRoles.filter((r) => r !== role) : [...savedRoles, role])
          }
        />
      );
    }
    if (p === '/skill-gap') {
      return <SkillGapPage initialRole={selectedRole} allRoles={allRoles} selectedSkills={selectedSkills} onSelectRole={setSelectedRole} onExploreJobs={handleExploreJobs} />;
    }
    if (p === '/roadmap') {
      return <RoadmapPage />;
    }
    if (p === '/market') {
      return <JobMarketPage initialRoleFilter={selectedRole} profileSkills={selectedSkills.map((skill) => skill.name)} onSelectRole={handleSelectRoleForGap} />;
    }
    if (p === '/saved') {
      return <SavedPage />;
    }
    if (p === '/applications') {
      return <ApplicationsPage />;
    }
    if (p === '/companies') {
      return <CompanyDirectoryPage onExploreRole={handleSelectRoleForGap} />;
    }
    if (p === '/compare') {
      return <ComparisonPage />;
    }
    if (p === '/learning') {
      return <LearningResourcesPage />;
    }
    if (p === '/trends') {
      return <MarketTrendsPage />;
    }
    if (p === '/resume') {
      return <ResumeCoachPage />;
    }
    if (p === '/interview') {
      return <InterviewPrepPage />;
    }
    if (p === '/lab') {
      return <DeepLearningLabPage />;
    }
    if (p === '/ai-model-workflows') {
      return <AIModelWorkflowsPage />;
    }
    if (p === '/profile') {
      return <ProfilePage />;
    }
    if (p === '/settings') {
      return <SettingsPage />;
    }
    if (p === '/notifications') {
      return <NotificationsPage />;
    }
    if (p === '/login') {
      return <LoginPage />;
    }
    if (p === '/register') {
      return <RegisterPage />;
    }
    if (p.startsWith('/roles/')) {
      return <DetailPage type="role" idOrName={decodeURIComponent(p.slice(7))} />;
    }
    if (p.startsWith('/jobs/')) {
      return <DetailPage type="job" idOrName={decodeURIComponent(p.slice(6))} />;
    }
    return <NotFoundPage />;
  };

  return (
    <AppShell
      health={health}
      user={user}
      pageTitle={currentTitle}
      recommendationsCount={recommendations.length}
    >
      {initialLoadError && (
        <StatusBanner tone="danger" action={<button type="button" className="font-semibold underline" onClick={() => void loadInitialData()}>Retry</button>}>
          {initialLoadError}
        </StatusBanner>
      )}
      {storageNotice && (
        <div className="mt-3">
          <StatusBanner tone="warning">Local journey storage note: {storageNotice}</StatusBanner>
        </div>
      )}
      <div className="mt-4">{renderContent()}</div>
    </AppShell>
  );
}

interface AppShellProps {
  children: ReactNode;
  health: HealthResponse | null;
  user: any;
  pageTitle: string;
  recommendationsCount: number;
}

function AppShell({ children, health, user, pageTitle, recommendationsCount }: AppShellProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(() => {
    try {
      return window.localStorage.getItem('vista-flare-sidebar-collapsed') === 'true';
    } catch {
      return false;
    }
  });

  const menuRef = useRef<HTMLElement>(null);
  const menuButtonRef = useRef<HTMLButtonElement>(null);
  const displayName = user?.display_name || user?.name || user?.email?.split('@')[0];

  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname, location.search]);

  useEffect(() => {
    try {
      window.localStorage.setItem('vista-flare-sidebar-collapsed', String(collapsed));
    } catch {
      // Optional preference storage
    }
  }, [collapsed]);

  useEffect(() => {
    if (!mobileOpen) {
      menuButtonRef.current?.focus();
      return;
    }
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setMobileOpen(false);
    };
    document.addEventListener('keydown', onKey);
    menuRef.current?.querySelector<HTMLButtonElement>('button')?.focus();
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onKey);
      document.body.style.overflow = prevOverflow;
    };
  }, [mobileOpen]);

  const modelStatus = health
    ? health.model_type === 'tensorflow'
      ? { label: 'ANN model active', tone: 'success' as const }
      : health.model_loaded
      ? { label: 'Fallback classifier', tone: 'warning' as const }
      : { label: 'Model offline', tone: 'danger' as const }
    : { label: 'Connecting...', tone: 'neutral' as const };

  const renderNavList = (isCollapsed: boolean) => (
    <div className="vf-sidebar-nav">
      {navGroups.map((group) => (
        <div key={group.label} className="vf-sidebar-group">
          <div className="vf-sidebar-label">{group.label}</div>
          {group.items.map((item) => {
            const Icon = item.icon;
            const currentFullPath = location.pathname + (location.pathname === '/ai-model-workflows' ? (location.search || '?tab=system') : location.search);
            const isActive = item.path.includes('?')
              ? currentFullPath === item.path
              : (location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path)));
            const badge = item.id === 'matches' && recommendationsCount > 0 ? 'Top 3' : undefined;

            return (
              <button
                key={item.id}
                type="button"
                className="vf-nav-link"
                aria-current={isActive ? 'page' : undefined}
                aria-label={isCollapsed ? item.label : undefined}
                title={isCollapsed ? item.label : undefined}
                onClick={() => {
                  navigate(item.path);
                  setMobileOpen(false);
                }}
              >
                <Icon className="h-4 w-4 shrink-0" />
                <span className="vf-nav-text">{item.label}</span>
                {badge && <span className="vf-nav-badge">{badge}</span>}
              </button>
            );
          })}
        </div>
      ))}
    </div>
  );

  return (
    <div className={`vf-shell ${collapsed ? 'vf-sidebar-collapsed' : ''}`}>
      {/* Desktop Sticky Left Navigation Sidebar */}
      <aside className="vf-sidebar" aria-label="Primary navigation">
        {/* Brand Header */}
        <div className="vf-sidebar-brand">
          <button
            type="button"
            className="vf-brand-button"
            onClick={() => navigate('/')}
            aria-label="Vista Flare Home"
          >
            {collapsed ? (
              <VistaFlareLogo variant="icon" size={32} />
            ) : (
              <VistaFlareLogo variant="full" size={34} />
            )}
          </button>
          <button
            type="button"
            className="vf-collapse-button"
            onClick={() => setCollapsed((v) => !v)}
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </button>
        </div>

        {/* Sidebar Nav */}
        {renderNavList(collapsed)}

        {/* Sidebar Bottom Controls */}
        <div className="vf-sidebar-bottom">
          <div className="vf-sidebar-status">
            {!collapsed && <span className="vf-sidebar-status-label">Inference Status</span>}
            <StatusPill tone={modelStatus.tone} title={health?.model_load_error || undefined}>
              {collapsed ? <span className="sr-only">{modelStatus.label}</span> : modelStatus.label}
            </StatusPill>
          </div>

          {displayName ? (
            <div className="space-y-1">
              <button
                type="button"
                className="vf-sidebar-account"
                onClick={() => navigate('/profile')}
                title={`Signed in as ${displayName}`}
              >
                <span className="vf-avatar">{displayName.slice(0, 1).toUpperCase()}</span>
                <span className="vf-account-copy">
                  <strong>{displayName}</strong>
                  <small>Profile &amp; Settings</small>
                </span>
              </button>
              {!collapsed && (
                <button
                  type="button"
                  onClick={() => void logout()}
                  className="w-full text-left px-3 py-1.5 text-[11px] font-semibold text-slate-500 hover:text-rose-600 flex items-center gap-1.5 rounded-lg transition-colors"
                >
                  <LogOut className="h-3.5 w-3.5" />
                  Sign Out
                </button>
              )}
            </div>
          ) : (
            <button
              type="button"
              className="vf-sidebar-account"
              onClick={() => navigate('/login')}
            >
              <UserRound className="h-4 w-4" />
              <span className="vf-account-copy">
                <strong>Sign In</strong>
                <small>Sync progress across devices</small>
              </span>
            </button>
          )}
        </div>
      </aside>

      {/* Mobile Drawer Backdrop */}
      {mobileOpen && (
        <button
          type="button"
          className="vf-mobile-backdrop lg:hidden"
          aria-label="Close navigation menu"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Main Content Column */}
      <div className="vf-main-column">
        {/* Minimal Top Utility Bar */}
        <header className="vf-topbar">
          <div className="vf-topbar-inner">
            <div className="flex items-center gap-3">
              <button
                ref={menuButtonRef}
                type="button"
                className="vf-mobile-menu lg:hidden"
                aria-label={mobileOpen ? 'Close navigation menu' : 'Open navigation menu'}
                aria-expanded={mobileOpen}
                aria-controls="mobile-navigation"
                onClick={() => setMobileOpen((v) => !v)}
              >
                {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </button>

              <div className="vf-breadcrumb">
                <button
                  type="button"
                  onClick={() => navigate('/')}
                  className="vf-eyebrow hover:text-slate-900 transition-colors"
                >
                  Vista Flare
                </button>
                <ChevronRight className="h-3.5 w-3.5 text-slate-400" />
                <span className="vf-page-title">{pageTitle}</span>
              </div>
            </div>

            <div className="vf-topbar-actions">
              <StatusPill tone={modelStatus.tone} title={health?.model_load_error || undefined}>
                {modelStatus.label}
              </StatusPill>
              {displayName ? (
                <button
                  type="button"
                  className="vf-header-action lg:hidden"
                  onClick={() => navigate('/profile')}
                  aria-label="Account profile"
                >
                  <span className="vf-avatar">{displayName.slice(0, 1).toUpperCase()}</span>
                </button>
              ) : (
                <button
                  type="button"
                  className="vf-header-action lg:hidden"
                  onClick={() => navigate('/login')}
                >
                  Sign In
                </button>
              )}
            </div>
          </div>
        </header>

        {/* Mobile Navigation Drawer */}
        {mobileOpen && (
          <aside
            ref={menuRef}
            id="mobile-navigation"
            className="vf-mobile-drawer lg:hidden"
            aria-label="Mobile navigation"
          >
            <div className="vf-mobile-drawer-header">
              <button
                type="button"
                className="flex items-center gap-2"
                onClick={() => {
                  navigate('/');
                  setMobileOpen(false);
                }}
                aria-label="Vista Flare Home"
              >
                <VistaFlareLogo variant="full" size={30} />
              </button>
              <button
                type="button"
                className="vf-collapse-button"
                onClick={() => setMobileOpen(false)}
                aria-label="Close navigation menu"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            {renderNavList(false)}
          </aside>
        )}

        {/* Page Content */}
        <main className="vf-main-content">{children}</main>

        {/* Professional Footer */}
        <footer className="vf-footer">
          <div className="vf-container py-8 text-xs text-slate-500 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-6">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <VistaFlareLogo variant="full" size={24} />
                  <span className="text-[10px] bg-slate-100 px-2 py-0.5 rounded text-slate-600 font-mono">v1.0.0</span>
                </div>
                <p className="text-xs text-slate-500">
                  AI-Powered Career &amp; Skill Matching Platform powered by Deep Learning and Job Market Intelligence.
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-4 text-xs font-semibold text-slate-600">
                <button type="button" onClick={() => navigate('/lab')} className="hover:text-indigo-600">
                  Model Lab
                </button>
                <button type="button" onClick={() => navigate('/skills')} className="hover:text-indigo-600">
                  Skill Taxonomy
                </button>
                <button type="button" onClick={() => navigate('/compare')} className="hover:text-indigo-600">
                  Compare Roles
                </button>
                <button type="button" onClick={() => navigate('/market')} className="hover:text-indigo-600">
                  Job Market
                </button>
                <a
                  href="mailto:support@vistaflare.local"
                  className="inline-flex items-center gap-1 hover:text-indigo-600"
                >
                  <Mail className="w-3.5 h-3.5" />
                  Contact Support
                </a>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-[11px] text-slate-400">
              <p>&copy; {new Date().getFullYear()} Vista Flare Platform. All rights reserved.</p>
              <p>Transparent ML Provenance &bull; WCAG 2.2 Accessible &bull; Deterministic Skill Alignments</p>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}

function DetailPage({ type, idOrName }: { type: 'role' | 'job'; idOrName: string }) {
  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    setLoading(true);
    setError(null);
    if (type === 'role') {
      const numericId = Number(idOrName);
      if (!isNaN(numericId) && numericId > 0) {
        api.getRole(numericId)
          .then(setData)
          .catch((err) => setError(err.message || 'Role not found.'))
          .finally(() => setLoading(false));
      } else {
        api.getRoles()
          .then((roles) => {
            const found = roles.find((r) => r.name.toLowerCase() === idOrName.toLowerCase());
            if (found) return api.getRole(found.id);
            throw new Error(`Role "${idOrName}" not found in catalog.`);
          })
          .then(setData)
          .catch((err) => setError(err.message || 'Role not found.'))
          .finally(() => setLoading(false));
      }
    } else {
      const numericId = Number(idOrName);
      fetch(`/api/jobs/${numericId}`)
        .then(async (r) => {
          if (!r.ok) throw new Error('Job not found.');
          return r.json();
        })
        .then(setData)
        .catch((err) => setError(err.message || 'Job posting not found.'))
        .finally(() => setLoading(false));
    }
  }, [type, idOrName]);

  if (loading) {
    return (
      <div className="py-16 flex flex-col items-center justify-center text-slate-400 space-y-2">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
        <span className="text-xs">Loading {type === 'role' ? 'career role' : 'job posting'} details...</span>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-2xl mx-auto py-12 text-center space-y-4">
        <div role="alert" className="p-5 bg-rose-50 border border-rose-200 rounded-2xl text-xs text-rose-800">
          {error || 'Resource not found'}
        </div>
        <button
          type="button"
          onClick={() => navigate('/market')}
          className="px-4 py-2 bg-slate-900 text-white rounded-xl text-xs font-semibold"
        >
          Return to Job Market
        </button>
      </div>
    );
  }

  if (type === 'role') {
    return (
      <article className="max-w-3xl mx-auto space-y-6">
        <div>
          <span className="text-xs font-bold text-indigo-600 uppercase tracking-wider">{data.category}</span>
          <h1 className="text-3xl font-extrabold text-slate-900 mt-1">{data.name}</h1>
        </div>
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
          <h2 className="text-sm font-bold text-slate-900">Standardized Required Competencies</h2>
          <div className="flex flex-wrap gap-1.5">
            {data.skills?.map((s: any) => (
              <span key={s.skill} className="px-2.5 py-1 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-700">
                {s.skill} {s.required ? '(Core)' : ''}
              </span>
            ))}
          </div>
          <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-100 text-xs">
            <div>
              <span className="text-slate-500 block">Catalogued Openings</span>
              <strong className="text-base text-slate-900">{data.job_count}</strong>
            </div>
            <div>
              <span className="text-slate-500 block">Average Salary Range</span>
              <strong className="text-base text-emerald-700">
                {data.avg_salary_min && data.avg_salary_max
                  ? `$${Math.round(data.avg_salary_min).toLocaleString()} – $${Math.round(data.avg_salary_max).toLocaleString()}`
                  : 'Not disclosed'}
              </strong>
            </div>
          </div>
          <div className="pt-4 border-t border-slate-100 flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => navigate(`/skill-gap?role=${encodeURIComponent(data.name)}`)}
              className="px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-semibold transition-colors"
            >
              Analyze Skill Gap for this Role
            </button>
            <button
              type="button"
              onClick={() => navigate('/market')}
              className="px-4 py-2.5 border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-semibold transition-colors"
            >
              View in Job Market
            </button>
          </div>
        </div>
      </article>
    );
  }

  return (
    <article className="max-w-3xl mx-auto space-y-6">
      <div>
        <span className="text-xs font-bold text-indigo-600 uppercase tracking-wider">{data.company}</span>
        <h1 className="text-3xl font-extrabold text-slate-900 mt-1">{data.title}</h1>
      </div>
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
        <div className="flex flex-wrap gap-4 text-xs text-slate-600">
          <span>Location: {data.location}</span>
          <span>Work mode: {data.work_mode}</span>
          <span>Role category: {data.role}</span>
        </div>
        {data.description && (
          <div>
            <h2 className="text-xs font-bold text-slate-900 mb-1">Description</h2>
            <p className="text-xs text-slate-600 whitespace-pre-wrap">{data.description}</p>
          </div>
        )}
        {data.skills?.length > 0 && (
          <div>
            <h2 className="text-xs font-bold text-slate-900 mb-2">Required Skills</h2>
            <div className="flex flex-wrap gap-1.5">
              {data.skills.map((sk: string) => (
                <span key={sk} className="px-2.5 py-1 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-700">
                  {sk}
                </span>
              ))}
            </div>
          </div>
        )}
        <div className="pt-4 border-t border-slate-100 flex flex-wrap gap-3">
          {data.source_url && (
            <a
              href={data.source_url}
              target="_blank"
              rel="noreferrer"
              className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold inline-flex items-center gap-1.5 transition-colors"
            >
              Open Original Posting <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
          <button
            type="button"
            onClick={() => navigate('/market')}
            className="px-4 py-2.5 border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-semibold transition-colors"
          >
            Back to Job Market
          </button>
        </div>
      </div>
    </article>
  );
}

export default App;
