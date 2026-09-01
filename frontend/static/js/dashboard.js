import { api } from './api.js';
import { renderMovimientos } from './render.js';

export async function cargarDashboard() {
    const data = await api("/api/dashboard");
    if (!data) return;

    document.getElementById("statInsumos").textContent = data.total_insumos;
    document.getElementById("statProductos").textContent = data.total_productos;
    document.getElementById("statAlertas").textContent = data.alertas.length;

    renderMovimientos(data.movimientos, "dashboardMovimientos");
}