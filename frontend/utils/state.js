const TOKEN_KEY = 'crm_token';
const TENANT_KEY = 'crm_tenant_id';

export function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
    if (!token) {
        localStorage.removeItem(TOKEN_KEY);
        return;
    }
    localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
    localStorage.removeItem(TOKEN_KEY);
}

export function getTenantId() {
    return localStorage.getItem(TENANT_KEY);
}

export function setTenantId(tenantId) {
    if (!tenantId) {
        localStorage.removeItem(TENANT_KEY);
        return;
    }
    localStorage.setItem(TENANT_KEY, tenantId);
}

export function clearTenantId() {
    localStorage.removeItem(TENANT_KEY);
}

export function clearAuthState() {
    clearToken();
    clearTenantId();
    localStorage.removeItem('crm_refresh');
}
