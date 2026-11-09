(() => {
  const list = document.getElementById('projects-list');
  if (!list) return;
  const search = document.getElementById('project-search');
  const input = search.querySelector('[name=title]');
  const form = document.getElementById('project-form');
  const modal = document.getElementById('project-modal');
  const records = new Map();
  let controller, timer, editing = null;

  function card(record, index) {
    const item = listElement('article', 'project-entry');
    const number = String(index + 1).padStart(2, '0');
    const media = listElement('div', 'project-visual');
    const imageURL = record.project_image_url && safeMediaUrl(record.project_image_url);
    if (imageURL) {
      const image = document.createElement('img');
      image.src = imageURL; image.alt = record.title; image.loading = 'lazy';
      image.addEventListener('error', () => {
        image.remove();
        media.classList.add('project-visual--type');
      });
      media.append(image);
    } else {
      media.classList.add('project-visual--type');
    }
    const specimen = listElement('div', 'project-specimen');
    specimen.setAttribute('aria-hidden', 'true');
    specimen.append(listElement('span', 'project-specimen-label', number),
      listElement('span', 'project-specimen-title', record.title),
      listElement('span', 'project-specimen-stack', record.tech_stack));
    media.append(specimen);
    const info = listElement('div', 'project-info');
    const meta = listElement('div', 'project-meta');
    meta.append(listElement('span', '', number), listElement('span', '', record.tech_stack));
    info.append(meta, listElement('h2', 'project-title', record.title), listElement('p', 'project-description', record.description));
    const url = record.project_url && safeMediaUrl(record.project_url);
    if (url) {
      const link = listElement('a', 'project-visit', 'Lihat project ↗');
      link.href = url; link.target = '_blank'; link.rel = 'noopener noreferrer'; info.append(link);
    }
    const actions = listElement('div', 'item-actions project-actions');
    if (list.dataset.authenticated === 'true') {
      const star = listElement('button', 'button button-like', `★ ${record.is_starred ? 'Batal Star' : 'Star'} (${record.star_count})`);
      star.type = 'button'; star.dataset.action = 'star'; star.dataset.id = record.id;
      star.setAttribute('aria-pressed', String(record.is_starred)); actions.append(star);
    } else {
      const login = listElement('a', 'button button-like', `Login untuk star (${record.star_count})`);
      login.href = list.dataset.loginUrl; actions.append(login);
    }
    if (record.starred_by_names) info.append(listElement('small', 'project-supporters', `Star oleh: ${record.starred_by_names}`));
    if (list.dataset.owner === 'true') {
      for (const [action, label] of [['edit', 'Edit'], ['delete', 'Hapus']]) {
        const button = listElement('button', 'button button-secondary', label);
        button.type = 'button'; button.dataset.action = action; button.dataset.id = record.id;
        actions.append(button);
      }
    }
    info.append(actions); item.append(media, info); return item;
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
      projects.forEach((project, index) => { records.set(project.id, project); list.append(card(project, index)); });
      if (!projects.length) {
        const empty = listElement('div', 'empty-state work-empty');
        empty.append(listElement('h2', '', input.value.trim() ? 'Tidak ada project.' : 'Belum ada project.'));
        list.append(empty);
      }
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
  if (form) bindApiFormValidation(form);
  form?.addEventListener('submit', async event => {
    event.preventDefault();
    const button = form.querySelector('[type=submit]');
    if (button.disabled) return;
    clearApiFormErrors(form);
    button.disabled = true;
    const payload = {};
    for (const key of ['title', 'description', 'tech_stack', 'project_url', 'project_image_url']) {
      payload[key] = form.elements.namedItem(key).value;
    }
    try {
      await writeResource(editing ? `${list.dataset.apiUrl}${editing}/` : list.dataset.apiUrl,
        editing ? 'PATCH' : 'POST', payload);
      modal.hidePopover(); showToast('Sukses', 'Project tersimpan.', 'success'); await refresh();
    } catch (error) {
      showApiFormErrors(form, error);
      showToast('Periksa isian', error.message, 'error');
    }
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
