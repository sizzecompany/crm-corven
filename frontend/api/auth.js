const AUTH_BASE_URL = 'http://localhost:8000/api/v1/auth';

async function authRequest(path, payload) {
    const response = await fetch(`${AUTH_BASE_URL}${path}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.detail || 'Erro de autenticação');
    }

    return data;
}

export async function requestOtp(email) {
    return authRequest('/request-otp', { email });
}

export async function verifyOtp(email, code) {
    return authRequest('/verify-otp', { email, code });
}
