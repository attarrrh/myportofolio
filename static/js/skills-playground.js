(() => {
  const stage = document.getElementById('skill-stage');
  if (!stage) return;
  const root = document.getElementById('skills');
  const filters = [...root.querySelectorAll('[data-skill-filter]')];
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const categories = {code: 'Code', tools: 'Tools', people: 'People'};
  const cards = [...stage.querySelectorAll('.skill-chip')].map(node => ({
    node, x: 0, y: 0, w: 0, h: 0, vx: 0, vy: 0, tilt: 0
  }));
  let frame = 0, lastTime = 0, dragging = null, visible = false, selected = cards[0];
  let filter = 'all', previousWidth = 0;
  const padding = 14;
  const activeCards = () => cards.filter(card => !card.node.hidden);
  const clamp = (value, min, max) => Math.max(min, Math.min(value, max));

  function paint(card) {
    card.node.style.transform = `translate3d(${card.x}px, ${card.y}px, 0) rotate(${card.tilt}deg)`;
  }

  function announce(message) {
    document.getElementById('skill-announcement').textContent = message;
  }

  function select(card, speak = true) {
    selected = card;
    for (const entry of cards) entry.node.setAttribute('aria-pressed', String(entry === card));
    const name = card.node.querySelector('.skill-chip-name').textContent;
    const level = card.node.dataset.level;
    document.getElementById('skill-name').textContent = name;
    document.getElementById('skill-category').textContent = categories[card.node.dataset.category];
    document.getElementById('skill-level-text').textContent = level + '%';
    const meter = document.getElementById('skill-level');
    meter.setAttribute('aria-valuenow', level);
    meter.setAttribute('aria-label', 'Penilaian pribadi untuk ' + name);
    meter.firstElementChild.style.width = level + '%';
    if (speak) announce(name + ', ' + categories[card.node.dataset.category] + '. Penilaian pribadi ' + level + ' persen.');
  }

  function stop() {
    cancelAnimationFrame(frame);
    frame = 0;
    for (const card of cards) { card.vx = 0; card.vy = 0; }
  }

  function contain(card) {
    const angle = card.tilt * Math.PI / 180;
    const extraX = Math.max(0, (Math.abs(card.w * Math.cos(angle)) + Math.abs(card.h * Math.sin(angle)) - card.w) / 2);
    const extraY = Math.max(0, (Math.abs(card.h * Math.cos(angle)) + Math.abs(card.w * Math.sin(angle)) - card.h) / 2);
    const minX = padding + extraX, minY = padding + extraY;
    const maxX = Math.max(minX, stage.clientWidth - card.w - padding - extraX);
    const maxY = Math.max(minY, stage.clientHeight - card.h - padding - extraY);
    if (card.x < minX || card.x > maxX) card.vx *= -.45;
    if (card.y < minY || card.y > maxY) card.vy *= -.45;
    card.x = clamp(card.x, minX, maxX);
    card.y = clamp(card.y, minY, maxY);
  }

  function scatter(entries, width, height) {
    let free = [{x: padding, y: padding, w: width - padding * 2, h: height - padding * 2}];
    const placements = [];
    // Larger cards go first, but their locations are not tied to DOM order or rows.
    const order = [...entries].sort((a, b) => b.w * b.h - a.w * a.h);
    for (const card of order) {
      const angle = card.tilt * Math.PI / 180;
      const w = Math.abs(card.w * Math.cos(angle)) + Math.abs(card.h * Math.sin(angle)) + 12;
      const h = Math.abs(card.h * Math.cos(angle)) + Math.abs(card.w * Math.sin(angle)) + 12;
      const choices = free.filter(rect => rect.w >= w && rect.h >= h).sort((a, b) => a.w * a.h - b.w * b.h);
      if (!choices.length) return null;
      const space = choices[Math.floor(Math.random() * Math.min(3, choices.length))];
      const box = {x: space.x + Math.random() * (space.w - w), y: space.y + Math.random() * (space.h - h), w, h};
      placements.push({card, x: box.x + (w - card.w) / 2, y: box.y + (h - card.h) / 2});
      const next = [];
      for (const rect of free) {
        if (box.x >= rect.x + rect.w || box.x + w <= rect.x || box.y >= rect.y + rect.h || box.y + h <= rect.y) {
          next.push(rect);
          continue;
        }
        if (box.x > rect.x) next.push({x: rect.x, y: rect.y, w: box.x - rect.x, h: rect.h});
        if (box.x + w < rect.x + rect.w) next.push({x: box.x + w, y: rect.y, w: rect.x + rect.w - box.x - w, h: rect.h});
        if (box.y > rect.y) next.push({x: rect.x, y: rect.y, w: rect.w, h: box.y - rect.y});
        if (box.y + h < rect.y + rect.h) next.push({x: rect.x, y: box.y + h, w: rect.w, h: rect.y + rect.h - box.y - h});
      }
      free = next.filter((rect, i) => !next.some((other, j) => i !== j &&
        other.x <= rect.x && other.y <= rect.y && other.x + other.w >= rect.x + rect.w && other.y + other.h >= rect.y + rect.h &&
        (other.w * other.h > rect.w * rect.h || j < i)));
    }
    return placements;
  }

  function arrange() {
    stop();
    dragging?.card.node.classList.remove('is-dragging');
    dragging = null;
    const width = stage.clientWidth;
    if (width <= padding * 2 + 12) return;
    const entries = activeCards();
    for (const card of entries) {
      card.node.style.maxWidth = Math.max(48, width - padding * 2 - 12) + 'px';
      card.w = card.node.offsetWidth;
      card.h = card.node.offsetHeight;
      card.tilt = (Math.random() - .5) * 24;
      const radians = card.tilt * Math.PI / 180;
      if (Math.abs(card.w * Math.cos(radians)) + Math.abs(card.h * Math.sin(radians)) + 12 > width - padding * 2) card.tilt = 0;
    }
    let height = parseFloat(getComputedStyle(stage).minHeight) || 390;
    let placements;
    // Give narrow screens extra room instead of stacking or clipping labels.
    for (let attempt = 0; attempt < 20; attempt++) {
      placements = scatter(entries, width, height);
      if (placements) break;
      height += 50;
    }
    if (!placements) {
      // Guaranteed readable fallback for unusually narrow containers.
      let y = padding;
      placements = entries.map(card => {
        card.tilt = 0;
        const placement = {card, x: (width - card.w) / 2, y};
        y += card.h + 24;
        return placement;
      });
      height = Math.max(height, y + padding);
    }
    stage.style.height = height + 'px';
    for (const {card, x, y} of placements) { card.x = x; card.y = y; contain(card); paint(card); }
    previousWidth = width;
  }

  // Lightweight inertia and rectangle collisions. The loop sleeps when movement
  // settles and is stopped when off-screen; no physics library or idle loop.
  function separate(entries) {
    for (let i = 0; i < entries.length; i++) {
      for (let j = i + 1; j < entries.length; j++) {
        const a = entries[i], b = entries[j];
        const dx = a.x + a.w / 2 - b.x - b.w / 2;
        const dy = a.y + a.h / 2 - b.y - b.h / 2;
        const overlapX = (a.w + b.w) / 2 + 6 - Math.abs(dx);
        const overlapY = (a.h + b.h) / 2 + 6 - Math.abs(dy);
        if (overlapX <= 0 || overlapY <= 0) continue;
        const axis = overlapX < overlapY ? 'x' : 'y';
        const velocity = axis === 'x' ? 'vx' : 'vy';
        const distance = (axis === 'x' ? overlapX : overlapY) + .2;
        const direction = (axis === 'x' ? dx : dy) >= 0 ? 1 : -1;
        const pinnedA = dragging?.card === a, pinnedB = dragging?.card === b;
        if (!pinnedA) a[axis] += distance * direction * (pinnedB ? 1 : .5);
        if (!pinnedB) b[axis] -= distance * direction * (pinnedA ? 1 : .5);
        const av = a[velocity], bv = b[velocity];
        if (!pinnedA) a[velocity] = bv * .65;
        if (!pinnedB) b[velocity] = av * .65;
      }
    }
  }

  function tick(time) {
    frame = 0;
    const dt = Math.min(2, (time - lastTime) / 16.67 || 1);
    lastTime = time;
    const entries = activeCards();
    for (const card of entries) {
      if (dragging?.card === card) continue;
      card.x += card.vx * dt;
      card.y += card.vy * dt;
      card.vx *= Math.pow(.94, dt);
      card.vy *= Math.pow(.94, dt);
    }
    separate(entries);
    for (const card of entries) { contain(card); paint(card); }
    if (visible && !motion.matches && (dragging || entries.some(card => Math.abs(card.vx) + Math.abs(card.vy) > .12))) {
      frame = requestAnimationFrame(tick);
    }
  }

  function animate() {
    if (frame || !visible || motion.matches) return;
    lastTime = performance.now();
    frame = requestAnimationFrame(tick);
  }

  for (const card of cards) {
    card.node.addEventListener('click', () => select(card));
    card.node.addEventListener('pointerdown', event => {
      if (!event.isPrimary || event.button !== 0) return;
      card.node.focus({preventScroll: true});
      select(card);
      const bounds = stage.getBoundingClientRect();
      dragging = {card, id: event.pointerId, offsetX: event.clientX - bounds.left - card.x,
        offsetY: event.clientY - bounds.top - card.y, time: performance.now()};
      card.node.setPointerCapture(event.pointerId);
      card.node.classList.add('is-dragging');
      card.vx = card.vy = 0;
      animate();
    });
    card.node.addEventListener('pointermove', event => {
      if (dragging?.card !== card || dragging.id !== event.pointerId) return;
      const bounds = stage.getBoundingClientRect();
      const x = event.clientX - bounds.left - dragging.offsetX;
      const y = event.clientY - bounds.top - dragging.offsetY;
      const now = performance.now();
      const dt = Math.max(8, now - dragging.time);
      card.vx = motion.matches ? 0 : clamp((x - card.x) * 16 / dt, -16, 16);
      card.vy = motion.matches ? 0 : clamp((y - card.y) * 16 / dt, -16, 16);
      card.x = x; card.y = y; dragging.time = now;
      contain(card); paint(card);
    });
    function release(event) {
      if (dragging?.card !== card || dragging.id !== event.pointerId) return;
      if (event.type !== 'pointerup') card.vx = card.vy = 0;
      dragging = null;
      card.node.classList.remove('is-dragging');
      if (card.node.hasPointerCapture(event.pointerId)) card.node.releasePointerCapture(event.pointerId);
      animate();
    }
    for (const event of ['pointerup', 'pointercancel', 'lostpointercapture']) card.node.addEventListener(event, release);
    card.node.addEventListener('keydown', event => {
      const steps = {ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1]};
      if (!steps[event.key]) return;
      event.preventDefault();
      stop();
      const [dx, dy] = steps[event.key];
      card.x += dx * (event.shiftKey ? 30 : 12);
      card.y += dy * (event.shiftKey ? 30 : 12);
      contain(card); paint(card); select(card, false);
      announce(card.node.querySelector('.skill-chip-name').textContent + ' digeser.');
    });
  }

  function applyFilter(category) {
    filter = category;
    for (const button of filters) button.setAttribute('aria-pressed', String(button.dataset.skillFilter === category));
    for (const card of cards) card.node.hidden = category !== 'all' && card.node.dataset.category !== category;
    if (selected.node.hidden) select(activeCards()[0], false);
    arrange();
    announce(activeCards().length + ' skill ditampilkan.');
  }
  for (const button of filters) button.addEventListener('click', () => applyFilter(button.dataset.skillFilter));
  document.getElementById('skill-reset').addEventListener('click', () => {
    applyFilter('all'); select(cards[0]);
  });
  document.getElementById('skill-shuffle').addEventListener('click', () => {
    const entries = activeCards();
    if (motion.matches) {
      // Instant rearrangement for people who opt out of animations.
      for (const card of entries) { card.x = stage.clientWidth - card.w - card.x; contain(card); paint(card); }
    } else {
      for (const card of entries) { card.vx = (Math.random() - .5) * 28; card.vy = (Math.random() - .5) * 24; }
      animate();
    }
    announce('Posisi kartu diacak.');
  });
  stage.classList.add('is-ready');
  arrange();
  document.fonts?.ready.then(() => arrange());
  new ResizeObserver(() => {
    if (Math.abs(stage.clientWidth - previousWidth) > 1) arrange();
  }).observe(stage);
  new IntersectionObserver(entries => {
    visible = entries[0].isIntersecting;
    if (!visible) stop();
  }).observe(stage);
  document.addEventListener('visibilitychange', () => { if (document.hidden) stop(); });
  motion.addEventListener('change', () => applyFilter(filter));
})();
