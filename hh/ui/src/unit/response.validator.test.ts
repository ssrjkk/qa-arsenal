import { describe, expect, it } from 'vitest';
import {
  ResponseValidator,
  authResponseRules,
  todoValidationRules,
} from '../helpers/response.validator';

function response(status: number, data: unknown) {
  return { status, data } as any;
}

describe('ResponseValidator.validateStructure', () => {
  it('passes a valid todo', () => {
    expect(() =>
      ResponseValidator.validateStructure(
        response(200, { id: '1', title: 'buy milk', completed: false, userId: 'u1' }),
        todoValidationRules
      )
    ).not.toThrow();
  });

  it('throws when a required field is missing', () => {
    expect(() =>
      ResponseValidator.validateStructure(response(200, { id: '1', title: 'x' }), todoValidationRules)
    ).toThrow(/required/);
  });

  it('throws on wrong type', () => {
    expect(() =>
      ResponseValidator.validateStructure(
        response(200, { id: '1', title: 'x', completed: 'yes', userId: 'u1' }),
        todoValidationRules
      )
    ).toThrow(/boolean/);
  });

  it('enforces minLength on strings', () => {
    expect(() =>
      ResponseValidator.validateStructure(
        response(200, { token: 'short', user: { id: '1', email: 'a@b.c', name: 'n' } }),
        authResponseRules
      )
    ).toThrow(/at least 10/);
  });
});

describe('ResponseValidator.validateStatus', () => {
  it('accepts the expected status', () => {
    expect(() => ResponseValidator.validateStatus(response(200, {}), 200)).not.toThrow();
  });

  it('rejects a mismatched status', () => {
    expect(() => ResponseValidator.validateStatus(response(404, {}), 200)).toThrow(/Expected status 200/);
  });
});

describe('ResponseValidator.validateStatusRange', () => {
  it('accepts a status inside the range', () => {
    expect(() => ResponseValidator.validateStatusRange(response(201, {}), 200, 299)).not.toThrow();
  });

  it('rejects a status outside the range', () => {
    expect(() => ResponseValidator.validateStatusRange(response(500, {}), 200, 299)).toThrow(/between 200-299/);
  });
});

describe('ResponseValidator.validateContains', () => {
  it('passes when the key exists', () => {
    expect(() => ResponseValidator.validateContains(response(200, { items: [] }), 'items')).not.toThrow();
  });

  it('throws when the key is missing', () => {
    expect(() => ResponseValidator.validateContains(response(200, {}), 'items')).toThrow(/items/);
  });
});

describe('ResponseValidator.validateArrayNotEmpty', () => {
  it('passes with a non-empty array', () => {
    expect(() =>
      ResponseValidator.validateArrayNotEmpty(response(200, { items: [1, 2, 3] }))
    ).not.toThrow();
  });

  it('throws when no non-empty array is present', () => {
    expect(() =>
      ResponseValidator.validateArrayNotEmpty(response(200, { items: [] }))
    ).toThrow(/non-empty array/);
  });
});