import { test, expect } from '@playwright/test';

test('administrador consegue acessar o painel', async ({ page }) => {
  await page.goto('http://127.0.0.1:8000/sair/');
  await page.goto('http://127.0.0.1:8000/login/');

  await page.locator('input[name="email"]').fill('gabryelmarques17@gmail.com');
  await page.locator('input[name="senha"]').fill('Mark6025@');
  await page.getByRole('button', { name: /Entrar na Plataforma/i }).click();

  await expect(page).toHaveURL(/painel|dashboard|admin/);
});
