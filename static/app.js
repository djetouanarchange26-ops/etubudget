// ── Service Worker ─────────────────────────────────────
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/sw.js')
    })
}

// ── Auth helpers ───────────────────────────────────────
function getToken()    { return localStorage.getItem('token') }
function getUsername() { return localStorage.getItem('username') }
function getUserId()   { return localStorage.getItem('user_id') }
function getSym()      { return localStorage.getItem('symbole') || '€' }
function getDevise()   { return localStorage.getItem('devise')  || 'EUR' }

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
function fmtAmount(amount, symbole) {
    return `${parseFloat(amount).toFixed(2)} ${symbole || getSym()}`
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
    const d  = new Date()
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
    const r = parseInt(hex.slice(1, 3), 16)
    const g = parseInt(hex.slice(3, 5), 16)
    const b = parseInt(hex.slice(5, 7), 16)
    return `rgba(${r},${g},${b},${alpha})`
}

// ── Nav active state ───────────────────────────────────
function setActiveNav(page) {
    document.querySelectorAll('.nav-item').forEach(el => {
        el.classList.toggle('active', el.dataset.page === page)
    })
}

// Cache en mémoire — évite les appels répétés
const _ratesCache = {}

function convertAmount(amount) {
    return Promise.resolve(parseFloat(amount))
}

// ── Onboarding PWA ─────────────────────────────────────
const ONBOARDING = {
    dashboard: {
        emoji: '👋',
        titre: 'Bienvenue sur ton dashboard',
        texte: 'Retrouve ici ton solde cumulé, le résumé du mois et tes dernières transactions. Change le mois en haut pour explorer ton historique.',
    },
    add: {
        emoji: '💸',
        titre: 'Ajouter une transaction',
        texte: 'Saisis ici tes dépenses et revenus. Le montant doit être positif — c\'est le type qui indique le sens. La catégorie est optionnelle mais utile pour les stats.',
    },
    history: {
        emoji: '📋',
        titre: 'Historique',
        texte: 'Retrouve toutes tes transactions. Utilise les filtres pour analyser un mois ou une catégorie précise.',
    },
    stats: {
        emoji: '📊',
        titre: 'Tes statistiques',
        texte: 'Visualise tes habitudes financières. Courbe des dépenses, camembert par catégorie, et barres comparatives.',
    },
    categories: {
        emoji: '🏷️',
        titre: 'Gérer tes catégories',
        texte: 'Crée des catégories personnalisées avec des couleurs. Supprimer une catégorie ne supprime pas les transactions liées.',
    },
    settings: {
        emoji: '⚙️',
        titre: 'Paramètres',
        texte: 'Change ta devise d\'affichage et exporte tes données en PDF. Tes préférences sont sauvegardées localement sur ton appareil.',
    },
}

function showOnboarding(page) {
    const seen = JSON.parse(localStorage.getItem('onboarding') || '{}')
    if (seen[page]) return

    const msg = ONBOARDING[page]
    if (!msg) return

    seen[page] = true
    localStorage.setItem('onboarding', JSON.stringify(seen))

    // Délai 600ms pour laisser la page se charger
    setTimeout(() => {
        const layout = document.querySelector('.app-layout')
        if (!layout) return

        const overlay = document.createElement('div')
        overlay.className = 'ob-overlay'
        overlay.innerHTML = `
            <div class="ob-card">
                <div class="ob-emoji">${msg.emoji}</div>
                <div class="ob-title">${msg.titre}</div>
                <div class="ob-text">${msg.texte}</div>
                <button class="ob-btn"
                    onclick="this.closest('.ob-overlay').remove()">
                    J'ai compris !
                </button>
            </div>
        `
        layout.appendChild(overlay)
    }, 600)
}