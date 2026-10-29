import type { ReactNode } from 'react';
import { VistaFlareLogo } from './VistaFlareLogo';

export { VistaFlareLogo } from './VistaFlareLogo';

export function StatusPill({
  tone = 'neutral',
  children,
  title,
}: {
  tone?: 'success' | 'warning' | 'danger' | 'neutral';
  children: ReactNode;
  title?: string;
}) {
  return <span title={title} className={`vf-status vf-status-${tone}`}><span aria-hidden="true" className="vf-status-dot" />{children}</span>;
}

export function StatusBanner({
  tone = 'info',
  children,
  action,
}: {
  tone?: 'info' | 'warning' | 'danger';
  children: ReactNode;
  action?: ReactNode;
}) {
  return <div role={tone === 'danger' ? 'alert' : 'status'} className={`vf-banner vf-banner-${tone}`}><span>{children}</span>{action}</div>;
}

export function LoadingState({ label = 'Loading' }: { label?: string }) {
  return (
    <div className="vf-loading flex flex-col items-center justify-center gap-2 py-6 text-center" role="status" aria-live="polite">
      <VistaFlareLogo variant="icon" size={28} className="opacity-80" />
      <div className="flex items-center gap-2 text-xs text-slate-500 font-medium">
        <span className="vf-spinner" aria-hidden="true" />
        {label}
      </div>
    </div>
  );
}
