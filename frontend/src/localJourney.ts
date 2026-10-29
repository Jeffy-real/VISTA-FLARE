import { useEffect, useState } from 'react';
import type { CareerRecommendation, SelectedSkill } from './types';

const record = (v: unknown): v is Record<string, unknown> => !!v && typeof v === 'object' && !Array.isArray(v);
export const validText = (v: unknown): v is string => typeof v === 'string' && v.length <= 300;
export const validSkills = (v: unknown): v is SelectedSkill[] => Array.isArray(v) && v.length <= 500 && v.every(s => record(s) && validText(s.name) && s.name.trim() && ['beginner', 'intermediate', 'advanced', 'expert'].includes(String(s.level))) && new Set(v.map(s => s.name.toLowerCase())).size === v.length;
export const validRecommendations = (v: unknown): v is CareerRecommendation[] => Array.isArray(v) && v.length <= 150 && v.every(r => record(r) && validText(r.role) && typeof r.rank === 'number' && Number.isInteger(r.rank) && r.rank > 0 && typeof r.score === 'number' && Number.isFinite(r.score) && r.score >= 0 && r.score <= 1);
export const validSavedRoles = (v: unknown): v is string[] => Array.isArray(v) && v.length <= 150 && v.every(validText);
export interface AnalysisHistory { at: string; skills: SelectedSkill[]; recommendations: CareerRecommendation[]; model: string }
export const validHistory = (v: unknown): v is AnalysisHistory[] => Array.isArray(v) && v.length <= 10 && v.every(h => record(h) && typeof h.at === 'string' && Number.isFinite(Date.parse(h.at)) && validSkills(h.skills) && validRecommendations(h.recommendations) && validText(h.model));
export type TaskStatus = 'not-started' | 'in-progress' | 'complete';
export type ProgressState = Record<string, TaskStatus>;
export const validProgress = (v: unknown): v is ProgressState => record(v) && Object.keys(v).length <= 10000 && Object.entries(v).every(([k, value]) => k.length <= 4000 && ['not-started', 'in-progress', 'complete'].includes(String(value)));

// Versioned, bounded data only. Storage is optional: failures leave the live state usable.
export function useLocalJourney<T>(key: string, fallback: T, validate: (value: unknown) => value is T) {
  const [initial] = useState(() => {
    try {
      const raw = window.localStorage.getItem(`vista-journey-v1:${key}`);
      if (!raw) return { value: fallback, error: '' };
      if (raw.length > 2_000_000) throw new Error('oversized');
      const value: unknown = JSON.parse(raw);
      if (!validate(value)) throw new Error('invalid');
      return { value, error: '' };
    } catch {
      return { value: fallback, error: 'Local data could not be restored. This session can still be used.' };
    }
  });
  const [value, setValue] = useState<T>(initial.value);
  const [error, setError] = useState(initial.error);
  useEffect(() => {
    try {
      if (!validate(value)) throw new Error('invalid');
      window.localStorage.setItem(`vista-journey-v1:${key}`, JSON.stringify(value));
      setError(initial.error);
    } catch {
      setError('Changes are only in memory: browser storage is unavailable or full. They may be lost when this page closes.');
    }
  }, [key, value, validate, initial.error]);
  return [value, setValue, error] as const;
}
