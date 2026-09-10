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

// ============================================================
// FUNCIONES PARA STEP Y REDONDEO
// ============================================================

export function obtenerStepPorUnidad(unidad) {
    const unidadesContinuas = ['m', 'kg', 'litro'];
    return unidadesContinuas.includes(unidad) ? 0.1 : 1;
}

function redondearSegunStep(valor, step) {
    if (isNaN(valor) || valor === '' || valor === null) return '';
    const num = parseFloat(valor);
    if (step === 1) {
        return Math.round(num);
    }
    if (step === 0.1) {
        return Math.round(num * 10) / 10;
    }
    return num;
}

function configurarRedondeoInput(inputId, stepGetter) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    // Función que aplica redondeo y actualiza el step
    const aplicarRedondeo = () => {
        const step = stepGetter();
        if (step && input.value !== '') {
            const valorActual = parseFloat(input.value);
            if (!isNaN(valorActual)) {
                const redondeado = redondearSegunStep(valorActual, step);
                input.value = redondeado;
            }
        }
    };

    // Redondear al perder el foco
    input.addEventListener('blur', aplicarRedondeo);
    
    // Redondear al escribir (opcional, puede ser molesto, pero útil para flechas)
    input.addEventListener('input', function() {
        // Solo si el usuario usa las flechas o pega un valor
        // No redondeamos en cada tecla para no bloquear la escritura
    });
}

// ============================================================
// NUEVA MP
// ============================================================

export function actualizarStepsNuevaMP() {
    const unidadSelect = document.getElementById('mpUnidad');
    if (!unidadSelect) return;
    const unidad = unidadSelect.value;
    const step = obtenerStepPorUnidad(unidad);
    ['mpCantidad', 'mpReorden', 'mpMaximo'].forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.step = step;
            const valorActual = parseFloat(input.value) || 0;
            input.value = redondearSegunStep(valorActual, step);
        }
    });
}

export function cargarSelectNuevaMP() {
    import('./ubicaciones.js').then(module => {
        const ubicaciones = module.getUbicaciones();
        const filtradas = ubicaciones.filter(u => u.tipo === "MP" || u.tipo === "MIXTA");
        llenarSelect("mpUbicacion", filtradas, u => u.nombre);
        actualizarStepsNuevaMP();
        // Configurar redondeo en blur para estos campos
        ['mpCantidad', 'mpReorden', 'mpMaximo'].forEach(id => {
            configurarRedondeoInput(id, () => {
                const unidad = document.getElementById('mpUnidad')?.value;
                return obtenerStepPorUnidad(unidad || 'unidad');
            });
        });
    });
}

// ============================================================
// ENTRADA MP
// ============================================================

export function actualizarStepEntrada() {
    const insumoSelect = document.getElementById('entradaInsumo');
    if (!insumoSelect) return;
    const insumoId = Number(insumoSelect.value);
    const insumo = insumos.find(i => i.id === insumoId);
    if (insumo) {
        const step = obtenerStepPorUnidad(insumo.unidad);
        const input = document.getElementById('entradaCantidad');
        if (input) {
            input.step = step;
            const valorActual = parseFloat(input.value) || 0;
            input.value = redondearSegunStep(valorActual, step);
        }
    }
}

export function cargarSelectEntrada() {
    llenarSelect("entradaInsumo", insumos, i => `${i.codigo} · ${i.nombre} (${i.cantidad} ${i.unidad})`);
    import('./ubicaciones.js').then(module => {
        const ubicaciones = module.getUbicaciones();
        const filtradas = ubicaciones.filter(u => u.tipo === "MP" || u.tipo === "MIXTA");
        llenarSelect("entradaUbicacion", filtradas, u => u.nombre);
        actualizarStepEntrada();
        // Configurar redondeo en blur para entrada
        configurarRedondeoInput('entradaCantidad', () => {
            const insumoSelect = document.getElementById('entradaInsumo');
            if (!insumoSelect) return 1;
            const insumoId = Number(insumoSelect.value);
            const insumo = insumos.find(i => i.id === insumoId);
            return insumo ? obtenerStepPorUnidad(insumo.unidad) : 1;
        });
    });
}

// ============================================================
// LISTENERS GLOBALES
// ============================================================

export function inicializarListenersStep() {
    // Nueva MP
    const unidadSelect = document.getElementById('mpUnidad');
    if (unidadSelect) {
        unidadSelect.removeEventListener('change', actualizarStepsNuevaMP);
        unidadSelect.addEventListener('change', actualizarStepsNuevaMP);
    }

    // Entrada MP
    const insumoSelect = document.getElementById('entradaInsumo');
    if (insumoSelect) {
        insumoSelect.removeEventListener('change', actualizarStepEntrada);
        insumoSelect.addEventListener('change', actualizarStepEntrada);
    }
}

export function actualizarStepConsumo() {
    const insumoSelect = document.getElementById('consumoInsumo');
    if (!insumoSelect) return;
    const insumoId = Number(insumoSelect.value);
    const insumo = insumos.find(i => i.id === insumoId);
    if (insumo) {
        const step = obtenerStepPorUnidad(insumo.unidad);
        const input = document.getElementById('consumoCantidad');
        if (input) {
            input.step = step;
            // Redondear el valor actual si existe
            const valorActual = parseFloat(input.value) || 0;
            input.value = redondearSegunStep(valorActual, step);
        }
    }
}

export function cargarSelectConsumo() {
    import('./ubicaciones.js').then(module => {
        const ubicaciones = module.getUbicaciones();
        llenarSelect("consumoInsumo", insumos, i => `${i.codigo} · ${i.nombre} (${i.cantidad} ${i.unidad})`);
        cargarUbicacionesConsumo();
        actualizarStepConsumo(); // <-- NUEVO
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
    // Actualizar step al cambiar el insumo
    actualizarStepConsumo();
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
        window.showToast("Materia prima registrada correctamente.");
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
        window.showToast("Introduce una cantidad válida.");
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
        window.showToast("Entrada registrada.");
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
        window.showToast("Introduce una cantidad válida.");
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
        window.showToast("Consumo registrado correctamente.", "success");
    } else {
        result.innerHTML = `<div class="alert alert-danger">No fue posible registrar el consumo.</div>`;
        window.showToast("No fue posible registrar el consumo.", "error");
    }
}