import { setToken, setCurrentUser } from './api.js';

export async function login() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    console.log("Username:", username);
    console.log("Password:", password);

    try {
        const res = await fetch("/api/auth/login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({username, password})
        });

        const data = await res.json();

        if (!res.ok) {
            document.getElementById("loginError").textContent = data.error || "Error de autenticación";
            return;
        }

        setToken(data.token);
        setCurrentUser(data.user);

        document.getElementById("loginView").classList.add("d-none");
        document.getElementById("appView").classList.remove("d-none");
        document.getElementById("userInfo").textContent = `${data.user.username} · ${data.user.rol}`;

        if (window.aplicarPermisos) window.aplicarPermisos();
        if (window.cargarTodo) window.cargarTodo();
    } catch (error) {
        document.getElementById("loginError").textContent = error.message || "Error de autenticación";
    }
}

export function logout() {
    localStorage.removeItem("rochsis_token");
    localStorage.removeItem("rochsis_user");
    location.reload();
}

// Asigna el evento al botón cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('loginBtn');
    if (btn) {
        btn.addEventListener('click', login);
    }
});