import { test, expect } from '@playwright/test';

test('Jornada do Aluno: responder pré-teste', async ({ page }) => {
  // ==========================================
  // 1. FAZER LOGIN (Direto pra Dashboard)
  // ==========================================
  await page.goto('http://127.0.0.1:8000/sair/');
  await page.goto('http://127.0.0.1:8000/login/');
  
  // ATENÇÃO: Coloque aqui o email e senha daquele aluno que você já aceitou o TCLE manualmente
  await page.locator('input[name="email"]').fill('aluno@teste.com'); 
  await page.locator('input[name="senha"]').fill('senha_do_aluno_123'); 
  await page.getByRole('button', { name: /Entrar na Plataforma/i }).click();

  // Agora ele vai direto pra Dashboard sem frescura!
  await expect(page).toHaveURL(/dashboard/);

  // ==========================================
  // 2. ENTRAR NO PRÉ-TESTE
  // ==========================================
  await page.getByRole('link', { name: 'Iniciar Pré-teste Agora' }).click();
  await expect(page).toHaveURL(/atividade/);

  // ==========================================
  // 3. RESPONDER O PRÉ-TESTE
  // ==========================================
  const primeiraAlternativa = page.locator('input[type="radio"]').first();
  if (await primeiraAlternativa.isVisible()) {
      await primeiraAlternativa.check();
  }

  await page.getByRole('button', { name: /Enviar|Finalizar|Responder/i }).first().click();

  // ---> PAUSA PARA INVESTIGAÇÃO <---
  // O robô vai parar aqui para você olhar na tela por que o sistema não deixou enviar a prova!
  await page.pause(); 

  await expect(page).not.toHaveURL(/atividade/);
});