import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { api } from '../api/client';
import { ApplicationsPage, ComparisonPage, SavedPage } from './WorkspacePages';

vi.mock('../api/client', () => ({ api: {
  getSavedJobs: vi.fn(), getApplications: vi.fn(), getRoles: vi.fn(), getRole: vi.fn(),
  deleteSavedJob: vi.fn(), updateApplication: vi.fn(),
} }));

const mockedApi = vi.mocked(api);
const renderRoute = (element: React.ReactElement, route = '/') => render(<MemoryRouter initialEntries={[route]}>{element}</MemoryRouter>);

describe('workspace rendering', () => {
  beforeEach(() => vi.clearAllMocks());

  it('renders saved jobs and applications from API records', async () => {
    mockedApi.getSavedJobs.mockResolvedValue([{ id: 1, job_id: 7, job: { title: 'Data Analyst', company: 'Acme', active: true } }]);
    mockedApi.getApplications.mockResolvedValue([{ id: 2, job_id: 8, status: 'Applied', job: { title: 'ML Engineer', company: 'Beta' }, notes: 'Tailor portfolio' }]);
    renderRoute(<><SavedPage /><ApplicationsPage /></>);
    expect(await screen.findByText('Data Analyst')).toBeInTheDocument();
    expect(await screen.findByText('ML Engineer')).toBeInTheDocument();
    expect(screen.getByText('Tailor portfolio')).toBeInTheDocument();
  });

  it('selects and removes roles in comparison query state', async () => {
    mockedApi.getRoles.mockResolvedValue([{ id: 1, name: 'Data Analyst', category: 'Data' }, { id: 2, name: 'ML Engineer', category: 'AI' }] as never);
    mockedApi.getRole.mockImplementation(async (id) => ({ id, name: id === 1 ? 'Data Analyst' : 'ML Engineer', category: 'Data', skills: [], job_count: 1, avg_salary_min: null, avg_salary_max: null } as never));
    renderRoute(<ComparisonPage />, '/compare?roles=1');
    expect(await screen.findByText('Data Analyst ×')).toBeInTheDocument();
    await userEvent.selectOptions(screen.getByLabelText('Add roles'), '2');
    await waitFor(() => expect(screen.getByText('ML Engineer ×')).toBeInTheDocument());
    await userEvent.click(screen.getByText('Data Analyst ×'));
    await waitFor(() => expect(screen.queryByText('Data Analyst ×')).not.toBeInTheDocument());
  });
});
