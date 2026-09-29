import { IResponse, IRequestConfig } from '../types/api.types';

export class Logger {
  private static isEnabled: boolean = process.env.ENABLE_LOGGING === 'true';

  static enable(): void {
    this.isEnabled = true;
  }

  static disable(): void {
    this.isEnabled = false;
  }

  static logRequest(config: IRequestConfig): void {
    if (!this.isEnabled) return;
    console.log(`📤 REQUEST: ${config.method} ${config.path}`);
    if (config.body) {
      console.log('   Body:', JSON.stringify(config.body, null, 2));
    }
    if (config.params) {
      console.log('   Params:', JSON.stringify(config.params, null, 2));
    }
  }

  static logResponse<T>(response: IResponse<T>): void {
    if (!this.isEnabled) return;
    console.log(`📥 RESPONSE: ${response.status}`);
    console.log('   Data:', JSON.stringify(response.data, null, 2));
  }

  static logError(error: Error): void {
    if (!this.isEnabled) return;
    console.error('❌ ERROR:', error.message);
  }

  static logTestStart(testName: string): void {
    if (!this.isEnabled) return;
    console.log(`\n🧪 START: ${testName}`);
  }

  static logTestEnd(testName: string, status: 'passed' | 'failed'): void {
    if (!this.isEnabled) return;
    const icon = status === 'passed' ? '✅' : '❌';
    console.log(`${icon} END: ${testName}\n`);
  }

  static logStep(step: string): void {
    if (!this.isEnabled) return;
    console.log(`   → ${step}`);
  }

  static logInfo(message: string): void {
    if (!this.isEnabled) return;
    console.log(`ℹ️  ${message}`);
  }
}

export const createStepLogger = (testName: string) => {
  let stepCount = 0;
  return {
    step: (action: string) => {
      stepCount++;
      Logger.logStep(`[${stepCount}] ${action}`);
    },
    start: () => Logger.logTestStart(testName),
    end: (status: 'passed' | 'failed') => Logger.logTestEnd(testName, status),
  };
};
