// ===== Theme switcher =====
const body = document.body;
const toggleBtn = document.getElementById('themeToggleBtn');
const panel = document.getElementById('themePanel');
const swatches = document.querySelectorAll('.swatch');
const widget = document.getElementById('themeWidget');

// Muat tema tersimpan (kalau ada), default: clay
const savedTheme = localStorage.getItem('portfolio-theme') || 'clay';
body.setAttribute('data-theme', savedTheme);

toggleBtn.addEventListener('click', () => {
    panel.classList.toggle('is-open');
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
        panel.classList.remove('is-open');
    }
});
