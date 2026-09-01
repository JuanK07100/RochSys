import { api } from './api.js';

export async function cargarAlertas() {
    const data = await api("/api/alertas");
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