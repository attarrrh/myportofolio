document.addEventListener('DOMContentLoaded', () => {
  const list = document.getElementById('gallery-list');
  const viewer = document.getElementById('journal-viewer');
  if (!list || !viewer) return;
  const filters = [...document.querySelectorAll('[data-media-filter]')];
  const empty = document.getElementById('journal-filter-empty');
  let active = 'all';
  const applyFilter = () => {
    const cards = [...list.querySelectorAll('.gallery-card')];
    cards.forEach(card => { card.hidden = active !== 'all' && card.dataset.mediaType !== active; });
    empty.hidden = list.getAttribute('aria-busy') === 'true' || !cards.length || cards.some(card => !card.hidden);
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
