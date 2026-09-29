import { APIRequestContext } from '@playwright/test';
import { BaseApi } from './base.api';
import { AuthApi } from './auth.api';
import { UsersApi } from './users.api';
import { TodosApi } from './todos.api';

export interface IApiFactory {
  auth: AuthApi;
  users: UsersApi;
  todos: TodosApi;
  base: BaseApi;
}

export class ApiFactory {
  private _baseApi: BaseApi;
  private _authApi: AuthApi | null = null;
  private _usersApi: UsersApi | null = null;
  private _todosApi: TodosApi | null = null;

  constructor(request: APIRequestContext, baseURL: string) {
    this._baseApi = new BaseApi(request, baseURL);
  }

  get auth(): AuthApi {
    if (!this._authApi) {
      this._authApi = new AuthApi(this._baseApi.request, this._baseApi.baseURL);
      this._authApi.setToken(this._baseApi.getTokenValue() || '');
      this._authApi.setParent(this._baseApi);
    }
    return this._authApi;
  }

  get users(): UsersApi {
    if (!this._usersApi) {
      this._usersApi = new UsersApi(this._baseApi.request, this._baseApi.baseURL);
      this._usersApi.setToken(this._baseApi.getTokenValue() || '');
      this._usersApi.setParent(this._baseApi);
    }
    return this._usersApi;
  }

  get todos(): TodosApi {
    if (!this._todosApi) {
      this._todosApi = new TodosApi(this._baseApi.request, this._baseApi.baseURL);
      this._todosApi.setToken(this._baseApi.getTokenValue() || '');
      this._todosApi.setParent(this._baseApi);
    }
    return this._todosApi;
  }

  get base(): BaseApi {
    return this._baseApi;
  }
}

export const createApiFactory = (request: APIRequestContext, baseURL: string): IApiFactory => {
  const factory = new ApiFactory(request, baseURL);
  return {
    auth: factory.auth,
    users: factory.users,
    todos: factory.todos,
    base: factory.base,
  };
};
