// state.js
export const state = {
    insumos: [],
    productos: [],
    ubicaciones: [],
    token: null,
    currentUser: null
};

export function setInsumos(data) {
    state.insumos = data;
}
export function setProductos(data) {
    state.productos = data;
}
export function setUbicaciones(data) {
    state.ubicaciones = data;
}
export function setToken(token) {
    state.token = token;
    localStorage.setItem("rochsis_token", token);
}
export function setCurrentUser(user) {
    state.currentUser = user;
    localStorage.setItem("rochsis_user", JSON.stringify(user));
}
export function clearAuth() {
    state.token = null;
    state.currentUser = null;
    localStorage.removeItem("rochsis_token");
    localStorage.removeItem("rochsis_user");
}
// Cargar desde localStorage
export function loadAuthFromStorage() {
    const token = localStorage.getItem("rochsis_token");
    const user = JSON.parse(localStorage.getItem("rochsis_user") || "null");
    if (token && user) {
        state.token = token;
        state.currentUser = user;
        return true;
    }
    return false;
}