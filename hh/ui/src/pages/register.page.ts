import { Page } from '@playwright/test';
import { BasePage } from './base.page';

export class RegisterPage extends BasePage {
  private nameInput = 'input[name="name"]';
  private emailInput = 'input[name="email"]';
  private passwordInput = 'input[name="password"]';
  private confirmPasswordInput = 'input[name="confirmPassword"]';
  private submitButton = 'button[type="submit"]';
  private errorMessage = '.error-message';
  private successMessage = '.success-message';
  private linkToLogin = 'a[href="/login"]';

  constructor(page: Page, baseURL: string = '') {
    super(page, baseURL);
  }

  async navigate(): Promise<void> {
    await super.navigate('/register');
    await this.waitForPageLoad();
  }

  async fillName(name: string): Promise<void> {
    await this.page.fill(this.nameInput, name);
  }

  async fillEmail(email: string): Promise<void> {
    await this.page.fill(this.emailInput, email);
  }

  async fillPassword(password: string): Promise<void> {
    await this.page.fill(this.passwordInput, password);
  }

  async fillConfirmPassword(password: string): Promise<void> {
    await this.page.fill(this.confirmPasswordInput, password);
  }

  async clickSubmit(): Promise<void> {
    await this.page.click(this.submitButton);
  }

  async register(name: string, email: string, password: string): Promise<void> {
    await this.fillName(name);
    await this.fillEmail(email);
    await this.fillPassword(password);
    await this.fillConfirmPassword(password);
    await this.clickSubmit();
  }

  async getErrorMessage(): Promise<string> {
    return this.getText(this.errorMessage);
  }

  async isErrorVisible(): Promise<boolean> {
    const el = this.page.locator(this.errorMessage);
    const style = await el.getAttribute('style');
    return style !== null && !style.includes('display:none');
  }

  async isSuccessVisible(): Promise<boolean> {
    const el = this.page.locator(this.successMessage);
    const style = await el.getAttribute('style');
    return style !== null && !style.includes('display:none');
  }

  async clickLoginLink(): Promise<void> {
    await this.clickElement(this.linkToLogin);
  }

  async isSubmitEnabled(): Promise<boolean> {
    const button = this.page.locator(this.submitButton);
    return button.isEnabled();
  }
}
