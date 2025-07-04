// static/main.js
document.addEventListener('DOMContentLoaded', () => {
  // --- Toggle “pago” (POST) ---
  document.querySelectorAll('.toggle-paid').forEach(checkbox => {
    checkbox.addEventListener('change', () => {
      fetch(checkbox.dataset.url, { method: 'POST' })
        .then(res => {
          if (res.ok) window.location.reload();
          else console.error('Erro ao atualizar pago:', res.statusText);
        })
        .catch(err => console.error(err));
    });
  });

  // --- Delete buttons (POST) ---
  document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      if (!confirm('Confirma a exclusão deste registro?')) return;
      fetch(btn.dataset.url, { method: 'POST' })
        .then(res => {
          if (res.ok) window.location.reload();
          else console.error('Erro ao excluir:', res.statusText);
        })
        .catch(err => console.error(err));
    });
  });

  // --- Edit Fixed Expense ---
  const fixedForm       = document.getElementById('fixed-form');
  const fixedFormTitle  = document.getElementById('fixed-form-title');
  const fixedSubmitBtn  = document.getElementById('fixed-submit-btn');
  const fixedIdInput    = document.getElementById('fixed-id');
  const fixedNameInput  = document.getElementById('fixed-name');
  const fixedValueInput = document.getElementById('fixed-value');
  const fixedDueInput   = document.getElementById('fixed-due');
  const fixedAffInput   = document.getElementById('fixed-affiliate');

  document.querySelectorAll('.edit-btn-fixed').forEach(btn => {
    btn.addEventListener('click', () => {
      // Preenche o formulário
      fixedIdInput.value    = btn.dataset.id;
      fixedNameInput.value  = btn.dataset.name;
      fixedValueInput.value = btn.dataset.value;
      fixedDueInput.value   = btn.dataset.due;
      fixedAffInput.value   = btn.dataset.affiliate;

      // Atualiza título, botão e action
      fixedFormTitle.innerText    = 'Editar Gasto Fixo';
      fixedSubmitBtn.innerText    = 'Atualizar';
      fixedForm.action            = `/fixed/edit/${btn.dataset.id}`;

      // Foca no primeiro campo
      fixedNameInput.focus();
    });
  });

  // --- Edit Installment Expense ---
  const instForm        = document.getElementById('installment-form');
  const instFormTitle   = document.getElementById('inst-form-title');
  const instSubmitBtn   = document.getElementById('inst-submit-btn');
  const instIdInput     = document.getElementById('inst-id');
  const instNameInput   = document.getElementById('inst-name');
  const instTotalInput  = document.getElementById('inst-total');
  const instParcInput   = document.getElementById('inst-parcels');
  const instStartInput  = document.getElementById('inst-start');
  const instAffInput    = document.getElementById('inst-affiliate');

  document.querySelectorAll('.edit-btn-inst').forEach(btn => {
    btn.addEventListener('click', () => {
      // Preenche o formulário
      instIdInput.value       = btn.dataset.id;
      instNameInput.value     = btn.dataset.name;
      instTotalInput.value    = btn.dataset.total;
      instParcInput.value     = btn.dataset.parcels;
      instStartInput.value    = btn.dataset.start;
      instAffInput.value      = btn.dataset.affiliate;

      // Atualiza título, botão e action
      instFormTitle.innerText  = 'Editar Parcelamento';
      instSubmitBtn.innerText  = 'Atualizar';
      instForm.action          = `/installments/edit/${btn.dataset.id}`;

      // Foca no primeiro campo
      instNameInput.focus();
    });
  });

  const editLimitBtn = document.getElementById('edit-limit-btn');
  if (editLimitBtn) {
    const configModalEl = document.getElementById('configModal');
    const bsConfigModal = new bootstrap.Modal(configModalEl);
    editLimitBtn.addEventListener('click', () => {
      bsConfigModal.show();
    });
  }
});
