import { api } from './api.js';
import { renderUbicaciones } from './render.js';
import { llenarSelect } from './ui.js';

let ubicaciones = [];

export function getUbicaciones() { return ubicaciones; }

export async function cargarUbicaciones() {
    ubicaciones = await api("/api/ubicaciones") || [];
    window.ubicaciones = ubicaciones;
    renderUbicaciones(ubicaciones);
}

export function cargarSelectNuevoPT() {
    const filtradas = ubicaciones.filter(u => u.tipo === "PT" || u.tipo === "MIXTA");
    llenarSelect("ptUbicacion", filtradas, u => u.nombre);
}

export async function crearUbicacion() {
    const payload = {
        nombre: document.getElementById("ubicNombre").value.trim(),
        tipo: document.getElementById("ubicTipo").value,
        descripcion: document.getElementById("ubicDescripcion").value.trim()
    };

    const res = await api("/api/ubicaciones", {
        method: "POST",
        body: JSON.stringify(payload)
    });

    if (res) {
        document.getElementById("ubicNombre").value = "";
        document.getElementById("ubicDescripcion").value = "";
        await cargarUbicaciones();
        window.showToast("Ubicación creada.");
    }
}