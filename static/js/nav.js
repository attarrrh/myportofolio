const navToggle = document.getElementById('navToggle');
const mainNav = document.getElementById('mainNav');

if (navToggle && mainNav) {
  const closeNav = function () {
    mainNav.hidden = true;
    mainNav.classList.remove('is-open');
    navToggle.setAttribute('aria-expanded', 'false');
    navToggle.setAttribute('aria-label', 'Buka menu navigasi');
  };

  navToggle.addEventListener('click', function () {
    const isOpen = navToggle.getAttribute('aria-expanded') === 'true';
    mainNav.hidden = isOpen;
    navToggle.setAttribute('aria-expanded', String(!isOpen));
    navToggle.setAttribute('aria-label', isOpen ? 'Buka menu navigasi' : 'Tutup menu navigasi');
    mainNav.classList.toggle('is-open', !isOpen);
  });

  mainNav.addEventListener('click', function (event) {
    if (event.target.closest('a')) closeNav();
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && !mainNav.hidden) {
      closeNav();
      navToggle.focus();
    }
  });

  document.addEventListener('click', function (event) {
    if (!mainNav.contains(event.target) && !navToggle.contains(event.target)) closeNav();
  });

  document.addEventListener('focusin', function (event) {
    if (!mainNav.contains(event.target) && event.target !== navToggle) closeNav();
  });
  mainNav.querySelectorAll('a').forEach(link => {
    if (new URL(link.href).pathname === window.location.pathname) link.setAttribute('aria-current', 'page');
  });
}
