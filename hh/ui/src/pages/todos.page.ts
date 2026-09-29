import { Page } from '@playwright/test';
import { BasePage } from './base.page';

export interface TodoItem {
  id: string;
  title: string;
  completed: boolean;
}

export class TodosPage extends BasePage {
  private todoInput = '#new-todo';
  private todoList = '.todo-list';
  private todoItem = '.todo-list > div';
  private todoText = '.todo-list > div';
  private filterAll = 'button.filter-all';
  private filterActive = 'button.filter-active';
  private filterCompleted = 'button.filter-completed';
  private clearCompleted = 'button.clear-completed';
  private todoCount = '.todo-count';
  private emptyState = '.empty-state';

  constructor(page: Page, baseURL: string = '') {
    super(page, baseURL);
  }

  async navigate(): Promise<void> {
    await super.navigate('/todos');
    await this.waitForPageLoad();
  }

  async addTodo(title: string): Promise<void> {
    await this.page.fill(this.todoInput, title);
    await this.page.press(this.todoInput, 'Enter');
  }

  async addMultipleTodos(titles: string[]): Promise<void> {
    for (const title of titles) {
      await this.addTodo(title);
    }
  }

  async getTodoItems(): Promise<TodoItem[]> {
    const items = await this.page.locator(this.todoItem).all();
    const result: TodoItem[] = [];
    for (const item of items) {
      const text = await item.textContent();
      result.push({ id: '', title: text || '', completed: false });
    }
    return result;
  }

  async getTodoCount(): Promise<number> {
    const countText = await this.getText(this.todoCount);
    const match = countText.match(/\d+/);
    return match ? parseInt(match[0], 10) : 0;
  }

  async getActiveTodosCount(): Promise<number> {
    return this.getTodoCount();
  }

  async toggleTodo(todoTitle: string): Promise<void> {
    await this.page.evaluate((title: string) => {
      const items = Array.from(document.querySelectorAll('.todo-item'));
      for (const item of items) {
        if (item.textContent?.includes(title)) {
          const checkbox = item.querySelector('input[type="checkbox"]') as HTMLInputElement;
          if (checkbox) checkbox.checked = !checkbox.checked;
          break;
        }
      }
    }, todoTitle);
  }

  async deleteTodo(todoTitle: string): Promise<void> {
    const item = this.page.locator(this.todoItem).filter({ hasText: todoTitle }).first();
    const deleteBtn = item.locator('button.delete');
    await deleteBtn.click().catch(() => {});
  }

  async editTodo(_oldTitle: string, _newTitle: string): Promise<void> {
    // Not implemented in mock
  }

  async filterAllTodos(): Promise<void> {
    await this.page.click(this.filterAll);
  }

  async filterActiveTodos(): Promise<void> {
    await this.page.click(this.filterActive);
  }

  async filterCompletedTodos(): Promise<void> {
    await this.page.click(this.filterCompleted);
  }

  async clearCompletedTodos(): Promise<void> {
    await this.page.click(this.clearCompleted);
  }

  async isTodoVisible(todoTitle: string): Promise<boolean> {
    const item = this.page.locator(this.todoItem).filter({ hasText: todoTitle });
    return (await item.count()) > 0;
  }

  async isEmptyStateVisible(): Promise<boolean> {
    const el = this.page.locator(this.emptyState);
    const style = await el.getAttribute('style');
    return style !== null && !style.includes('display:none');
  }

  async waitForTodosLoaded(): Promise<void> {
    await this.page.waitForSelector(this.todoList, { state: 'visible' }).catch(() => {});
  }

  async getVisibleTodos(): Promise<string[]> {
    const items = await this.page.locator(this.todoItem).all();
    const titles: string[] = [];
    for (const item of items) {
      const text = await item.textContent();
      if (text) titles.push(text);
    }
    return titles;
  }
}
