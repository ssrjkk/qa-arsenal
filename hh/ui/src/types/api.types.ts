export interface IUser {
  id: string;
  email: string;
  name: string;
  password: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface ICreateUserRequest {
  email: string;
  name: string;
  password: string;
}

export interface IUpdateUserRequest {
  name?: string;
  email?: string;
  password?: string;
}

export interface IUserResponse {
  id: string;
  email: string;
  name: string;
  createdAt: string;
  updatedAt: string;
}

export interface IUsersListResponse {
  users: IUserResponse[];
  total: number;
  page: number;
  limit: number;
}

export interface IAuthLoginRequest {
  email: string;
  password: string;
}

export interface IAuthLoginResponse {
  token: string;
  user: IUserResponse;
  expiresAt: string;
}

export interface IAuthRegisterRequest {
  email: string;
  name: string;
  password: string;
}

export interface IAuthRegisterResponse {
  token: string;
  user: IUserResponse;
}

export interface ITodo {
  id: string;
  title: string;
  completed: boolean;
  userId: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface ICreateTodoRequest {
  title: string;
  completed?: boolean;
}

export interface IUpdateTodoRequest {
  title?: string;
  completed?: boolean;
}

export interface ITodoResponse {
  id: string;
  title: string;
  completed: boolean;
  userId: string;
  createdAt: string;
  updatedAt: string;
}

export interface ITodosListResponse {
  todos: ITodoResponse[];
  total: number;
  page: number;
  limit: number;
}

export interface IApiError {
  message: string;
  code: string;
  statusCode: number;
  details?: Record<string, unknown>;
}

export interface IApiResponse<T> {
  data?: T;
  error?: IApiError;
  statusCode: number;
}

export interface IPaginationParams {
  page?: number;
  limit?: number;
}

export interface IFilterParams {
  search?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export type ApiMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export interface IRequestConfig {
  method: ApiMethod;
  path: string;
  body?: unknown;
  params?: Record<string, string | number | boolean>;
  headers?: Record<string, string>;
}

export interface IResponse<T> {
  data: T;
  status: number;
  headers: Record<string, string>;
}

export interface IValidationError {
  field: string;
  message: string;
}

export interface IApiValidationResponse {
  message: string;
  errors: IValidationError[];
}
