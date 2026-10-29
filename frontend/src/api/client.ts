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
  JobSearchResponse,
  InferenceTrace,
  SelectedSkill,
  PredictionResponse,
  SkillAnalysisResponse,
} from '../types';

const API_BASE = '/api';

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const csrf = document.cookie.split('; ').find((entry) => entry.startsWith('vista_flare_csrf='))?.split('=').slice(1).join('=');
  const isFormData = typeof FormData !== 'undefined' && options?.body instanceof FormData;
  const headers: Record<string, string> = {
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...(csrf ? { 'X-CSRF-Token': decodeURIComponent(csrf) } : {}),
    ...(options?.headers as Record<string, string> | undefined),
  };
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    credentials: 'include',
    headers,
  });

  if (!response.ok) {
    let detail = '';
    try {
      const body = await response.json() as { detail?: string };
      detail = body.detail ? `: ${body.detail}` : '';
    } catch {
      // Some proxies return an empty/non-JSON error body.
    }
    throw new Error(`API Error: ${response.status} ${response.statusText}${detail}`);
  }

  return response.json();
}

export interface AuthUser { id?: number; email: string; display_name?: string; name?: string; skills?: unknown[] }

export const api = {
  async login(email: string, password: string): Promise<AuthUser> { return fetchAPI<AuthUser>('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }); },
  async register(name: string, email: string, password: string): Promise<AuthUser> { return fetchAPI<AuthUser>('/auth/register', { method: 'POST', body: JSON.stringify({ display_name: name, email, password }) }); },
  async logout(): Promise<void> { await fetchAPI('/auth/logout', { method: 'POST' }); },
  async getProfile(): Promise<AuthUser> { return fetchAPI<AuthUser>('/profile'); },
  async updateProfile(profile: Partial<AuthUser>): Promise<AuthUser> { return fetchAPI<AuthUser>('/profile', { method: 'PATCH', body: JSON.stringify({ display_name: profile.display_name || profile.name }) }); },
  async importJourney(data: Record<string, string | null>): Promise<void> { await fetchAPI('/profile/import', { method: 'POST', body: JSON.stringify({ data }) }); },
  async getRoadmaps(): Promise<any[]> { return fetchAPI<any[]>('/roadmap'); },
  async createRoadmap(target_role: string, content: string): Promise<any> { return fetchAPI<any>('/roadmap', { method: 'POST', body: JSON.stringify({ target_role, content }) }); },
  async updateRoadmap(id: number, target_role: string, content: string): Promise<any> { return fetchAPI<any>(`/roadmap/${id}`, { method: 'PATCH', body: JSON.stringify({ target_role, content }) }); },
  async getSavedJobs(): Promise<any[]> { return fetchAPI<any[]>('/saved-jobs'); },
  async saveJob(job_id: number): Promise<any> { return fetchAPI<any>('/saved-jobs', { method: 'POST', body: JSON.stringify({ job_id }) }); },
  async deleteSavedJob(job_id: number): Promise<void> { await fetchAPI(`/saved-jobs/${job_id}`, { method: 'DELETE' }); },
  async getApplications(): Promise<any[]> { return fetchAPI<any[]>('/applications'); },
  async createApplication(job_id: number, status: string, notes?: string): Promise<any> { return fetchAPI<any>('/applications', { method: 'POST', body: JSON.stringify({ job_id, status, notes }) }); },
  async updateApplication(id: number, status: string, notes?: string): Promise<any> { return fetchAPI<any>(`/applications/${id}`, { method: 'PATCH', body: JSON.stringify({ status, notes }) }); },
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

  async searchJobs(params: Record<string, string | number | undefined>): Promise<JobSearchResponse> {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== '') query.set(key, String(value));
    });
    return fetchAPI<JobSearchResponse>(`/job-search?${query.toString()}`);
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

  // AI & Model Workflows
  async getWorkflowOverview(): Promise<any> { return fetchAPI<any>('/workflows/overview'); },
  async getWorkflowModel(model: 'ann' | 'cnn' | 'lstm'): Promise<any> { return fetchAPI<any>(`/workflows/models/${model}`); },
  async getWorkflowComparison(): Promise<any> { return fetchAPI<any>('/workflows/comparison'); },
  async getWorkflowConfusion(model: 'ann' | 'cnn' | 'lstm', className?: string): Promise<any> {
    const query = className ? `?class_name=${encodeURIComponent(className)}` : '';
    return fetchAPI<any>(`/workflows/models/${model}/confusion${query}`);
  },
  async getWorkflowProviders(): Promise<any> { return fetchAPI<any>('/workflows/providers'); },
  async getWorkflowModelHealth(): Promise<any> { return fetchAPI<any>('/workflows/model-health'); },
  async getInferenceTraces(): Promise<{ items: InferenceTrace[]; retention_hours: number }> {
    return fetchAPI<{ items: InferenceTrace[]; retention_hours: number }>('/workflows/inference-traces');
  },
  async getInferenceTrace(traceId: string, accessToken?: string): Promise<InferenceTrace> {
    const query = accessToken ? `?trace_access_token=${encodeURIComponent(accessToken)}` : '';
    return fetchAPI<InferenceTrace>(`/workflows/inference-traces/${encodeURIComponent(traceId)}${query}`);
  },

  // Career Intelligence & Market Trends
  async getMarketTrends(role?: string): Promise<any> {
    const query = role ? `?role=${encodeURIComponent(role)}` : '';
    return fetchAPI<any>(`/market-trends${query}`);
  },

  // Resume Coach & Matching
  async analyzeResume(body: FormData | { resume_text: string; job_id?: number }): Promise<any> {
    if (typeof FormData !== 'undefined' && body instanceof FormData) {
      return fetchAPI<any>('/resume/analyze', { method: 'POST', body });
    }
    const form = new FormData();
    const data = body as { resume_text: string; job_id?: number };
    if (data.resume_text) form.append('resume_text', data.resume_text);
    if (data.job_id != null) form.append('job_id', String(data.job_id));
    return fetchAPI<any>('/resume/analyze', { method: 'POST', body: form });
  },

  // Interview Coach & Prep
  async getInterviewCoach(roleId: number): Promise<any> {
    return fetchAPI<any>(`/interview/roles/${roleId}`);
  },

  async saveInterviewProgress(roleId: number, notes: string, completedQuestions: string[]): Promise<any> {
    const form = new URLSearchParams();
    form.append('notes', notes);
    form.append('completed_questions', JSON.stringify(completedQuestions));
    return fetchAPI<any>(`/interview/roles/${roleId}/progress`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: form.toString(),
    });
  },

  // Notifications
  async getNotifications(unreadOnly = false): Promise<any[]> {
    return fetchAPI<any[]>(`/notifications?unread_only=${unreadOnly}`);
  },

  async markNotificationRead(id: number): Promise<any> {
    return fetchAPI<any>(`/notifications/${id}/read`, { method: 'POST' });
  },

  // Alert & Notification Preferences
  async getAlertPreferences(): Promise<any> {
    return fetchAPI<any>('/alert-preferences');
  },

  async updateAlertPreferences(payload: any): Promise<any> {
    return fetchAPI<any>('/alert-preferences', {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  },

  // Admin Ingestion & Database Operational Status
  async getAdminStatus(adminSecret: string): Promise<any> {
    return fetchAPI<any>('/admin/status', {
      headers: { 'X-Ingestion-Secret': adminSecret },
    });
  },

  async triggerJobIngestion(adminSecret: string, provider?: string, limit = 50): Promise<any> {
    const params = new URLSearchParams();
    if (provider) params.set('provider', provider);
    if (limit) params.set('limit', String(limit));
    const query = params.toString() ? `?${params.toString()}` : '';
    return fetchAPI<any>(`/admin/jobs/ingest${query}`, {
      method: 'POST',
      headers: { 'X-Ingestion-Secret': adminSecret },
    });
  },
};
