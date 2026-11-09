// ===== Theme switcher =====
const body = document.body;
const toggleBtn = document.getElementById('themeToggleBtn');
const panel = document.getElementById('themePanel');
const swatches = document.querySelectorAll('.swatch');
const widget = document.getElementById('themeWidget');

// Muat tema tersimpan (kalau ada), default: clay
const savedTheme = localStorage.getItem('portfolio-theme') || 'clay';
body.setAttribute('data-theme', savedTheme);

function setThemePanelOpen(open) {
    panel.classList.toggle('is-open', open);
    panel.inert = !open;
    toggleBtn.setAttribute('aria-expanded', String(open));
}

toggleBtn.addEventListener('click', () => {
    setThemePanelOpen(!panel.classList.contains('is-open'));
});

swatches.forEach((btn) => {
    btn.addEventListener('click', () => {
        const theme = btn.dataset.theme;
        body.setAttribute('data-theme', theme);
        localStorage.setItem('portfolio-theme', theme);
    });
});

// Tutup panel kalau klik di luar widget
document.addEventListener('click', (e) => {
    if (!widget.contains(e.target)) {
        setThemePanelOpen(false);
    }
});

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && panel.classList.contains('is-open')) {
        setThemePanelOpen(false);
        toggleBtn.focus();
    }
});
