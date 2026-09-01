export function showSection(section) {
    document.querySelectorAll(".section").forEach(s => s.classList.remove("active-section"));
    document.getElementById(section).classList.add("active-section");

    document.querySelectorAll(".menu-item").forEach(b => b.classList.remove("active"));
    document.querySelector(`.menu-item[data-section="${section}"]`)?.classList.add("active");

    if (section === "inventario") {
        if (window.renderInsumos) window.renderInsumos();
        if (window.renderProductos) window.renderProductos();
    }
    if (section === "movimientos") {
        if (window.cargarMovimientos) window.cargarMovimientos();
    }
    if (section === "alertas") {
        if (window.cargarAlertas) window.cargarAlertas();
    }
    if (section === "configuracion") {
        if (window.cargarUbicaciones) window.cargarUbicaciones();
    }
}

export function openModal(id) {
    if (id === "modalEntrada") {
        if (window.cargarSelectEntrada) window.cargarSelectEntrada();
    }
    if (id === "modalNuevaMP") {
        if (window.cargarSelectNuevaMP) window.cargarSelectNuevaMP();
    }
    if (id === "modalNuevoPT") {
        if (window.cargarSelectNuevoPT) window.cargarSelectNuevoPT();
    }
    bootstrap.Modal.getOrCreateInstance(document.getElementById(id)).show();
}

export function closeModal(id) {
    bootstrap.Modal.getOrCreateInstance(document.getElementById(id)).hide();
}

export function aplicarPermisos() {
    import('./api.js').then(module => {
        const user = module.getCurrentUser();
        if (user?.rol !== "Administrador") {
            document.querySelectorAll(".admin-only").forEach(el => el.remove());
        }
    });
}

export function mostrarInventario(tipo, btn) {
    document.querySelectorAll("#inventario .nav-link").forEach(x => x.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById("inventarioMP").classList.toggle("d-none", tipo !== "mp");
    document.getElementById("inventarioPT").classList.toggle("d-none", tipo !== "pt");
}

export function llenarSelect(selectId, items, textFn) {
    const select = document.getElementById(selectId);
    if (!select) return;
    select.innerHTML = items.map(x => `<option value="${x.id}">${textFn(x)}</option>`).join("");
}