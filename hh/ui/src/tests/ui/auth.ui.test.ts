import { test as base, expect } from '@playwright/test';
import { LoginPage, RegisterPage, TodosPage } from '../../pages';
import { DataFactory } from '../../data/data.factory';

const uiTest = base.extend<{
  loginPage: LoginPage;
  registerPage: RegisterPage;
  todosPage: TodosPage;
}>({
  loginPage: async ({ page }, use) => {
    const baseURL = process.env.BASE_URL || 'http://localhost:3000';
    await use(new LoginPage(page, baseURL));
  },
  registerPage: async ({ page }, use) => {
    const baseURL = process.env.BASE_URL || 'http://localhost:3000';
    await use(new RegisterPage(page, baseURL));
  },
  todosPage: async ({ page }, use) => {
    const baseURL = process.env.BASE_URL || 'http://localhost:3000';
    await use(new TodosPage(page, baseURL));
  },
});

uiTest.describe('UI: Auth', () => {
  uiTest('@smoke @critical should register new user @e2e', async ({ registerPage }) => {
    const user = DataFactory.generateUser();

    await registerPage.navigate();
    await registerPage.register(user.name, user.email, user.password);
  });

  uiTest(
    '@smoke @critical should login with valid credentials @e2e',
    async ({ loginPage, registerPage }) => {
      const user = DataFactory.generateUser();

      await registerPage.navigate();
      await registerPage.register(user.name, user.email, user.password);
      await registerPage.page.waitForTimeout(500);

      await loginPage.navigate();
      await loginPage.login(user.email, user.password);
    },
  );

  uiTest('@regression should show error for invalid credentials @e2e', async ({ loginPage }) => {
    await loginPage.navigate();
    await loginPage.login('invalid@test.com', 'wrongpassword');
  });

  uiTest('@regression should navigate to register page @e2e', async ({ loginPage }) => {
    await loginPage.navigate();
    await loginPage.clickRegisterLink();

    await expect(loginPage.page).toHaveURL(/register/);
  });
});

uiTest.describe('UI: Todos', () => {
  uiTest('@smoke @critical should add new todo @e2e', async ({ todosPage }) => {
    await todosPage.navigate();
    const todo = DataFactory.generateTodo();

    await todosPage.addTodo(todo.title);
  });

  uiTest('@smoke should add multiple todos @e2e', async ({ todosPage }) => {
    await todosPage.navigate();
    const todos = DataFactory.generateMultipleTodos(3);

    for (const todo of todos) {
      await todosPage.addTodo(todo.title);
    }
  });

  uiTest('@regression should toggle todo completion @e2e', async ({ todosPage }) => {
    await todosPage.navigate();
    const todo = DataFactory.generateTodo();

    await todosPage.addTodo(todo.title);
    await todosPage.toggleTodo(todo.title);
  });

  uiTest('@regression should delete todo @e2e', async ({ todosPage }) => {
    await todosPage.navigate();
    const todo = DataFactory.generateTodo();

    await todosPage.addTodo(todo.title);
    await todosPage.deleteTodo(todo.title);
  });

  uiTest('@regression should filter todos @e2e', async ({ todosPage }) => {
    await todosPage.navigate();

    const todo1 = DataFactory.generateTodo();
    const todo2 = DataFactory.generateTodo();

    await todosPage.addTodo(todo1.title);
    await todosPage.addTodo(todo2.title);
    await todosPage.toggleTodo(todo2.title);

    await todosPage.filterCompletedTodos();
    await todosPage.filterActiveTodos();
  });

  uiTest('@regression should clear completed todos @e2e', async ({ todosPage }) => {
    await todosPage.navigate();

    const todo = DataFactory.generateTodo();
    await todosPage.addTodo(todo.title);
    await todosPage.toggleTodo(todo.title);

    await todosPage.clearCompletedTodos();
  });
});

export { uiTest };
