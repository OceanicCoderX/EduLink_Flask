/* ============================================================
   common.js — EduLink Shared JavaScript
   Handles: theme toggle, toast system, avatar rendering,
            profession badge helper, 10-min activity tracker,
            mobile nav active state, stack pop animation
   Loaded on every page via base.html
   ============================================================ */


/* ── Theme (already in script.js — kept for compatibility) ── */
// initializeTheme() already handled by script.js


/* ── Toast System ────────────────────────────────────────── */

function ensureToastContainer() {
    let c = document.getElementById('toast-container');
    if (!c) {
        c = document.createElement('div');
        c.id = 'toast-container';
        document.body.appendChild(c);
    }
    return c;
}

/**
 * Show a toast notification.
 * @param {string} message  - Text to display
 * @param {string} type     - 'success' | 'error' | 'info' | 'stack' | 'warning'
 * @param {number} duration - ms before auto-dismiss (default 3500)
 */
function showToast(message, type = 'info', duration = 3500) {
    const icons = {
        success: 'fa-check-circle',
        error:   'fa-exclamation-circle',
        info:    'fa-info-circle',
        stack:   'fa-layer-group',
        warning: 'fa-exclamation-triangle'
    };

    const container = ensureToastContainer();
    const toast     = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="fas ${icons[type] || 'fa-bell'} toast-icon"></i>
        <span class="toast-text">${message}</span>
        <button class="toast-close" onclick="dismissToast(this.parentElement)">
            <i class="fas fa-times"></i>
        </button>
    `;

    container.appendChild(toast);

    // Auto dismiss
    const timer = setTimeout(() => dismissToast(toast), duration);
    toast._timer = timer;

    return toast;
}

function dismissToast(toast) {
    if (!toast || toast._dismissed) return;
    toast._dismissed = true;
    clearTimeout(toast._timer);
    toast.classList.add('hide');
    setTimeout(() => toast.remove(), 350);
}

// Backward compat with old showNotification()
function showNotification(message) { showToast(message, 'info'); }


/* ── Stack Pop Animation ─────────────────────────────────── */

function showStackPop(amount = 1) {
    const el = document.createElement('div');
    el.className = 'stack-pop';
    el.textContent = `+${amount} Stack! 🔥`;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 2100);
}

function updateStackDisplay(newTotal) {
    // Update any .stack-counter elements on the page
    document.querySelectorAll('.stack-counter').forEach(el => {
        el.textContent = newTotal;
    });
    // Update sidebar stacks
    const sidebarStacks = document.getElementById('sidebarStackCount');
    if (sidebarStacks) sidebarStacks.textContent = newTotal;
}


/* ── Profession Badge Helper ─────────────────────────────── */

const PROFESSION_ICONS = {
    'Student':      '📚',
    'Teacher':      '🎓',
    'Individual':   '👤',
    'Professional': '💼',
    'Other':        '⭐'
};

/**
 * Get the CSS class for a profession badge.
 */
function getProfessionClass(profession) {
    const map = {
        'Student':      'badge-student',
        'Teacher':      'badge-teacher',
        'Individual':   'badge-individual',
        'Professional': 'badge-professional',
        'Other':        'badge-other'
    };
    return map[profession] || 'badge-other';
}

/**
 * Render a profession badge HTML string.
 */
function renderProfessionBadge(profession) {
    if (!profession) return '';
    const cls  = getProfessionClass(profession);
    const icon = PROFESSION_ICONS[profession] || '⭐';
    return `<span class="profession-badge ${cls}">${icon} ${profession}</span>`;
}


/* ── Avatar Renderer ─────────────────────────────────────── */

const AVATAR_EMOJIS = [
    '', '📚', '🦊', '🌊', '🔥', '⭐',
    '🌙', '🎯', '🚀', '💎', '🎨', '🌿', '⚡'
];

/**
 * Render avatar HTML for a given avatar_id and initials fallback.
 * @param {number} avatarId  - 1-12
 * @param {string} initials  - e.g. "K" (first letter of name)
 * @param {string} profilePicUrl - Optional full URL to an image
 * @returns {string} HTML
 */
function renderAvatarHtml(avatarId, initials, profilePicUrl) {
    if (profilePicUrl && profilePicUrl.trim() !== '' && !profilePicUrl.includes('undefined') && profilePicUrl !== '/static/') {
        let finalUrl = profilePicUrl;
        if (profilePicUrl.startsWith('images/') || profilePicUrl.startsWith('uploads/')) {
            finalUrl = '/static/' + profilePicUrl;
        }
        // Ensure finalUrl actually points to a file, not just a directory
        if (finalUrl.endsWith('/')) return renderFallbackAvatar(avatarId, initials);

        return `<img src="${finalUrl}" class="avatar-img" alt="Avatar" onerror="this.style.display='none'; this.parentElement.innerHTML = renderFallbackAvatar(${avatarId}, '${initials}')">`;
    }
    return renderFallbackAvatar(avatarId, initials);
}

function renderFallbackAvatar(avatarId, initials) {
    const id    = avatarId || 1;
    const emoji = AVATAR_EMOJIS[id] || '';
    const label = emoji || (initials || 'U').charAt(0).toUpperCase();
    return `<div class="svg-avatar avatar-${id}">${label}</div>`;
}

/**
 * Apply avatar to an element.
 */
function applyAvatar(element, avatarId, initials, profilePicUrl) {
    if (!element) return;
    element.innerHTML = renderAvatarHtml(avatarId, initials, profilePicUrl);
}


/* ── 10-Minute Activity Tracker (Rule 8a) ─────────────────── */

let _activityTimer = null;

function startActivityTracker() {
    // Only run if user is logged in (check for sidebar presence)
    if (!document.getElementById('sidebar')) return;

    // Ping every 10 minutes to award +1 Stack
    const TEN_MINUTES = 10 * 60 * 1000;

    _activityTimer = setInterval(async () => {
        try {
            const res  = await fetch('/api/award-focus-interval', { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                updateStackDisplay(data.new_total);
                showStackPop(1);
                showToast('+1 Stack for staying active! 🔥', 'stack', 4000);
            }
        } catch (e) {
            // Silently fail — user may have navigated away
        }
    }, TEN_MINUTES);
}

function stopActivityTracker() {
    if (_activityTimer) {
        clearInterval(_activityTimer);
        _activityTimer = null;
    }
}


/* ── Mobile Nav Active State ─────────────────────────────── */

function setMobileNavActive() {
    const path = window.location.pathname;
    document.querySelectorAll('.mobile-nav-item').forEach(item => {
        const href = item.getAttribute('href') || '';
        if (path === href || (href !== '/' && path.startsWith(href))) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}


/* ── Modal Helpers ───────────────────────────────────────── */

function openModal(modalId) {
    const el = document.getElementById(modalId);
    if (el) el.classList.add('active');
}

function closeModal(modalId) {
    const el = document.getElementById(modalId);
    if (el) el.classList.remove('active');
}

// Close modal when clicking overlay background
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal-overlay')) {
        e.target.classList.remove('active');
    }
});


/* ── Initialization ──────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', function() {
    setMobileNavActive();
    startActivityTracker();

    // Apply avatar to main avatar elements if data attributes exist
    document.querySelectorAll('[data-avatar-id]').forEach(el => {
        const id       = parseInt(el.dataset.avatarId) || 1;
        const initials = el.dataset.initials || 'U';
        const url      = el.dataset.avatarUrl || '';
        applyAvatar(el, id, initials, url);
    });
});

// Stop tracker on page unload
window.addEventListener('beforeunload', stopActivityTracker);
