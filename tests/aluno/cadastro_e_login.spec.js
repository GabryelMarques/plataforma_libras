import { test, expect } from '@playwright/test';

test('um novo aluno consegue se cadastrar e entrar na plataforma', async ({ page }) => {
  const email = `aluno.playwright.${Date.now()}@example.com`;

  await page.goto('/cadastro/');
  await page.locator('input[name="nome"]').fill('Aluno Playwright');
  await page.locator('input[name="email"]').fill(email);
  await page.locator('select[name="escola"]').selectOption({ index: 1 });
  await page.locator('input[name="senha"]').fill('senha1234');
  await page.locator('input[name="confirmar_senha"]').fill('senha1234');
  await page.getByRole('button', { name: /Criar Conta/i }).click();

  await expect(page).toHaveURL(/dashboard|tcle/);
});
