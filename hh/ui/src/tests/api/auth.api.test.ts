import { apiTest, expect, DataFactory, ResponseValidator } from '../../test.setup';
import { userValidationRules, authResponseRules } from '../../helpers/response.validator';

apiTest.describe('API: Auth', () => {
  apiTest.beforeEach(async ({ api }) => {
    api.base.clearToken();
  });

  apiTest('@smoke @critical should register new user @api', async ({ api }) => {
    const user = DataFactory.generateUser();

    const response = await api.auth.register({
      email: user.email,
      name: user.name,
      password: user.password,
    });

    expect(response.status).toBe(201);
    ResponseValidator.validateStructure(response, authResponseRules);
    expect(response.data?.token).toBeDefined();
  });

  apiTest('@smoke @critical should login with valid credentials @api', async ({ api }) => {
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

    expect(loginResponse.status).toBe(200);
    ResponseValidator.validateStructure(loginResponse, authResponseRules);
  });

  apiTest('@regression should not login with invalid password @api', async ({ api }) => {
    const user = DataFactory.generateUser();

    await api.auth.register({
      email: user.email,
      name: user.name,
      password: user.password,
    });

    const response = await api.auth.login({
      email: user.email,
      password: 'wrongpassword123',
    });

    expect(response.status).toBe(401);
  });

  apiTest('@regression should not register with existing email @api', async ({ api }) => {
    const user = DataFactory.generateUser();

    await api.auth.register({
      email: user.email,
      name: user.name,
      password: user.password,
    });

    const response = await api.auth.register({
      email: user.email,
      name: user.name,
      password: user.password,
    });

    expect(response.status).toBe(400);
  });

  apiTest('@regression should not login with non-existent email @api', async ({ api }) => {
    const user = DataFactory.generateUser();

    const response = await api.auth.login({
      email: user.email,
      password: user.password,
    });

    expect(response.status).toBe(401);
  });

  apiTest('@smoke should get current user info when authenticated @api', async ({ api }) => {
    const user = DataFactory.generateUser();

    const registerResponse = await api.auth.register({
      email: user.email,
      name: user.name,
      password: user.password,
    });

    const token = registerResponse.data?.token;
    api.base.setToken(token || '');

    const response = await api.auth.me();

    expect(response.status).toBe(200);
    ResponseValidator.validateStructure(response, userValidationRules);
  });

  apiTest('@regression should not get user info when not authenticated @api', async ({ api }) => {
    const response = await api.auth.me();

    expect(response.status).toBe(401);
  });
});

apiTest.describe('API: Todos', () => {
  let authToken: string;
  let testUser: { email: string; password: string };

  apiTest.beforeEach(async ({ api }) => {
    testUser = DataFactory.generateUser();
    const registerResponse = await api.auth.register({
      email: testUser.email,
      name: 'Test User',
      password: testUser.password,
    });
    authToken = registerResponse.data?.token || '';
    api.base.setToken(authToken);
  });

  apiTest('@smoke @critical should create new todo @api', async ({ api }) => {
    const todo = DataFactory.generateTodo();

    const response = await api.todos.createTodo({
      title: todo.title,
      completed: todo.completed,
    });

    expect(response.status).toBe(201);
    expect(response.data?.title).toBe(todo.title);
    expect(response.data?.completed).toBe(false);
  });

  apiTest('@regression should get all todos for user @api', async ({ api }) => {
    const todo1 = DataFactory.generateTodo();
    const todo2 = DataFactory.generateTodo();

    await api.todos.createTodo({ title: todo1.title });
    await api.todos.createTodo({ title: todo2.title });

    const response = await api.todos.getTodos();

    expect(response.status).toBe(200);
    expect(response.data?.todos).toBeDefined();
    expect(response.data?.todos.length).toBeGreaterThanOrEqual(2);
  });

  apiTest('@regression should update todo @api', async ({ api }) => {
    const todo = DataFactory.generateTodo();

    const createResponse = await api.todos.createTodo({ title: todo.title });
    const todoId = createResponse.data?.id;

    const updateResponse = await api.todos.updateTodo(todoId!, {
      title: 'Updated Title',
      completed: true,
    });

    expect(updateResponse.status).toBe(200);
    expect(updateResponse.data?.title).toBe('Updated Title');
    expect(updateResponse.data?.completed).toBe(true);
  });

  apiTest('@regression should delete todo @api', async ({ api }) => {
    const todo = DataFactory.generateTodo();

    const createResponse = await api.todos.createTodo({ title: todo.title });
    const todoId = createResponse.data?.id;

    const deleteResponse = await api.todos.deleteTodo(todoId!);

    expect(deleteResponse.status).toBe(204);
  });

  apiTest('@regression should toggle todo completion @api', async ({ api }) => {
    const todo = DataFactory.generateTodo();

    const createResponse = await api.todos.createTodo({ title: todo.title });
    const todoId = createResponse.data?.id;

    const toggleResponse = await api.todos.toggleTodo(todoId!);

    expect(toggleResponse.status).toBe(200);
  });
});

apiTest.describe('API: Validation', () => {
  apiTest('@regression should return 400 for invalid email format @api', async ({ api }) => {
    const user = DataFactory.generateUser();
    user.email = DataFactory.generateInvalidEmail();

    const response = await api.auth.register({
      email: user.email,
      name: user.name,
      password: user.password,
    });

    expect(response.status).toBe(400);
  });

  apiTest('@regression should return 400 for weak password @api', async ({ api }) => {
    const user = DataFactory.generateUser();
    user.password = DataFactory.generateWeakPassword();

    const response = await api.auth.register({
      email: user.email,
      name: user.name,
      password: user.password,
    });

    expect(response.status).toBe(400);
  });

  apiTest('@regression should return 422 for missing required fields @api', async ({ api }) => {
    const response = await api.auth.register({
      email: 'test@test.com',
      name: 'Test',
      password: '',
    });

    expect(response.status).toBe(422);
  });
});
