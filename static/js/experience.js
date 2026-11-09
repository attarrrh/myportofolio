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
  item.className = 'timeline-item experience-entry';

  const date = document.createElement('div');
  date.className = 'timeline-date';
  const started = record.started || '';
  const ended = record.is_ongoing ? 'Present' : (record.ended || 'Present');
  date.textContent = started ? started + ' \u2014 ' + ended : (record.is_ongoing ? 'Saat ini' : ended);

  const body = document.createElement('div');
  body.className = 'timeline-body';

  const details = document.createElement('details');
  details.className = 'exp-details';

  const summary = document.createElement('summary');
  summary.className = 'exp-summary';

  const title = document.createElement('h3');
  title.className = 'exp-title';
  title.textContent = record.title || 'Judul tidak tersedia';

  const meta = document.createElement('div');
  meta.className = 'experience-meta';
  const category = document.createElement('span');
  category.className = 'experience-category';
  category.textContent = record.category_display || 'Experience';
  const state = document.createElement('span');
  state.className = record.is_ongoing ? 'experience-status is-current' : 'experience-status';
  state.textContent = record.is_ongoing ? 'Berlangsung' : 'Selesai';
  meta.append(category, state);
  const preview = document.createElement('p');
  preview.className = 'experience-preview';
  preview.textContent = record.description || '';
  const indicator = document.createElement('span');
  indicator.className = 'experience-expand';
  indicator.setAttribute('aria-hidden', 'true');
  indicator.textContent = '+';
  summary.append(meta, title, preview, indicator);
  details.appendChild(summary);

  const content = document.createElement('div');
  content.className = 'exp-content';

  const description = document.createElement('p');
  description.textContent = record.description || '';

  content.appendChild(description);

  const media = Array.isArray(record.media) ? record.media : [];
  if (media.length) {
    const mediaWrap = document.createElement('div');
    mediaWrap.className = 'exp-media';

    media.forEach(function (file) {
      const fileUrl = file && file.url ? safeMediaUrl(file.url) : '';
      if (!fileUrl) return;
      const fileName = file && file.filename ? file.filename : 'file';

      if (file && file.is_image) {
        const imgLink = document.createElement('a');
        imgLink.href = fileUrl;
        imgLink.target = '_blank';
        imgLink.rel = 'noopener noreferrer';
        imgLink.className = 'exp-thumb-link';

        const img = document.createElement('img');
        img.src = fileUrl;
        img.alt = record.title || 'Gallery image';
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
    form.addEventListener('submit', async event => {
      event.preventDefault();
      if (confirmDelete.disabled) return;
      confirmDelete.disabled = true;
      try {
        const list = document.getElementById('experience-list');
        await writeResource(`${list.dataset.apiUrl}${encodeURIComponent(pk)}/`, 'DELETE');
        list.dispatchEvent(new Event('portfolio:refresh'));
        showToast('Sukses', 'Experience dihapus.', 'success');
      } catch (error) { showToast('Gagal menghapus', error.message, 'error'); }
      finally { confirmDelete.disabled = false; }
    });
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
    const canDelete = document.getElementById('experience-list')?.dataset.canDelete === 'true';
    if (canDelete) actions.appendChild(deleteButton);

    content.appendChild(actions);
    if (canDelete) content.appendChild(deleteWrap);
  }

  details.appendChild(content);
  body.appendChild(details);
  item.appendChild(date);
  item.appendChild(body);

  return item;
}
