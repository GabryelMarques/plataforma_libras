import { test, expect } from '@playwright/test';

test('administrador consegue criar um novo modulo', async ({ page }) => {
  // 1. Fazer o Login
  await page.goto('http://127.0.0.1:8000/sair/');
  await page.goto('http://127.0.0.1:8000/login/');
  await page.locator('input[name="email"]').fill('grobo@teste.com');
  await page.locator('input[name="senha"]').fill('SenhaFalsa123.');
  await page.getByRole('button', { name: /Entrar na Plataforma/i }).click();

  // ---> A MÁGICA DA CORREÇÃO AQUI <---
  // Faz o robô esperar o Django carregar a dashboard (confirmando que logou)
  await expect(page).toHaveURL(/painel|dashboard|admin|gestao/);

  // 2. Ir direto para a rota de criação de módulo
  await page.goto('http://127.0.0.1:8000/criar-modulo/');

  // 3. Preencher o formulário
  const tituloModulo = 'Módulo Playwright ' + Date.now(); 
  
  await page.locator('input[name="titulo"]').fill(tituloModulo);
  await page.locator('textarea[name="descricao"]').fill('Módulo criado através de automação de testes do Playwright.');
  await page.locator('input[name="ordem"]').fill('99');
  
  // 4. Clicar em salvar
  await page.getByRole('button', { name: /Salvar|Criar/i }).click();

// 5. Verificações de sucesso
  await expect(page).toHaveURL(/gestao-modulos/);
  
  // ---> A CORREÇÃO AQUI <---
  // Usamos .first() para o Playwright não reclamar se achar o nome também dentro do modal de excluir
  await expect(page.getByText(tituloModulo).first()).toBeVisible();
});
