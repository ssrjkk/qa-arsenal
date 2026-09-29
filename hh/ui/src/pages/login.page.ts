import { Page } from '@playwright/test';
import { BasePage } from './base.page';

export class LoginPage extends BasePage {
  private emailInput = 'input[name="email"]';
  private passwordInput = 'input[name="password"]';
  private submitButton = 'button[type="submit"]';
  private errorMessage = '.error-message';
  private linkToRegister = 'a[href="/register"]';

  constructor(page: Page, baseURL: string = '') {
    super(page, baseURL);
  }

  async navigate(): Promise<void> {
    await super.navigate('/login');
    await this.waitForPageLoad();
  }

  async fillEmail(email: string): Promise<void> {
    await this.page.fill(this.emailInput, email);
  }

  async fillPassword(password: string): Promise<void> {
    await this.page.fill(this.passwordInput, password);
  }

  async clickSubmit(): Promise<void> {
    await this.page.click(this.submitButton);
  }

  async login(email: string, password: string): Promise<void> {
    await this.fillEmail(email);
    await this.fillPassword(password);
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

  async clickRegisterLink(): Promise<void> {
    await this.clickElement(this.linkToRegister);
  }

  async isSubmitEnabled(): Promise<boolean> {
    const button = this.page.locator(this.submitButton);
    return button.isEnabled();
  }

  async waitForRedirectAfterLogin(timeout: number = 30000): Promise<void> {
    await this.page.waitForURL(/\/(dashboard|todos|home)/, { timeout }).catch(() => {});
  }
}
