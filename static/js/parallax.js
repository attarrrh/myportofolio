// ===== Parallax scroll: "Get to Know More" section =====
(function () {
  const bg = document.getElementById('parallaxBg');
  const section = document.getElementById('get-to-know');
  if (!bg || !section) return;

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReducedMotion) return;

  let ticking = false;

  function updateParallax() {
    const rect = section.getBoundingClientRect();
    const vh = window.innerHeight;

    // progress: -1 saat section di bawah layar, 0 saat di tengah, 1 saat di atas layar
    const progress = (vh / 2 - (rect.top + rect.height / 2)) / (vh / 2 + rect.height / 2);
    const offset = progress * 70; // seberapa jauh background bergerak (px)

    bg.style.transform = `translateY(${offset}px)`;
    ticking = false;
  }

  function onScroll() {
    if (!ticking) {
      requestAnimationFrame(updateParallax);
      ticking = true;
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
  updateParallax();
})();
