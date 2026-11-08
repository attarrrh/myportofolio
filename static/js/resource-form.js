// Existing edit pages submit to DRF and stay open on validation/permission errors.
document.addEventListener('DOMContentLoaded', function () {
  const form = document.querySelector('[data-api-form]');
  if (!form) return;
  form.addEventListener('submit', async function (event) {
    event.preventDefault();
    const submit = form.querySelector('[type=submit]');
    if (submit.disabled) return;
    submit.disabled = true;
    const body = new FormData(form);
    body.delete('csrfmiddlewaretoken');
    for (const [key, value] of [...body.entries()]) {
      if (key.endsWith('-clear') || (value instanceof File && !value.name)) body.delete(key);
    }
    try {
      await writeResource(form.dataset.apiUrl, form.dataset.apiMethod, body);
      // Keep the form and page in place so the user can continue editing.
      showToast('Sukses', 'Data berhasil disimpan.', 'success');
    } catch (error) {
      showToast('Gagal menyimpan data', error.message, 'error');
    } finally {
      submit.disabled = false;
    }
  });
});
