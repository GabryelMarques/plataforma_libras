/* ============================================== */
/* MÁGICA DA NAVEGAÇÃO DO QUIZ / MOTOR DE TESTES  */
/* ============================================== */

document.addEventListener("DOMContentLoaded", function() {
    const steps = document.querySelectorAll('.question-step');
    if (steps.length === 0) return;

    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');
    const btnSubmit = document.getElementById('btn-submit');
    const progressText = document.getElementById('progress-text');
    const progressBar = document.getElementById('progress-bar');
    const avisoErro = document.getElementById('aviso-erro'); 
    const form = document.getElementById('quiz-form');
    
    let currentStep = 0;
    const totalSteps = steps.length;

    // Esconde o aviso de erro
    function esconderErro() {
        if (avisoErro) avisoErro.style.display = 'none';
    }

    // Mostra o aviso de erro
    function mostrarErro() {
        if (avisoErro) {
            avisoErro.style.display = 'flex';
            // Dá uma tremidinha na caixa para chamar atenção
            avisoErro.animate([
                { transform: 'translateX(0px)' },
                { transform: 'translateX(-5px)' },
                { transform: 'translateX(5px)' },
                { transform: 'translateX(0px)' }
            ], { duration: 300 });
        }
    }

    function updateUI() {
        steps.forEach((step, index) => {
            step.style.display = index === currentStep ? 'block' : 'none';
        });

        if (progressText) progressText.innerText = `Questão ${currentStep + 1} de ${totalSteps}`;
        if (progressBar) progressBar.style.width = `${((currentStep + 1) / totalSteps) * 100}%`;

        if (btnPrev) btnPrev.style.visibility = currentStep > 0 ? 'visible' : 'hidden';

        if (currentStep === totalSteps - 1) {
            if (btnNext) btnNext.style.display = 'none';
            if (btnSubmit) btnSubmit.style.display = 'block';
        } else {
            if (btnNext) btnNext.style.display = 'block';
            if (btnSubmit) btnSubmit.style.display = 'none';
        }
    }

    function validateCurrentStep() {
        const currentQuestion = steps[currentStep];
        const radioInputs = currentQuestion.querySelectorAll('input[type="radio"]');
        const selectInputs = currentQuestion.querySelectorAll('select');
        let isValid = true;

        if (radioInputs.length > 0) {
            const isChecked = currentQuestion.querySelector('input[type="radio"]:checked');
            if (!isChecked) isValid = false;
        }

        if (selectInputs.length > 0) {
            selectInputs.forEach(select => {
                if (select.value === "") isValid = false;
            });
        }

        if (!isValid) {
            mostrarErro();
        } else {
            esconderErro();
        }
        return isValid;
    }

    // Lógica do botão Próxima
    if (btnNext) {
        btnNext.addEventListener('click', function() {
            if (validateCurrentStep()) {
                currentStep++;
                updateUI();
                window.scrollTo(0, 0);
            }
        });
    }

    // Lógica do botão Finalizar
    if (btnSubmit) {
        btnSubmit.addEventListener('click', function(e) {
            if (!validateCurrentStep()) {
                e.preventDefault(); 
            } else {
                form.submit(); 
            }
        });
    }

    // Lógica do botão Anterior
    if (btnPrev) {
        btnPrev.addEventListener('click', function() {
            esconderErro();
            currentStep--;
            updateUI();
            window.scrollTo(0, 0);
        });
    }

    // Esconde o erro automaticamente se o aluno preencher
    document.querySelectorAll('input[type="radio"], select').forEach(input => {
        input.addEventListener('change', esconderErro);
    });

    updateUI();
});