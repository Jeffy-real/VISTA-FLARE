import { FormEvent, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Loader2, ShieldCheck } from 'lucide-react';
import { useAuth } from '../auth/AuthContext';
import { VistaFlareLogo } from '../components/VistaFlareLogo';

function AuthForm({ mode }: { mode: 'login' | 'register' }) {
  const { login, register } = useAuth();
  const nav = useNavigate();
  const loc = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      if (mode === 'login') await login(email, password);
      else await register(name, email, password);
      nav(new URLSearchParams(loc.search).get('next') || '/profile');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to continue. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="page-shell max-w-md mx-auto py-8 sm:py-12">
      <div className="surface-card p-6 sm:p-8">
        <div className="flex items-center justify-between mb-6">
          <Link to="/" aria-label="Vista Flare Home">
            <VistaFlareLogo variant="full" size={32} />
          </Link>
          <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-700 bg-indigo-50 border border-indigo-100 rounded-full px-2.5 py-1">
            <ShieldCheck className="w-3.5 h-3.5" /> Secure
          </div>
        </div>
        <h1 className="text-2xl font-bold text-slate-900 mb-2">
          {mode === 'login' ? 'Welcome back' : 'Create your Vista Flare account'}
        </h1>
        <p className="text-sm text-slate-500 mb-6">Your saved journey syncs securely across devices.</p>
        <form onSubmit={submit} className="space-y-4" aria-describedby={error ? 'auth-error' : undefined}>
          {mode === 'register' && <label className="block text-sm font-semibold text-slate-700">Name
            <input required value={name} onChange={(e) => setName(e.target.value)} placeholder="Your name" autoComplete="name" className="mt-1 w-full rounded-xl border border-slate-200 p-3" />
          </label>}
          <label className="block text-sm font-semibold text-slate-700">Email
            <input required type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" autoComplete="email" className="mt-1 w-full rounded-xl border border-slate-200 p-3" />
          </label>
          <label className="block text-sm font-semibold text-slate-700">Password
            <input required minLength={8} type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="At least 8 characters" autoComplete={mode === 'login' ? 'current-password' : 'new-password'} className="mt-1 w-full rounded-xl border border-slate-200 p-3" />
          </label>
          {error && <p id="auth-error" role="alert" className="text-sm text-rose-700 bg-rose-50 border border-rose-200 rounded-xl p-3">{error}</p>}
          <button disabled={submitting} className="w-full rounded-xl bg-slate-900 hover:bg-slate-800 text-white p-3 font-semibold disabled:opacity-60 inline-flex justify-center items-center gap-2">
            {submitting && <Loader2 className="w-4 h-4 animate-spin" />}{submitting ? 'Working…' : mode === 'login' ? 'Sign in' : 'Register'}
          </button>
        </form>
        <p className="text-sm text-center mt-5 text-slate-600">{mode === 'login' ? <>New here? <Link className="text-indigo-600 font-semibold" to="/register">Create an account</Link></> : <>Already registered? <Link className="text-indigo-600 font-semibold" to="/login">Sign in</Link></>}</p>
      </div>
    </main>
  );
}

export const LoginPage = () => <AuthForm mode="login" />;
export const RegisterPage = () => <AuthForm mode="register" />;
