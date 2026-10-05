// All server text is inserted through textContent, never interpolated into HTML.
function listElement(tag, className, text) {
  const element = document.createElement(tag);
  element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

function safeMediaUrl(value) {
  try {
    const url = new URL(value, window.location.origin);
    return ['http:', 'https:'].includes(url.protocol) ? url.href : '';
  } catch (_) {
    return '';
  }
}

function getCsrfToken() {
  return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

function buildGalleryCard(item, list) {
  const record = item.fields;
  const pk = encodeURIComponent(item.pk);
  const card = listElement('div', 'gallery-card');
  const media = listElement('div', 'gallery-media');
  const source = safeMediaUrl(record.media_url);
  if (source) {
    const visual = document.createElement(record.media_type === 'video' ? 'video' : 'img');
    visual.src = source;
    if (record.media_type === 'video') {
      visual.controls = true;
      visual.preload = 'metadata';
    } else {
      visual.alt = record.title;
      visual.loading = 'lazy';
    }
    media.appendChild(visual);
  }
  const info = listElement('div', 'gallery-info');
  info.appendChild(listElement('span', 'gallery-category', record.category_display));
  info.appendChild(listElement('h3', '', record.title));
  if (record.caption) info.appendChild(listElement('p', '', record.caption));

  const star = listElement('button', 'button button-like');
  star.type = 'button';
  const updateStar = function (state) {
    star.classList.toggle('is-liked', state.is_starred);
    star.setAttribute('aria-pressed', String(state.is_starred));
    star.textContent = `★ ${state.is_starred ? 'Batal Star' : 'Star'} (${state.star_count})`;
  };
  updateStar(record);
  if (list.dataset.authenticated !== 'true') {
    star.disabled = true;
    star.title = 'Login untuk memberi star';
  }
  star.addEventListener('click', async function () {
    star.disabled = true;
    try {
      const response = await fetch(`/about/${pk}/like/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrfToken(), 'Accept': 'application/json' }
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || 'Gagal memperbarui star.');
      updateStar(result);
    } catch (error) {
      showToast('Gagal memperbarui star', error.message, 'error');
    } finally {
      star.disabled = false;
    }
  });
  info.appendChild(star);

  if (list.dataset.canManage === 'true') {
    const actions = listElement('p', 'item-actions');
    const edit = listElement('a', 'button button-secondary', 'Edit');
    edit.href = `/about/${pk}/edit/`;
    actions.appendChild(edit);
    const form = document.createElement('form');
    form.method = 'post';
    form.action = `/about/${pk}/delete/`;
    const token = document.createElement('input');
    token.type = 'hidden';
    token.name = 'csrfmiddlewaretoken';
    token.value = getCsrfToken();
    const remove = listElement('button', 'button button-danger', 'Hapus');
    remove.type = 'submit';
    form.append(token, remove);
    form.addEventListener('submit', function (event) {
      if (!window.confirm(`Hapus ${record.title}?`)) event.preventDefault();
    });
    info.append(actions, form);
  }
  card.append(media, info);
  return card;
}

document.addEventListener('DOMContentLoaded', function () {
  const list = document.querySelector('[data-list-kind]');
  if (!list) return;
  const search = document.querySelector('[data-live-search]');
  const input = search.querySelector('input[type=search]');
  const kind = list.dataset.listKind;
  let timer;
  let controller;

  function showState(message) {
    const state = listElement(kind === 'experience' ? 'li' : 'p', 'empty-state', message);
    state.setAttribute('role', 'status');
    list.replaceChildren(state);
  }

  async function refresh() {
    controller?.abort();
    const current = new AbortController();
    controller = current;
    list.setAttribute('aria-busy', 'true');
    showState(kind === 'experience' ? 'Memuat data experience...' : 'Memuat data galeri...');
    const url = new URL(list.dataset.apiUrl, window.location.origin);
    const query = input.value.trim();
    if (query) url.searchParams.set('title', query);
    try {
      const response = await fetch(url, {
        signal: current.signal,
        headers: { 'Accept': 'application/json' }
      });
      if (!response.ok) throw new Error('Gagal memuat data.');
      const items = await response.json();
      if (current.signal.aborted) return false;
      if (!Array.isArray(items)) throw new Error('Respons data tidak valid.');
      list.replaceChildren();
      if (!items.length) {
        showState(query ? 'Tidak ada data dengan judul tersebut.' :
          (kind === 'experience' ? 'Belum ada pengalaman yang ditambahkan.' : 'Belum ada item galeri yang ditambahkan.'));
      } else {
        for (const item of items) {
          list.appendChild(kind === 'experience' ? buildExperienceCardElement(item) : buildGalleryCard(item, list));
        }
      }
      return true;
    } catch (error) {
      if (current.signal.aborted) return false;
      showState('Tidak dapat memuat data. Silakan coba lagi.');
      showToast('Gagal memuat data', 'Periksa koneksi lalu coba cari kembali.', 'error');
      return false;
    } finally {
      if (controller === current) list.setAttribute('aria-busy', 'false');
    }
  }

  input.addEventListener('input', function () {
    clearTimeout(timer);
    controller?.abort();
    timer = setTimeout(refresh, Number(search.dataset.debounceMs || 450));
  });
  search.addEventListener('submit', function (event) {
    event.preventDefault();
    clearTimeout(timer);
    refresh();
  });

  const form = document.getElementById(kind === 'experience' ? 'experience-form' : 'gallery-item-form');
  if (form) form.addEventListener('submit', async function (event) {
    event.preventDefault();
    const submit = form.querySelector('[type=submit]');
    if (submit.disabled) return;
    submit.disabled = true;
    try {
      const response = await fetch(form.dataset.ajaxUrl, {
        method: 'POST',
        body: new FormData(form),
        headers: { 'X-CSRFToken': getCsrfToken(), 'Accept': 'application/json' }
      });
      const result = await response.json();
      if (!response.ok) {
        const errors = Object.values(result.errors || {}).flat().map(error => error.message || error).join('\n');
        showToast('Gagal menambahkan data', errors || result.message || 'Periksa kembali isian form.', 'error');
        return;
      }
      form.closest('[popover]')?.hidePopover();
      form.reset();
      input.value = '';
      clearTimeout(timer);
      const loaded = await refresh();
      showToast('Sukses', result.message + (loaded ? '' : ' Daftar gagal dimuat, silakan coba cari kembali.'), 'success');
    } catch (_) {
      showToast('Gagal menambahkan data', 'Permintaan gagal. Periksa daftar sebelum mencoba lagi.', 'error');
    } finally {
      submit.disabled = false;
    }
  });
  refresh();
});
