import { IResponse } from '../types/api.types';

export interface ValidationRule {
  field: string;
  type: 'required' | 'string' | 'number' | 'boolean' | 'array' | 'object' | 'email' | 'enum';
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  enum?: string[];
  schema?: ValidationRule[];
}

export class ResponseValidator {
  static validateStructure<T>(response: IResponse<T>, rules: ValidationRule[]): void {
    const data = response.data as Record<string, unknown>;

    for (const rule of rules) {
      const value = data[rule.field];

      if (rule.required && (value === undefined || value === null)) {
        throw new Error(`Field '${rule.field}' is required but was ${value}`);
      }

      if (value !== undefined && value !== null) {
        this.validateType(rule.field, value, rule.type);

        if (rule.type === 'string') {
          if (rule.minLength && (value as string).length < rule.minLength) {
            throw new Error(`Field '${rule.field}' must be at least ${rule.minLength} characters`);
          }
          if (rule.maxLength && (value as string).length > rule.maxLength) {
            throw new Error(`Field '${rule.field}' must be at most ${rule.maxLength} characters`);
          }
          if (rule.pattern && !rule.pattern.test(value as string)) {
            throw new Error(`Field '${rule.field}' does not match required pattern`);
          }
        }

        if (rule.enum && !rule.enum.includes(value as string)) {
          throw new Error(`Field '${rule.field}' must be one of: ${rule.enum.join(', ')}`);
        }

        if (rule.type === 'array' && rule.schema && Array.isArray(value)) {
          for (let i = 0; i < value.length; i++) {
            this.validateObject(value[i], rule.schema, `${rule.field}[${i}]`);
          }
        }

        if (rule.type === 'object' && rule.schema) {
          this.validateObject(value as Record<string, unknown>, rule.schema, rule.field);
        }
      }
    }
  }

  private static validateType(field: string, value: unknown, type: string): void {
    switch (type) {
      case 'string':
        if (typeof value !== 'string') {
          throw new Error(`Field '${field}' must be a string, got ${typeof value}`);
        }
        break;
      case 'number':
        if (typeof value !== 'number') {
          throw new Error(`Field '${field}' must be a number, got ${typeof value}`);
        }
        break;
      case 'boolean':
        if (typeof value !== 'boolean') {
          throw new Error(`Field '${field}' must be a boolean, got ${typeof value}`);
        }
        break;
      case 'array':
        if (!Array.isArray(value)) {
          throw new Error(`Field '${field}' must be an array, got ${typeof value}`);
        }
        break;
      case 'object':
        if (typeof value !== 'object' || value === null || Array.isArray(value)) {
          throw new Error(`Field '${field}' must be an object, got ${typeof value}`);
        }
        break;
    }
  }

  private static validateObject(obj: unknown, rules: ValidationRule[], path: string): void {
    if (typeof obj !== 'object' || obj === null) {
      throw new Error(`Expected object at '${path}', got ${typeof obj}`);
    }

    const data = obj as Record<string, unknown>;
    for (const rule of rules) {
      const value = data[rule.field];
      if (rule.required && (value === undefined || value === null)) {
        throw new Error(`Field '${path}.${rule.field}' is required`);
      }
      if (value !== undefined && value !== null) {
        this.validateType(`${path}.${rule.field}`, value, rule.type);
      }
    }
  }

  static validateStatus(response: IResponse<unknown>, expectedStatus: number): void {
    if (response.status !== expectedStatus) {
      throw new Error(`Expected status ${expectedStatus}, got ${response.status}`);
    }
  }

  static validateStatusRange(response: IResponse<unknown>, min: number, max: number): void {
    if (response.status < min || response.status > max) {
      throw new Error(`Expected status between ${min}-${max}, got ${response.status}`);
    }
  }

  static validateContains<T>(response: IResponse<T>, key: string): void {
    const data = response.data as Record<string, unknown>;
    if (!(key in data)) {
      throw new Error(`Response does not contain expected key: ${key}`);
    }
  }

  static validateArrayNotEmpty<T>(response: IResponse<T>): void {
    const data = response.data as Record<string, unknown>;
    const arrayField = Object.values(data).find(Array.isArray);
    if (!arrayField || arrayField.length === 0) {
      throw new Error('Expected non-empty array in response');
    }
  }
}

export const userValidationRules: ValidationRule[] = [
  { field: 'id', type: 'string', required: true },
  { field: 'email', type: 'string', required: true },
  { field: 'name', type: 'string', required: true },
];

export const todoValidationRules: ValidationRule[] = [
  { field: 'id', type: 'string', required: true },
  { field: 'title', type: 'string', required: true },
  { field: 'completed', type: 'boolean', required: true },
  { field: 'userId', type: 'string', required: true },
];

export const authResponseRules: ValidationRule[] = [
  { field: 'token', type: 'string', required: true, minLength: 10 },
  { field: 'user', type: 'object', required: true, schema: userValidationRules },
];
