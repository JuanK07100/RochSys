import { api } from './api.js';
import { renderProductos } from './render.js';

let productos = [];

export function getProductos() { return productos; }

export async function cargarProductos() {
    productos = await api("/api/productos") || [];
    window.productos = productos;
    renderProductos(productos);
}

export function cargarSelectVerificacion() {
    const select = document.getElementById("verifProducto");
    if (!select) return;
    select.innerHTML = productos
        .map(p => `<option value="${p.referencia}">${p.referencia} · ${p.nombre}</option>`)
        .join("");
}

export async function crearProducto() {
    const payload = {
        referencia: document.getElementById("ptRef").value.trim(),
        nombre: document.getElementById("ptNombre").value.trim(),
        cantidad_inicial: parseFloat(document.getElementById("ptCantidad").value) || 0,
        ubicacion_id: document.getElementById("ptUbicacion").value,
        descripcion: document.getElementById("ptDescripcion").value.trim()
    };

    const res = await api("/api/productos", {
        method: "POST",
        body: JSON.stringify(payload)
    });

    if (res) {
        const modal = bootstrap.Modal.getInstance(document.getElementById("modalNuevoPT"));
        if (modal) modal.hide();
        if (window.cargarTodo) window.cargarTodo();
        alert("Producto terminado registrado.");
    }
}