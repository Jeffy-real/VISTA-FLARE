import { useState, useMemo } from 'react';
import {
  Search,
  Plus,
  X,
  Sparkles,
  Loader2,
  AlertCircle,
  Wand2,
  Target,
  Compass,
  Building,
} from 'lucide-react';
import { SelectedSkill, SkillLevel, Skill } from '../types';

interface SkillAnalyzerPageProps {
  availableSkills: Skill[];
  selectedSkills: SelectedSkill[];
  onChangeSkills: (skills: SelectedSkill[]) => void;
  onAnalyze: () => void;
  loading: boolean;
  error: string | null;
}

const PRESET_PROFILES = [
  {
    name: 'Data Science & Analytics',
    skills: [
      { name: 'Python', level: 'advanced' as SkillLevel },
      { name: 'SQL', level: 'advanced' as SkillLevel },
      { name: 'Pandas', level: 'advanced' as SkillLevel },
      { name: 'NumPy', level: 'intermediate' as SkillLevel },
      { name: 'Machine Learning', level: 'intermediate' as SkillLevel },
      { name: 'Statistics', level: 'intermediate' as SkillLevel },
      { name: 'Data Visualization', level: 'intermediate' as SkillLevel },
    ],
  },
  {
    name: 'Full Stack Web Developer',
    skills: [
      { name: 'JavaScript', level: 'advanced' as SkillLevel },
      { name: 'TypeScript', level: 'intermediate' as SkillLevel },
      { name: 'React', level: 'advanced' as SkillLevel },
      { name: 'Node.js', level: 'intermediate' as SkillLevel },
      { name: 'HTML', level: 'expert' as SkillLevel },
      { name: 'CSS', level: 'advanced' as SkillLevel },
      { name: 'PostgreSQL', level: 'intermediate' as SkillLevel },
      { name: 'REST API', level: 'advanced' as SkillLevel },
    ],
  },
  {
    name: 'Cloud & DevOps Engineer',
    skills: [
      { name: 'AWS', level: 'advanced' as SkillLevel },
      { name: 'Docker', level: 'advanced' as SkillLevel },
      { name: 'Kubernetes', level: 'intermediate' as SkillLevel },
      { name: 'Linux', level: 'advanced' as SkillLevel },
      { name: 'CI/CD', level: 'intermediate' as SkillLevel },
      { name: 'Terraform', level: 'intermediate' as SkillLevel },
      { name: 'Python', level: 'intermediate' as SkillLevel },
    ],
  },
  {
    name: 'Cybersecurity Analyst',
    skills: [
      { name: 'Network Security', level: 'advanced' as SkillLevel },
      { name: 'Cybersecurity', level: 'advanced' as SkillLevel },
      { name: 'SIEM', level: 'intermediate' as SkillLevel },
      { name: 'SOC', level: 'intermediate' as SkillLevel },
      { name: 'Linux', level: 'intermediate' as SkillLevel },
      { name: 'Incident Response', level: 'intermediate' as SkillLevel },
      { name: 'Firewalls', level: 'advanced' as SkillLevel },
    ],
  },
];

export const SkillAnalyzerPage: React.FC<SkillAnalyzerPageProps> = ({
  availableSkills,
  selectedSkills,
  onChangeSkills,
  onAnalyze,
  loading,
  error,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [goalMode, setGoalMode] = useState<'exploring' | 'target_role' | 'target_company'>('exploring');

  const categories = useMemo(() => {
    const cats = new Set(availableSkills.map((s) => s.category || 'General'));
    return ['All', ...Array.from(cats).sort()];
  }, [availableSkills]);

  const filteredSkills = useMemo(() => {
    const selectedNames = new Set(selectedSkills.map((s) => s.name.toLowerCase()));
    return availableSkills.filter((s) => {
      const matchesSearch = s.name.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = selectedCategory === 'All' || s.category === selectedCategory;
      const notSelected = !selectedNames.has(s.name.toLowerCase());
      return matchesSearch && matchesCategory && notSelected;
    });
  }, [availableSkills, selectedSkills, searchTerm, selectedCategory]);

  const addSkill = (name: string) => {
    onChangeSkills([...selectedSkills, { name, level: 'intermediate' }]);
    setSearchTerm('');
  };

  const removeSkill = (name: string) => {
    onChangeSkills(selectedSkills.filter((s) => s.name !== name));
  };

  const updateLevel = (name: string, level: SkillLevel) => {
    onChangeSkills(selectedSkills.map((s) => (s.name === name ? { ...s, level } : s)));
  };

  const loadPreset = (preset: (typeof PRESET_PROFILES)[0]) => {
    onChangeSkills(preset.skills);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 py-2 animate-fade-in">
      {/* Title */}
      <header className="text-center space-y-2">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          Career Profile & Skills
        </h1>
        <p className="text-slate-600 max-w-xl mx-auto text-sm">
          Select the technologies you know and your experience level. Our Deep Learning ANN model
          will project your skill vector onto 85 career roles.
        </p>
      </header>

      {/* Goal Mode Selection */}
      <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm">
           <span id="goal-label" className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3 block">
          Step 1: Your Career Goal
        </span>
         <div className="grid sm:grid-cols-3 gap-3" role="group" aria-labelledby="goal-label">
          <button
            onClick={() => setGoalMode('exploring')}
            aria-pressed={goalMode === 'exploring'}
            className={`p-3.5 rounded-xl border text-left transition-all flex items-start gap-3 ${
              goalMode === 'exploring'
                ? 'border-primary-500 bg-primary-50/50 ring-2 ring-primary-500/20'
                : 'border-slate-200 hover:border-slate-300 bg-white'
            }`}
          >
            <Compass className="w-5 h-5 text-primary-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm font-semibold text-slate-900">Explore Best Fit</p>
              <p className="text-xs text-slate-500">Unbiased Top 3 recommendations based on your profile.</p>
            </div>
          </button>

          <button
            onClick={() => setGoalMode('target_role')}
            aria-pressed={goalMode === 'target_role'}
            className={`p-3.5 rounded-xl border text-left transition-all flex items-start gap-3 ${
              goalMode === 'target_role'
                ? 'border-primary-500 bg-primary-50/50 ring-2 ring-primary-500/20'
                : 'border-slate-200 hover:border-slate-300 bg-white'
            }`}
          >
            <Target className="w-5 h-5 text-indigo-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm font-semibold text-slate-900">Target Role Focus</p>
              <p className="text-xs text-slate-500">Deep dive into specific role requirements & gaps.</p>
            </div>
          </button>

          <button
            onClick={() => setGoalMode('target_company')}
            aria-pressed={goalMode === 'target_company'}
            className={`p-3.5 rounded-xl border text-left transition-all flex items-start gap-3 ${
              goalMode === 'target_company'
                ? 'border-primary-500 bg-primary-50/50 ring-2 ring-primary-500/20'
                : 'border-slate-200 hover:border-slate-300 bg-white'
            }`}
          >
            <Building className="w-5 h-5 text-purple-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm font-semibold text-slate-900">Company Matching</p>
              <p className="text-xs text-slate-500">Find companies with hiring needs aligned with your skills.</p>
            </div>
          </button>
        </div>
      </div>

      {/* Optional starter profiles */}
      <div className="bg-slate-50 rounded-2xl border border-slate-200 p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500 inline-flex items-center gap-1.5">
            <Wand2 className="w-3.5 h-3.5 text-indigo-500" />
             Optional starter profiles
          </span>
           <span className="text-xs text-slate-400">Choose one only if useful</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {PRESET_PROFILES.map((preset) => (
            <button
              key={preset.name}
              onClick={() => loadPreset(preset)}
              className="px-3 py-1.5 rounded-lg bg-white hover:bg-indigo-50 hover:text-indigo-700 border border-slate-200 text-xs font-medium text-slate-700 transition-colors shadow-sm"
            >
              + {preset.name}
            </button>
          ))}
        </div>
      </div>

      {/* Main Skill Selector */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-6">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500 block mb-2">
            Step 2: Add Your Skills ({selectedSkills.length} selected)
          </span>

          {/* Search bar */}
          <div className="relative">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
             <input
              type="text"
              id="skill-search-input"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
               placeholder="Search skills (e.g. Python, SQL, React, AWS, Docker, Machine Learning)..."
               aria-label="Search available skills"
              className="w-full pl-10 pr-4 py-3 bg-slate-50 hover:bg-white focus:bg-white border border-slate-200 rounded-xl text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all"
            />
          </div>
        </div>

        {/* Category Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs" role="group" aria-label="Filter skills by category">
          {categories.slice(0, 10).map((cat) => (
            <button
              key={cat}
               onClick={() => setSelectedCategory(cat)}
               aria-pressed={selectedCategory === cat}
              className={`px-3 py-1 rounded-lg font-medium whitespace-nowrap transition-colors ${
                selectedCategory === cat
                  ? 'bg-slate-900 text-white'
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-600'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Filtered Available Skills Grid */}
         <div className="max-h-48 overflow-y-auto pr-1" aria-live="polite">
          <div className="flex flex-wrap gap-2">
            {filteredSkills.slice(0, 36).map((skill) => (
              <button
                key={skill.id}
                onClick={() => addSkill(skill.name)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-primary-50 hover:border-primary-300 text-xs text-slate-700 transition-all"
              >
                <Plus className="w-3 h-3 text-slate-400" />
                <span>{skill.name}</span>
                <span className="text-[10px] text-slate-400">({skill.category})</span>
              </button>
            ))}
             {availableSkills.length === 0 ? <p className="text-xs text-slate-400 py-3 italic">Skill catalog is unavailable right now.</p> : filteredSkills.length === 0 && (
              <p className="text-xs text-slate-400 py-3 italic">
                No matching skills found. Try searching for another term.
              </p>
            )}
          </div>
        </div>

        {/* Selected Skills with Level Adjuster */}
        {selectedSkills.length > 0 && (
          <div className="pt-4 border-t border-slate-100 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-700">
                Your Selected Skills & Proficiency Levels
              </span>
              <button
                onClick={() => onChangeSkills([])}
                className="text-xs text-rose-600 hover:text-rose-700"
              >
                Clear all
              </button>
            </div>

            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
              {selectedSkills.map((skill) => (
                <div
                  key={skill.name}
                  className="flex items-center justify-between p-2.5 rounded-xl border border-slate-200 bg-slate-50/60"
                >
                  <div className="min-w-0 pr-2">
                    <p className="text-xs font-bold text-slate-900 truncate">{skill.name}</p>
                  </div>

                  <div className="flex items-center gap-1.5">
                    {/* Level selector buttons */}
                    <div className="flex bg-white rounded-lg border border-slate-200 p-0.5 text-[10px]">
                      {(['beginner', 'intermediate', 'advanced', 'expert'] as SkillLevel[]).map(
                        (lvl) => (
                          <button
                            key={lvl}
                             onClick={() => updateLevel(skill.name, lvl)}
                             aria-label={`${skill.name}: set ${lvl} proficiency`}
                             aria-pressed={skill.level === lvl}
                            className={`px-1.5 py-0.5 rounded capitalize font-medium transition-colors ${
                              skill.level === lvl
                                ? 'bg-primary-600 text-white shadow-xs'
                                : 'text-slate-500 hover:text-slate-800'
                            }`}
                          >
                            {lvl[0].toUpperCase()}
                          </button>
                        )
                      )}
                    </div>

                    <button
                       onClick={() => removeSkill(skill.name)}
                       aria-label={`Remove ${skill.name}`}
                      className="p-1 hover:bg-slate-200 rounded text-slate-400 hover:text-slate-600"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
            <button type="button" onClick={onAnalyze} className="ml-auto font-semibold underline" disabled={loading}>Retry</button>
          </div>
        )}

        {/* Submit Prediction */}
        <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-slate-500">
            {selectedSkills.length >= 3
              ? 'Profile vector ready for Deep Learning multi-class classification.'
              : 'Add at least 1-3 skills for optimal recommendations.'}
          </p>

          <button
            id="run-career-model-btn"
            onClick={onAnalyze}
            disabled={loading || selectedSkills.length === 0}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-3.5 bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-700 hover:to-indigo-700 text-white font-bold rounded-xl shadow-lg shadow-primary-500/25 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Running ANN Model...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Analyze with Deep Learning</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
