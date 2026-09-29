import { test as base, Page, APIRequestContext } from '@playwright/test';
import { createApiFactory, IApiFactory } from '../api/api.factory';
import { DataFactory, IUserData, ITodoData } from '../data/data.factory';
import { IUser } from '../types/api.types';

export interface TestUser {
  user: IUserData;
  token: string;
}

export interface TestData {
  users: IUserData[];
  todos: ITodoData[];
}

export interface AuthenticatedUser {
  user: IUser;
  token: string;
}

export interface PageFixtures {
  page: Page;
}

export interface ApiFixtures {
  request: APIRequestContext;
}

interface TestDataFixtures {
  uniqueUser: IUserData;
  uniqueTodo: ITodoData;
}

interface AuthFixtures {
  testUser: TestUser;
  authenticatedUser: AuthenticatedUser;
  api: IApiFactory;
}

export const testDataFixture = base.extend<TestDataFixtures>({
  uniqueUser: async (_params, use) => {
    const user = DataFactory.generateUser();
    await use(user);
  },

  uniqueTodo: async (_params, use) => {
    const todo = DataFactory.generateTodo();
    await use(todo);
  },
});

export const authFixture = base.extend<AuthFixtures>({
  testUser: async ({ api }, use) => {
    const user = DataFactory.generateUser();
    const response = await api.auth.register({
      email: user.email,
      name: user.name,
      password: user.password,
    });

    if (response.status === 201 || response.status === 200) {
      await use({
        user,
        token: response.data?.token || '',
      });
    } else {
      await use({
        user,
        token: '',
      });
    }
  },

  authenticatedUser: async ({ api }, use) => {
    const user = DataFactory.generateUser();
    await api.auth.register({
      email: user.email,
      name: user.name,
      password: user.password,
    });

    const loginResponse = await api.auth.login({
      email: user.email,
      password: user.password,
    });

    const token = loginResponse.data?.token || '';
    api.base.setToken(token);

    await use({
      user: {
        id: 'test-id',
        email: user.email,
        name: user.name,
        password: user.password,
      },
      token,
    });
  },
});

export interface ApiFixtureType {
  api: IApiFactory;
  page: Page;
  request: APIRequestContext;
}

export const apiFixture = base.extend<{ api: IApiFactory }>({
  api: async ({ request }, use) => {
    const baseURL = process.env.API_BASE_URL || process.env.BASE_URL || 'http://localhost:3000';
    const apiFactory = createApiFactory(request, baseURL);
    await use(apiFactory);
  },
});

export { Page, APIRequestContext };
