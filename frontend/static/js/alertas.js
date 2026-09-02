import { api } from './api.js';

export async function cargarAlertas() {
    const data = await api("/api/alertas");
    actualizarBadgeAlertas(data);

    const c = document.getElementById("alertasLista");
    if (!c || !data) return;

    if (!data.length) {
        c.innerHTML = `<div class="alert alert-success">No hay materias primas por debajo del punto de reorden.</div>`;
        return;
    }

    c.innerHTML = data.map(a => `
        <div class="alert-card">
            <strong><i class="fa-solid fa-triangle-exclamation text-danger"></i> ${a.codigo} · ${a.nombre}</strong>
            <div class="mt-2">
                Stock actual: <strong>${a.cantidad} ${a.unidad}</strong>
                · Punto de reorden: <strong>${a.punto_reorden} ${a.unidad}</strong>
            </div>
        </div>
    `).join("");
}

export function actualizarBadgeAlertas(data) {
    const badge = document.getElementById("alertasBadge");
    if (!badge) return;

    const total = data ? data.length : 0;
    if (total > 0) {
        badge.textContent = total > 99 ? "99+" : total;
        badge.classList.remove("d-none");
    } else {
        badge.classList.add("d-none");
    }
}