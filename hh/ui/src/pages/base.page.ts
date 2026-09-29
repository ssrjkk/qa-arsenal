import { Page, Locator, FrameLocator } from '@playwright/test';

export class BasePage {
  public page: Page;
  protected baseURL: string;

  constructor(page: Page, baseURL: string = '') {
    this.page = page;
    this.baseURL = baseURL;
  }

  async navigate(path: string = ''): Promise<void> {
    const url = this.baseURL ? `${this.baseURL}${path}` : path;
    await this.page.goto(url);
  }

  async waitForPageLoad(): Promise<void> {
    await this.page.waitForLoadState('domcontentloaded');
  }

  async waitForNetworkIdle(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
  }

  async getTitle(): Promise<string> {
    return this.page.title();
  }

  async getCurrentUrl(): Promise<string> {
    return this.page.url();
  }

  async reload(): Promise<void> {
    await this.page.reload();
  }

  async goBack(): Promise<void> {
    await this.page.goBack();
  }

  async goForward(): Promise<void> {
    await this.page.goForward();
  }

  protected async clickElement(selector: string): Promise<void> {
    await this.page.click(selector);
  }

  protected async fillInput(selector: string, value: string): Promise<void> {
    await this.page.fill(selector, value);
  }

  protected async getText(selector: string): Promise<string> {
    return (await this.page.textContent(selector)) ?? '';
  }

  protected async isVisible(selector: string): Promise<boolean> {
    return this.page.isVisible(selector);
  }

  protected async isHidden(selector: string): Promise<boolean> {
    return this.page.isHidden(selector);
  }

  protected async waitForSelector(
    selector: string,
    _options?: { state?: 'visible' | 'hidden' | 'attached'; timeout?: number },
  ): Promise<Locator> {
    return this.page.locator(selector).first();
  }

  protected getLocator(selector: string): Locator {
    return this.page.locator(selector);
  }

  protected getFrameLocator(frameSelector: string): FrameLocator {
    return this.page.frameLocator(frameSelector);
  }

  async waitForResponse(
    urlPattern: string | RegExp,
    options?: { timeout?: number },
  ): Promise<void> {
    await this.page.waitForResponse(urlPattern, options);
  }

  async waitForRequest(urlPattern: string | RegExp, options?: { timeout?: number }): Promise<void> {
    await this.page.waitForRequest(urlPattern, options);
  }
}
