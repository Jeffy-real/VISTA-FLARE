import { useCallback, useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Activity, ArrowRight, Brain, Database, GitBranch, Layers3, Loader2, Network, RefreshCw, Workflow } from 'lucide-react';
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { api } from '../api/client';
import { useAuth } from '../auth/AuthContext';
import type { InferenceTrace } from '../types';

type Tab = 'system' | 'architectures' | 'training' | 'inference' | 'evaluation' | 'data';
type ModelKey = 'ann' | 'cnn' | 'lstm';

const tabs: { id: Tab; label: string; icon: typeof Workflow }[] = [
  { id: 'system', label: 'System Workflow', icon: Workflow }, { id: 'architectures', label: 'Model Architectures', icon: Layers3 },
  { id: 'training', label: 'Training Pipeline', icon: GitBranch }, { id: 'inference', label: 'Live Inference', icon: Activity },
  { id: 'evaluation', label: 'Evaluation & Comparison', icon: Brain }, { id: 'data', label: 'Live Data Pipeline', icon: Database },
];

const modelLabels: Record<ModelKey, string> = { ann: 'ANN / MLP', cnn: '1D CNN', lstm: 'LSTM' };

function FlowDiagram({ nodes, title, category }: { nodes: any[]; title: string; category?: boolean }) {
  const [selected, setSelected] = useState(0);
  const node = nodes[selected];
  useEffect(() => setSelected(0), [nodes]);
  if (!nodes.length) return <div className="state-panel">No verified workflow metadata is available.</div>;
  return <section className="surface-card p-5 space-y-5"><h2 className="font-bold text-slate-900">{title}</h2><div className="overflow-x-auto pb-1"><div className="flex min-w-max items-center gap-2" role="list" aria-label={`${title} flow`}>
    {nodes.map((item, index) => <div className="flex items-center gap-2" key={item.id || item.name || index}><button type="button" role="listitem" aria-pressed={selected === index} onClick={() => setSelected(index)} className={`min-h-20 w-36 rounded-xl border p-3 text-left text-xs transition ${selected === index ? 'border-indigo-400 bg-indigo-50 text-indigo-900 ring-2 ring-indigo-100' : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300'}`}><strong className="block text-sm">{item.label || item.name}</strong><span className="mt-1 block text-slate-500">{category ? item.kind : item.output || item.kind || item.description || 'Select for details'}</span></button>{index < nodes.length - 1 && <ArrowRight className="w-4 h-4 shrink-0 text-slate-400" aria-hidden="true" />}</div>)}
  </div></div>{node && <aside aria-live="polite" className="rounded-xl bg-slate-50 p-4 text-sm text-slate-700"><h3 className="font-bold text-slate-900">{node.label || node.name}</h3>{node.purpose && <p className="mt-1">{node.purpose}</p>}<dl className="mt-3 grid gap-2 sm:grid-cols-2 text-xs"><div><dt className="font-semibold text-slate-500">Input</dt><dd>{node.input || node.kind || 'Not recorded'}</dd></div><div><dt className="font-semibold text-slate-500">Output</dt><dd>{node.output || node.endpoint || 'Not recorded'}</dd></div><div><dt className="font-semibold text-slate-500">Implementation</dt><dd><code>{node.module || node.training_script || 'Not recorded'}</code></dd></div><div><dt className="font-semibold text-slate-500">API / status</dt><dd>{node.endpoint || node.status || 'Not recorded'}</dd></div></dl></aside>}</section>;
}

function StageList({ trace }: { trace: InferenceTrace }) {
  return <ol className="grid gap-2 md:grid-cols-2">{trace.stages.map((stage) => <li key={`${stage.name}-${stage.at}`} className="flex items-center justify-between gap-3 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs"><span className="font-semibold text-slate-700">{stage.name.replace(/_/g, ' ')}</span><span className={`rounded-full px-2 py-0.5 font-semibold ${stage.status === 'completed' ? 'bg-emerald-50 text-emerald-700' : stage.status === 'failed' ? 'bg-rose-50 text-rose-700' : 'bg-amber-50 text-amber-700'}`}>{stage.status}</span></li>)}</ol>;
}

export const AIModelWorkflowsPage: React.FC = () => {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const currentTabParam = searchParams.get('tab') as Tab | null;
  const validTabs: Tab[] = ['system', 'architectures', 'training', 'inference', 'evaluation', 'data'];
  const tab: Tab = currentTabParam && validTabs.includes(currentTabParam) ? currentTabParam : 'system';

  const setTab = (nextTab: Tab) => {
    setSearchParams({ tab: nextTab });
  };
  const [modelKey, setModelKey] = useState<ModelKey>('ann');
  const [overview, setOverview] = useState<any>(null);
  const [models, setModels] = useState<Record<string, any>>({});
  const [comparison, setComparison] = useState<any[]>([]);
  const [traces, setTraces] = useState<InferenceTrace[]>([]);
  const [retentionHours, setRetentionHours] = useState<number | null>(null);
  const [selectedClass, setSelectedClass] = useState('');
  const [confusion, setConfusion] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true); setError(null);
    try {
      const [nextOverview, ann, cnn, lstm, nextComparison] = await Promise.all([
        api.getWorkflowOverview(), api.getWorkflowModel('ann'), api.getWorkflowModel('cnn'), api.getWorkflowModel('lstm'), api.getWorkflowComparison(),
      ]);
      setOverview(nextOverview); setModels({ ann, cnn, lstm }); setComparison(nextComparison.comparison || []);
      const labels: string[] = ann.class_labels || [];
      setSelectedClass((current) => current || labels[0] || '');
    } catch (err) { setError(err instanceof Error ? err.message : 'Workflow data could not be loaded.'); }
    finally { setLoading(false); }
  };
  const loadTraces = useCallback(async () => {
    if (!user) { setTraces([]); return; }
    try { const result = await api.getInferenceTraces(); setTraces(result.items); setRetentionHours(result.retention_hours); } catch { setTraces([]); }
  }, [user]);
  useEffect(() => { void load(); }, []);
  useEffect(() => { void loadTraces(); }, [loadTraces]);
  useEffect(() => {
    if (!selectedClass) return;
    api.getWorkflowConfusion(modelKey, selectedClass).then(setConfusion).catch(() => setConfusion(null));
  }, [modelKey, selectedClass]);

  const selectedModel = models[modelKey];
  const history = useMemo(() => (selectedModel?.history || []).map((point: any) => ({
    ...point, accuracy: point.accuracy == null ? null : Number((point.accuracy * 100).toFixed(2)),
    val_accuracy: point.val_accuracy == null ? null : Number((point.val_accuracy * 100).toFixed(2)),
  })), [selectedModel]);
  const trainingNodes = selectedModel ? [
    { id: 'examples', label: 'Training examples', output: selectedModel.training?.dataset || 'Not recorded', module: selectedModel.training_script, purpose: 'Synthetic role-skill examples are loaded for the recorded training run.' },
    { id: 'encoding', label: 'Feature & label encoding', output: `${selectedModel.metrics?.num_skills || 'Unknown'} skills / ${selectedModel.metrics?.num_classes || 'Unknown'} classes`, module: 'scripts/common.py', purpose: 'Stored encoders define the feature vocabulary and class mapping.' },
    { id: 'split', label: 'Stratified split', output: selectedModel.training?.split, module: selectedModel.training_script, purpose: 'The scripts split examples before training and evaluation.' },
    { id: 'train', label: 'Model training', output: `${selectedModel.training?.epochs_ran || 'Unknown'} recorded epochs`, module: selectedModel.training_script, purpose: `Optimizer: ${selectedModel.training?.optimizer || 'Not recorded'}; loss: ${selectedModel.training?.loss || 'Not recorded'}.` },
    { id: 'validate', label: 'Validation & checkpoints', output: (selectedModel.training?.callbacks || []).join('; ') || 'Not recorded', module: selectedModel.training_script, purpose: 'Callbacks choose/restore checkpoints based on validation loss.' },
    { id: 'evaluate', label: 'Test evaluation', output: `${selectedModel.training?.test_samples || 'Not recorded'} test examples`, module: 'scripts/evaluate_models.py', purpose: 'Reports, histories, and confusion matrices are saved artifacts.' },
  ] : [];

  return <main className="page-shell max-w-6xl mx-auto space-y-6 py-2 animate-fade-in">
    <header className="space-y-2"><span className="page-eyebrow"><Network className="w-3.5 h-3.5" /> Technical workspace</span><h1 className="text-3xl font-extrabold tracking-tight text-slate-900">AI &amp; Model Workflows</h1><p className="max-w-3xl text-sm text-slate-600">A code- and artifact-backed view of Vista Flare’s inference, training, model comparison, and job-data pipeline. Model scores rank career classes; they are not predictions of hiring outcomes.</p></header>
    <nav className="tab-list border-b border-slate-200" role="tablist" aria-label="AI workflow views">{tabs.map(({ id, label, icon: Icon }) => <button key={id} type="button" role="tab" aria-selected={tab === id} onClick={() => setTab(id)} className={`inline-flex items-center gap-2 border-b-2 px-3 py-3 text-sm font-semibold ${tab === id ? 'border-indigo-600 text-indigo-700' : 'border-transparent text-slate-500 hover:text-slate-800'}`}><Icon className="w-4 h-4" />{label}</button>)}</nav>
    {loading && <div className="state-panel"><Loader2 className="mx-auto mb-2 h-6 w-6 animate-spin text-indigo-600" />Reading saved artifacts and current service state…</div>}
    {error && <div role="alert" className="vf-banner vf-banner-danger"><span>{error}</span><button type="button" onClick={() => void load()} className="underline font-semibold">Retry</button></div>}
    {!loading && overview && <>
      {tab === 'system' && <div className="space-y-6"><section className="grid gap-4 md:grid-cols-3"><div className="surface-card p-4"><p className="text-xs font-semibold text-slate-500">Active inference</p><p className="mt-1 font-bold text-slate-900">{overview.model_health.active_model}</p><p className="mt-1 text-xs text-slate-500">{overview.model_health.status}</p></div><div className="surface-card p-4"><p className="text-xs font-semibold text-slate-500">Last successful inference</p><p className="mt-1 font-bold text-slate-900">{overview.model_health.last_successful_inference ? new Date(overview.model_health.last_successful_inference).toLocaleString() : 'Not recorded'}</p></div><div className="surface-card p-4"><p className="text-xs font-semibold text-slate-500">Last measured duration</p><p className="mt-1 font-bold text-slate-900">{overview.model_health.last_inference_duration_ms == null ? 'Not recorded' : `${overview.model_health.last_inference_duration_ms} ms`}</p></div></section><FlowDiagram title="Career recommendation workflow" nodes={overview.system_workflow} /><FlowDiagram title="Website system architecture" nodes={overview.system_architecture} category /></div>}
      {tab === 'architectures' && <div className="space-y-5"><ModelTabs active={modelKey} onChange={setModelKey} /><section className="surface-card p-5 space-y-3"><div><h2 className="font-bold text-slate-900">{selectedModel?.name}</h2><p className="mt-1 text-sm text-slate-600">{selectedModel?.input_interpretation}</p><p className="provenance-note mt-2">Architecture source: {selectedModel?.architecture_source} · <code>{selectedModel?.training_script}</code></p></div><FlowDiagram title="Interactive layer sequence" nodes={selectedModel?.layers || []} /><dl className="grid gap-3 text-sm sm:grid-cols-3"><div><dt className="text-xs font-semibold text-slate-500">Output classes</dt><dd className="font-bold">{selectedModel?.metrics?.num_classes ?? 'Not recorded'}</dd></div><div><dt className="text-xs font-semibold text-slate-500">Parameter count</dt><dd className="font-bold">{selectedModel?.total_parameters?.toLocaleString?.() || 'Unavailable'}</dd></div><div><dt className="text-xs font-semibold text-slate-500">Artifact</dt><dd className="font-bold">{selectedModel?.artifact_available ? 'Available' : 'Unavailable'}</dd></div></dl></section></div>}
      {tab === 'training' && <div className="space-y-5"><ModelTabs active={modelKey} onChange={setModelKey} /><FlowDiagram title="Verified training pipeline" nodes={trainingNodes} /><section className="surface-card p-5"><h2 className="font-bold text-slate-900">Recorded configuration</h2><dl className="mt-4 grid gap-4 text-sm sm:grid-cols-2 lg:grid-cols-4"><Meta label="Framework" value={selectedModel?.training?.framework} /><Meta label="Batch size" value={selectedModel?.training?.batch_size} /><Meta label="Epochs run" value={selectedModel?.training?.epochs_ran} /><Meta label="Loss" value={selectedModel?.training?.loss} /><Meta label="Training samples" value={selectedModel?.training?.training_samples} /><Meta label="Validation samples" value={selectedModel?.training?.validation_samples} /><Meta label="Test samples" value={selectedModel?.training?.test_samples} /><Meta label="Callbacks" value={(selectedModel?.training?.callbacks || []).join(', ')} /></dl></section></div>}
      {tab === 'inference' && <section className="space-y-5"><div className="surface-card p-5"><div className="flex flex-wrap items-start justify-between gap-3"><div><h2 className="font-bold text-slate-900">Real inference traces</h2><p className="mt-1 text-sm text-slate-600">Stages are persisted only after the backend executes them. Submitted skills and resumes are never stored in this trace.</p></div><button type="button" onClick={() => void loadTraces()} className="inline-flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-700"><RefreshCw className="w-4 h-4" />Refresh traces</button></div>{!user ? <p className="mt-4 vf-banner vf-banner-info">Sign in, run a career recommendation, then return here to view your own retained inference trace.</p> : traces.length === 0 ? <p className="mt-4 text-sm text-slate-500">No retained inference traces yet. Run a career recommendation to create one.</p> : <div className="mt-4 space-y-4">{traces.map((trace) => <article key={trace.trace_id} className="rounded-xl border border-slate-200 bg-slate-50 p-4 space-y-3"><div className="flex flex-wrap items-center justify-between gap-2"><div><h3 className="font-semibold text-slate-900">{trace.status === 'completed' ? 'Completed' : trace.status} · {trace.model_type || 'Unavailable'}</h3><p className="text-xs text-slate-500">{new Date(trace.created_at).toLocaleString()} · {trace.duration_ms == null ? 'duration unavailable' : `${trace.duration_ms} ms`} · {trace.input_feature_count ?? '—'} input features · {trace.output_class_count ?? '—'} classes</p></div>{trace.error_category && <span className="rounded-full bg-rose-50 px-2 py-1 text-xs font-semibold text-rose-700">{trace.error_category}</span>}</div><StageList trace={trace} />{trace.top_results.length > 0 && <p className="text-xs text-slate-600">Top results: {trace.top_results.map((item) => `${item.role} (${(item.score * 100).toFixed(1)}%)`).join(', ')}</p>}</article>)}</div>}</div>{retentionHours != null && <p className="provenance-note">Trace retention: {retentionHours} hours. Access is limited to the signed-in owner.</p>}</section>}
      {tab === 'evaluation' && <div className="space-y-5"><ModelTabs active={modelKey} onChange={setModelKey} /><section className="surface-card overflow-x-auto"><table className="w-full text-left text-xs"><caption className="p-4 text-left text-sm font-bold text-slate-900">Saved evaluation-artifact comparison</caption><thead className="bg-slate-50 text-slate-500"><tr><th className="p-3">Model</th><th className="p-3">Top-1</th><th className="p-3">Top-3</th><th className="p-3">Precision</th><th className="p-3">Recall</th><th className="p-3">F1</th><th className="p-3">Loss</th></tr></thead><tbody>{comparison.map((row) => <tr key={row.Model} className="border-t border-slate-100"><td className="p-3 font-semibold">{row.Model}</td><td className="p-3">{(row.Accuracy * 100).toFixed(2)}%</td><td className="p-3">{(row['Top-3 Accuracy'] * 100).toFixed(2)}%</td><td className="p-3">{(row.Precision * 100).toFixed(2)}%</td><td className="p-3">{(row.Recall * 100).toFixed(2)}%</td><td className="p-3">{(row['F1 Score'] * 100).toFixed(2)}%</td><td className="p-3">{row.Loss ?? 'Not recorded'}</td></tr>)}</tbody></table></section><p className="provenance-note">Top-3 accuracy is the share of test examples whose correct class appears among the model’s three highest-scoring classes.</p><div className="grid gap-5 lg:grid-cols-2"><Chart title="Accuracy by epoch" data={history} lines={[['accuracy', 'Training'], ['val_accuracy', 'Validation']]} suffix="%" /><Chart title="Loss by epoch" data={history} lines={[['loss', 'Training'], ['val_loss', 'Validation']]} /></div><section className="surface-card p-5"><div className="flex flex-wrap items-center justify-between gap-3"><div><h2 className="font-bold text-slate-900">Confusion-matrix class inspection</h2><p className="mt-1 text-xs text-slate-500">Actual-class row from the saved {modelLabels[modelKey]} confusion matrix.</p></div><select aria-label="Select actual career class" value={selectedClass} onChange={(e) => setSelectedClass(e.target.value)} className="rounded-lg border border-slate-200 px-3 py-2 text-sm">{(selectedModel?.class_labels || []).map((label: string) => <option key={label}>{label}</option>)}</select></div>{confusion?.available ? <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-4 lg:grid-cols-7">{confusion.values.map((value: number, index: number) => <div key={`${index}-${value}`} title={`Predicted ${confusion.labels[index]}: ${value}`} className="rounded p-2 text-xs" style={{ background: `rgba(79, 70, 229, ${Math.min(.82, .08 + value / Math.max(1, ...confusion.values) * .74)})`, color: value > Math.max(1, ...confusion.values) * .55 ? '#fff' : '#1e1b4b' }}><span className="block truncate">{confusion.labels[index]}</span><strong>{value}</strong></div>)}</div> : <p className="mt-4 text-sm text-slate-500">Saved confusion matrix unavailable.</p>}</section></div>}
      {tab === 'data' && <div className="space-y-5"><section className="grid gap-4 md:grid-cols-3"><Stat label="External listings" value={overview.providers.external_listing_count} /><Stat label="Seed/demo listings" value={overview.providers.seed_listing_count} /><Stat label="Configured providers" value={overview.providers.providers.filter((provider: any) => provider.configuration === 'configured').length} /></section><section className="surface-card overflow-x-auto"><table className="w-full text-left text-xs"><caption className="p-4 text-left text-sm font-bold text-slate-900">Provider and ingestion status</caption><thead className="bg-slate-50 text-slate-500"><tr><th className="p-3">Provider</th><th className="p-3">Configuration</th><th className="p-3">Operational status</th><th className="p-3">Last success</th><th className="p-3">Latest run</th><th className="p-3">New / updated</th></tr></thead><tbody>{overview.providers.providers.map((provider: any) => <tr key={provider.provider} className="border-t border-slate-100"><td className="p-3 font-semibold">{provider.display_name}</td><td className="p-3">{provider.configuration}</td><td className="p-3">{provider.operational_status}</td><td className="p-3">{provider.last_success ? new Date(provider.last_success).toLocaleString() : 'Not yet verified'}</td><td className="p-3">{provider.latest_run?.status || 'No run recorded'}</td><td className="p-3">{provider.latest_run ? `${provider.latest_run.created} / ${provider.latest_run.updated}` : '—'}</td></tr>)}</tbody></table></section><FlowDiagram title="Persisted job-data pipeline" nodes={[{ id: 'fetch', label: 'Provider fetch', output: 'Validated provider records', module: 'backend/app/services/job_provider.py', purpose: 'Server-only provider adapters make bounded, retrying requests.' }, { id: 'normalize', label: 'Normalize & deduplicate', output: 'Provider-neutral jobs', module: 'backend/app/services/job_ingestion.py', purpose: 'Unique provider/listing keys prevent duplicate persisted rows.' }, { id: 'persist', label: 'Upsert & freshness', output: 'Cached job listings', module: 'backend/app/services/job_ingestion.py', purpose: 'Failed fetches preserve prior cached listings; only successful pulls update staleness.' }, { id: 'match', label: 'Search & relevance', output: 'Job result page', module: 'backend/app/api/data.py', purpose: 'Job relevance remains separate from the career classifier score.' }]} /></div>}
    </>}
  </main>;
};

function ModelTabs({ active, onChange }: { active: ModelKey; onChange: (model: ModelKey) => void }) {
  return <div className="flex flex-wrap gap-2" role="tablist" aria-label="Model selection">{(Object.keys(modelLabels) as ModelKey[]).map((model) => <button type="button" key={model} role="tab" aria-selected={active === model} onClick={() => onChange(model)} className={`rounded-lg border px-3 py-2 text-sm font-semibold ${active === model ? 'border-indigo-300 bg-indigo-50 text-indigo-700' : 'border-slate-200 text-slate-600'}`}>{modelLabels[model]}</button>)}</div>;
}

function Meta({ label, value }: { label: string; value: unknown }) { return <div><dt className="text-xs font-semibold text-slate-500">{label}</dt><dd className="mt-1 break-words font-semibold text-slate-800">{value == null || value === '' ? 'Not recorded' : String(value)}</dd></div>; }
function Stat({ label, value }: { label: string; value: number }) { return <div className="surface-card p-4"><p className="text-xs font-semibold text-slate-500">{label}</p><p className="mt-1 text-2xl font-extrabold text-slate-900">{value.toLocaleString()}</p></div>; }
function Chart({ title, data, lines, suffix = '' }: { title: string; data: any[]; lines: [string, string][]; suffix?: string }) { return <section className="surface-card p-4"><h2 className="font-bold text-slate-900">{title}</h2>{data.length === 0 ? <p className="mt-3 text-sm text-slate-500">Training history not recorded.</p> : <div className="mt-3 h-64"><ResponsiveContainer width="100%" height="100%"><LineChart data={data}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="epoch" /><YAxis /><Tooltip formatter={(value: number) => [`${value}${suffix}`, '']} /><Legend />{lines.map(([key, name], index) => <Line key={key} type="monotone" dataKey={key} name={name} stroke={index ? '#dc2626' : '#4f46e5'} dot={false} strokeWidth={2} />)}</LineChart></ResponsiveContainer></div>}</section>; }
