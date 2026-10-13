/**
 * MoneyLeak Core Application Helpers
 * Handles CSRF headers, modal management, toasts, Quick-Add Modal with Quick Access categories,
 * bidirectional Category synchronization, and Custom Category Management.
 */

// Helper to get CSRF token from meta tag
function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.getAttribute('content') : '';
}

// Wrapper for fetch API with automatic CSRF and JSON headers
async function secureFetch(url, options = {}) {
  const defaults = {
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken()
    }
  };

  const config = {
    ...options,
    headers: {
      ...defaults.headers,
      ...(options.headers || {})
    }
  };

  try {
    const res = await fetch(url, config);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.error || data.message || `Request failed (${res.status})`);
    }
    return data;
  } catch (err) {
    console.error('Fetch error:', err);
    throw err;
  }
}

// Toast notification helper
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) {
    alert(message);
    return;
  }

  const toast = document.createElement('div');
  toast.className = `flash-alert ${type}`;
  toast.innerHTML = `
    <span>${message}</span>
    <button type="button" style="background:none;border:none;cursor:pointer;font-weight:bold;margin-left:12px;" onclick="this.parentElement.remove()">×</button>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 4500);
}

// Modal open/close helpers
function openModal(modalId) {
  const el = document.getElementById(modalId);
  if (el) el.classList.add('active');
  if (modalId === 'quick-add-modal') {
    const typeSelect = document.getElementById('quick-txn-type');
    const currentType = typeSelect ? typeSelect.value : 'EXPENSE';
    loadQuickAccessCategories(currentType);
  }
}

function closeModal(modalId) {
  const el = document.getElementById(modalId);
  if (el) el.classList.remove('active');
}

// Global dismiss alert
async function dismissAlert(alertId, btnEl) {
  try {
    await secureFetch(`/api/analysis/alerts/${alertId}/dismiss`, { method: 'POST' });
    const card = btnEl.closest('.alert-card-item');
    if (card) {
      card.style.opacity = '0';
      card.style.transform = 'translateY(-10px)';
      setTimeout(() => card.remove(), 250);
    }
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

// ==========================================================================
// QUICK ACCESS & CATEGORIES ENGINE
// ==========================================================================

const categoryState = {
  type: 'EXPENSE',
  quickAccess: [],
  categories: [],
  defaultCategoryId: null,
  showAllChips: false
};

let allManageCategories = [];
let currentManageFilter = 'ALL';
let isAddCategoryFormOpen = false;

// Load categories for Quick Add form
async function loadQuickAccessCategories(txnType) {
  categoryState.type = txnType || 'EXPENSE';
  const categorySelect = document.getElementById('quick-txn-category');
  const chipsContainer = document.getElementById('quick-access-chips');
  const searchInput = document.getElementById('quick-cat-search');

  if (!categorySelect || !chipsContainer) return;

  try {
    const res = await secureFetch(`/api/categories/quick-access?type=${encodeURIComponent(categoryState.type)}`);
    categoryState.quickAccess = res.quick_access || [];
    categoryState.categories = res.categories || [];
    categoryState.defaultCategoryId = res.default_category_id;

    // Preserve previous selection if it is compatible with new type
    const previousSelection = categorySelect.value;
    const isPreviousValid = previousSelection && categoryState.categories.some(c => String(c.id) === String(previousSelection));

    // Populate Category Dropdown
    categorySelect.innerHTML = '<option value="">Select a Category</option>';
    categoryState.categories.forEach(cat => {
      const opt = document.createElement('option');
      opt.value = cat.id;
      const groupLabel = cat.budget_group ? ` (${cat.budget_group})` : '';
      opt.textContent = `${cat.name}${groupLabel}`;
      categorySelect.appendChild(opt);
    });

    // Preselect Category:
    // 1. Saved default category if configured
    // 2. Or most recently used valid category (resolved by backend)
    // 3. Or leave unselected
    if (isPreviousValid) {
      categorySelect.value = previousSelection;
    } else if (categoryState.defaultCategoryId) {
      categorySelect.value = String(categoryState.defaultCategoryId);
    } else {
      categorySelect.value = '';
    }

    // Show/hide Search Filter
    if (searchInput) {
      searchInput.value = '';
      searchInput.style.display = categoryState.categories.length > 6 ? 'block' : 'none';
    }

    // Render Quick Access Chips
    renderQuickAccessChips();

  } catch (err) {
    console.error('Failed to load categories:', err);
  }
}

// Render Quick Access Chips
function renderQuickAccessChips() {
  const container = document.getElementById('quick-access-chips');
  const categorySelect = document.getElementById('quick-txn-category');
  if (!container || !categorySelect) return;

  container.innerHTML = '';
  const selectedId = categorySelect.value ? String(categorySelect.value) : '';
  const total = categoryState.quickAccess.length;

  if (total === 0) {
    container.innerHTML = '<span style="font-size:12px;color:var(--text-muted);">No categories available for this type.</span>';
    return;
  }

  // Determine which chips to show
  const limit = 5;
  const showAll = categoryState.showAllChips;
  const displayedChips = showAll ? categoryState.quickAccess : categoryState.quickAccess.slice(0, limit);

  displayedChips.forEach(cat => {
    const chip = document.createElement('button');
    chip.type = 'button';
    chip.className = 'category-chip';
    chip.dataset.id = cat.id;
    chip.textContent = cat.name;

    if (String(cat.id) === selectedId) {
      chip.classList.add('active');
    }

    // Click handler: immediately selects in dropdown, updates highlight, stays open
    chip.addEventListener('click', (e) => {
      e.preventDefault();
      categorySelect.value = String(cat.id);
      updateActiveChip();
    });

    container.appendChild(chip);
  });

  // Render "+ More" / "− Less" chip if total > limit
  if (total > limit) {
    const moreBtn = document.createElement('button');
    moreBtn.type = 'button';
    moreBtn.className = 'category-chip-more';
    moreBtn.textContent = showAll ? '− Less' : `+ More (${total - limit})`;
    moreBtn.addEventListener('click', (e) => {
      e.preventDefault();
      categoryState.showAllChips = !categoryState.showAllChips;
      renderQuickAccessChips();
    });
    container.appendChild(moreBtn);
  }
}

// Update Active Chip state when category select changes
function updateActiveChip() {
  const categorySelect = document.getElementById('quick-txn-category');
  const container = document.getElementById('quick-access-chips');
  if (!categorySelect || !container) return;

  const selectedId = categorySelect.value ? String(categorySelect.value) : '';
  const chips = container.querySelectorAll('.category-chip');

  let foundInVisible = false;
  chips.forEach(chip => {
    if (chip.dataset.id === selectedId) {
      chip.classList.add('active');
      foundInVisible = true;
    } else {
      chip.classList.remove('active');
    }
  });

  // If selected category is in quickAccess list but hidden under "+ More", expand automatically
  if (!foundInVisible && selectedId && !categoryState.showAllChips) {
    const inQuickList = categoryState.quickAccess.some(c => String(c.id) === selectedId);
    if (inQuickList) {
      categoryState.showAllChips = true;
      renderQuickAccessChips();
    }
  }
}

// Filter dropdown options dynamically with search input
function filterCategoryDropdown(query) {
  const select = document.getElementById('quick-txn-category');
  if (!select) return;

  const q = (query || '').toLowerCase().trim();
  const options = select.options;

  for (let i = 1; i < options.length; i++) {
    const opt = options[i];
    const match = !q || opt.text.toLowerCase().includes(q);
    opt.style.display = match ? '' : 'none';
  }
}

// ==========================================================================
// MANAGE CATEGORIES MODAL & OPERATIONS
// ==========================================================================

function openManageCategoriesModal() {
  openModal('manage-categories-modal');
  loadManageCategories();
}

function toggleAddCategoryForm() {
  const form = document.getElementById('create-category-form');
  const icon = document.getElementById('add-cat-toggle-icon');
  if (!form) return;
  isAddCategoryFormOpen = !isAddCategoryFormOpen;
  form.style.display = isAddCategoryFormOpen ? 'block' : 'none';
  if (icon) icon.textContent = isAddCategoryFormOpen ? '▴' : '▾';
}

async function loadManageCategories() {
  const listEl = document.getElementById('manage-categories-list');
  if (!listEl) return;

  listEl.innerHTML = '<div style="text-align:center;padding:20px;color:var(--text-muted);font-size:12px;">Loading categories...</div>';

  try {
    const res = await secureFetch('/api/categories?include_archived=true');
    allManageCategories = res.categories || [];
    renderManageCategoriesList();
  } catch (err) {
    listEl.innerHTML = `<div style="color:#dc2626;padding:12px;font-size:12px;">${err.message}</div>`;
  }
}

function renderManageCategoriesList() {
  const listEl = document.getElementById('manage-categories-list');
  if (!listEl) return;

  listEl.innerHTML = '';

  let filtered = allManageCategories;
  if (currentManageFilter === 'ARCHIVED') {
    filtered = allManageCategories.filter(c => c.is_archived);
  } else if (currentManageFilter !== 'ALL') {
    filtered = allManageCategories.filter(c => !c.is_archived && (c.transaction_type === currentManageFilter || c.transaction_type === 'ALL'));
  } else {
    filtered = allManageCategories.filter(c => !c.is_archived);
  }

  if (filtered.length === 0) {
    listEl.innerHTML = '<div style="text-align:center;padding:24px;color:var(--text-muted);font-size:12px;">No categories in this view.</div>';
    return;
  }

  // Filter pinned categories to support reordering
  const pinnedList = filtered.filter(c => c.is_pinned);

  filtered.forEach((cat) => {
    const item = document.createElement('div');
    item.className = `cat-manage-item ${cat.is_archived ? 'archived' : ''}`;
    item.id = `cat-item-${cat.id}`;

    const defaultBadge = cat.is_default ? '<span style="font-size:10px;background:#fef08a;color:#854d0e;padding:2px 6px;border-radius:4px;font-weight:700;">Default</span>' : '';
    const pinnedBadge = cat.is_pinned ? `<span style="font-size:10px;background:#dbeafe;color:#1e40af;padding:2px 6px;border-radius:4px;font-weight:700;">Pinned #${cat.display_order || ''}</span>` : '';
    const archivedBadge = cat.is_archived ? '<span style="font-size:10px;background:#fee2e2;color:#dc2626;padding:2px 6px;border-radius:4px;font-weight:700;">Archived</span>' : '';

    const pinnedIdx = pinnedList.findIndex(p => p.id === cat.id);
    const reorderButtons = (!cat.is_archived && cat.is_pinned) ? `
      <button type="button" class="cat-action-btn" title="Move Up" onclick="moveCategoryOrder(${cat.id}, -1)" ${pinnedIdx === 0 ? 'disabled style="opacity:0.4;cursor:default;"' : ''}>↑</button>
      <button type="button" class="cat-action-btn" title="Move Down" onclick="moveCategoryOrder(${cat.id}, 1)" ${pinnedIdx === pinnedList.length - 1 ? 'disabled style="opacity:0.4;cursor:default;"' : ''}>↓</button>
    ` : '';

    item.innerHTML = `
      <div style="flex:1;min-width:0;">
        <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
          <strong style="font-size:13px;color:var(--text-primary);">${cat.name}</strong>
          <span style="font-size:10px;background:rgba(0,0,0,0.06);padding:2px 6px;border-radius:4px;font-weight:600;">${cat.transaction_type}</span>
          <span style="font-size:10px;color:var(--text-muted);">(${cat.budget_group})</span>
          ${defaultBadge}
          ${pinnedBadge}
          ${archivedBadge}
        </div>
        ${cat.description ? `<div style="font-size:11px;color:var(--text-muted);margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${cat.description}</div>` : ''}
      </div>

      <div style="display:flex;align-items:center;gap:4px;flex-shrink:0;">
        ${reorderButtons}
        ${!cat.is_archived ? `
          <button type="button" class="cat-action-btn ${cat.is_pinned ? 'pinned' : ''}" title="${cat.is_pinned ? 'Unpin from Quick Access' : 'Pin to Quick Access'}" onclick="toggleCategoryPin(${cat.id}, ${!cat.is_pinned})">
            📌 ${cat.is_pinned ? 'Pinned' : 'Pin'}
          </button>
          <button type="button" class="cat-action-btn ${cat.is_default ? 'active' : ''}" title="Toggle Default for ${cat.transaction_type}" onclick="toggleCategoryDefault(${cat.id}, '${cat.transaction_type}', ${!cat.is_default})">
            ⭐ ${cat.is_default ? 'Default' : 'Set Default'}
          </button>
          <button type="button" class="cat-action-btn" title="Edit Category" onclick="startEditCategory(${cat.id})">
            ✏️
          </button>
          <button type="button" class="cat-action-btn danger" title="Archive Category" onclick="archiveCategory(${cat.id})">
            Archive
          </button>
        ` : `
          <button type="button" class="cat-action-btn" title="Restore Category" onclick="unarchiveCategory(${cat.id})">
            Restore
          </button>
        `}
      </div>
    `;

    listEl.appendChild(item);
  });
}

// Reorder Pinned categories
async function moveCategoryOrder(catId, direction) {
  const pinnedCats = allManageCategories.filter(c => c.is_pinned && !c.is_archived);
  const idx = pinnedCats.findIndex(c => c.id === catId);
  if (idx < 0) return;

  const targetIdx = idx + direction;
  if (targetIdx < 0 || targetIdx >= pinnedCats.length) return;

  // Swap
  const temp = pinnedCats[idx];
  pinnedCats[idx] = pinnedCats[targetIdx];
  pinnedCats[targetIdx] = temp;

  const orderedIds = pinnedCats.map(c => c.id);

  try {
    await secureFetch('/api/categories/reorder', {
      method: 'POST',
      body: JSON.stringify({ ordered_ids: orderedIds })
    });
    showToast('Category order updated.', 'success');
    await loadManageCategories();
    loadQuickAccessCategories(categoryState.type);
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

// Inline edit category
function startEditCategory(catId) {
  const cat = allManageCategories.find(c => c.id === catId);
  const item = document.getElementById(`cat-item-${catId}`);
  if (!cat || !item) return;

  item.innerHTML = `
    <div style="display:flex;flex-direction:column;gap:8px;width:100%;padding:4px 0;">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
        <input type="text" id="edit-cat-name-${cat.id}" class="form-control" style="font-size:12px;padding:6px 8px;" value="${cat.name}" placeholder="Category Name" required>
        <select id="edit-cat-type-${cat.id}" class="form-control" style="font-size:12px;padding:6px 8px;">
          <option value="EXPENSE" ${cat.transaction_type === 'EXPENSE' ? 'selected' : ''}>Expense</option>
          <option value="INCOME" ${cat.transaction_type === 'INCOME' ? 'selected' : ''}>Income</option>
          <option value="SAVINGS_CONTRIBUTION" ${cat.transaction_type === 'SAVINGS_CONTRIBUTION' ? 'selected' : ''}>Investment & Savings</option>
          <option value="TRANSFER" ${cat.transaction_type === 'TRANSFER' ? 'selected' : ''}>Account Transfer</option>
          <option value="DEBT_REPAYMENT" ${cat.transaction_type === 'DEBT_REPAYMENT' ? 'selected' : ''}>Loan EMI / Debt</option>
          <option value="REFUND" ${cat.transaction_type === 'REFUND' ? 'selected' : ''}>Refund</option>
          <option value="ALL" ${cat.transaction_type === 'ALL' ? 'selected' : ''}>All Types</option>
        </select>
      </div>
      <div style="display:flex;justify-content:flex-end;gap:6px;">
        <button type="button" class="btn btn-secondary btn-sm" onclick="renderManageCategoriesList()">Cancel</button>
        <button type="button" class="btn btn-primary btn-sm" onclick="saveEditCategory(${cat.id})">Save Changes</button>
      </div>
    </div>
  `;
}

async function saveEditCategory(catId) {
  const nameInput = document.getElementById(`edit-cat-name-${catId}`);
  const typeSelect = document.getElementById(`edit-cat-type-${catId}`);
  if (!nameInput || !typeSelect) return;

  const newName = nameInput.value.trim();
  const newType = typeSelect.value;

  if (!newName) {
    showToast('Category name cannot be empty.', 'danger');
    return;
  }

  try {
    await secureFetch(`/api/categories/${catId}`, {
      method: 'PATCH',
      body: JSON.stringify({ name: newName, transaction_type: newType })
    });
    showToast('Category updated successfully!', 'success');
    await loadManageCategories();
    // Refresh quick add form if open
    loadQuickAccessCategories(categoryState.type);
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

// Toggle Pin
async function toggleCategoryPin(catId, newPinned) {
  try {
    await secureFetch(`/api/categories/${catId}`, {
      method: 'PATCH',
      body: JSON.stringify({ is_pinned: newPinned })
    });
    showToast(newPinned ? 'Category pinned to Quick Access.' : 'Category unpinned.', 'success');
    await loadManageCategories();
    loadQuickAccessCategories(categoryState.type);
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

// Toggle Default
async function toggleCategoryDefault(catId, txnType, makeDefault) {
  try {
    await secureFetch('/api/categories/defaults', {
      method: 'POST',
      body: JSON.stringify({
        transaction_type: txnType,
        category_id: makeDefault ? catId : null
      })
    });
    showToast(makeDefault ? `Set as default category for ${txnType}.` : `Default category cleared for ${txnType}.`, 'success');
    await loadManageCategories();
    loadQuickAccessCategories(categoryState.type);
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

// Archive Category
async function archiveCategory(catId) {
  try {
    await secureFetch(`/api/categories/${catId}/archive`, { method: 'POST' });
    showToast('Category archived.', 'info');
    await loadManageCategories();
    loadQuickAccessCategories(categoryState.type);
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

// Unarchive Category
async function unarchiveCategory(catId) {
  try {
    await secureFetch(`/api/categories/${catId}/unarchive`, { method: 'POST' });
    showToast('Category restored.', 'success');
    await loadManageCategories();
    loadQuickAccessCategories(categoryState.type);
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

// ==========================================================================
// DOM INITIALIZATION
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
  // Set default date
  const todayStr = new Date().toISOString().split('T')[0];
  const quickDate = document.getElementById('quick-txn-date');
  if (quickDate && !quickDate.value) quickDate.value = todayStr;

  const quickType = document.getElementById('quick-txn-type');
  const quickCat = document.getElementById('quick-txn-category');
  const quickCatSearch = document.getElementById('quick-cat-search');

  // Type change updates categories and Quick Access
  if (quickType) {
    quickType.addEventListener('change', () => {
      loadQuickAccessCategories(quickType.value);
    });
    // Initial load
    loadQuickAccessCategories(quickType.value);
  }

  // Category select change updates highlighted chip
  if (quickCat) {
    quickCat.addEventListener('change', () => {
      updateActiveChip();
    });
  }

  // Category search filter
  if (quickCatSearch) {
    quickCatSearch.addEventListener('input', (e) => {
      filterCategoryDropdown(e.target.value);
    });
  }

  // Manage Categories type filter tabs
  const filterTabs = document.querySelectorAll('#manage-type-tabs .cat-filter-tab');
  filterTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      filterTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      currentManageFilter = tab.dataset.type || 'ALL';
      renderManageCategoriesList();
    });
  });

  // Create Category form in Manage modal
  const createCatForm = document.getElementById('create-category-form');
  if (createCatForm) {
    createCatForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        name: document.getElementById('new-cat-name').value.trim(),
        transaction_type: document.getElementById('new-cat-type').value,
        budget_group: document.getElementById('new-cat-group').value,
        description: document.getElementById('new-cat-desc').value.trim(),
        is_pinned: document.getElementById('new-cat-pin').checked,
        is_default: document.getElementById('new-cat-default').checked
      };

      try {
        await secureFetch('/api/categories', {
          method: 'POST',
          body: JSON.stringify(payload)
        });
        showToast('Category created successfully!', 'success');
        createCatForm.reset();
        await loadManageCategories();
        loadQuickAccessCategories(categoryState.type);
      } catch (err) {
        showToast(err.message, 'danger');
      }
    });
  }

  // Quick Add Transaction form handler
  const quickForm = document.getElementById('quick-add-txn-form');
  if (quickForm) {
    quickForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const categoryIdVal = document.getElementById('quick-txn-category').value;
      const payload = {
        amount: document.getElementById('quick-txn-amount').value,
        transaction_type: document.getElementById('quick-txn-type').value,
        category_id: categoryIdVal ? parseInt(categoryIdVal, 10) : null,
        transaction_date: document.getElementById('quick-txn-date').value,
        description: document.getElementById('quick-txn-desc').value,
        merchant: document.getElementById('quick-txn-merchant').value,
        notes: document.getElementById('quick-txn-notes').value
      };

      try {
        const res = await secureFetch('/api/transactions', {
          method: 'POST',
          body: JSON.stringify(payload)
        });
        showToast(res.message || 'Transaction added successfully!', 'success');
        closeModal('quick-add-modal');
        quickForm.reset();
        // Refresh page or trigger custom event
        setTimeout(() => window.location.reload(), 600);
      } catch (err) {
        showToast(err.message, 'danger');
      }
    });
  }

  // Initialize ThemeManager UI bindings
  ThemeManager.init();
});

// ==========================================================================
// APPEARANCE & THEME MANAGER (Light | Dark | System)
// ==========================================================================

const ThemeManager = {
  STORAGE_KEY: 'moneyleak_theme_preference',

  getPreference() {
    return localStorage.getItem(this.STORAGE_KEY) ||
           document.documentElement.getAttribute('data-theme-preference') ||
           'system';
  },

  getSystemTheme() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  },

  resolveTheme(preference) {
    if (preference === 'system') {
      return this.getSystemTheme();
    }
    return preference === 'dark' ? 'dark' : 'light';
  },

  updateChartDefaults(resolvedTheme) {
    if (typeof Chart !== 'undefined') {
      if (resolvedTheme === 'dark') {
        Chart.defaults.color = '#94a3b8';
        Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.08)';
      } else {
        Chart.defaults.color = '#525c56';
        Chart.defaults.borderColor = 'rgba(0, 0, 0, 0.06)';
      }
      if (Chart.instances) {
        Object.values(Chart.instances).forEach(chart => {
          try {
            chart.update('none');
          } catch (e) {}
        });
      }
    }
  },

  updateSegmentedControlUI(preference) {
    const segmented = document.querySelector('.theme-segmented-control');
    if (!segmented) return;

    const buttons = segmented.querySelectorAll('.theme-option-btn');
    buttons.forEach(btn => {
      const val = btn.getAttribute('data-theme-value');
      const isActive = val === preference;
      btn.classList.toggle('active', isActive);
      btn.setAttribute('aria-checked', isActive ? 'true' : 'false');
    });

    const statusText = document.getElementById('theme-status-text');
    if (statusText) {
      if (preference === 'light') {
        statusText.textContent = 'Active: Light theme';
      } else if (preference === 'dark') {
        statusText.textContent = 'Active: Dark theme';
      } else {
        const sys = this.getSystemTheme();
        const cap = sys.charAt(0).toUpperCase() + sys.slice(1);
        statusText.textContent = `Active: System preference (currently ${cap})`;
      }
    }
  },

  applyTheme(preference, saveToServer = false) {
    const resolved = this.resolveTheme(preference);

    document.documentElement.setAttribute('data-theme', resolved);
    document.documentElement.setAttribute('data-theme-preference', preference);

    try {
      localStorage.setItem(this.STORAGE_KEY, preference);
    } catch (e) {}

    this.updateSegmentedControlUI(preference);
    this.updateChartDefaults(resolved);

    window.dispatchEvent(new CustomEvent('themechange', {
      detail: { theme: resolved, preference: preference }
    }));

    if (saveToServer) {
      this.savePreferenceToServer(preference);
    }
  },

  async savePreferenceToServer(preference) {
    try {
      await secureFetch('/api/settings/appearance', {
        method: 'POST',
        body: JSON.stringify({ theme: preference })
      });
    } catch (err) {
      console.warn('Could not persist theme to server:', err);
    }
  },

  init() {
    const currentPref = this.getPreference();
    this.applyTheme(currentPref, false);

    // Watch OS appearance changes (only reacts when preference is 'system')
    if (window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleSystemChange = () => {
        if (this.getPreference() === 'system') {
          this.applyTheme('system', false);
        }
      };
      if (mediaQuery.addEventListener) {
        mediaQuery.addEventListener('change', handleSystemChange);
      } else if (mediaQuery.addListener) {
        mediaQuery.addListener(handleSystemChange);
      }
    }

    // Attach listeners to segmented control buttons
    const themeButtons = document.querySelectorAll('.theme-option-btn');
    themeButtons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const chosen = btn.getAttribute('data-theme-value');
        if (chosen) {
          this.applyTheme(chosen, true);
        }
      });
    });
  }
};

// Immediate pre-run to ensure variables and attributes are synchronous
try {
  ThemeManager.applyTheme(ThemeManager.getPreference(), false);
} catch (e) {}

// Expose ThemeManager globally
window.ThemeManager = ThemeManager;

