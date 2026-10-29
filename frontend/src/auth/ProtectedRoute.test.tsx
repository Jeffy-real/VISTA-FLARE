import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { ProtectedRoute } from './ProtectedRoute';

vi.mock('./AuthContext', () => ({ useAuth: vi.fn() }));
import { useAuth } from './AuthContext';
const mockedUseAuth = vi.mocked(useAuth);

describe('protected routes', () => {
  it('redirects anonymous users to login with the original path', () => {
    mockedUseAuth.mockReturnValue({ user: null, loading: false } as never);
    render(<MemoryRouter initialEntries={['/saved?tab=all']}><Routes><Route element={<ProtectedRoute />}><Route path="/saved" element={<p>Private</p>} /></Route><Route path="/login" element={<p>Login screen</p>} /></Routes></MemoryRouter>);
    expect(screen.getByText('Login screen')).toBeInTheDocument();
  });
});
