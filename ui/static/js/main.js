/**
 * Smart College Assistant — Main JavaScript
 * Global utilities: theme, auth state, toasts, loader.
 */

"use strict";

// ── Theme Management ──────────────────────────────────────────
function toggleTheme() {
  const html = document.documentElement;
  const current = html.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  document.getElementById('themeIcon').className =
    next === 'dark' ? 'bi bi-moon-stars-fill' : 'bi bi-sun-fill';
}

(function initTheme() {
  const saved = localStorage.getItem('theme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
  const icon = document.getElementById('themeIcon');
  if (icon) icon.className = saved === 'dark' ? 'bi bi-moon-stars-fill' : 'bi bi-sun-fill';
})();

// ── Page Loader ───────────────────────────────────────────────
window.addEventListener('load', () => {
  const loader = document.getElementById('page-loader');
  if (loader) {
    setTimeout(() => {
      loader.classList.add('hidden');
      setTimeout(() => loader.remove(), 500);
    }, 600);
  }
});

// ── Toast Notifications ───────────────────────────────────────
function showToast(message, type = 'info', duration = 4000) {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const colors = {
    success: '#22d3a5', danger: '#f87171',
    warning: '#fbbf24', info: '#38bdf8',
  };
  const icons = {
    success: 'bi-check-circle-fill', danger: 'bi-x-circle-fill',
    warning: 'bi-exclamation-triangle-fill', info: 'bi-info-circle-fill',
  };

  const id = 'toast-' + Date.now();
  const toastEl = document.createElement('div');
  toastEl.id = id;
  toastEl.innerHTML = `
    <div class="toast-custom d-flex align-items-center gap-2 p-3 mb-2">
      <i class="bi ${icons[type] || 'bi-info-circle-fill'}" style="color:${colors[type] || '#38bdf8'};font-size:1.1rem;"></i>
      <span style="flex:1;font-size:0.875rem;">${message}</span>
      <button onclick="this.closest('[id^=toast-]').remove()" style="background:none;border:none;color:var(--text-muted);cursor:pointer;padding:0;"><i class="bi bi-x-lg"></i></button>
    </div>
  `;

  container.appendChild(toastEl);
  toastEl.style.animation = 'slideInToast 0.3s ease';
  setTimeout(() => {
    toastEl.style.animation = 'fadeOutToast 0.3s ease forwards';
    setTimeout(() => toastEl.remove(), 300);
  }, duration);
}

// ── Auth State Management ─────────────────────────────────────
async function checkAuthState() {
  try {
    const res = await fetch('/api/auth/me', { credentials: 'include' });
    const data = await res.json();
    const navAuth = document.getElementById('navAuthSection');
    if (!navAuth) return;

    if (data.success && data.user) {
      const user = data.user;
      const roleBadge = { admin: '🛡️ Admin', student: '🎓 Student', faculty: '👨‍🏫 Faculty' };
      navAuth.innerHTML = `
        <div class="d-flex align-items-center gap-2">
          <a href="/dashboard" class="btn-outline-glow btn-sm" style="padding:6px 12px;">
            <i class="bi bi-speedometer2 me-1"></i>Dashboard
          </a>
          <div class="dropdown">
            <button class="btn-icon dropdown-toggle" data-bs-toggle="dropdown">
              <i class="bi bi-person-circle"></i>
            </button>
            <ul class="dropdown-menu glass-dropdown dropdown-menu-end">
              <li><div class="px-3 py-2 border-bottom border-opacity-25">
                <div class="fw-bold small">${user.profile?.name || user.username}</div>
                <div class="text-muted" style="font-size:0.75rem;">${roleBadge[user.role] || user.role}</div>
              </div></li>
              <li><a class="dropdown-item" href="/dashboard"><i class="bi bi-speedometer2 me-2"></i>Dashboard</a></li>
              <li><button class="dropdown-item text-danger" onclick="logout()"><i class="bi bi-box-arrow-right me-2"></i>Logout</button></li>
            </ul>
          </div>
        </div>
      `;
    } else {
      navAuth.innerHTML = `
        <a href="/login" class="btn-primary-glow btn-sm" style="padding:7px 16px;">
          <i class="bi bi-box-arrow-in-right me-1"></i>Login
        </a>
      `;
    }
  } catch (e) {
    console.warn('Auth check failed:', e);
  }
}

async function logout() {
  try {
    await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' });
    showToast('Logged out successfully.', 'success');
    setTimeout(() => { window.location.href = '/'; }, 800);
  } catch (e) {
    showToast('Logout failed.', 'danger');
  }
}

// ── Navbar Scroll Effect ──────────────────────────────────────
(function initNavbarScroll() {
  const nav = document.getElementById('mainNav');
  if (!nav) return;
  window.addEventListener('scroll', () => {
    nav.style.boxShadow = window.scrollY > 20 ? '0 8px 30px rgba(0,0,0,0.3)' : 'none';
  });
})();

// ── Auto-resize Textarea ──────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const textareas = document.querySelectorAll('textarea.chat-textarea');
  textareas.forEach(ta => {
    ta.addEventListener('input', function () {
      this.style.height = 'auto';
      this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });
  });

  // Initialize auth state in navbar
  checkAuthState();
});

// ── CSS Animations for Toasts ─────────────────────────────────
(function injectToastAnimations() {
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideInToast {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
    @keyframes fadeOutToast {
      to { transform: translateX(100%); opacity: 0; }
    }
  `;
  document.head.appendChild(style);
})();
