// static/js/cadastro.js

function togglePassword(inputId, iconElement) {
    const input = document.getElementById(inputId);
    if (input.type === "password") {
        input.type = "text";
        iconElement.classList.remove("bi-eye");
        iconElement.classList.add("bi-eye-slash");
    } else {
        input.type = "password";
        iconElement.classList.remove("bi-eye-slash");
        iconElement.classList.add("bi-eye");
    }
}