import { api } from './api.js';

let currentProductoReferencia = null;
let recetaItems = [];

export function cargarSelectProductoReceta() {
    const productos = window.productos || [];
    const select = document.getElementById("recetaProducto");
    if (!select) return;

    select.innerHTML = `<option value="">-- Seleccionar --</option>` +
        productos.map(p => `<option value="${p.referencia}">${p.referencia} · ${p.nombre}</option>`).join('');

    select.removeEventListener('change', cargarReceta);
    select.addEventListener('change', cargarReceta);
}

export async function cargarReceta() {
    const referencia = document.getElementById("recetaProducto").value;
    if (!referencia) {
        recetaItems = [];
        renderTablaReceta();
        return;
    }
    currentProductoReferencia = referencia;
    const data = await api(`/api/recetas/${referencia}`);
    if (data) {
        recetaItems = data.map(item => ({
            insumo_id: item.insumo_id,
            cantidad_necesaria: item.cantidad_necesaria,
            _codigo: item.codigo,
            _nombre: item.nombre,
            _unidad: item.unidad
        }));
    } else {
        recetaItems = [];
    }
    renderTablaReceta();
}

function renderTablaReceta() {
    const container = document.getElementById("tablaReceta");
    if (!container) return;

    if (!recetaItems.length) {
        container.innerHTML = `<div class="text-muted">No hay insumos definidos para este producto.</div>`;
        return;
    }

    const insumos = window.insumos || [];

    let html = `
        <div class="table-responsive">
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>Insumo</th>
                    <th>Cantidad por unidad</th>
                    <th>Acción</th>
                </tr>
            </thead>
            <tbody>
    `;

    recetaItems.forEach((item, index) => {
        html += `
            <tr>
                <td>
                    <select class="form-select receta-insumo" data-index="${index}">
                        ${insumos.map(i => `
                            <option value="${i.id}" ${i.id == item.insumo_id ? 'selected' : ''}>
                                ${i.codigo} · ${i.nombre} (${i.unidad})
                            </option>
                        `).join('')}
                    </select>
                </td>
                <td>
                    <input type="number" class="form-control receta-cantidad" data-index="${index}"
                           value="${item.cantidad_necesaria || ''}" step="0.01" min="0" placeholder="Cantidad">
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-danger" onclick="window.eliminarFilaReceta(${index})">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
        </div>
    `;
    container.innerHTML = html;
}

export function agregarFilaReceta() {
    // Recolectar valores actuales antes de agregar
    recolectarValoresActuales();
    recetaItems.push({ insumo_id: '', cantidad_necesaria: '' });
    renderTablaReceta();
}

export function eliminarFilaReceta(index) {
    recolectarValoresActuales();
    recetaItems.splice(index, 1);
    renderTablaReceta();
}

function recolectarValoresActuales() {
    const selects = document.querySelectorAll('.receta-insumo');
    const inputs = document.querySelectorAll('.receta-cantidad');
    selects.forEach((select, i) => {
        if (recetaItems[i]) {
            recetaItems[i].insumo_id = parseInt(select.value) || '';
            recetaItems[i].cantidad_necesaria = parseFloat(inputs[i].value) || '';
        }
    });
}

export async function guardarReceta() {
    if (!currentProductoReferencia) {
        alert("Primero selecciona un producto y carga su receta.");
        return;
    }

    // Recolectar valores finales
    recolectarValoresActuales();

    const items = recetaItems
        .filter(item => item.insumo_id && item.cantidad_necesaria > 0)
        .map(item => ({
            insumo_id: item.insumo_id,
            cantidad_necesaria: item.cantidad_necesaria
        }));

    if (items.length === 0) {
        if (!confirm("¿Estás seguro de dejar este producto sin insumos?")) {
            return;
        }
    }

    const res = await api(`/api/recetas/${currentProductoReferencia}`, {
        method: "POST",
        body: JSON.stringify({ items })
    });

    if (res) {
        alert("Receta guardada correctamente.");
        await cargarReceta();
    }
}

export async function eliminarReceta() {
    if (!currentProductoReferencia) {
        alert("Selecciona un producto primero.");
        return;
    }
    if (!confirm(`¿Eliminar toda la receta para ${currentProductoReferencia}?`)) {
        return;
    }
    const res = await api(`/api/recetas/${currentProductoReferencia}`, {
        method: "DELETE"
    });
    if (res) {
        alert("Receta eliminada.");
        recetaItems = [];
        renderTablaReceta();
    }
}