import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30_000,

  use: {
    baseURL: 'http://127.0.0.1:8000',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'retain-on-failure',
  },

  webServer: {
    command: 'python manage.py runserver 127.0.0.1:8000',
    url: 'http://127.0.0.1:8000/',
    reuseExistingServer: true,
    timeout: 120_000,
  },
});