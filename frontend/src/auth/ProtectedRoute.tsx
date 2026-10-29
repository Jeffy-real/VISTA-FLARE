import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';
export function ProtectedRoute() { const { user, loading } = useAuth(); const location = useLocation(); if (loading) return <div className="p-10 text-center text-slate-500">Loading your workspace…</div>; return user ? <Outlet /> : <Navigate to={`/login?next=${encodeURIComponent(location.pathname + location.search)}`} replace />; }
