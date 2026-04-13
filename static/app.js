// ── Auth helpers ───────────────────────────────────────
function getToken()    { return localStorage.getItem('token') }
function getUsername() { return localStorage.getItem('username') }
function getUserId()   { return localStorage.getItem('user_id') }

function authHeaders() {
    return {
        'Content-Type':  'application/json',
        'Authorization': `Bearer ${getToken()}`,
    }
}

function requireAuth() {
    if (!getToken()) {
        window.location.href = '/auth/login'
        return false
    }
    return true
}

function logout() {
    localStorage.clear()
    window.location.href = '/auth/login'
}

// ── Fetch helper ───────────────────────────────────────
async function api(path, options = {}) {
    const res = await fetch(path, {
        headers: authHeaders(),
        ...options,
    })
    if (res.status === 401) {
        logout()
        return null
    }
    return res
}

// ── Format helpers ─────────────────────────────────────
function fmtAmount(amount, symbole = '€') {
    return `${parseFloat(amount).toFixed(2)} ${symbole}`
}

function fmtDate(dateStr) {
    if (!dateStr) return ''
    const [y, m, d] = dateStr.split('-')
    return `${d}/${m}/${y}`
}

function todayISO() {
    return new Date().toISOString().split('T')[0]
}

function todayFR() {
    const d = new Date()
    const dd = String(d.getDate()).padStart(2, '0')
    const mm = String(d.getMonth() + 1).padStart(2, '0')
    const yyyy = d.getFullYear()
    return `${dd}/${mm}/${yyyy}`
}

function currentMonth() {
    const d = new Date()
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
}

// ── Color helpers ──────────────────────────────────────
function hexToRgba(hex, alpha = 0.15) {
    const r = parseInt(hex.slice(1,3), 16)
    const g = parseInt(hex.slice(3,5), 16)
    const b = parseInt(hex.slice(5,7), 16)
    return `rgba(${r},${g},${b},${alpha})`
}

// ── Nav active state ───────────────────────────────────
function setActiveNav(page) {
    document.querySelectorAll('.nav-item').forEach(el => {
        el.classList.toggle('active', el.dataset.page === page)
    })
}