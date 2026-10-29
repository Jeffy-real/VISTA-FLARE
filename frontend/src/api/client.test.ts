import { afterEach, describe, expect, it, vi } from 'vitest';
import { api } from './client';

describe('API client errors', () => {
  afterEach(() => vi.restoreAllMocks());

  it('includes JSON detail in a deterministic error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: 'Not authorized' }), { status: 403, statusText: 'Forbidden', headers: { 'Content-Type': 'application/json' } })));
    await expect(api.health()).rejects.toThrow('API Error: 403 Forbidden: Not authorized');
  });

  it('handles non-JSON proxy errors', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('upstream unavailable', { status: 502, statusText: 'Bad Gateway' })));
    await expect(api.health()).rejects.toThrow('API Error: 502 Bad Gateway');
  });
});
