/**
 * Transaction Management Interactive Logic
 * Filtering, searching, sorting, pagination, and modal CRUD operations.
 */

let currentPage = 1;
let debounceTimeout = null;

document.addEventListener('DOMContentLoaded', () => {
  loadTransactions(1);

  // Search input with debounce
  const searchInput = document.getElementById('txn-search');
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      clearTimeout(debounceTimeout);
      debounceTimeout = setTimeout(() => loadTransactions(1), 300);
    });
  }

  // Filter selects
  ['txn-filter-category', 'txn-filter-type', 'txn-filter-sort'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('change', () => loadTransactions(1));
  });

  // Date filters
  ['txn-filter-start', 'txn-filter-end'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('change', () => loadTransactions(1));
  });

  // Edit form submission
  const editForm = document.getElementById('edit-txn-form');
  if (editForm) {
    editForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const id = document.getElementById('edit-txn-id').value;
      const payload = {
        amount: document.getElementById('edit-txn-amount').value,
        transaction_type: document.getElementById('edit-txn-type').value,
        category_id: document.getElementById('edit-txn-category').value,
        transaction_date: document.getElementById('edit-txn-date').value,
        description: document.getElementById('edit-txn-desc').value,
        merchant: document.getElementById('edit-txn-merchant').value,
        notes: document.getElementById('edit-txn-notes').value
      };

      try {
        await secureFetch(`/api/transactions/${id}`, {
          method: 'PATCH',
          body: JSON.stringify(payload)
        });
        showToast('Transaction updated successfully!', 'success');
        closeModal('edit-txn-modal');
        loadTransactions(currentPage);
      } catch (err) {
        showToast(err.message, 'danger');
      }
    });
  }
});

async function loadTransactions(page = 1) {
  currentPage = page;
  const tbody = document.getElementById('transactions-table-body');
  if (!tbody) return;

  tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:28px;color:#959e93;">Loading transactions...</td></tr>`;

  const search = document.getElementById('txn-search')?.value || '';
  const categoryId = document.getElementById('txn-filter-category')?.value || '';
  const type = document.getElementById('txn-filter-type')?.value || '';
  const sort = document.getElementById('txn-filter-sort')?.value || 'date_desc';
  const start = document.getElementById('txn-filter-start')?.value || '';
  const end = document.getElementById('txn-filter-end')?.value || '';

  const params = new URLSearchParams({
    page: page,
    per_page: 15,
    search: search,
    category_id: categoryId,
    type: type,
    sort_by: sort,
    start_date: start,
    end_date: end
  });

  try {
    const res = await secureFetch(`/api/transactions?${params.toString()}`);
    const items = res.transactions || [];

    if (items.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7" style="text-align:center;padding:36px;color:#959e93;">
            <div style="font-size:24px;margin-bottom:6px;">🧾</div>
            <strong>No transactions found.</strong><br>
            <span style="font-size:12px;">Try adjusting filters or record a new transaction above.</span>
          </td>
        </tr>`;
      renderPagination(0, 1);
      return;
    }

    tbody.innerHTML = items.map(t => {
      let badgeClass = 'badge-dark';
      if (t.transaction_type === 'SAVINGS_CONTRIBUTION') badgeClass = 'badge-lime';
      else if (t.transaction_type === 'REFUND') badgeClass = 'badge-blue';
      else if (t.transaction_type === 'DEBT_REPAYMENT') badgeClass = 'badge-peach';

      const typeLabel = t.transaction_type.replace('_', ' ');

      return `
        <tr>
          <td><span style="font-weight:700;">${t.transaction_date}</span></td>
          <td>
            <div style="font-weight:700;color:var(--text-primary);">${escapeHtml(t.description)}</div>
            ${t.merchant ? `<div style="font-size:11px;color:var(--text-muted);">${escapeHtml(t.merchant)}</div>` : ''}
          </td>
          <td>
            <span class="badge-pill badge-dark" style="font-size:10px;">${escapeHtml(t.category_name)}</span>
            <span style="font-size:10px;color:var(--text-muted);margin-left:4px;">(${t.budget_group})</span>
          </td>
          <td><span class="badge-pill ${badgeClass}" style="font-size:10px;">${typeLabel}</span></td>
          <td style="font-weight:800;font-size:14px;text-align:right;">${t.formatted_amount}</td>
          <td><span style="font-size:12px;color:var(--text-secondary);">${escapeHtml(t.notes || '-')}</span></td>
          <td style="text-align:right;">
            <button class="btn btn-secondary btn-sm" onclick="openEditModal(${t.id})">Edit</button>
            <button class="btn btn-secondary btn-sm" style="color:#ef4444;" onclick="deleteTransaction(${t.id})">Delete</button>
          </td>
        </tr>
      `;
    }).join('');

    renderPagination(res.pages, res.page);
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:#ef4444;">${err.message}</td></tr>`;
  }
}

function renderPagination(totalPages, activePage) {
  const container = document.getElementById('pagination-controls');
  if (!container) return;

  if (totalPages <= 1) {
    container.innerHTML = '';
    return;
  }

  let html = `<div style="display:flex;align-items:center;gap:6px;justify-content:center;margin-top:20px;">`;
  for (let i = 1; i <= totalPages; i++) {
    const active = i === activePage ? 'background:var(--brand-lime);font-weight:800;' : 'background:#fff;';
    html += `<button class="btn btn-secondary btn-sm" style="${active}" onclick="loadTransactions(${i})">${i}</button>`;
  }
  html += `</div>`;
  container.innerHTML = html;
}

async function openEditModal(txnId) {
  try {
    const res = await secureFetch(`/api/transactions/${txnId}`);
    const t = res.transaction;

    document.getElementById('edit-txn-id').value = t.id;
    document.getElementById('edit-txn-desc').value = t.description;
    document.getElementById('edit-txn-merchant').value = t.merchant || '';
    document.getElementById('edit-txn-type').value = t.transaction_type;
    document.getElementById('edit-txn-category').value = t.category_id || '';
    document.getElementById('edit-txn-date').value = t.transaction_date;
    document.getElementById('edit-txn-notes').value = t.notes || '';

    // Major amount representation
    const rawAmt = t.amount_minor_units;
    document.getElementById('edit-txn-amount').value = (rawAmt / 100).toFixed(2);

    openModal('edit-txn-modal');
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

async function deleteTransaction(txnId) {
  if (!confirm('Are you sure you want to delete this transaction?')) return;
  try {
    await secureFetch(`/api/transactions/${txnId}`, { method: 'DELETE' });
    showToast('Transaction deleted successfully.', 'success');
    loadTransactions(currentPage);
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
