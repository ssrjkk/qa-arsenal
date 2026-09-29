import { BaseApi } from './base.api';
import {
  IAuthLoginRequest,
  IAuthLoginResponse,
  IAuthRegisterRequest,
  IAuthRegisterResponse,
  IUserResponse,
  IResponse,
} from '../types/api.types';

export class AuthApi extends BaseApi {
  async login(credentials: IAuthLoginRequest): Promise<IResponse<IAuthLoginResponse>> {
    return this.post<IAuthLoginResponse>('/api/auth/login', credentials);
  }

  async register(data: IAuthRegisterRequest): Promise<IResponse<IAuthRegisterResponse>> {
    return this.post<IAuthRegisterResponse>('/api/auth/register', data);
  }

  async logout(): Promise<IResponse<void>> {
    return this.post<void>('/api/auth/logout');
  }

  async me(): Promise<IResponse<IUserResponse>> {
    return this.get<IUserResponse>('/api/auth/me');
  }

  async refreshToken(): Promise<IResponse<{ token: string }>> {
    return this.post<{ token: string }>('/api/auth/refresh');
  }

  async changePassword(oldPassword: string, newPassword: string): Promise<IResponse<void>> {
    return this.post<void>('/api/auth/change-password', { oldPassword, newPassword });
  }

  async requestPasswordReset(email: string): Promise<IResponse<{ message: string }>> {
    return this.post<{ message: string }>('/api/auth/reset-password', { email });
  }

  async verifyEmail(token: string): Promise<IResponse<{ message: string }>> {
    return this.post<{ message: string }>('/api/auth/verify-email', { token });
  }

  async resendVerificationEmail(): Promise<IResponse<{ message: string }>> {
    return this.post<{ message: string }>('/api/auth/resend-verification');
  }
}
