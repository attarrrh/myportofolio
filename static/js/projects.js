(() => {
  const list = document.getElementById('projects-list');
  if (!list) return;
  const search = document.getElementById('project-search');
  const input = search.querySelector('[name=title]');
  const form = document.getElementById('project-form');
  const modal = document.getElementById('project-modal');
  const records = new Map();
  let controller, timer, editing = null;

  function card(record) {
    const item = listElement('article', 'gallery-card');
    const imageURL = record.project_image_url && safeMediaUrl(record.project_image_url);
    if (imageURL) {
      const media = listElement('div', 'gallery-media');
      const image = document.createElement('img');
      image.src = imageURL; image.alt = record.title; image.loading = 'lazy';
      media.append(image); item.append(media);
    }
    const info = listElement('div', 'gallery-info');
    info.append(listElement('h2', '', record.title), listElement('p', '', record.description),
      listElement('p', 'gallery-category', record.tech_stack));
    const url = record.project_url && safeMediaUrl(record.project_url);
    if (url) {
      const link = listElement('a', 'button button-secondary', 'Lihat project');
      link.href = url; link.target = '_blank'; link.rel = 'noopener noreferrer'; info.append(link);
    }
    const actions = listElement('div', 'item-actions');
    if (list.dataset.authenticated === 'true') {
      const star = listElement('button', 'button button-like', `★ ${record.is_starred ? 'Batal Star' : 'Star'} (${record.star_count})`);
      star.type = 'button'; star.dataset.action = 'star'; star.dataset.id = record.id;
      star.setAttribute('aria-pressed', String(record.is_starred)); actions.append(star);
    } else {
      const login = listElement('a', 'button button-like', `Login untuk star (${record.star_count})`);
      login.href = list.dataset.loginUrl; actions.append(login);
    }
    if (record.starred_by_names) info.append(listElement('small', '', `Star oleh: ${record.starred_by_names}`));
    if (list.dataset.owner === 'true') {
      for (const [action, label] of [['edit', 'Edit'], ['delete', 'Hapus']]) {
        const button = listElement('button', 'button button-secondary', label);
        button.type = 'button'; button.dataset.action = action; button.dataset.id = record.id;
        actions.append(button);
      }
    }
    info.append(actions); item.append(info); return item;
  }

  async function refresh() {
    controller?.abort();
    const current = new AbortController(); controller = current;
    list.setAttribute('aria-busy', 'true');
    list.replaceChildren(listElement('p', 'empty-state', 'Memuat projects...'));
    const url = new URL(list.dataset.apiUrl, location.origin);
    if (input.value.trim()) url.searchParams.set('title', input.value.trim());
    try {
      const response = await fetch(url, {signal: current.signal, headers: {Accept: 'application/json'}});
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const projects = await response.json();
      if (current.signal.aborted) return;
      records.clear(); list.replaceChildren();
      for (const project of projects) { records.set(project.id, project); list.append(card(project)); }
      if (!projects.length) list.append(listElement('p', 'empty-state', 'Tidak ada project yang sesuai.'));
    } catch (error) {
      if (current.signal.aborted) return;
      list.replaceChildren(listElement('p', 'empty-state', 'Gagal memuat projects. Coba cari kembali.'));
      showToast('Gagal memuat data', error.message, 'error');
    } finally { if (controller === current) list.setAttribute('aria-busy', 'false'); }
  }

  input.addEventListener('input', () => {
    clearTimeout(timer); controller?.abort(); timer = setTimeout(refresh, 300);
  });
  search.addEventListener('submit', event => { event.preventDefault(); clearTimeout(timer); refresh(); });
  modal?.addEventListener('beforetoggle', event => {
    if (event.newState === 'closed') { editing = null; form.reset(); }
  });
  document.querySelector('[popovertarget="project-modal"]')?.addEventListener('click', () => {
    editing = null; form.reset(); document.getElementById('project-modal-title').textContent = 'Tambah Project';
  });
  form?.addEventListener('submit', async event => {
    event.preventDefault();
    const button = form.querySelector('[type=submit]');
    if (button.disabled) return;
    button.disabled = true;
    const payload = {};
    for (const key of ['title', 'description', 'tech_stack', 'project_url', 'project_image_url']) {
      payload[key] = form.elements.namedItem(key).value;
    }
    try {
      await writeResource(editing ? `${list.dataset.apiUrl}${editing}/` : list.dataset.apiUrl,
        editing ? 'PATCH' : 'POST', payload);
      modal.hidePopover(); showToast('Sukses', 'Project tersimpan.', 'success'); await refresh();
    } catch (error) { showToast('Periksa isian', error.message, 'error'); }
    finally { button.disabled = false; }
  });
  list.addEventListener('click', async event => {
    const button = event.target.closest('button[data-action]');
    if (!button || button.disabled) return;
    const {action, id} = button.dataset;
    if (action === 'edit') {
      editing = id;
      const record = records.get(id);
      for (const key of ['title', 'description', 'tech_stack', 'project_url', 'project_image_url']) form.elements.namedItem(key).value = record[key] || '';
      document.getElementById('project-modal-title').textContent = 'Edit Project';
      modal.showPopover(); return;
    }
    if (action === 'delete' && !window.confirm('Hapus project ini?')) return;
    button.disabled = true;
    try {
      await writeResource(`${list.dataset.apiUrl}${encodeURIComponent(id)}/${action === 'star' ? 'star/' : ''}`,
        action === 'star' ? 'POST' : 'DELETE');
      showToast('Sukses', action === 'star' ? 'Star diperbarui.' : 'Project dihapus.', 'success'); await refresh();
    } catch (error) { showToast('Permintaan gagal', error.message, 'error'); }
    finally { button.disabled = false; }
  });
  refresh();
})();
