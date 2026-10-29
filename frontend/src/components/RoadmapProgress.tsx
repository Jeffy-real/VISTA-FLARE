import type { RoadmapStage } from '../types';
import { useLocalJourney, validProgress, type ProgressState, type TaskStatus } from '../localJourney';

export function RoadmapProgress({ role, stages }: { role: string; stages: RoadmapStage[] }) {
  const [progress, setProgress, error] = useLocalJourney<ProgressState>('roadmap', {}, validProgress);
  const tasks = stages.flatMap(stage => stage.suggested_projects.map((project, index) => ({
    key: JSON.stringify([role, stage.stage_number, stage.stage_name, index, project]), project, stage,
  })));
  const completed = tasks.filter(t => progress[t.key] === 'complete').length;
  const update = (keys: string[], status: TaskStatus) => setProgress(prev => ({ ...prev, ...Object.fromEntries(keys.map(key => [key, status])) }));
  return <section className="surface-card p-5 space-y-4" aria-labelledby="roadmap-progress-title">
    <h2 id="roadmap-progress-title" className="font-bold text-slate-900">Your roadmap progress</h2>
    <p className="text-xs text-slate-600">Local-only tracking on this browser; no server saving or account sync. Marking a task complete does not change your skill profile.</p>
    {error && <p role="alert" className="text-sm text-rose-700">{error}</p>}
    <p aria-live="polite" className="text-sm font-semibold text-slate-700">{completed} of {tasks.length} project tasks complete</p>
    <progress aria-label="Completed roadmap tasks" value={completed} max={tasks.length || 1} className="w-full" />
    {!tasks.length && <p>No project tasks were returned for this roadmap.</p>}
    {stages.map(stage => {
      const stageTasks = tasks.filter(t => t.stage === stage);
      const statuses = stageTasks.map(t => progress[t.key] || 'not-started');
      const status = statuses.length && statuses.every(s => s === 'complete') ? 'complete' : statuses.some(s => s !== 'not-started') ? 'in-progress' : 'not-started';
      return <fieldset key={stage.stage_number} className="border rounded-xl p-3 space-y-3">
        <legend className="font-semibold text-sm">{stage.stage_number}. {stage.stage_name}</legend>
        <label className="flex gap-3 items-center text-sm">Stage status (updates all tasks)
          <select disabled={!stageTasks.length} value={status} onChange={e => update(stageTasks.map(t => t.key), e.target.value as TaskStatus)} className="border rounded p-1">
            <option value="not-started">Not started</option><option value="in-progress">In progress</option><option value="complete">Complete</option>
          </select>
        </label>
        {stageTasks.map(t => <label key={t.key} className="flex justify-between gap-3 text-sm"><span>{t.project}</span>
          <select aria-label={`Status: ${t.project}`} value={progress[t.key] || 'not-started'} onChange={e => update([t.key], e.target.value as TaskStatus)} className="border rounded p-1">
            <option value="not-started">Not started</option><option value="in-progress">In progress</option><option value="complete">Complete</option>
          </select>
        </label>)}
      </fieldset>;
    })}
  </section>;
}
