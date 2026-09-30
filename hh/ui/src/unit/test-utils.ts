import type { APIRequestContext, APIResponse } from '@playwright/test';

export class FakeResponse {
  constructor(
    private opts: { status: number; json?: unknown; text?: string; headers?: Record<string, string> },
  ) {}
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

export class FakeRequest {
  public calls: Array<{ url: string; opts: Record<string, unknown> }> = [];
  constructor(private responder: (url: string, opts: Record<string, unknown>) => FakeResponse) {}
  async fetch(url: string, opts: Record<string, unknown>) {
    this.calls.push({ url, opts });
    return this.responder(url, opts);
  }
  asApiRequestContext(): APIRequestContext {
    return this as unknown as APIRequestContext;
  }
}

export function makeRequest(status = 200, data: unknown = {}) {
  return new FakeRequest(() => new FakeResponse({ status, json: data }));
}

export type { APIResponse };