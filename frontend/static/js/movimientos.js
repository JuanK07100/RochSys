import { api } from './api.js';
import { renderMovimientos } from './render.js';

export async function cargarMovimientos() {
    const data = await api("/api/movimientos");
    if (data) {
        window.movimientos = data;
        renderMovimientos(data, "tablaMovimientos");
    }
}