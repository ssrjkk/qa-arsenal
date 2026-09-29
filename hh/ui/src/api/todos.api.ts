import { BaseApi } from './base.api';
import {
  ITodoResponse,
  ITodosListResponse,
  ICreateTodoRequest,
  IUpdateTodoRequest,
  IPaginationParams,
  IResponse,
} from '../types/api.types';

export class TodosApi extends BaseApi {
  async getTodos(params?: IPaginationParams): Promise<IResponse<ITodosListResponse>> {
    return this.get<ITodosListResponse>(
      '/api/todos',
      params as Record<string, string | number | boolean>,
    );
  }

  async getTodo(id: string): Promise<IResponse<ITodoResponse>> {
    return this.get<ITodoResponse>(`/api/todos/${id}`);
  }

  async createTodo(data: ICreateTodoRequest): Promise<IResponse<ITodoResponse>> {
    return this.post<ITodoResponse>('/api/todos', data);
  }

  async updateTodo(id: string, data: IUpdateTodoRequest): Promise<IResponse<ITodoResponse>> {
    return this.patch<ITodoResponse>(`/api/todos/${id}`, data);
  }

  async deleteTodo(id: string): Promise<IResponse<void>> {
    return this.delete<void>(`/api/todos/${id}`);
  }

  async toggleTodo(id: string): Promise<IResponse<ITodoResponse>> {
    return this.post<ITodoResponse>(`/api/todos/${id}/toggle`);
  }

  async getUserTodos(
    userId: string,
    params?: IPaginationParams,
  ): Promise<IResponse<ITodosListResponse>> {
    return this.get<ITodosListResponse>(
      `/api/users/${userId}/todos`,
      params as Record<string, string | number | boolean>,
    );
  }

  async deleteCompletedTodos(): Promise<IResponse<{ deleted: number }>> {
    return this.delete<{ deleted: number }>('/api/todos/completed');
  }
}
