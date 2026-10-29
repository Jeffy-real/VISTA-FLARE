// API & Data Types for Vista Flare

export type SkillLevel = 'beginner' | 'intermediate' | 'advanced' | 'expert';

export interface SelectedSkill {
  name: string;
  level: SkillLevel;
}

export interface SkillInput {
  name: string;
  level?: string;
}

export interface CareerRecommendation {
  rank: number;
  role: string;
  score: number;
}

export interface PredictionResponse {
  model: string;
  model_version: string;
  recommendations: CareerRecommendation[];
  trace_id?: string | null;
  trace_access_token?: string | null;
}

export interface SkillMatch {
  skill: string;
  importance: number;
  user_level: string;
  required_level: string;
  status: 'strong' | 'developing' | 'missing';
  explanation: string;
}

export interface RoadmapStage {
  stage_number: number;
  stage_name: string;
  description: string;
  skills: string[];
  suggested_projects: string[];
  estimated_weeks: number;
}

export interface CompanyMatch {
  company_id: number;
  company_name: string;
  industry: string;
  location: string;
  match_score: number;
  matched_skills: string[];
  open_jobs_count: number;
}

export interface SkillAnalysisResponse {
  target_role: string;
  role_category: string;
  ai_match_score?: number | null;
  skill_match_score: number;
  strong_skills: SkillMatch[];
  developing_skills: SkillMatch[];
  missing_skills: SkillMatch[];
  learning_resources: LearningResource[];
  company_matches: CompanyMatch[];
  roadmap: RoadmapStage[];
}

export interface Skill {
  id: number;
  name: string;
  category: string;
}

export interface Role {
  id: number;
  name: string;
  category: string;
}

export interface RoleDetail {
  id: number;
  name: string;
  category: string;
  skills: { skill: string; importance: number; level: string; required: boolean }[];
  job_count: number;
  avg_salary_min?: number | null;
  avg_salary_max?: number | null;
}

export interface Job {
  id: number;
  company: string;
  title: string;
  role: string;
  category: string;
  employment_type: string;
  experience_level: string;
  work_mode: string;
  location: string;
  country: string;
  city: string;
  salary_min?: number | null;
  salary_max?: number | null;
  currency: string;
  skills: string[];
  posting_date: string;
  salary_period?: string | null;
  source?: string | null;
  provider_name?: string | null;
  provider_id?: string | null;
  source_url?: string | null;
  source_kind?: 'external' | 'seed' | string | null;
  active?: boolean;
  stale?: boolean;
  first_seen?: string | null;
  last_seen?: string | null;
  last_checked?: string | null;
  freshness?: string;
  freshness_label?: string;
  match_score?: number | null;
  matched_skills?: string[];
}

export interface JobSearchResponse {
  items: Job[];
  page: number;
  page_size: number;
  total: number;
  score_explanation: string;
}

export interface InferenceTrace {
  trace_id: string;
  created_at: string;
  completed_at?: string | null;
  status: 'running' | 'completed' | 'failed' | string;
  model_type?: string | null;
  model_version?: string | null;
  duration_ms?: number | null;
  input_feature_count?: number | null;
  output_class_count?: number | null;
  error_category?: string | null;
  stages: { name: string; status: string; at: string; [key: string]: unknown }[];
  top_results: CareerRecommendation[];
}

export interface Company {
  id: number;
  name: string;
  country: string;
  city: string;
  industry: string;
  size: string;
  website: string;
  job_count: number;
}

export interface LearningResource {
  id: number;
  skill: string;
  title: string;
  platform: string;
  type: string;
  url: string;
  difficulty: string;
  duration: string;
  free_or_paid: string;
  provider: string;
  description: string;
}

export interface ModelMetrics {
  model: string;
  model_version: string;
  accuracy: number;
  top_3_accuracy: number;
  precision_weighted: number;
  recall_weighted: number;
  f1_weighted: number;
  num_skills: number;
  num_classes: number;
  training_samples: number;
  validation_samples?: number;
  test_samples?: number;
  epochs_ran?: number;
  training_time_seconds?: number;
  total_parameters?: number;
  architecture: string;
  trained_at: string;
}

export interface ModelComparisonItem {
  Model: string;
  Role?: string;
  Accuracy: number;
  'Top-3 Accuracy': number;
  Precision: number;
  Recall: number;
  'F1 Score': number;
  Loss?: number;
  Parameters?: number;
  'Latency (ms/sample)'?: number;
  'Training Time'?: string;
}

export interface ModelHistory {
  model?: string;
  epochs: number[];
  accuracy: number[];
  val_accuracy: number[];
  loss: number[];
  val_loss: number[];
  top_3_accuracy: number[];
  val_top_3_accuracy: number[];
}

export interface MarketOverview {
  total_jobs: number;
  total_companies: number;
  total_roles: number;
  avg_salary: number;
  work_mode_distribution: Record<string, number>;
  top_demanded_roles: { role: string; count: number; avg_salary_min?: number; avg_salary_max?: number }[];
  top_in_demand_skills: { skill: string; count: number; percentage: number }[];
}

export interface HealthResponse {
  status: string;
  app_name: string;
  model_loaded: boolean;
  model_type?: string | null;
  model_load_error?: string | null;
  database_connected: boolean;
}
