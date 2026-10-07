import type {
  HealthResponse,
  Skill,
  Role,
  RoleDetail,
  Company,
  Job,
  LearningResource,
  ModelMetrics,
  ModelHistory,
  ModelComparisonItem,
  MarketOverview,
  SelectedSkill,
  PredictionResponse,
  SkillAnalysisResponse,
} from '../types';

const API_BASE = '/api';

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export const api = {
  // Health check
  async health(): Promise<HealthResponse> {
    return fetchAPI<HealthResponse>('/health');
  },

  // Skills
  async getSkills(): Promise<Skill[]> {
    return fetchAPI<Skill[]>('/skills?limit=500');
  },

  // Roles
  async getRoles(): Promise<Role[]> {
    return fetchAPI<Role[]>('/roles?limit=150');
  },

  async getRole(id: number): Promise<RoleDetail> {
    return fetchAPI<RoleDetail>(`/roles/${id}`);
  },

  // Companies
  async getCompanies(): Promise<Company[]> {
    return fetchAPI<Company[]>('/companies?limit=100');
  },

  // Jobs
  async getJobs(role?: string, location?: string): Promise<Job[]> {
    let query = '?limit=150';
    if (role) query += `&role=${encodeURIComponent(role)}`;
    if (location) query += `&location=${encodeURIComponent(location)}`;
    return fetchAPI<Job[]>(`/jobs${query}`);
  },

  // Learning resources
  async getLearning(skill?: string): Promise<LearningResource[]> {
    const query = skill ? `?skill=${encodeURIComponent(skill)}` : '?limit=100';
    return fetchAPI<LearningResource[]>(`/learning${query}`);
  },

  // Career prediction with ANN
  async predict(skills: SelectedSkill[]): Promise<PredictionResponse> {
    const payload = {
      skills: skills.map((s) => ({
        name: s.name,
        level: s.level,
      })),
    };
    return fetchAPI<PredictionResponse>('/predict', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  // Skill gap analysis, company matching, and roadmap
  async analyzeSkills(targetRole: string, skills: SelectedSkill[]): Promise<SkillAnalysisResponse> {
    const payload = {
      target_role: targetRole,
      skills: skills.map((s) => ({
        name: s.name,
        level: s.level,
      })),
    };
    return fetchAPI<SkillAnalysisResponse>('/analyze-skills', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  // Market analytics
  async getMarketOverview(): Promise<MarketOverview> {
    return fetchAPI<MarketOverview>('/market/overview');
  },

  async getMarketRoles(): Promise<any[]> {
    return fetchAPI<any[]>('/market/roles');
  },

  async getMarketSkills(): Promise<any[]> {
    return fetchAPI<any[]>('/market/skills');
  },

  async getMarketSalaries(): Promise<any[]> {
    return fetchAPI<any[]>('/market/salaries');
  },

  // Model and Deep Learning Lab
  async getModelMetrics(model = 'ann'): Promise<ModelMetrics> {
    return fetchAPI<ModelMetrics>(`/model/metrics?model=${model}`);
  },

  async getModelHistory(model = 'ann'): Promise<ModelHistory> {
    return fetchAPI<ModelHistory>(`/model/history?model=${model}`);
  },

  async getModelComparison(): Promise<ModelComparisonItem[]> {
    return fetchAPI<ModelComparisonItem[]>('/model/comparison');
  },

  async getModelArchitecture(model = 'ann'): Promise<any> {
    return fetchAPI<any>(`/model/architecture?model=${model}`);
  },

  async getConfusionMatrix(model = 'ann'): Promise<any> {
    return fetchAPI<any>(`/model/confusion-matrix?model=${model}`);
  },
};
