import { describe, expect, it } from 'vitest';
import type { APIRequestContext, APIResponse } from '@playwright/test';
import { BaseApi } from '../api/base.api';

class FakeResponse {
  constructor(private opts: { status: number; json?: unknown; text?: string; headers?: Record<string, string> }) {}
  status() {
    return this.opts.status;
  }
  url() {
    return 'http://stub';
  }
  headers() {
    return this.opts.headers ?? { 'content-type': 'application/json' };
  }
  async json() {
    if (this.opts.json === undefined) {
      throw new Error('not json');
    }
    return this.opts.json;
  }
  async text() {
    return this.opts.text ?? JSON.stringify(this.opts.json ?? {});
  }
}

class FakeRequest {
  public calls: Array<{ url: string; opts: Record<string, unknown> }> = [];
  constructor(private responder: (url: string, opts: Record<string, unknown>) => FakeResponse) {}
  async fetch(url: string, opts: Record<string, unknown>) {
    this.calls.push({ url, opts });
    return this.responder(url, opts);
  }
}

function makeApi(status = 200, data: unknown = {}) {
  const request = new FakeRequest(() => new FakeResponse({ status, json: data }));
  const api = new BaseApi(request as unknown as APIRequestContext, 'https://api.example');
  return { api, request };
}

describe('BaseApi.requestWrapper', () => {
  it('GET returns data and status', async () => {
    const { api } = makeApi(200, { items: [1] });
    const res = await api.get<{ items: number[] }>('/todos');
    expect(res.status).toBe(200);
    expect(res.data.items).toEqual([1]);
  });

  it('POST sends JSON body and headers', async () => {
    const { api, request } = makeApi(201, { id: '1' });
    await api.post('/todos', { title: 'x' });
    const call = request.calls[0];
    expect(call.opts.method).toBe('POST');
    expect(call.opts.data).toBe(JSON.stringify({ title: 'x' }));
    expect(call.url).toContain('/todos');
  });

  it('PUT and DELETE map methods', async () => {
    const { api, request } = makeApi();
    await api.put('/todos/1', { title: 'y' });
    await api.delete('/todos/1');
    expect(request.calls[0].opts.method).toBe('PUT');
    expect(request.calls[1].opts.method).toBe('DELETE');
  });

  it('appends query params', async () => {
    const { api, request } = makeApi();
    await api.get('/todos', { page: 2, active: true });
    const url = request.calls[0].url;
    expect(url).toContain('page=2');
    expect(url).toContain('active=true');
  });
});

describe('BaseApi token handling', () => {
  it('includes Authorization when token is set', async () => {
    const { api, request } = makeApi();
    api.setToken('abc');
    await api.get('/me');
    const headers = request.calls[0].opts.headers as Record<string, string>;
    expect(headers.Authorization).toBe('Bearer abc');
  });

  it('omits Authorization without token', async () => {
    const { api, request } = makeApi();
    await api.get('/public');
    const headers = request.calls[0].opts.headers as Record<string, string>;
    expect(headers.Authorization).toBeUndefined();
  });

  it('clearToken removes it', async () => {
    const { api, request } = makeApi();
    api.setToken('abc');
    api.clearToken();
    await api.get('/x');
    const headers = request.calls[0].opts.headers as Record<string, string>;
    expect(headers.Authorization).toBeUndefined();
  });
});

describe('BaseApi error helpers', () => {
  it('assertSuccess throws on mismatch', () => {
    const api = makeApi().api;
    expect(() => api['assertSuccess']({ status: 404, data: {}, headers: {} }, 200)).toThrow();
    expect(() => api['assertSuccess']({ status: 200, data: {}, headers: {} }, 200)).not.toThrow();
  });

  it('assertStatus accepts one of the statuses', () => {
    const api = makeApi().api;
    expect(() => api['assertStatus']({ status: 201, data: {}, headers: {} }, [200, 201])).not.toThrow();
    expect(() => api['assertStatus']({ status: 500, data: {}, headers: {} }, [200, 201])).toThrow();
  });

  it('handleError extracts message from JSON body', async () => {
    const api = makeApi().api;
    const resp = new FakeResponse({ status: 400, json: { message: 'bad', code: 'BAD_INPUT' } });
    const err = await api['handleError'](resp as unknown as APIResponse);
    expect(err.message).toBe('bad');
    expect(err.code).toBe('BAD_INPUT');
    expect(err.statusCode).toBe(400);
  });

  it('handleError falls back to text on non-JSON', async () => {
    const api = makeApi().api;
    const resp = new FakeResponse({ status: 500, text: 'boom', headers: { 'content-type': 'text/plain' } });
    const err = await api['handleError'](resp as unknown as APIResponse);
    expect(err.message).toBe('boom');
  });
});