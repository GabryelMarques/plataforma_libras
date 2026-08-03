// @ts-check
import { test, expect } from '@playwright/test';

test('a home da Plataforma Libras abre corretamente', async ({ page }) => {
  await page.goto('/');

  await expect(page).toHaveTitle(/Evolução em Libras/i);
  await expect(page.getByRole('heading', { name: /Aprenda/i })).toBeVisible();
});
