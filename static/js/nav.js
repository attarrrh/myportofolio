const navToggle = document.getElementById('navToggle');
const mainNav = document.getElementById('mainNav');

if (navToggle && mainNav) {
  const closeNav = function () {
    mainNav.classList.remove('is-open');
    navToggle.setAttribute('aria-expanded', 'false');
    navToggle.setAttribute('aria-label', 'Buka menu navigasi');
  };

  navToggle.addEventListener('click', function () {
    const isOpen = navToggle.getAttribute('aria-expanded') === 'true';
    navToggle.setAttribute('aria-expanded', String(!isOpen));
    navToggle.setAttribute('aria-label', isOpen ? 'Buka menu navigasi' : 'Tutup menu navigasi');
    mainNav.classList.toggle('is-open', !isOpen);
  });

  mainNav.addEventListener('click', function (event) {
    if (event.target.closest('a')) closeNav();
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
      closeNav();
      navToggle.focus();
    }
  });

  document.addEventListener('click', function (event) {
    if (!mainNav.contains(event.target) && !navToggle.contains(event.target)) closeNav();
  });

  window.addEventListener('resize', function () {
    if (window.innerWidth > 860) closeNav();
  });
}
