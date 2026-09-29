import { test as base, expect, APIRequestContext } from '@playwright/test';
import { createApiFactory, IApiFactory } from './api/api.factory';
import { DataFactory } from './data/data.factory';
import { ResponseValidator } from './helpers/response.validator';

const apiTest = base.extend<{ api: IApiFactory }>({
  api: async ({ request }, use) => {
    const baseURL = process.env.API_BASE_URL || process.env.BASE_URL || 'http://localhost:3000';
    const apiFactory = createApiFactory(request, baseURL);
    await use(apiFactory);
  },
});

export { expect, apiTest };
export { DataFactory, ResponseValidator };

export type { APIRequestContext };
export type { IApiFactory } from './api/api.factory';
