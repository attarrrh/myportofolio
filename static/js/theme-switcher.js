(() => {
// ===== Theme switcher =====
const body = document.body;
const toggleBtn = document.getElementById('themeToggleBtn');
const panel = document.getElementById('themePanel');
const swatches = document.querySelectorAll('.swatch');
const widget = document.getElementById('themeWidget');

// Invalid saved themes fall back to the same default used by the CSS.
const themes = new Set(Array.from(swatches, button => button.dataset.theme));
let savedTheme = 'cobalt';
try {
    const storedTheme = localStorage.getItem('portfolio-theme');
    if (themes.has(storedTheme)) savedTheme = storedTheme;
} catch (_) {
    // Theme selection still works when browser storage is unavailable.
}
body.setAttribute('data-theme', savedTheme);

function setThemePanelOpen(open) {
    panel.classList.toggle('is-open', open);
    panel.inert = !open;
    toggleBtn.setAttribute('aria-expanded', String(open));
}

setThemePanelOpen(false);

toggleBtn.addEventListener('click', () => {
    setThemePanelOpen(!panel.classList.contains('is-open'));
});

swatches.forEach((btn) => {
    btn.addEventListener('click', () => {
        const theme = btn.dataset.theme;
        body.setAttribute('data-theme', theme);
        try {
            localStorage.setItem('portfolio-theme', theme);
        } catch (_) {
            // Applying a color must not depend on saving the preference.
        }
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
})();
