import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import App from './App';

vi.mock('./api/client', () => ({ api: {
  getProfile: vi.fn(), getSkills: vi.fn(() => new Promise(() => undefined)),
  getRoles: vi.fn(() => new Promise(() => undefined)), getModelMetrics: vi.fn(() => new Promise(() => undefined)), health: vi.fn(() => new Promise(() => undefined)),
} }));
vi.mock('./auth/AuthContext', () => ({ useAuth: () => ({ user: null }) }));

describe('routing', () => {
  it('renders the not-found page for an unknown route', async () => {
    render(<MemoryRouter initialEntries={['/does-not-exist']}><App /></MemoryRouter>);
    expect(screen.getByText('404')).toBeInTheDocument();
    expect(screen.getByText('That career path does not exist.')).toBeInTheDocument();
  });
});
