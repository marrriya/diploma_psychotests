const loginForm = document.getElementById('loginForm')
const registerForm = document.getElementById('registerForm')

const loginTab = document.getElementById('loginTab')
const registerTab = document.getElementById('registerTab')

//switcher
function showForm(type) {
    loginForm.classList.remove('active')
    registerForm.classList.remove('active')
    loginTab.classList.remove('active')
    registerTab.classList.remove('active')

    if (type === 'register') {
        registerForm.classList.add('active')
        registerTab.classList.add('active')
    } else {
        loginForm.classList.add('active')
        loginTab.classList.add('active')
    }
}

// кнопки
loginTab.onclick = () => showForm('login')
registerTab.onclick = () => showForm('register')

// стартовая форма
window.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search)
    const mode = params.get('mode')

    if (mode === 'register') {
        showForm('register')
    } else {
        showForm('login')
    }
})

//login

loginForm.onsubmit = async (e) => {
    e.preventDefault()

    let formData = new FormData(loginForm)

    let res = await fetch('/login', {
        method: 'POST',
        body: formData
    })

    let data = await res.json()

    clearErrors()

    if (data.success) {
        window.location.href = data.redirect
    } else {
        for (let key in data.errors) {
            document.getElementById(`login_${key}_error`).innerText = data.errors[key]
        }
    }
}

// ==========================
// REGISTER
// ==========================

registerForm.onsubmit = async (e) => {
    e.preventDefault()

    let formData = new FormData(registerForm)

    let res = await fetch('/register', {
        method: 'POST',
        body: formData
    })

    let data = await res.json()

    clearErrors()

    if (data.success) {
        window.location.href = data.redirect
    } else {
        for (let key in data.errors) {
            document.getElementById(`reg_${key}_error`).innerText = data.errors[key]
        }
    }
}


function clearErrors() {
    document.querySelectorAll('.error').forEach(e => e.innerText = "")
}