import { describe, expect, it } from 'vitest';
import { TodosApi } from '../api/todos.api';
import { makeRequest } from './test-utils';

function makeApi() {
  const request = makeRequest(200, { items: [], total: 0 });
  const api = new TodosApi(request.asApiRequestContext(), 'https://api.example');
  return { api, request };
}

describe('TodosApi', () => {
  it('getTodos calls GET /api/todos with params', async () => {
    const { api, request } = makeApi();
    await api.getTodos({ page: 1, limit: 20 });
    const call = request.calls[0];
    expect(call.opts.method).toBe('GET');
    expect(call.url).toContain('/api/todos');
    expect(call.url).toContain('page=1');
    expect(call.url).toContain('limit=20');
  });

  it('getTodo calls GET /api/todos/:id', async () => {
    const { api, request } = makeApi();
    await api.getTodo('42');
    expect(request.calls[0].opts.method).toBe('GET');
    expect(request.calls[0].url).toContain('/api/todos/42');
  });

  it('createTodo calls POST with body', async () => {
    const { api, request } = makeApi();
    await api.createTodo({ title: 'buy milk', completed: false });
    const call = request.calls[0];
    expect(call.opts.method).toBe('POST');
    expect(call.opts.data).toBe(JSON.stringify({ title: 'buy milk', completed: false }));
  });

  it('updateTodo calls PATCH with body', async () => {
    const { api, request } = makeApi();
    await api.updateTodo('1', { title: 'new' });
    expect(request.calls[0].opts.method).toBe('PATCH');
    expect(request.calls[0].url).toContain('/api/todos/1');
  });

  it('deleteTodo calls DELETE', async () => {
    const { api, request } = makeApi();
    await api.deleteTodo('7');
    expect(request.calls[0].opts.method).toBe('DELETE');
    expect(request.calls[0].url).toContain('/api/todos/7');
  });

  it('toggleTodo posts to /toggle', async () => {
    const { api, request } = makeApi();
    await api.toggleTodo('3');
    expect(request.calls[0].opts.method).toBe('POST');
    expect(request.calls[0].url).toContain('/api/todos/3/toggle');
  });

  it('getUserTodos hits the user-scoped path', async () => {
    const { api, request } = makeApi();
    await api.getUserTodos('u1');
    expect(request.calls[0].url).toContain('/api/users/u1/todos');
  });

  it('deleteCompletedTodos hits the completed path', async () => {
    const { api, request } = makeApi();
    await api.deleteCompletedTodos();
    expect(request.calls[0].opts.method).toBe('DELETE');
    expect(request.calls[0].url).toContain('/api/todos/completed');
  });
});