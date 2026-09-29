import { BaseApi } from './base.api';
import {
  IUserResponse,
  IUsersListResponse,
  ICreateUserRequest,
  IUpdateUserRequest,
  IPaginationParams,
  IResponse,
} from '../types/api.types';

export class UsersApi extends BaseApi {
  async getUsers(params?: IPaginationParams): Promise<IResponse<IUsersListResponse>> {
    return this.get<IUsersListResponse>(
      '/api/users',
      params as Record<string, string | number | boolean>,
    );
  }

  async getUser(id: string): Promise<IResponse<IUserResponse>> {
    return this.get<IUserResponse>(`/api/users/${id}`);
  }

  async createUser(data: ICreateUserRequest): Promise<IResponse<IUserResponse>> {
    return this.post<IUserResponse>('/api/users', data);
  }

  async updateUser(id: string, data: IUpdateUserRequest): Promise<IResponse<IUserResponse>> {
    return this.patch<IUserResponse>(`/api/users/${id}`, data);
  }

  async deleteUser(id: string): Promise<IResponse<void>> {
    return this.delete<void>(`/api/users/${id}`);
  }

  async searchUsers(query: string): Promise<IResponse<IUsersListResponse>> {
    return this.get<IUsersListResponse>('/api/users/search', { q: query });
  }
}
