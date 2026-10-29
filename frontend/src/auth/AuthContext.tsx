import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { api } from '../api/client';

export interface UserProfile { id?: number; email: string; display_name?: string; name?: string; skills?: unknown[] }
interface AuthContextValue { user: UserProfile | null; loading: boolean; login: (email: string, password: string) => Promise<void>; register: (name: string, email: string, password: string) => Promise<void>; logout: () => Promise<void>; refresh: () => Promise<void> }
const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const normalize = (value: Awaited<ReturnType<typeof api.getProfile>>) => ({ ...value, name: value.display_name || value.name });
  const refresh = useCallback(async () => {
    try {
      setUser(normalize(await api.getProfile()));
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => { void refresh(); }, [refresh]);
  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      refresh,
      login: async (email, password) => { setUser(normalize(await api.login(email, password))); },
      register: async (name, email, password) => { setUser(normalize(await api.register(name, email, password))); },
      logout: async () => { await api.logout(); setUser(null); },
    }),
    [user, loading, refresh]
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() { const value = useContext(AuthContext); if (!value) throw new Error('useAuth must be used inside AuthProvider'); return value; }
