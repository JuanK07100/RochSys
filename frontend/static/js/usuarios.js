import { api } from './api.js';
import { llenarSelect } from './ui.js';

let usuarios = [];

export function getUsuarios() { return usuarios; }

export async function cargarUsuarios() {
    usuarios = await api("/api/usuarios") || [];
    window.usuarios = usuarios;
    renderUsuarios(usuarios);
}

export function renderUsuarios(data, containerId = "tablaUsuarios") {
    const c = document.getElementById(containerId);
    if (!c) return;

    const usuariosData = data || window.usuarios || [];

    if (!usuariosData.length) {
        c.innerHTML = `<div class="text-muted">No hay usuarios registrados.</div>`;
        return;
    }

    c.innerHTML = `
        <div class="table-responsive">
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Usuario</th>
                    <th>Rol</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                ${usuariosData.map(u => `
                    <tr>
                        <td>${u.id}</td>
                        <td><strong>${u.username}</strong></td>
                        <td><span class="badge ${u.rol === 'Administrador' ? 'text-bg-danger' : 'text-bg-secondary'}">${u.rol}</span></td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary" onclick="window.abrirEditarUsuario(${u.id})">
                                <i class="fa-solid fa-pen"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="window.eliminarUsuario(${u.id})">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </td>
                    </tr>
                `).join("")}
            </tbody>
        </table>
        </div>
    `;
}

export function abrirEditarUsuario(userId) {
    const user = usuarios.find(u => u.id === userId);
    if (!user) return;

    document.getElementById("editUserId").value = user.id;
    document.getElementById("editUsername").value = user.username;
    document.getElementById("editRol").value = user.rol;
    document.getElementById("editPassword").value = "";
    document.getElementById("editPasswordHelp").classList.remove("d-none");
    // Abrir modal
    bootstrap.Modal.getOrCreateInstance(document.getElementById("modalEditarUsuario")).show();
}

export async function guardarEdicionUsuario() {
    const userId = document.getElementById("editUserId").value;
    const rol = document.getElementById("editRol").value;
    const password = document.getElementById("editPassword").value.trim();

    const payload = { rol };
    if (password) payload.password = password;

    const res = await api(`/api/usuarios/${userId}`, {
        method: "PUT",
        body: JSON.stringify(payload)
    });

    if (res) {
        bootstrap.Modal.getInstance(document.getElementById("modalEditarUsuario")).hide();
        await cargarUsuarios();
        window.showToast("Usuario actualizado correctamente.");
    }
}

export async function eliminarUsuario(userId) {
    if (!confirm("¿Seguro que deseas eliminar este usuario?")) return;

    const res = await api(`/api/usuarios/${userId}`, {
        method: "DELETE"
    });

    if (res) {
        await cargarUsuarios();
        window.showToast("Usuario eliminado.");
    }
}

export async function crearUsuario() {
    const payload = {
        username: document.getElementById("nuevoUsername").value.trim(),
        password: document.getElementById("nuevoPassword").value,
        rol: document.getElementById("nuevoRol").value
    };

    if (!payload.username || !payload.password) {
        window.showToast("Usuario y contraseña son obligatorios.");
        return;
    }

    const res = await api("/api/usuarios", {
        method: "POST",
        body: JSON.stringify(payload)
    });

    if (res) {
        bootstrap.Modal.getInstance(document.getElementById("modalNuevoUsuario")).hide();
        await cargarUsuarios();
        window.showToast("Usuario creado correctamente.");
        // Limpiar campos
        document.getElementById("nuevoUsername").value = "";
        document.getElementById("nuevoPassword").value = "";
    }
}