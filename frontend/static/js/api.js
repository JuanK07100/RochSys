let token = localStorage.getItem("rochsis_token");
let currentUser = JSON.parse(localStorage.getItem("rochsis_user") || "null");

export function authHeaders() {
    return {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
    };
}

export async function api(url, options = {}) {
    const config = {...options, headers: {...authHeaders(), ...(options.headers || {})}};
    const res = await fetch(url, config);

    if (res.status === 401 || res.status === 403) {
        return null;
    }

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
        throw new Error(data.error || "Ocurrió un error");
    }

    return data;
}

export function setToken(newToken) {
    token = newToken;
    localStorage.setItem("rochsis_token", token);
}

export function setCurrentUser(user) {
    currentUser = user;
    localStorage.setItem("rochsis_user", JSON.stringify(user));
}

export function getToken() { return token; }
export function getCurrentUser() { return currentUser; }