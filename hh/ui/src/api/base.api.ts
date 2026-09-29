import { test as base, APIRequestContext, APIResponse } from '@playwright/test';
import { IResponse, IApiError, ApiMethod, IRequestConfig } from '../types/api.types';

export class BaseApi {
  public request: APIRequestContext;
  public baseURL: string;
  protected _token: string | null = null;
  private parent: BaseApi | null = null;

  constructor(request: APIRequestContext, baseURL: string) {
    this.request = request;
    this.baseURL = baseURL;
  }

  setToken(token: string): void {
    this._token = token;
  }

  getToken(): string | null {
    if (this.parent) {
      return this.parent.getToken();
    }
    return this._token;
  }

  getTokenValue(): string | null {
    return this._token;
  }

  setParent(parent: BaseApi): void {
    this.parent = parent;
  }

  clearToken(): void {
    this._token = null;
  }

  protected getDefaultHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    };
    const token = this.getToken();
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    return headers;
  }

  private buildUrl(path: string, params?: Record<string, string | number | boolean>): string {
    const url = new URL(path, this.baseURL);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, String(value));
      });
    }
    return url.toString();
  }

  private logRequest(method: ApiMethod, url: string, body?: unknown): void {
    console.log(`→ ${method} ${url}`);
    if (body) {
      console.log('  Body:', JSON.stringify(body, null, 2));
    }
  }

  private logResponse(response: APIResponse): void {
    console.log(`← ${response.status()} ${response.url()}`);
  }

  async requestWrapper<T>(config: IRequestConfig): Promise<IResponse<T>> {
    const url = this.buildUrl(config.path, config.params);
    this.logRequest(config.method, url, config.body);

    const response = await this.request.fetch(url, {
      method: config.method,
      headers: { ...this.getDefaultHeaders(), ...config.headers },
      data: config.body ? JSON.stringify(config.body) : undefined,
    });

    this.logResponse(response);

    let data: T | null = null;
    const contentType = response.headers()['content-type'] || '';

    if (contentType.includes('application/json')) {
      data = await response.json();
    } else if (contentType.includes('text/')) {
      data = (await response.text()) as T;
    }

    return {
      data: data as T,
      status: response.status(),
      headers: response.headers(),
    };
  }

  async get<T>(
    path: string,
    params?: Record<string, string | number | boolean>,
  ): Promise<IResponse<T>> {
    return this.requestWrapper<T>({
      method: 'GET',
      path,
      params,
    });
  }

  async post<T>(path: string, body?: unknown): Promise<IResponse<T>> {
    return this.requestWrapper<T>({
      method: 'POST',
      path,
      body,
    });
  }

  async put<T>(path: string, body?: unknown): Promise<IResponse<T>> {
    return this.requestWrapper<T>({
      method: 'PUT',
      path,
      body,
    });
  }

  async patch<T>(path: string, body?: unknown): Promise<IResponse<T>> {
    return this.requestWrapper<T>({
      method: 'PATCH',
      path,
      body,
    });
  }

  async delete<T>(path: string): Promise<IResponse<T>> {
    return this.requestWrapper<T>({
      method: 'DELETE',
      path,
    });
  }

  protected async handleError(response: APIResponse): Promise<IApiError> {
    const statusCode = response.status();
    let message = 'Unknown error';
    let code = 'UNKNOWN_ERROR';
    let details: Record<string, unknown> | undefined;

    try {
      const body = await response.json();
      if (body && typeof body === 'object') {
        message = ((body as Record<string, unknown>).message as string) || message;
        code = ((body as Record<string, unknown>).code as string) || code;
        details = (body as Record<string, unknown>).details as Record<string, unknown> | undefined;
      }
    } catch {
      message = (await response.text()) || message;
    }

    return { message, code, statusCode, details };
  }

  protected assertSuccess<T>(response: IResponse<T>, expectedStatus: number = 200): void {
    if (response.status !== expectedStatus) {
      throw new Error(
        `Expected status ${expectedStatus}, but got ${response.status}. Response: ${JSON.stringify(response.data)}`,
      );
    }
  }

  protected assertStatus<T>(response: IResponse<T>, statuses: number[]): void {
    if (!statuses.includes(response.status)) {
      throw new Error(
        `Expected one of statuses [${statuses.join(', ')}], but got ${response.status}. Response: ${JSON.stringify(response.data)}`,
      );
    }
  }
}

export const testApi = base.extend<{ api: BaseApi }>({
  api: async ({ request }, use) => {
    const baseURL = process.env.API_BASE_URL || process.env.BASE_URL || 'http://localhost:3000';
    const api = new BaseApi(request, baseURL);
    await use(api);
  },
});
