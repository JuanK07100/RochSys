import { login, logout } from './auth.js';
import {
    cargarUsuarios,
    renderUsuarios,
    abrirEditarUsuario,
    guardarEdicionUsuario,
    eliminarUsuario,
    crearUsuario
} from './usuarios.js';
import {
    showSection,
    openModal,
    closeModal,
    aplicarPermisos,
    mostrarInventario,
    llenarSelect
} from './ui.js';
import {
    cargarInsumos,
    cargarSelectConsumo,
    cargarUbicacionesConsumo,
    cargarSelectEntrada,
    cargarSelectNuevaMP,
    crearInsumo,
    registrarEntrada,
    registrarConsumo
} from './insumos.js';
import {
    cargarProductos,
    cargarSelectVerificacion,
    crearProducto
} from './productos.js';
import {
    cargarUbicaciones,
    cargarSelectNuevoPT,
    crearUbicacion
} from './ubicaciones.js';
import { cargarMovimientos } from './movimientos.js';
import { cargarDashboard } from './dashboard.js';
import { cargarAlertas } from './alertas.js';
import { verificarPedido } from './produccion.js';
import { renderInsumos, renderProductos, renderUbicaciones, renderMovimientos } from './render.js';
import { getToken, getCurrentUser } from './api.js';

// Exponer funciones globales para el HTML
window.login = login;
window.logout = logout;
window.showSection = showSection;
window.openModal = openModal;
window.closeModal = closeModal;
window.aplicarPermisos = aplicarPermisos;
window.mostrarInventario = mostrarInventario;
window.llenarSelect = llenarSelect;
window.cargarInsumos = cargarInsumos;
window.cargarProductos = cargarProductos;
window.cargarUbicaciones = cargarUbicaciones;
window.cargarMovimientos = cargarMovimientos;
window.cargarDashboard = cargarDashboard;
window.cargarAlertas = cargarAlertas;
window.cargarSelectConsumo = cargarSelectConsumo;
window.cargarUbicacionesConsumo = cargarUbicacionesConsumo;
window.cargarSelectEntrada = cargarSelectEntrada;
window.cargarSelectNuevaMP = cargarSelectNuevaMP;
window.cargarSelectNuevoPT = cargarSelectNuevoPT;
window.cargarSelectVerificacion = cargarSelectVerificacion;
window.crearInsumo = crearInsumo;
window.registrarEntrada = registrarEntrada;
window.registrarConsumo = registrarConsumo;
window.crearProducto = crearProducto;
window.crearUbicacion = crearUbicacion;
window.verificarPedido = verificarPedido;
window.renderInsumos = renderInsumos;
window.renderProductos = renderProductos;
window.renderUbicaciones = renderUbicaciones;
window.renderMovimientos = renderMovimientos;
window.cargarUsuarios = cargarUsuarios;
window.renderUsuarios = renderUsuarios;
window.abrirEditarUsuario = abrirEditarUsuario;
window.guardarEdicionUsuario = guardarEdicionUsuario;
window.eliminarUsuario = eliminarUsuario;
window.crearUsuario = crearUsuario;

// Función central para recargar todo
export async function cargarTodo() {
    await Promise.all([
        cargarInsumos(),
        cargarProductos(),
        cargarUbicaciones(),
        cargarDashboard(),
        cargarMovimientos(),
        cargarUsuarios()
    ]);
    cargarSelectConsumo();
    cargarSelectVerificacion();
}
window.cargarTodo = cargarTodo;

// === NUEVO: Asignar eventos a los menús ===
// Esto reemplaza el código que estaba en app.js
document.querySelectorAll(".menu-item").forEach(btn => {
    btn.addEventListener("click", () => showSection(btn.dataset.section));
});

