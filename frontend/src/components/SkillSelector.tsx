import { useState, useMemo } from 'react';
import { Search, Plus, X, ChevronDown } from 'lucide-react';
import { SelectedSkill, SkillLevel } from '../types';

interface SkillSelectorProps {
  availableSkills: string[];
  selectedSkills: SelectedSkill[];
  onChange: (skills: SelectedSkill[]) => void;
}

const SKILL_LEVELS: { value: SkillLevel; label: string; color: string }[] = [
  { value: 'beginner', label: 'Beginner', color: 'bg-yellow-100 text-yellow-800 border-yellow-300' },
  { value: 'intermediate', label: 'Intermediate', color: 'bg-blue-100 text-blue-800 border-blue-300' },
  { value: 'advanced', label: 'Advanced', color: 'bg-purple-100 text-purple-800 border-purple-300' },
  { value: 'expert', label: 'Expert', color: 'bg-green-100 text-green-800 border-green-300' },
];

export function SkillSelector({ availableSkills, selectedSkills, onChange }: SkillSelectorProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);

  const filteredSkills = useMemo(() => {
    const selected = new Set(selectedSkills.map(s => s.name.toLowerCase()));
    return availableSkills
      .filter(skill =>
        skill.toLowerCase().includes(searchTerm.toLowerCase()) &&
        !selected.has(skill.toLowerCase())
      )
      .slice(0, 10);
  }, [availableSkills, searchTerm, selectedSkills]);

  const addSkill = (skillName: string) => {
    onChange([...selectedSkills, { name: skillName, level: 'intermediate' }]);
    setSearchTerm('');
    setShowDropdown(false);
  };

  const removeSkill = (skillName: string) => {
    onChange(selectedSkills.filter(s => s.name !== skillName));
  };

  const updateLevel = (skillName: string, level: SkillLevel) => {
    onChange(selectedSkills.map(s =>
      s.name === skillName ? { ...s, level } : s
    ));
  };

  return (
    <div className="space-y-4">
      {/* Search Input */}
      <div className="relative">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search skills to add..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setShowDropdown(true);
            }}
            onFocus={() => setShowDropdown(true)}
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all"
          />
        </div>

        {/* Dropdown */}
        {showDropdown && filteredSkills.length > 0 && (
          <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-auto">
            {filteredSkills.map((skill) => (
              <button
                key={skill}
                onClick={() => addSkill(skill)}
                className="w-full px-4 py-2 text-left hover:bg-primary-50 flex items-center gap-2 transition-colors"
              >
                <Plus className="h-4 w-4 text-primary-500" />
                <span>{skill}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Selected Skills */}
      {selectedSkills.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-700">Selected Skills ({selectedSkills.length})</p>
          <div className="flex flex-wrap gap-2">
            {selectedSkills.map((skill) => (
              <div
                key={skill.name}
                className="flex items-center gap-1 px-3 py-1.5 bg-gray-100 rounded-lg border border-gray-200 animate-fade-in"
              >
                <span className="font-medium text-sm">{skill.name}</span>

                {/* Level Selector */}
                <div className="relative group">
                  <button className="flex items-center gap-1 ml-1 px-2 py-0.5 rounded text-xs font-medium border border-current">
                    <span className="capitalize">{skill.level}</span>
                    <ChevronDown className="h-3 w-3" />
                  </button>
                  <div className="absolute left-0 top-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10 min-w-max">
                    {SKILL_LEVELS.map((level) => (
                      <button
                        key={level.value}
                        onClick={() => updateLevel(skill.name, level.value)}
                        className={`block w-full px-3 py-1.5 text-left text-xs hover:bg-gray-50 ${
                          skill.level === level.value ? 'font-semibold bg-gray-50' : ''
                        }`}
                      >
                        {level.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Remove Button */}
                <button
                  onClick={() => removeSkill(skill.name)}
                  className="ml-1 p-0.5 rounded hover:bg-gray-200 transition-colors"
                >
                  <X className="h-3.5 w-3.5 text-gray-500" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Click outside to close dropdown */}
      {showDropdown && (
        <div
          className="fixed inset-0 z-0"
          onClick={() => setShowDropdown(false)}
        />
      )}
    </div>
  );
}
