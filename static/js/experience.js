function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function sanitizeText(value) {
  return String(value ?? '').replace(/[<>]/g, function (char) {
    return char === '<' ? '&lt;' : '&gt;';
  });
}

function getExperienceFields(experience) {
  if (experience && experience.fields) {
    return {
      ...experience.fields,
      pk: experience.pk || experience.fields.pk || experience.fields.id
    };
  }
  return experience || {};
}

function buildExperienceCardElement(experience) {
  const record = getExperienceFields(experience);
  const item = document.createElement('li');
  item.className = 'timeline-item';

  const date = document.createElement('div');
  date.className = 'timeline-date';
  const started = record.started || 'Unknown';
  const ended = record.is_ongoing ? 'Present' : (record.ended || 'Present');
  date.textContent = `${started} — ${ended}`;

  const body = document.createElement('div');
  body.className = 'timeline-body';

  const details = document.createElement('details');
  details.className = 'exp-details';

  const summary = document.createElement('summary');
  summary.className = 'exp-summary';

  const title = document.createElement('h3');
  title.className = 'exp-title';
  title.textContent = record.title || 'Judul tidak tersedia';

  const category = document.createElement('span');
  category.textContent = record.category_display || 'Uncategorized';

  title.appendChild(category);
  summary.appendChild(title);
  details.appendChild(summary);

  const content = document.createElement('div');
  content.className = 'exp-content';

  const status = document.createElement('p');
  status.className = 'timeline-loc';
  status.textContent = record.is_ongoing ? 'Sedang berlangsung' : 'Selesai';

  const description = document.createElement('p');
  description.textContent = record.description || '';

  content.appendChild(status);
  content.appendChild(description);

  const media = Array.isArray(record.media) ? record.media : [];
  if (media.length) {
    const mediaWrap = document.createElement('div');
    mediaWrap.className = 'exp-media';

    media.forEach(function (file) {
      const fileUrl = file && file.url ? file.url : '#';
      const fileName = file && file.filename ? file.filename : 'file';

      if (file && file.is_image) {
        const imgLink = document.createElement('a');
        imgLink.href = fileUrl;
        imgLink.target = '_blank';
        imgLink.rel = 'noopener noreferrer';
        imgLink.className = 'exp-thumb-link';

        const img = document.createElement('img');
        img.src = fileUrl;
        img.alt = sanitizeText(record.title || 'Gallery image');
        img.loading = 'lazy';
        img.className = 'exp-thumb';

        imgLink.appendChild(img);
        mediaWrap.appendChild(imgLink);
        return;
      }

      if (file && file.is_video) {
        const video = document.createElement('video');
        video.src = fileUrl;
        video.className = 'exp-thumb';
        video.controls = true;
        video.preload = 'metadata';
        mediaWrap.appendChild(video);
        return;
      }

      const fileLink = document.createElement('a');
      fileLink.href = fileUrl;
      fileLink.target = '_blank';
      fileLink.rel = 'noopener noreferrer';
      fileLink.className = 'exp-file';
      fileLink.textContent = fileName;
      mediaWrap.appendChild(fileLink);
    });

    content.appendChild(mediaWrap);
  }

  const pk = record.pk || record.id || '';
  const canManage = window.canManageExperience ?? (
    document.getElementById('experience-list')?.dataset.canManage === 'true'
  );
  if (canManage && pk) {
    const actions = document.createElement('p');
    actions.className = 'item-actions';

    const editLink = document.createElement('a');
    editLink.href = `/experience/${pk}/edit/`;
    editLink.className = 'button button-secondary';
    editLink.textContent = 'Edit';

    const deleteWrap = document.createElement('div');
    deleteWrap.className = 'delete-modal';
    deleteWrap.id = `delete-${pk}`;
    deleteWrap.setAttribute('popover', 'auto');
    deleteWrap.setAttribute('role', 'dialog');
    deleteWrap.setAttribute('aria-modal', 'true');

    const deleteBackdrop = document.createElement('button');
    deleteBackdrop.type = 'button';
    deleteBackdrop.className = 'delete-modal__backdrop';
    deleteBackdrop.setAttribute('popovertarget', `delete-${pk}`);
    deleteBackdrop.setAttribute('popovertargetaction', 'hide');
    deleteBackdrop.setAttribute('aria-label', 'Tutup konfirmasi hapus');

    const deleteContent = document.createElement('div');
    deleteContent.className = 'delete-modal__content';

    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'delete-modal__close';
    closeButton.setAttribute('popovertarget', `delete-${pk}`);
    closeButton.setAttribute('popovertargetaction', 'hide');
    closeButton.setAttribute('aria-label', 'Tutup konfirmasi hapus');
    closeButton.textContent = '×';

    const modalTitle = document.createElement('h2');
    modalTitle.id = `delete-modal-title-${pk}`;
    modalTitle.textContent = 'Hapus?';

    const confirmText = document.createElement('p');
    confirmText.textContent = 'Apakah Anda yakin ingin menghapus pengalaman ini?';

    const modalActions = document.createElement('div');
    modalActions.className = 'delete-modal__actions';

    const cancelButton = document.createElement('button');
    cancelButton.type = 'button';
    cancelButton.className = 'button button-secondary';
    cancelButton.setAttribute('popovertarget', `delete-${pk}`);
    cancelButton.setAttribute('popovertargetaction', 'hide');
    cancelButton.textContent = 'Batal';

    const form = document.createElement('form');
    form.method = 'post';
    form.action = `/experience/${pk}/delete/`;

    const csrf = document.createElement('input');
    csrf.type = 'hidden';
    csrf.name = 'csrfmiddlewaretoken';
    csrf.value = document.cookie
      .split('; ')
      .find((part) => part.startsWith('csrftoken='))
      ?.split('=')[1] || '';

    const confirmDelete = document.createElement('button');
    confirmDelete.type = 'submit';
    confirmDelete.className = 'button button-danger';
    confirmDelete.textContent = 'Ya, Hapus';

    form.appendChild(csrf);
    form.appendChild(confirmDelete);
    modalActions.appendChild(cancelButton);
    modalActions.appendChild(form);

    deleteContent.appendChild(closeButton);
    deleteContent.appendChild(modalTitle);
    deleteContent.appendChild(confirmText);
    deleteContent.appendChild(modalActions);

    deleteWrap.appendChild(deleteBackdrop);
    deleteWrap.appendChild(deleteContent);

    const deleteButton = document.createElement('button');
    deleteButton.type = 'button';
    deleteButton.className = 'button button-danger';
    deleteButton.setAttribute('popovertarget', `delete-${pk}`);
    deleteButton.setAttribute('aria-label', `Hapus ${record.title || 'pengalaman'}`);
    deleteButton.textContent = 'Hapus';

    actions.appendChild(editLink);
    actions.appendChild(deleteButton);

    content.appendChild(actions);
    content.appendChild(deleteWrap);
  }

  details.appendChild(content);
  body.appendChild(details);
  item.appendChild(date);
  item.appendChild(body);

  return item;
}

function renderExperienceList(listEl, experiences) {
  if (!listEl) return;

  listEl.innerHTML = '';

  if (!Array.isArray(experiences) || experiences.length === 0) {
    const empty = document.createElement('p');
    empty.className = 'empty-state';
    empty.textContent = 'Belum ada pengalaman yang ditambahkan.';
    listEl.appendChild(empty);
    return;
  }

  experiences.forEach(function (experience) {
    listEl.appendChild(buildExperienceCardElement(experience));
  });
}

async function fetchExperienceData(query = '') {
  const listEl = document.getElementById('experience-list');
  const apiUrl = listEl?.dataset.apiUrl || '/api/experience/';
  const url = new URL(apiUrl, window.location.origin);
  if (query) {
    url.searchParams.set('title', query);
  }

  const response = await fetch(url.toString(), {
    headers: { 'Accept': 'application/json' }
  });

  if (!response.ok) {
    throw new Error('Gagal mengambil data experience');
  }

  return response.json();
}

function bindExperienceSearch() {
  const form = document.querySelector('[data-live-search]');
  const listEl = document.getElementById('experience-list');
  if (!form || !listEl) return;

  const input = form.querySelector('input[type="search"]');
  if (!input) return;

  let timer = null;
  const delay = Number(form.dataset.debounceMs || 450);

  const refresh = function () {
    const query = input.value.trim();
    fetchExperienceData(query)
      .then(function (items) {
        renderExperienceList(listEl, items);
      })
      .catch(function () {
        const empty = document.createElement('p');
        empty.className = 'empty-state';
        empty.textContent = 'Tidak dapat memuat data experience.';
        listEl.innerHTML = '';
        listEl.appendChild(empty);
      });
  };

  input.addEventListener('input', function () {
    window.clearTimeout(timer);
    timer = window.setTimeout(refresh, delay);
  });

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    refresh();
  });
}

document.addEventListener('DOMContentLoaded', function () {
  bindExperienceSearch();

  const listEl = document.getElementById('experience-list');
  if (!listEl) return;

  const query = new URLSearchParams(window.location.search).get('title') || '';
  fetchExperienceData(query)
    .then(function (items) {
      renderExperienceList(listEl, items);
    })
    .catch(function () {
      const empty = document.createElement('p');
      empty.className = 'empty-state';
      empty.textContent = 'Tidak dapat memuat data experience.';
      listEl.innerHTML = '';
      listEl.appendChild(empty);
    });
});

window.buildExperienceCardElement = buildExperienceCardElement;
window.escapeHtml = escapeHtml;
window.sanitizeText = sanitizeText;
window.fetchExperienceData = fetchExperienceData;
window.renderExperienceList = renderExperienceList;
