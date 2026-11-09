document.addEventListener('DOMContentLoaded', () => {
  const list = document.getElementById('gallery-list');
  const viewer = document.getElementById('journal-viewer');
  if (!list || !viewer) return;
  const filters = [...document.querySelectorAll('[data-media-filter]')];
  const empty = document.getElementById('journal-filter-empty');
  const positions = new WeakMap();
  let topLayer = 1;
  let dragged = null;
  let suppressClickUntil = 0;
  let layoutFrame;
  list.classList.add('is-playground');
  const clamp = (value, max) => Math.max(12, Math.min(value, Math.max(12, max)));
  const place = (card, x, y) => {
    const state = positions.get(card);
    state.x = clamp(x, list.clientWidth - card.offsetWidth - 12);
    state.y = clamp(y, list.offsetHeight - card.offsetHeight - 12);
    card.style.left = `${state.x}px`;
    card.style.top = `${state.y}px`;
  };
  function layout(reset = false, shuffle = false) {
    if (dragged) return;
    const cards = [...list.querySelectorAll('.gallery-card:not([hidden])')];
    if (!cards.length) { list.style.height = ''; return; }
    const lanes = list.clientWidth > 760 ? 3 : 2;
    const laneWidth = list.clientWidth / lanes;
    const bottoms = Array(lanes).fill(18);
    const defaults = [];
    if (shuffle) cards.sort(() => Math.random() - .5);
    cards.forEach((card, index) => {
      const lane = bottoms.indexOf(Math.min(...bottoms));
      const factor = shuffle ? .79 + Math.random() * .1 : [.88, .79, .84, .82][index % 4];
      card.style.width = `${Math.max(100, laneWidth * factor)}px`;
      const x = lane * laneWidth + (laneWidth - card.offsetWidth) / 2;
      const y = bottoms[lane] + (index % 3) * 14;
      defaults.push({card, x, y});
      bottoms[lane] = y + card.offsetHeight + 42;
      let state = positions.get(card);
      if (!state) {
        state = {x, y, moved: false};
        positions.set(card, state);
        bindDrag(card);
      }
      if (reset) state.moved = false;
      if (!state.moved) card.style.setProperty('--photo-angle', `${shuffle ? Math.random() * 8 - 4 : [-2, 2.5, -1, 3, -2.5][index % 5]}deg`);
    });
    list.style.height = `${Math.max(...bottoms) + 30}px`;
    defaults.forEach(({card, x, y}) => {
      const state = positions.get(card);
      place(card, state.moved ? state.x : x, state.moved ? state.y : y);
    });
  }
  const scheduleLayout = () => {
    cancelAnimationFrame(layoutFrame);
    layoutFrame = requestAnimationFrame(() => layout());
  };
  const cardObserver = new ResizeObserver(scheduleLayout);
  let previousWidth = 0;
  new ResizeObserver(() => {
    if (list.clientWidth !== previousWidth) {
      previousWidth = list.clientWidth;
      layout(true);
    }
  }).observe(list);
  function bindDrag(card) {
    const handle = document.createElement('button');
    handle.type = 'button';
    handle.className = 'journal-drag-handle';
    handle.textContent = '↔';
    handle.setAttribute('aria-label', `Geser ${card.querySelector('h3').textContent}`);
    handle.title = 'Geser · tombol panah';
    card.prepend(handle);
    card.addEventListener('dragstart', event => event.preventDefault());
    card.addEventListener('pointerdown', event => {
      if (!event.isPrimary || event.button !== 0) return;
      const fromHandle = event.target.closest('.journal-drag-handle');
      const fromPhoto = event.target.closest('[data-journal-photo]');
      if (!fromHandle && !(fromPhoto && event.pointerType === 'mouse')) return;
      const state = positions.get(card);
      dragged = {card, id: event.pointerId, startX: event.clientX, startY: event.clientY, x: state.x, y: state.y, moved: false};
      card.style.zIndex = String(++topLayer);
      // Capture on the original button so a simple photo click still opens it.
      dragged.capture = fromHandle || fromPhoto;
      dragged.capture.setPointerCapture(event.pointerId);
    });
    card.addEventListener('pointermove', event => {
      if (dragged?.card !== card || dragged.id !== event.pointerId) return;
      const dx = event.clientX - dragged.startX;
      const dy = event.clientY - dragged.startY;
      if (!dragged.moved && Math.hypot(dx, dy) < 6) return;
      dragged.moved = true;
      positions.get(card).moved = true;
      card.classList.add('is-dragging');
      place(card, dragged.x + dx, dragged.y + dy);
    });
    const release = event => {
      if (dragged?.card !== card || dragged.id !== event.pointerId) return;
      if (dragged.moved) suppressClickUntil = performance.now() + 350;
      card.classList.remove('is-dragging');
      dragged = null;
    };
    card.addEventListener('pointerup', release);
    card.addEventListener('pointercancel', release);
    card.addEventListener('lostpointercapture', release);
    handle.addEventListener('keydown', event => {
      const deltas = {ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1]};
      if (!deltas[event.key]) return;
      event.preventDefault();
      const state = positions.get(card);
      const [dx, dy] = deltas[event.key];
      const step = event.shiftKey ? 40 : 12;
      state.moved = true;
      card.style.zIndex = String(++topLayer);
      place(card, state.x + dx * step, state.y + dy * step);
    });
  }
  document.getElementById('journal-shuffle').addEventListener('click', () => layout(true, true));
  document.getElementById('journal-reset').addEventListener('click', () => layout(true));
  let active = 'all';
  const applyFilter = () => {
    cardObserver.disconnect();
    const cards = [...list.querySelectorAll('.gallery-card')];
    cards.forEach(card => { card.hidden = active !== 'all' && card.dataset.mediaType !== active; });
    empty.hidden = list.getAttribute('aria-busy') === 'true' || !cards.length || cards.some(card => !card.hidden);
    layout(true);
    cards.forEach(card => cardObserver.observe(card));
  };
  filters.forEach(button => button.addEventListener('click', () => {
    active = button.dataset.mediaFilter;
    filters.forEach(filter => filter.setAttribute('aria-pressed', String(filter === button)));
    applyFilter();
  }));
  list.addEventListener('portfolio:loaded', applyFilter);
  applyFilter();
  const content = viewer.querySelector('.journal-viewer-media');
  list.addEventListener('click', event => {
    if (performance.now() < suppressClickUntil) return;
    const photo = event.target.closest('[data-journal-photo]');
    if (!photo?.dataset.source) return;
    const image = document.createElement('img');
    image.src = photo.dataset.source;
    image.alt = photo.dataset.title;
    content.replaceChildren(image);
    viewer.querySelector('h2').textContent = photo.dataset.title;
    viewer.querySelector('p').textContent = photo.dataset.caption;
    viewer.showModal();
  });
  viewer.querySelector('.journal-viewer-close').addEventListener('click', () => viewer.close());
  viewer.addEventListener('click', event => {
    if (event.target !== viewer) return;
    const bounds = viewer.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) viewer.close();
  });
  viewer.addEventListener('close', () => content.replaceChildren());
});
