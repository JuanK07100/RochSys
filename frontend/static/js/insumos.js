import { api } from './api.js';
import { renderInsumos } from './render.js';
import { llenarSelect } from './ui.js';

let insumos = [];

export function getInsumos() { return insumos; }

export async function cargarInsumos() {
    insumos = await api("/api/insumos") || [];
    window.insumos = insumos;
    renderInsumos(insumos);
}

export function cargarSelectConsumo() {
    import('./ubicaciones.js').then(module => {
        const ubicaciones = module.getUbicaciones();
        llenarSelect("consumoInsumo", insumos, i => `${i.codigo} · ${i.nombre} (${i.cantidad} ${i.unidad})`);
        cargarUbicacionesConsumo();
    });
}

export function cargarUbicacionesConsumo() {
    const insumoId = Number(document.getElementById("consumoInsumo")?.value);
    const insumo = insumos.find(i => i.id === insumoId);
    const select = document.getElementById("consumoUbicacion");
    if (!select) return;
    select.innerHTML = (insumo?.ubicaciones || [])
        .filter(u => u.cantidad > 0)
        .map(u => `<option value="${u.ubicacion_id}">${u.ubicacion} · ${u.cantidad} ${insumo.unidad}</option>`)
        .join("");
}

export function cargarSelectEntrada() {
    llenarSelect("entradaInsumo", insumos, i => `${i.codigo} · ${i.nombre} (${i.cantidad} ${i.unidad})`);
    import('./ubicaciones.js').then(module => {
        const ubicaciones = module.getUbicaciones();
        const filtradas = ubicaciones.filter(u => u.tipo === "MP" || u.tipo === "MIXTA");
        llenarSelect("entradaUbicacion", filtradas, u => u.nombre);
    });
}

export function cargarSelectNuevaMP() {
    import('./ubicaciones.js').then(module => {
        const ubicaciones = module.getUbicaciones();
        const filtradas = ubicaciones.filter(u => u.tipo === "MP" || u.tipo === "MIXTA");
        llenarSelect("mpUbicacion", filtradas, u => u.nombre);
    });
}

export async function crearInsumo() {
    const payload = {
        codigo: document.getElementById("mpCodigo").value.trim(),
        nombre: document.getElementById("mpNombre").value.trim(),
        unidad: document.getElementById("mpUnidad").value,
        categoria: document.getElementById("mpCategoria").value.trim(),
        proveedor: document.getElementById("mpProveedor").value.trim(),
        cantidad_inicial: parseFloat(document.getElementById("mpCantidad").value) || 0,
        punto_reorden: parseFloat(document.getElementById("mpReorden").value) || 0,
        stock_maximo: parseFloat(document.getElementById("mpMaximo").value) || 0,
        costo_unitario: parseFloat(document.getElementById("mpCosto").value) || 0,
        ubicacion_id: document.getElementById("mpUbicacion").value,
        descripcion: document.getElementById("mpDescripcion").value.trim()
    };

    const res = await api("/api/insumos", {
        method: "POST",
        body: JSON.stringify(payload)
    });

    if (res) {
        const modal = bootstrap.Modal.getInstance(document.getElementById("modalNuevaMP"));
        if (modal) modal.hide();
        if (window.cargarTodo) window.cargarTodo();
        alert("Materia prima registrada correctamente.");
    }
}

export async function registrarEntrada() {
    const payload = {
        insumo_id: document.getElementById("entradaInsumo").value,
        ubicacion_id: document.getElementById("entradaUbicacion").value,
        cantidad: parseFloat(document.getElementById("entradaCantidad").value),
        referencia: document.getElementById("entradaReferencia").value.trim(),
        motivo: document.getElementById("entradaMotivo").value.trim()
    };

    if (!payload.cantidad || payload.cantidad <= 0) {
        alert("Introduce una cantidad válida.");
        return;
    }

    const res = await api("/api/insumos/entrada", {
        method: "POST",
        body: JSON.stringify(payload)
    });

    if (res) {
        const modal = bootstrap.Modal.getInstance(document.getElementById("modalEntrada"));
        if (modal) modal.hide();
        if (window.cargarTodo) window.cargarTodo();
        alert("Entrada registrada.");
    }
}

export async function registrarConsumo() {
    const payload = {
        insumo_id: document.getElementById("consumoInsumo").value,
        ubicacion_id: document.getElementById("consumoUbicacion").value,
        cantidad: parseFloat(document.getElementById("consumoCantidad").value),
        motivo: document.getElementById("consumoMotivo").value.trim()
    };

    if (!payload.cantidad || payload.cantidad <= 0) {
        alert("Introduce una cantidad válida.");
        return;
    }

    const res = await api("/api/insumos/consumo", {
        method: "POST",
        body: JSON.stringify(payload)
    });

    const result = document.getElementById("consumoResultado");

    if (res) {
        result.innerHTML = `<div class="alert alert-success">Consumo registrado correctamente.</div>`;
        document.getElementById("consumoCantidad").value = "";
        document.getElementById("consumoMotivo").value = "";
        if (window.cargarTodo) window.cargarTodo();
    } else {
        result.innerHTML = `<div class="alert alert-danger">No fue posible registrar el consumo.</div>`;
    }
}