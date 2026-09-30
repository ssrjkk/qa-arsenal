import { afterEach, describe, expect, it, vi } from 'vitest';
import type { IRequestConfig, IResponse } from '../types/api.types';
import { Logger } from '../helpers/logger';

const spy = () => vi.spyOn(console, 'log').mockImplementation(() => {});

const req = (overrides: Partial<IRequestConfig> = {}): IRequestConfig => ({
  method: 'GET',
  path: '/x',
  ...overrides,
});

const res = <T>(data: T): IResponse<T> => ({ status: 200, data, headers: {} });

afterEach(() => {
  vi.restoreAllMocks();
  Logger.disable();
});

describe('Logger', () => {
  it('does not log when disabled', () => {
    const log = spy();
    Logger.disable();
    Logger.logRequest(req());
    expect(log).not.toHaveBeenCalled();
  });

  it('logs request when enabled', () => {
    const log = spy();
    Logger.enable();
    Logger.logRequest(req({ path: '/todos' }));
    expect(log).toHaveBeenCalled();
  });

  it('does not log response when disabled', () => {
    const log = spy();
    Logger.disable();
    Logger.logResponse(res({}));
    expect(log).not.toHaveBeenCalled();
  });

  it('logs response when enabled', () => {
    const log = spy();
    Logger.enable();
    Logger.logResponse(res({ id: 1 }));
    expect(log).toHaveBeenCalled();
  });

  it('includes status in response log', () => {
    const log = spy();
    Logger.enable();
    Logger.logResponse({ status: 404, data: {}, headers: {} });
    const text = log.mock.calls.map((c) => String(c[0])).join(' ');
    expect(text).toContain('404');
  });

  it('disable stops further logging', () => {
    const log = spy();
    Logger.enable();
    Logger.logRequest(req({ path: '/a' }));
    Logger.disable();
    Logger.logRequest(req({ method: 'POST', path: '/b' }));
    expect(log).toHaveBeenCalledTimes(1);
  });
});