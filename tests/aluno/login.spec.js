import { test, expect } from '@playwright/test';

test('o login de aluno funciona', async ({ page }) => {
  const email = `aluno.login.${Date.now()}@example.com`;
  const senha = 'senha1234';

  await page.goto('http://127.0.0.1:8000/cadastro/');
  await page.locator('input[name="nome"]').fill('Aluno Login');
  await page.locator('input[name="email"]').fill(email);
  await page.locator('select[name="escola"]').selectOption({ index: 1 });
  await page.locator('input[name="senha"]').fill(senha);
  await page.locator('input[name="confirmar_senha"]').fill(senha);
  await page.getByRole('button', { name: /Criar Conta/i }).click();

  await page.goto('http://127.0.0.1:8000/sair/');
  await page.goto('http://127.0.0.1:8000/login/');
  await page.waitForLoadState('domcontentloaded');
  await page.locator('input[name="email"]').fill(email);
  await page.locator('input[name="senha"]').fill(senha);
  await page.getByRole('button', { name: /Entrar na Plataforma/i }).click();

  await expect(page).toHaveURL(/dashboard|tcle/);
});
