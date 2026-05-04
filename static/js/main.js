document.addEventListener('DOMContentLoaded', () => {

    const loginTab = document.getElementById('loginTab');
    const registerTab = document.getElementById('registerTab');
    const authModal = document.getElementById('authModal');

    if (loginTab) loginTab.addEventListener('change', switchForm);
    if (registerTab) registerTab.addEventListener('change', switchForm);

    if (authModal) {
        authModal.addEventListener('click', function (e) {
            if (e.target === this) closeModal();
        });
    }

    // LOGIN
    const loginForm = document.getElementById('loginForm');

    if (loginForm) {
        loginForm.onsubmit = async (e) => {
            e.preventDefault();

            let formData = new FormData(loginForm);

            let res = await fetch('/login', {
                method: 'POST',
                body: formData
            });

            let data = await res.json();

            clearErrors();

            if (data.success) {
                window.location.href = data.redirect;
            } else {
                for (let key in data.errors) {
                    document.getElementById(`login_${key}_error`).innerText = data.errors[key];
                }
            }
        };
    }

    // REGISTER
    const registerForm = document.getElementById('registerForm');

    if (registerForm) {
        registerForm.onsubmit = async (e) => {
            e.preventDefault();

            let formData = new FormData(registerForm);

            let res = await fetch('/register', {
                method: 'POST',
                body: formData
            });

            let data = await res.json();

            clearErrors();

            if (data.success) {
                window.location.href = data.redirect;
            } else {
                for (let key in data.errors) {
                    document.getElementById(`reg_${key}_error`).innerText = data.errors[key];
                }
            }
        };
    }
});


function clearErrors() {
    document.querySelectorAll('.error').forEach(e => e.innerText = "");
}