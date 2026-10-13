/**
 * MoneyLeak - Investment Explorer & Future Wealth Projection Suite
 * 
 * Manages:
 * 1. Explore Investment Options (Stocks & Equity, Equity Mutual Funds with SIP/LumpSum, SIP Investments, Gold)
 * 2. Personalize Your Investment & Recommendation Engine
 * 3. Side-by-Side Comparison Matrix
 * 4. Future Wealth Projection (Single Calculation, 3 Scenarios: Conservative, Moderate, Optimistic)
 * 5. Combined Multi-Asset Portfolio Aggregation without double-counting SIP investments
 * 6. Historical What-If Analysis & Scheme Factsheet Modals
 */

let calcChart = null;
let whatIfChart = null;
let currentWhatIfYears = 5;
let activeModalScheme = null;
let cachedSchemes = [];
let currentMfMethod = 'SIP'; // 'SIP' or 'LUMPSUM'

// Multi-investment portfolio state
let portfolioInvestments = [
  {
    id: 'parag-parikh-flexi-cap',
    name: 'Parag Parikh Flexi Cap Fund',
    category: 'EQUITY_MUTUAL_FUNDS',
    method: 'SIP',
    amount: 5000,
    expected_return_pct: 16.0,
    underlying_scheme_id: 'parag-parikh-flexi-cap'
  },
  {
    id: 'reliance-industries',
    name: 'Reliance Industries Limited',
    category: 'STOCKS_EQUITY',
    method: 'LUMPSUM',
    amount: 50000,
    expected_return_pct: 14.0
  },
  {
    id: 'nippon-gold-bees-etf',
    name: 'Nippon India ETF Gold BeES',
    category: 'GOLD',
    method: 'LUMPSUM',
    amount: 25000,
    expected_return_pct: 11.5
  }
];

document.addEventListener('DOMContentLoaded', () => {
  initTopNavTabs();
  initSchemeExplorer();
  initDedicatedSIPCalculator();
  initPersonalizedRecommendations();
  initCompare();
  initFutureCalc();
  initPortfolioBuilder();
  initWhatIfCalc();
  initSchemeModal();
  initCardDelegation();

  // Initial loads
  loadSchemesCache();
  recalculateWhatIf();
  recalculateDedicatedSIP();
  updatePortfolioDOM();
});

// ============================================================================
// 1. TOP-LEVEL TAB NAVIGATION
// ============================================================================
function initTopNavTabs() {
  const tabButtons = document.querySelectorAll('.calc-tabs-bar .calc-tab-btn');
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-tab');
      switchTopTab(targetId);
    });
  });
}

function switchTopTab(tabId) {
  document.querySelectorAll('.calc-tabs-bar .calc-tab-btn').forEach(b => {
    b.classList.toggle('active', b.getAttribute('data-tab') === tabId);
  });

  document.querySelectorAll('.calc-tab-content').forEach(c => {
    c.classList.toggle('active', c.id === tabId);
  });

  if (tabId === 'tab-future' && calcChart) {
    setTimeout(() => calcChart.resize(), 60);
  } else if (tabId === 'tab-what-if' && whatIfChart) {
    setTimeout(() => whatIfChart.resize(), 60);
  }
}

// ============================================================================
// 2. SCHEME EXPLORER (TEXT-ONLY TABS & FUNCTIONAL FILTER BAR)
// ============================================================================

const explorerState = {
  activeTab: 'ALL', // 'ALL', 'STOCKS_EQUITY', 'EQUITY_MUTUAL_FUNDS', 'SIP_INVESTMENTS', 'GOLD'
  searchQuery: '',
  riskFilter: 'ALL',
  durationFilter: 'ALL',
  minInvestmentFilter: 'ALL',
  maxExpenseRatioFilter: 'ALL',
  returnPeriod: '5y',
  sortBy: 'relevance'
};

function initSchemeExplorer() {
  // Tab buttons click listeners
  const tabBtns = document.querySelectorAll('#scheme-explorer-tabs .explorer-tab-btn');
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.getAttribute('data-tab');
      switchExplorerTab(tab);
    });
  });

  // Filter bar controls listeners
  const searchInput = document.getElementById('explorer-search');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      explorerState.searchQuery = e.target.value;
      applySchemeExplorerFilters();
    });
  }

  const riskSelect = document.getElementById('explorer-risk');
  if (riskSelect) {
    riskSelect.addEventListener('change', (e) => {
      explorerState.riskFilter = e.target.value;
      applySchemeExplorerFilters();
    });
  }

  const durationSelect = document.getElementById('explorer-duration');
  if (durationSelect) {
    durationSelect.addEventListener('change', (e) => {
      explorerState.durationFilter = e.target.value;
      applySchemeExplorerFilters();
    });
  }

  const minInvestSelect = document.getElementById('explorer-min-investment');
  if (minInvestSelect) {
    minInvestSelect.addEventListener('change', (e) => {
      explorerState.minInvestmentFilter = e.target.value;
      applySchemeExplorerFilters();
    });
  }

  const expenseRatioSelect = document.getElementById('explorer-expense-ratio');
  if (expenseRatioSelect) {
    expenseRatioSelect.addEventListener('change', (e) => {
      explorerState.maxExpenseRatioFilter = e.target.value;
      applySchemeExplorerFilters();
    });
  }

  const returnPeriodSelect = document.getElementById('explorer-return-period');
  if (returnPeriodSelect) {
    returnPeriodSelect.addEventListener('change', (e) => {
      explorerState.returnPeriod = e.target.value;
      applySchemeExplorerFilters();
    });
  }

  const sortSelect = document.getElementById('explorer-sort');
  if (sortSelect) {
    sortSelect.addEventListener('change', (e) => {
      explorerState.sortBy = e.target.value;
      applySchemeExplorerFilters();
    });
  }

  // Reset Filters button
  const resetBtn = document.getElementById('btn-reset-filters');
  if (resetBtn) {
    resetBtn.addEventListener('click', resetSchemeExplorerFilters);
  }

  const emptyResetBtn = document.getElementById('btn-empty-reset');
  if (emptyResetBtn) {
    emptyResetBtn.addEventListener('click', resetSchemeExplorerFilters);
  }

  // Initial render
  applySchemeExplorerFilters();
}

function switchExplorerTab(newTab) {
  if (explorerState.activeTab === newTab) return;
  explorerState.activeTab = newTab;

  // Highlight active tab
  document.querySelectorAll('#scheme-explorer-tabs .explorer-tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-tab') === newTab);
  });

  // Reset incompatible filters:
  // Expense Ratio filter is incompatible with Stocks & Equity.
  const expenseSelect = document.getElementById('explorer-expense-ratio');
  const expenseNote = document.getElementById('expense-ratio-note');

  if (newTab === 'STOCKS_EQUITY') {
    explorerState.maxExpenseRatioFilter = 'ALL';
    if (expenseSelect) {
      expenseSelect.value = 'ALL';
      expenseSelect.disabled = true;
    }
    if (expenseNote) expenseNote.style.display = 'block';
  } else {
    if (expenseSelect) expenseSelect.disabled = false;
    if (expenseNote) expenseNote.style.display = 'none';
  }

  // Keep search query and compatible filter selections!
  applySchemeExplorerFilters();
}

function resetSchemeExplorerFilters() {
  explorerState.searchQuery = '';
  explorerState.riskFilter = 'ALL';
  explorerState.durationFilter = 'ALL';
  explorerState.minInvestmentFilter = 'ALL';
  explorerState.maxExpenseRatioFilter = 'ALL';
  explorerState.sortBy = 'relevance';
  // Note: activeTab is preserved!

  const searchInput = document.getElementById('explorer-search');
  if (searchInput) searchInput.value = '';

  const riskSelect = document.getElementById('explorer-risk');
  if (riskSelect) riskSelect.value = 'ALL';

  const durationSelect = document.getElementById('explorer-duration');
  if (durationSelect) durationSelect.value = 'ALL';

  const minInvestSelect = document.getElementById('explorer-min-investment');
  if (minInvestSelect) minInvestSelect.value = 'ALL';

  const expenseRatioSelect = document.getElementById('explorer-expense-ratio');
  if (expenseRatioSelect) expenseRatioSelect.value = 'ALL';

  const sortSelect = document.getElementById('explorer-sort');
  if (sortSelect) sortSelect.value = 'relevance';

  applySchemeExplorerFilters();
}

function applySchemeExplorerFilters() {
  const filtered = computeFilteredSchemes();
  renderExplorerResults(filtered);
  renderActiveFilterChips();
  updateResultsCount(filtered.length);
}

function computeFilteredSchemes() {
  // 1. Start with eligible, deduplicated product dataset
  let baseItems = Array.isArray(window.__ALL_SCHEMES__) && window.__ALL_SCHEMES__.length > 0
    ? [...window.__ALL_SCHEMES__]
    : [...cachedSchemes];

  // Ensure deduplication by unique scheme/product ID
  const seenIds = new Set();
  let items = [];
  for (const item of baseItems) {
    if (!seenIds.has(item.id)) {
      seenIds.add(item.id);
      items.push(item);
    }
  }

  // 2. Apply selected main tab
  if (explorerState.activeTab === 'STOCKS_EQUITY') {
    items = items.filter(s => s.category === 'STOCKS_EQUITY');
  } else if (explorerState.activeTab === 'EQUITY_MUTUAL_FUNDS') {
    items = items.filter(s => s.category === 'EQUITY_MUTUAL_FUNDS');
  } else if (explorerState.activeTab === 'SIP_INVESTMENTS') {
    // Only eligible equity mutual funds that currently support SIP investments
    items = items.filter(s => s.category === 'EQUITY_MUTUAL_FUNDS' && s.supports_sip === true);
  } else if (explorerState.activeTab === 'GOLD') {
    items = items.filter(s => s.category === 'GOLD');
  } // 'ALL' keeps all eligible stocks, equity mutual funds, and gold

  // 3. Apply search query (case-insensitive across name, company_name, ticker, subcategory)
  const q = (explorerState.searchQuery || '').trim().toLowerCase();
  if (q) {
    items = items.filter(s => {
      const name = (s.name || '').toLowerCase();
      const comp = (s.company_name || s.provider || '').toLowerCase();
      const ticker = (s.ticker || '').toLowerCase();
      const subcat = (s.subcategory || '').toLowerCase();
      return name.includes(q) || comp.includes(q) || ticker.includes(q) || subcat.includes(q);
    });
  }

  // 4. Apply all selected compatible filters using AND logic
  // 4a. Risk Level
  if (explorerState.riskFilter !== 'ALL') {
    const targetRisk = explorerState.riskFilter.toLowerCase();
    items = items.filter(s => {
      const r = (s.risk_level || '').trim().toLowerCase();
      if (!r || r === 'not available' || r === 'unknown' || r === 'n/a') return false;
      if (targetRisk === 'moderate') return r.includes('moderate');
      return r === targetRisk;
    });
  }

  // 4b. Investment Duration
  if (explorerState.durationFilter !== 'ALL') {
    const targetDur = explorerState.durationFilter;
    items = items.filter(s => {
      const durations = s.supported_durations || [];
      return durations.includes(targetDur);
    });
  }

  // 4c. Minimum Investment threshold (in INR)
  if (explorerState.minInvestmentFilter !== 'ALL') {
    const maxThreshold = parseFloat(explorerState.minInvestmentFilter);
    const isSipTab = (explorerState.activeTab === 'SIP_INVESTMENTS');
    items = items.filter(s => {
      const val = isSipTab ? (s.min_sip ?? s.min_investment) : s.min_investment;
      return val !== null && val !== undefined && val <= maxThreshold;
    });
  }

  // 4d. Expense Ratio (Applicable to mutual funds and SIP-enabled mutual funds only; not stocks)
  if (explorerState.activeTab !== 'STOCKS_EQUITY' && explorerState.maxExpenseRatioFilter !== 'ALL') {
    const maxTer = parseFloat(explorerState.maxExpenseRatioFilter);
    items = items.filter(s => {
      if (s.category === 'STOCKS_EQUITY') return false;
      return s.expense_ratio_pct !== null && s.expense_ratio_pct !== undefined && s.expense_ratio_pct <= maxTer;
    });
  }

  // 5. Sort filtered results
  const period = explorerState.returnPeriod || '5y';
  const cagrKey = `cagr_${period}`;

  if (explorerState.sortBy === 'return_desc') {
    // Place products with unavailable returns after products with valid values
    items.sort((a, b) => {
      const aVal = a[cagrKey];
      const bVal = b[cagrKey];
      const aValid = (aVal !== null && aVal !== undefined && !isNaN(aVal));
      const bValid = (bVal !== null && bVal !== undefined && !isNaN(bVal));
      if (aValid && bValid) return bVal - aVal;
      if (aValid && !bValid) return -1;
      if (!aValid && bValid) return 1;
      return 0;
    });
  } else if (explorerState.sortBy === 'expense_asc') {
    // Lowest Expense Ratio; unavailable values placed after valid values
    items.sort((a, b) => {
      const aVal = a.expense_ratio_pct;
      const bVal = b.expense_ratio_pct;
      const aValid = (aVal !== null && aVal !== undefined && !isNaN(aVal));
      const bValid = (bVal !== null && bVal !== undefined && !isNaN(bVal));
      if (aValid && bValid) return aVal - bVal;
      if (aValid && !bValid) return -1;
      if (!aValid && bValid) return 1;
      return 0;
    });
  } else if (explorerState.sortBy === 'name_asc') {
    items.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
  }

  return items;
}

function renderExplorerResults(items) {
  const grid = document.getElementById('explorer-results-grid');
  const emptyState = document.getElementById('explorer-empty-state');
  if (!grid) return;

  if (items.length === 0) {
    grid.innerHTML = '';
    if (emptyState) emptyState.style.display = 'block';
    return;
  }

  if (emptyState) emptyState.style.display = 'none';

  const period = explorerState.returnPeriod || '5y';
  const periodLabel = period === '5y' ? '5Y CAGR' : (period === '3y' ? '3Y CAGR' : '1Y Return');
  const isSipTab = (explorerState.activeTab === 'SIP_INVESTMENTS');

  grid.innerHTML = items.map(s => {
    // Risk display
    const rawRisk = s.risk_level;
    const hasRisk = (rawRisk && rawRisk.trim().length > 0 && rawRisk.toLowerCase() !== 'not available');
    const riskLabel = hasRisk ? rawRisk : 'Not Available';
    let riskBadgeClass = 'badge-dark';
    if (riskLabel === 'Very High' || riskLabel === 'High') riskBadgeClass = 'badge-danger';
    else if (riskLabel === 'Moderate') riskBadgeClass = 'badge-peach';

    // Historical Returns display
    const cagrVal = s[`cagr_${period}`];
    const hasReturn = (cagrVal !== null && cagrVal !== undefined && !isNaN(cagrVal));
    const returnDisplay = hasReturn ? `+${cagrVal}% p.a.` : 'Not Available';
    const returnColor = hasReturn ? '#16a34a' : 'var(--text-muted)';

    // Minimum Investment display
    const minVal = isSipTab ? (s.min_sip ?? s.min_investment) : s.min_investment;
    const minLabel = isSipTab ? 'Min Monthly SIP' : 'Min Investment';
    const minDisplay = minVal ? `₹${Number(minVal).toLocaleString('en-IN')}${isSipTab ? ' / month' : ''}` : 'Not Available';

    // Expense Ratio display
    let expenseDisplay = s.expense_ratio;
    if (s.category === 'STOCKS_EQUITY') {
      expenseDisplay = 'Not Applicable (Direct Equity)';
    } else if (!expenseDisplay || expenseDisplay.trim() === '') {
      expenseDisplay = 'Not Available';
    }

    // Investment type display
    let typeDisplay = s.investment_type || s.subcategory || 'Investment';
    if (isSipTab) {
      typeDisplay = `SIP Investment (${s.subcategory || 'Equity MF'})`;
    }

    // Default projection method and amount
    const projMethod = isSipTab ? 'SIP' : (s.category === 'EQUITY_MUTUAL_FUNDS' ? 'SIP' : 'LUMPSUM');
    const projAmount = isSipTab ? (s.min_sip || 5000) : (s.category === 'EQUITY_MUTUAL_FUNDS' ? 5000 : (s.min_investment || 50000));
    const projRate = (hasReturn ? cagrVal : (s.cagr_5y || s.expected_annual_return || 12.0));

    return `
      <div class="scheme-card explorer-card" data-id="${s.id}">
        <div>
          <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:8px;">
            <span class="badge-pill badge-mint" style="font-size:10px;font-weight:700;">${typeDisplay}</span>
            <span class="badge-pill ${riskBadgeClass}" style="font-size:10px;font-weight:700;">${riskLabel}</span>
          </div>

          <div class="scheme-title" style="font-size:15px;font-weight:800;color:var(--text-primary);margin-bottom:2px;line-height:1.3;">${s.name}</div>
          <div class="scheme-provider" style="font-size:12px;color:var(--text-muted);margin-bottom:12px;">
            ${s.company_name || s.provider} ${s.ticker ? `• Ticker: ${s.ticker}` : ''}
          </div>

          <div class="scheme-meta-grid" style="grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px;">
            <div class="scheme-meta-item">
              <div class="scheme-meta-label">Historical Returns (${periodLabel})</div>
              <div class="scheme-meta-val" style="color:${returnColor};font-weight:800;">${returnDisplay}</div>
            </div>
            <div class="scheme-meta-item">
              <div class="scheme-meta-label">${minLabel}</div>
              <div class="scheme-meta-val" style="font-weight:800;color:var(--text-primary);">${minDisplay}</div>
            </div>
            <div class="scheme-meta-item">
              <div class="scheme-meta-label">Expense Ratio</div>
              <div class="scheme-meta-val">${expenseDisplay}</div>
            </div>
            <div class="scheme-meta-item">
              <div class="scheme-meta-label">Settlement / Liquidity</div>
              <div class="scheme-meta-val" style="font-size:10px;">${s.liquidity ? s.liquidity.substring(0, 32) + (s.liquidity.length > 32 ? '...' : '') : 'High Liquidity'}</div>
            </div>
          </div>

          ${isSipTab || s.supports_sip ? `
            <div style="font-size:11px;color:#15803d;background:#f0fdf4;border-radius:4px;padding:6px 10px;margin-bottom:12px;border:1px solid #dcfce7;">
              Underlying Fund • ${s.sip_availability || 'SIP Available'}
            </div>
          ` : ''}

          <div style="display:flex;justify-content:space-between;align-items:center;font-size:10px;color:var(--text-muted);padding-top:8px;border-top:1px solid rgba(0,0,0,0.05);">
            <span>Source: ${s.data_source || 'Official Filings'}</span>
            <span>${s.last_updated || 'October 2026'}</span>
          </div>
        </div>

        <div class="scheme-card-actions" style="margin-top:14px;display:flex;gap:8px;">
          <button type="button" class="btn btn-secondary btn-sm action-view-details" data-id="${s.id}" style="flex:1;font-weight:700;">
            View Details
          </button>
          <button type="button" class="btn btn-primary btn-sm action-project-scheme" 
            data-id="${s.id}" 
            data-name="${s.name}" 
            data-rate="${projRate}" 
            data-method="${projMethod}" 
            data-amount="${projAmount}" 
            style="flex:1;font-weight:700;">
            Add to Projection
          </button>
        </div>
      </div>
    `;
  }).join('');
}

function renderActiveFilterChips() {
  const container = document.getElementById('explorer-active-chips');
  if (!container) return;

  const chips = [];

  // Search chip
  if (explorerState.searchQuery && explorerState.searchQuery.trim().length > 0) {
    chips.push({
      key: 'search',
      label: `Search: "${explorerState.searchQuery.trim()}"`
    });
  }

  // Risk chip
  if (explorerState.riskFilter !== 'ALL') {
    chips.push({
      key: 'risk',
      label: `Risk: ${explorerState.riskFilter}`
    });
  }

  // Duration chip
  if (explorerState.durationFilter !== 'ALL') {
    const durLabels = {
      'UP_TO_1Y': 'Up to 1 year',
      '1_TO_3Y': '1–3 years',
      '3_TO_5Y': '3–5 years',
      '5_TO_10Y': '5–10 years',
      'MORE_THAN_10Y': 'More than 10 years'
    };
    chips.push({
      key: 'duration',
      label: `Duration: ${durLabels[explorerState.durationFilter] || explorerState.durationFilter}`
    });
  }

  // Min investment chip
  if (explorerState.minInvestmentFilter !== 'ALL') {
    chips.push({
      key: 'min_investment',
      label: `Min Investment: Up to ₹${Number(explorerState.minInvestmentFilter).toLocaleString('en-IN')}`
    });
  }

  // Max expense ratio chip
  if (explorerState.maxExpenseRatioFilter !== 'ALL' && explorerState.activeTab !== 'STOCKS_EQUITY') {
    chips.push({
      key: 'expense_ratio',
      label: `Max Expense: ${explorerState.maxExpenseRatioFilter}%`
    });
  }

  // Sort chip if not relevance
  if (explorerState.sortBy !== 'relevance') {
    const sortLabels = {
      'return_desc': 'Sort: Returns High to Low',
      'expense_asc': 'Sort: Lowest Expense',
      'name_asc': 'Sort: Name A–Z'
    };
    chips.push({
      key: 'sort',
      label: sortLabels[explorerState.sortBy] || 'Sorted'
    });
  }

  if (chips.length === 0) {
    container.innerHTML = '';
    return;
  }

  container.innerHTML = chips.map(c => `
    <button type="button" class="active-filter-chip" data-chip-key="${c.key}">
      <span>${c.label}</span>
      <span class="active-filter-chip-remove" title="Remove filter"><i data-lucide="x" style="width:12px;height:12px;"></i></span>
    </button>
  `).join('');
  if (window.refreshIcons) window.refreshIcons(container);

  // Add click listeners to remove filter chip
  container.querySelectorAll('.active-filter-chip').forEach(btn => {
    btn.addEventListener('click', () => {
      const key = btn.getAttribute('data-chip-key');
      removeExplorerFilter(key);
    });
  });
}

function removeExplorerFilter(key) {
  if (key === 'search') {
    explorerState.searchQuery = '';
    const input = document.getElementById('explorer-search');
    if (input) input.value = '';
  } else if (key === 'risk') {
    explorerState.riskFilter = 'ALL';
    const select = document.getElementById('explorer-risk');
    if (select) select.value = 'ALL';
  } else if (key === 'duration') {
    explorerState.durationFilter = 'ALL';
    const select = document.getElementById('explorer-duration');
    if (select) select.value = 'ALL';
  } else if (key === 'min_investment') {
    explorerState.minInvestmentFilter = 'ALL';
    const select = document.getElementById('explorer-min-investment');
    if (select) select.value = 'ALL';
  } else if (key === 'expense_ratio') {
    explorerState.maxExpenseRatioFilter = 'ALL';
    const select = document.getElementById('explorer-expense-ratio');
    if (select) select.value = 'ALL';
  } else if (key === 'sort') {
    explorerState.sortBy = 'relevance';
    const select = document.getElementById('explorer-sort');
    if (select) select.value = 'relevance';
  }
  applySchemeExplorerFilters();
}

function updateResultsCount(count) {
  const badge = document.getElementById('explorer-results-count-badge');
  if (badge) {
    const word = count === 1 ? 'investment' : 'investments';
    badge.innerText = `Showing ${count} ${word}`;
  }
}

// ============================================================================
// 5. DEDICATED SIP INTERACTIVE PLANNER & CALCULATOR
// ============================================================================
function initDedicatedSIPCalculator() {
  const fundSel = document.getElementById('sip-dedicated-fund');
  const amtInput = document.getElementById('sip-dedicated-amount');
  const durInput = document.getElementById('sip-dedicated-duration');
  const rateInput = document.getElementById('sip-dedicated-rate');

  if (fundSel) {
    fundSel.addEventListener('change', () => {
      const opt = fundSel.options[fundSel.selectedIndex];
      const rate = opt.getAttribute('data-rate');
      if (rate && rateInput) {
        rateInput.value = parseFloat(rate).toFixed(1);
      }
      recalculateDedicatedSIP();
    });
  }

  [amtInput, durInput, rateInput].forEach(el => {
    if (el) el.addEventListener('input', debounce(recalculateDedicatedSIP, 150));
  });

  // Transfer buttons
  document.getElementById('btn-sip-quick-transfer')?.addEventListener('click', () => {
    const fundOpt = fundSel ? fundSel.options[fundSel.selectedIndex] : null;
    const name = fundOpt?.getAttribute('data-name') || 'Selected SIP Fund';
    const amount = parseFloat(amtInput?.value || 5000);
    const duration = parseInt(durInput?.value || 10);
    const rate = parseFloat(rateInput?.value || 15);
    const schemeId = fundSel?.value || null;

    transferToProjection({
      scheme_id: schemeId,
      name: name,
      category: 'SIP_INVESTMENTS',
      method: 'SIP',
      amount: amount,
      duration: duration,
      expected_return: rate
    });
  });

  document.getElementById('btn-sip-quick-portfolio')?.addEventListener('click', () => {
    const fundOpt = fundSel ? fundSel.options[fundSel.selectedIndex] : null;
    const name = fundOpt?.getAttribute('data-name') || 'Equity Fund SIP';
    const amount = parseFloat(amtInput?.value || 5000);
    const rate = parseFloat(rateInput?.value || 15);
    const schemeId = fundSel?.value || 'sip-item';

    addInvestmentToPortfolio({
      id: schemeId,
      name: `${name} (Monthly SIP)`,
      category: 'SIP_INVESTMENTS',
      method: 'SIP',
      amount: amount,
      expected_return_pct: rate,
      underlying_scheme_id: schemeId
    });
  });
}

function recalculateDedicatedSIP() {
  const amount = parseFloat(document.getElementById('sip-dedicated-amount')?.value || 5000);
  const years = parseInt(document.getElementById('sip-dedicated-duration')?.value || 10);
  const ratePct = parseFloat(document.getElementById('sip-dedicated-rate')?.value || 15.0);

  const months = years * 12;
  const totalInvested = amount * months;
  const monthlyRate = (ratePct / 100.0) / 12.0;

  // Monthly annuity due: FV = P * [((1 + r)^n - 1) / r] * (1 + r)
  let fv = 0;
  if (monthlyRate > 0) {
    fv = amount * ((Math.pow(1.0 + monthlyRate, months) - 1.0) / monthlyRate) * (1.0 + monthlyRate);
  } else {
    fv = totalInvested;
  }

  const gains = Math.max(0, fv - totalInvested);
  const multiplier = totalInvested > 0 ? (fv / totalInvested).toFixed(2) : '1.00';

  const invEl = document.getElementById('sip-calc-invested');
  const fvEl = document.getElementById('sip-calc-fv');
  const gainsEl = document.getElementById('sip-calc-gains');
  const mulEl = document.getElementById('sip-calc-multiplier');

  if (invEl) invEl.innerText = formatINR(totalInvested);
  if (fvEl) fvEl.innerText = formatINR(fv);
  if (gainsEl) gainsEl.innerText = `+${formatINR(gains)}`;
  if (mulEl) mulEl.innerText = `${multiplier}x`;
}

// ============================================================================
// 6. PERSONALIZED RECOMMENDATIONS ENGINE
// ============================================================================
function initPersonalizedRecommendations() {
  const btn = document.getElementById('btn-trigger-recs');
  if (btn) btn.addEventListener('click', fetchPersonalizedRecommendations);

  // Auto-refresh when preference inputs change
  ['pref-amount', 'pref-freq', 'pref-duration', 'pref-risk', 'pref-objective', 'pref-category', 'pref-liquidity'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('change', debounce(fetchPersonalizedRecommendations, 300));
  });
}

async function fetchPersonalizedRecommendations() {
  const amount = parseFloat(document.getElementById('pref-amount')?.value || 10000);
  const frequency = document.getElementById('pref-freq')?.value || 'MONTHLY';
  const duration = parseInt(document.getElementById('pref-duration')?.value || 5);
  const risk = document.getElementById('pref-risk')?.value || 'High';
  const objective = document.getElementById('pref-objective')?.value || 'wealth_accumulation';
  const preferredCat = document.getElementById('pref-category')?.value || 'ALL';
  const liquidity = document.getElementById('pref-liquidity')?.value || 'HIGH';

  const container = document.getElementById('recommendations-container');
  if (container) {
    container.style.opacity = '0.5';
  }

  try {
    const res = await secureFetch('/api/schemes/recommend', {
      method: 'POST',
      body: JSON.stringify({
        amount: amount,
        frequency: frequency,
        duration_years: duration,
        risk_tolerance: risk,
        objective: objective,
        preferred_category: preferredCat,
        liquidity: liquidity
      })
    });

    if (res && res.recommendations) {
      renderRecommendationsDOM(res.recommendations);
    }
  } catch (err) {
    console.error('Failed to fetch recommendations:', err);
  } finally {
    if (container) container.style.opacity = '1';
  }
}

function renderRecommendationsDOM(recommendations) {
  const container = document.getElementById('recommendations-container');
  if (!container) return;

  const countBadge = document.getElementById('recs-count-badge');
  if (countBadge) countBadge.innerText = `${recommendations.length} Matches Found`;

  if (!recommendations.length) {
    container.innerHTML = `
      <div style="grid-column: 1 / -1; padding: 32px; text-align: center; color: var(--text-muted); background: #fafbf9; border-radius: var(--radius-sm);">
        No direct matches found for strict filter. Try broadening your risk tolerance or horizon.
      </div>
    `;
    return;
  }

  container.innerHTML = recommendations.map(r => `
    <div class="scheme-card" style="border-top:3px solid var(--brand-lime);">
      <div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <span class="badge-pill badge-mint" style="font-size:10px;">${r.category_label || r.category}</span>
          <span class="badge-pill" style="background:#eef8ed;color:#166534;font-size:10px;font-weight:700;display:inline-flex;align-items:center;gap:4px;">
            <i data-lucide="star" style="width:12px;height:12px;"></i> ${r.match_score}% Match
          </span>
        </div>

        <div class="scheme-title" style="font-size:15px;font-weight:800;">${r.name}</div>
        <div class="scheme-provider" style="font-size:12px;color:var(--text-muted);margin-bottom:10px;">${r.provider}</div>

        <div style="background:#fafbf9;border-left:3px solid var(--pastel-mint-accent);border-radius:4px;padding:10px 12px;margin-bottom:12px;font-size:11px;color:var(--text-secondary);line-height:1.5;">
          <strong style="color:var(--pastel-mint-accent);display:block;margin-bottom:2px;">Why Recommended:</strong>
          ${r.recommendation_reason}
        </div>

        <div class="scheme-meta-grid" style="grid-template-columns:1fr 1fr;gap:8px;">
          <div class="scheme-meta-item">
            <div class="scheme-meta-label">5Y Return (CAGR)</div>
            <div class="scheme-meta-val" style="color:#16a34a;font-weight:800;">
              ${r.cagr_5y ? `+${r.cagr_5y}% p.a.` : (r.cagr_3y ? `+${r.cagr_3y}% p.a.` : `~${r.expected_annual_return}%`)}
            </div>
          </div>
          <div class="scheme-meta-item">
            <div class="scheme-meta-label">Expense / Charges</div>
            <div class="scheme-meta-val">${r.expense_ratio}</div>
          </div>
        </div>

        <div style="display:flex;justify-content:space-between;align-items:center;font-size:10px;color:var(--text-muted);margin-top:10px;padding-top:8px;border-top:1px solid rgba(0,0,0,0.04);">
          <span>Source: ${r.data_source}</span>
          <span>Updated: ${r.last_updated}</span>
        </div>
      </div>

      <div class="scheme-card-actions" style="margin-top:12px;">
        <button type="button" class="btn btn-secondary btn-sm action-view-details" data-id="${r.id}">Details</button>
        <button type="button" class="btn btn-primary btn-sm action-project-scheme" 
          data-id="${r.id}" 
          data-rate="${r.cagr_5y || r.expected_annual_return}" 
          data-name="${r.name}" 
          data-method="${r.category === 'SIP_INVESTMENTS' ? 'SIP' : 'LUMPSUM'}" 
          data-amount="10000"><i data-lucide="chart-no-axes-combined"></i> Project</button>
        <button type="button" class="btn btn-dark btn-sm action-add-portfolio" 
          data-id="${r.id}" 
          data-category="${r.category}" 
          data-underlying="${r.underlying_scheme_id || ''}" 
          data-rate="${r.cagr_5y || r.expected_annual_return}" 
          data-name="${r.name}" 
          data-method="${r.category === 'SIP_INVESTMENTS' ? 'SIP' : 'LUMPSUM'}" 
          data-amount="10000"><i data-lucide="plus"></i> Portfolio</button>
      </div>
    </div>
  `).join('');
  if (window.refreshIcons) window.refreshIcons(container);
}

// ============================================================================
// 7. SIDE-BY-SIDE COMPARISON MATRIX
// ============================================================================
function initCompare() {
  const btnRun = document.getElementById('btn-run-compare');
  if (btnRun) btnRun.addEventListener('click', runComparisonMatrix);
}

function addSchemeToCompare(schemeId) {
  const s1 = document.getElementById('compare-s1');
  const s2 = document.getElementById('compare-s2');
  const s3 = document.getElementById('compare-s3');
  const s4 = document.getElementById('compare-s4');

  if (s1 && !s1.value) s1.value = schemeId;
  else if (s2 && !s2.value) s2.value = schemeId;
  else if (s3 && !s3.value) s3.value = schemeId;
  else if (s4 && !s4.value) s4.value = schemeId;
  else if (s3) s3.value = schemeId;

  // Scroll to compare section
  const compSection = document.getElementById('compare-s1')?.closest('.calc-section');
  if (compSection) {
    compSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    runComparisonMatrix();
  }
}

async function runComparisonMatrix() {
  const s1 = document.getElementById('compare-s1')?.value;
  const s2 = document.getElementById('compare-s2')?.value;
  const s3 = document.getElementById('compare-s3')?.value;
  const s4 = document.getElementById('compare-s4')?.value;

  const schemeIds = [s1, s2, s3, s4].filter(id => id && id.trim().length > 0);
  if (schemeIds.length < 2) {
    alert('Please select at least 2 options to compare.');
    return;
  }

  const amount = parseFloat(document.getElementById('compare-amount')?.value || 50000);
  const duration = parseInt(document.getElementById('compare-duration')?.value || 5);
  const method = document.getElementById('compare-method')?.value || 'LUMPSUM';

  const wrapper = document.getElementById('compare-results-wrapper');
  if (wrapper) {
    wrapper.innerHTML = '<div style="padding:32px;text-align:center;color:var(--text-muted);">Comparing schemes side-by-side...</div>';
  }

  try {
    const res = await secureFetch('/api/schemes/compare', {
      method: 'POST',
      body: JSON.stringify({
        scheme_ids: schemeIds,
        amount: amount,
        duration_years: duration,
        method: method
      })
    });

    if (res && res.comparison) {
      renderComparisonTable(res.comparison);
    }
  } catch (err) {
    console.error('Comparison error:', err);
    if (wrapper) wrapper.innerHTML = `<div style="padding:24px;color:red;text-align:center;">Failed to run comparison: ${err.message}</div>`;
  }
}

function renderComparisonTable(comp) {
  const wrapper = document.getElementById('compare-results-wrapper');
  if (!wrapper || !comp.schemes) return;

  const schemes = comp.schemes;

  let tableHtml = `
    <table class="custom-table" style="min-width:700px;">
      <thead>
        <tr>
          <th style="width:200px;background:#f8faf6;">Comparison Parameter</th>
          ${schemes.map(s => `
            <th style="min-width:180px;text-align:left;">
              <span class="badge-pill badge-mint" style="font-size:9px;">${s.category_label || s.category}</span>
              <div style="font-weight:800;font-size:13px;margin-top:4px;">${s.name}</div>
            </th>
          `).join('')}
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="font-weight:700;background:#f8faf6;">Risk Level</td>
          ${schemes.map(s => `<td><span class="badge-pill badge-dark" style="font-size:10px;">${s.risk_level}</span></td>`).join('')}
        </tr>
        <tr>
          <td style="font-weight:700;background:#f8faf6;">Historical 5Y Return</td>
          ${schemes.map(s => `<td style="color:#16a34a;font-weight:800;">${s.cagr_5y ? `+${s.cagr_5y}% p.a.` : 'N/A'}</td>`).join('')}
        </tr>
        <tr>
          <td style="font-weight:700;background:#f8faf6;">Fees / Expense Ratio</td>
          ${schemes.map(s => `<td>${s.expense_ratio}</td>`).join('')}
        </tr>
        <tr>
          <td style="font-weight:700;background:#f8faf6;">Liquidity & Exit</td>
          ${schemes.map(s => `<td style="font-size:11px;">${s.liquidity}</td>`).join('')}
        </tr>
        <tr>
          <td style="font-weight:700;background:#f8faf6;">Minimum Investment</td>
          ${schemes.map(s => `<td>${s.min_investment_formatted}</td>`).join('')}
        </tr>
        <tr>
          <td style="font-weight:700;background:#f8faf6;">Lock-In Period</td>
          ${schemes.map(s => `<td>${s.lock_in}</td>`).join('')}
        </tr>
        <tr style="background:#f0fdf4;">
          <td style="font-weight:800;color:#166534;">Projected Future Value</td>
          ${schemes.map(s => `
            <td style="font-weight:800;font-size:15px;color:#166534;">
              ${s.future_projection.future_value_formatted}
            </td>
          `).join('')}
        </tr>
        <tr>
          <td style="font-weight:700;background:#f8faf6;">Key Advantages</td>
          ${schemes.map(s => `
            <td style="font-size:11px;color:#15803d;">
              ${(s.advantages || []).slice(0, 2).map(a => `<div style="display:flex;align-items:flex-start;gap:4px;margin-bottom:2px;"><i data-lucide="check" style="width:12px;height:12px;flex-shrink:0;margin-top:2px;"></i><span>${a}</span></div>`).join('')}
            </td>
          `).join('')}
        </tr>
        <tr>
          <td style="font-weight:700;background:#f8faf6;">Limitations & Risks</td>
          ${schemes.map(s => `
            <td style="font-size:11px;color:#b91c1c;">
              ${(s.disadvantages || []).slice(0, 2).map(d => `<div style="display:flex;align-items:flex-start;gap:4px;margin-bottom:2px;"><i data-lucide="alert-triangle" style="width:12px;height:12px;flex-shrink:0;margin-top:2px;"></i><span>${d}</span></div>`).join('')}
            </td>
          `).join('')}
        </tr>
        <tr>
          <td style="background:#f8faf6;">Quick Action</td>
          ${schemes.map(s => `
            <td>
              <button type="button" class="btn btn-primary btn-sm action-project-scheme" 
                data-id="${s.id}" 
                data-rate="${s.cagr_5y || 12.0}" 
                data-name="${s.name}" 
                data-method="${comp.parameters?.method || 'LUMPSUM'}" 
                data-amount="${comp.parameters?.amount || 50000}">
                <i data-lucide="chart-no-axes-combined"></i> Project
              </button>
            </td>
          `).join('')}
        </tr>
      </tbody>
    </table>
  `;

  wrapper.innerHTML = tableHtml;
  if (window.refreshIcons) window.refreshIcons(wrapper);
}

// ============================================================================
// 8. FUTURE COMPOUND GROWTH CALCULATOR (SECTION 5)
// ============================================================================
function initFutureCalc() {
  const form = document.getElementById('investment-calc-form');
  if (!form) return;

  const schemeLink = document.getElementById('calc-scheme-link');
  if (schemeLink) {
    schemeLink.addEventListener('change', () => {
      const opt = schemeLink.options[schemeLink.selectedIndex];
      const rate = opt.getAttribute('data-rate');
      const badge = document.getElementById('active-linked-badge');
      if (rate) {
        document.getElementById('calc-return').value = parseFloat(rate).toFixed(2);
      }
      if (badge) {
        badge.innerText = opt.value ? `Linked: ${opt.getAttribute('data-name') || opt.text}` : 'Manual Custom Parameters';
      }
      recalculateInvestment();
    });
  }

  const inputs = ['calc-initial', 'calc-periodic', 'calc-freq', 'calc-return', 'calc-duration', 'calc-step-up', 'calc-timing'];
  inputs.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('input', debounce(recalculateInvestment, 200));
  });

  document.getElementById('btn-reset-calc')?.addEventListener('click', () => {
    document.getElementById('calc-scheme-link').value = '';
    document.getElementById('calc-initial').value = '10000';
    document.getElementById('calc-periodic').value = '5000';
    document.getElementById('calc-freq').value = 'MONTHLY';
    document.getElementById('calc-return').value = '12.0';
    document.getElementById('calc-duration').value = '10';
    document.getElementById('calc-step-up').value = '0';
    document.getElementById('active-linked-badge').innerText = 'Manual Custom Parameters';
    recalculateInvestment();
  });

  document.getElementById('btn-add-current-to-portfolio')?.addEventListener('click', () => {
    const schemeId = document.getElementById('calc-scheme-link')?.value || 'custom-investment';
    const opt = document.getElementById('calc-scheme-link')?.selectedOptions[0];
    const name = opt?.value ? (opt.getAttribute('data-name') || opt.text) : 'Custom Investment';
    const cat = opt?.getAttribute('data-category') || 'EQUITY_MUTUAL_FUNDS';
    const initial = parseFloat(document.getElementById('calc-initial')?.value || 0);
    const periodic = parseFloat(document.getElementById('calc-periodic')?.value || 0);
    const method = periodic > 0 ? 'SIP' : 'LUMPSUM';
    const amount = periodic > 0 ? periodic : initial;
    const rate = parseFloat(document.getElementById('calc-return')?.value || 12);

    addInvestmentToPortfolio({
      id: schemeId,
      name: name,
      category: cat,
      method: method,
      amount: amount,
      expected_return_pct: rate
    });
  });

  // Initial run
  recalculateInvestment();
}

async function recalculateInvestment() {
  const initial = parseFloat(document.getElementById('calc-initial')?.value || 0);
  const periodic = parseFloat(document.getElementById('calc-periodic')?.value || 0);
  const freq = document.getElementById('calc-freq')?.value || 'MONTHLY';
  const returnPct = parseFloat(document.getElementById('calc-return')?.value || 12);
  const duration = parseInt(document.getElementById('calc-duration')?.value || 10);
  const timing = document.getElementById('calc-timing')?.value || 'BEGINNING';
  const stepUp = parseFloat(document.getElementById('calc-step-up')?.value || 0);
  const schemeId = document.getElementById('calc-scheme-link')?.value || null;

  try {
    const res = await secureFetch('/api/tools/investment-calculate', {
      method: 'POST',
      body: JSON.stringify({
        initial_amount: initial,
        periodic_contribution: periodic,
        frequency: freq,
        annual_return_pct: returnPct,
        duration_years: duration,
        timing: timing,
        step_up_pct: stepUp,
        scheme_id: schemeId
      })
    });

    if (res && res.result) {
      updateFutureCalcDOM(res.result);
      updateThreeScenarios(initial, periodic, freq, returnPct, duration, timing, stepUp);
    }
  } catch (err) {
    console.error('Future investment calculation error:', err);
  }
}

function updateFutureCalcDOM(result) {
  const sum = result.summary;
  document.getElementById('calc-invested-display').innerText = sum.total_invested_formatted;
  document.getElementById('calc-returns-display').innerText = sum.estimated_returns_formatted;
  document.getElementById('calc-fv-display').innerText = sum.future_value_formatted;
  const ratioEl = document.getElementById('calc-gain-ratio-display');
  if (ratioEl) ratioEl.innerText = sum.gain_ratio_pct + '%';

  // Schedule table
  const tbody = document.getElementById('calc-schedule-tbody');
  if (tbody && result.schedule) {
    tbody.innerHTML = result.schedule.map(row => `
      <tr>
        <td style="font-weight:700;">Year ${row.year}</td>
        <td>${row.invested_formatted}</td>
        <td style="color:#16a34a;font-weight:700;">+${row.returns_formatted}</td>
        <td style="font-weight:800;">${row.future_value_formatted}</td>
      </tr>
    `).join('');
  }

  // Update Trajectory Chart
  updateInvestmentChart(result.schedule);
}

function updateThreeScenarios(initial, periodic, freq, baseReturn, duration, timing, stepUp) {
  const consRate = Math.max(1.0, baseReturn - 2.5);
  const optRate = baseReturn + 2.5;

  const rateConsEl = document.getElementById('scenario-rate-cons');
  const rateModEl = document.getElementById('scenario-rate-mod');
  const rateOptEl = document.getElementById('scenario-rate-opt');

  if (rateConsEl) rateConsEl.innerText = `${consRate.toFixed(1)}%`;
  if (rateModEl) rateModEl.innerText = `${baseReturn.toFixed(1)}%`;
  if (rateOptEl) rateOptEl.innerText = `${optRate.toFixed(1)}%`;

  // Fetch conservative & optimistic FV
  Promise.all([
    secureFetch('/api/tools/investment-calculate', {
      method: 'POST',
      body: JSON.stringify({
        initial_amount: initial,
        periodic_contribution: periodic,
        frequency: freq,
        annual_return_pct: consRate,
        duration_years: duration,
        timing: timing,
        step_up_pct: stepUp
      })
    }),
    secureFetch('/api/tools/investment-calculate', {
      method: 'POST',
      body: JSON.stringify({
        initial_amount: initial,
        periodic_contribution: periodic,
        frequency: freq,
        annual_return_pct: optRate,
        duration_years: duration,
        timing: timing,
        step_up_pct: stepUp
      })
    })
  ]).then(([consRes, optRes]) => {
    if (consRes?.result) {
      const fvCons = document.getElementById('scenario-fv-cons');
      const gainCons = document.getElementById('scenario-gain-cons');
      if (fvCons) fvCons.innerText = consRes.result.summary.future_value_formatted;
      if (gainCons) gainCons.innerText = `Gains: +${consRes.result.summary.estimated_returns_formatted}`;
    }
    if (optRes?.result) {
      const fvOpt = document.getElementById('scenario-fv-opt');
      const gainOpt = document.getElementById('scenario-gain-opt');
      if (fvOpt) fvOpt.innerText = optRes.result.summary.future_value_formatted;
      if (gainOpt) gainOpt.innerText = `Gains: +${optRes.result.summary.estimated_returns_formatted}`;
    }
  }).catch(err => console.error('Scenario fetch error:', err));
}

function updateInvestmentChart(schedule) {
  const canvas = document.getElementById('investmentChart');
  if (!canvas || !window.Chart) return;

  const labels = schedule.map(r => `Year ${r.year}`);
  const investedData = schedule.map(r => r.invested_minor / 100);
  const fvData = schedule.map(r => r.future_value_minor / 100);

  if (calcChart) {
    calcChart.data.labels = labels;
    calcChart.data.datasets[0].data = investedData;
    calcChart.data.datasets[1].data = fvData;
    calcChart.update();
    return;
  }

  const ctx = canvas.getContext('2d');
  calcChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Total Capital Invested',
          data: investedData,
          borderColor: '#0284c7',
          backgroundColor: 'rgba(2, 132, 199, 0.08)',
          fill: true,
          tension: 0.3,
          borderWidth: 2,
          pointRadius: 3
        },
        {
          label: 'Estimated Future Corpus',
          data: fvData,
          borderColor: '#16a34a',
          backgroundColor: 'rgba(22, 163, 74, 0.12)',
          fill: true,
          tension: 0.35,
          borderWidth: 3,
          pointRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'top', labels: { boxWidth: 12, font: { size: 11, weight: '600' } } },
        tooltip: {
          callbacks: {
            label: function(context) {
              return `${context.dataset.label}: ${formatINR(context.parsed.y)}`;
            }
          }
        }
      },
      scales: {
        y: {
          ticks: {
            callback: function(val) {
              if (val >= 10000000) return '₹' + (val / 10000000).toFixed(1) + ' Cr';
              if (val >= 100000) return '₹' + (val / 100000).toFixed(1) + ' L';
              if (val >= 1000) return '₹' + (val / 1000).toFixed(0) + 'k';
              return '₹' + val;
            }
          }
        }
      }
    }
  });
}

// ============================================================================
// 9. MULTI-INVESTMENT PORTFOLIO BUILDER (NO DOUBLE-COUNTING SIP)
// ============================================================================
function initPortfolioBuilder() {
  document.getElementById('btn-clear-portfolio')?.addEventListener('click', () => {
    portfolioInvestments = [];
    updatePortfolioDOM();
  });
}

function addInvestmentToPortfolio(inv) {
  portfolioInvestments.push(inv);
  updatePortfolioDOM();

  // Scroll smoothly down to portfolio
  const card = document.getElementById('portfolio-builder-card');
  if (card) {
    card.scrollIntoView({ behavior: 'smooth', block: 'start' });
    card.style.boxShadow = '0 0 0 3px var(--brand-lime)';
    setTimeout(() => { card.style.boxShadow = ''; }, 1200);
  }
}

function removeInvestmentFromPortfolio(idx) {
  portfolioInvestments.splice(idx, 1);
  updatePortfolioDOM();
}

async function updatePortfolioDOM() {
  const countBadge = document.getElementById('portfolio-count-badge');
  if (countBadge) countBadge.innerText = `${portfolioInvestments.length} Items in Portfolio`;

  const tbody = document.getElementById('portfolio-tbody');
  if (!tbody) return;

  if (!portfolioInvestments.length) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" style="text-align:center;color:var(--text-muted);padding:24px;">
          No investments added yet. Click "+ Portfolio" on any card above or "Add Current Projection to Portfolio".
        </td>
      </tr>
    `;
    resetPortfolioSummary();
    return;
  }

  try {
    const res = await secureFetch('/api/tools/portfolio-calculate', {
      method: 'POST',
      body: JSON.stringify({
        investments: portfolioInvestments,
        duration_years: 10
      })
    });

    if (res && res.portfolio) {
      renderPortfolioResults(res.portfolio);
    }
  } catch (err) {
    console.error('Portfolio calculation error:', err);
  }
}

function renderPortfolioResults(port) {
  const tbody = document.getElementById('portfolio-tbody');
  if (!tbody || !port.items) return;

  tbody.innerHTML = port.items.map((item, idx) => `
    <tr>
      <td style="font-weight:700;">${item.name}</td>
      <td>
        <span class="badge-pill badge-mint" style="font-size:10px;">${item.category}</span>
        ${item.category === 'SIP_INVESTMENTS' ? '<span style="font-size:10px;color:var(--text-muted);display:block;">(Linked to Equity MF)</span>' : ''}
      </td>
      <td><span class="badge-pill badge-dark" style="font-size:10px;">${item.method}</span></td>
      <td style="font-weight:600;">₹${item.amount.toLocaleString()}</td>
      <td style="color:#16a34a;font-weight:700;">${item.expected_return_pct}%</td>
      <td>${item.total_invested_formatted}</td>
      <td style="font-weight:800;color:var(--text-primary);">${item.future_value_formatted}</td>
      <td>
        <button type="button" class="btn btn-danger btn-sm" onclick="removeInvestmentFromPortfolio(${idx})" style="padding:4px 8px;font-size:11px;display:inline-flex;align-items:center;gap:4px;" title="Remove investment">
          <i data-lucide="trash-2" style="width:13px;height:13px;"></i> Remove
        </button>
      </td>
    </tr>
  `).join('');

  // Update Asset Allocation Progress Bar (Strictly 3 Underlying Classes)
  const alloc = port.asset_allocation || {};
  const pctStocks = alloc.STOCKS_EQUITY?.percentage || 0;
  const pctMf = alloc.EQUITY_MUTUAL_FUNDS?.percentage || 0;
  const pctGold = alloc.GOLD?.percentage || 0;

  const barStocks = document.getElementById('alloc-bar-stocks');
  const barMf = document.getElementById('alloc-bar-mf');
  const barGold = document.getElementById('alloc-bar-gold');

  if (barStocks) barStocks.style.width = `${pctStocks}%`;
  if (barMf) barMf.style.width = `${pctMf}%`;
  if (barGold) barGold.style.width = `${pctGold}%`;

  const labelStocks = document.getElementById('alloc-label-stocks');
  const labelMf = document.getElementById('alloc-label-mf');
  const labelGold = document.getElementById('alloc-label-gold');

  if (labelStocks) labelStocks.innerText = `${pctStocks}% (${alloc.STOCKS_EQUITY?.formatted || '₹0'})`;
  if (labelMf) labelMf.innerText = `${pctMf}% (${alloc.EQUITY_MUTUAL_FUNDS?.formatted || '₹0'})`;
  if (labelGold) labelGold.innerText = `${pctGold}% (${alloc.GOLD?.formatted || '₹0'})`;

  // Update Consolidated Totals
  const totInvEl = document.getElementById('port-total-invested');
  const totFvEl = document.getElementById('port-total-fv');
  const totGainEl = document.getElementById('port-total-gains');
  const scenEl = document.getElementById('port-scenarios');

  if (totInvEl) totInvEl.innerText = port.total_invested_formatted;
  if (totFvEl) totFvEl.innerText = port.future_value_formatted;
  if (totGainEl) totGainEl.innerText = `+${port.estimated_returns_formatted} (${port.gain_ratio_pct}%)`;

  const scen = port.scenarios || {};
  if (scenEl) {
    scenEl.innerText = `${scen.conservative?.future_value_formatted || '₹0'} / ${scen.optimistic?.future_value_formatted || '₹0'}`;
  }
  if (window.refreshIcons) window.refreshIcons(tbody);
}

function resetPortfolioSummary() {
  document.getElementById('alloc-bar-stocks')?.style.setProperty('width', '33%');
  document.getElementById('alloc-bar-mf')?.style.setProperty('width', '34%');
  document.getElementById('alloc-bar-gold')?.style.setProperty('width', '33%');
  document.getElementById('alloc-label-stocks').innerText = '0% (₹0)';
  document.getElementById('alloc-label-mf').innerText = '0% (₹0)';
  document.getElementById('alloc-label-gold').innerText = '0% (₹0)';
  document.getElementById('port-total-invested').innerText = '₹0';
  document.getElementById('port-total-fv').innerText = '₹0';
  document.getElementById('port-total-gains').innerText = '+₹0';
  document.getElementById('port-scenarios').innerText = '₹0 / ₹0';
}

// ============================================================================
// 10. TRANSFER PARAMETERS HELPER
// ============================================================================
function transferToProjection(data) {
  const schemeSel = document.getElementById('calc-scheme-link');
  if (schemeSel && data.scheme_id) {
    schemeSel.value = data.scheme_id;
  }

  const badge = document.getElementById('active-linked-badge');
  if (badge) {
    badge.innerText = `Linked: ${data.name || 'Selected Instrument'}`;
  }

  const initialInput = document.getElementById('calc-initial');
  const periodicInput = document.getElementById('calc-periodic');
  const freqSel = document.getElementById('calc-freq');
  const rateInput = document.getElementById('calc-return');
  const durInput = document.getElementById('calc-duration');

  if (data.method === 'SIP') {
    if (initialInput) initialInput.value = '0';
    if (periodicInput) periodicInput.value = data.amount || 5000;
    if (freqSel) freqSel.value = 'MONTHLY';
  } else {
    if (initialInput) initialInput.value = data.amount || 50000;
    if (periodicInput) periodicInput.value = '0';
    if (freqSel) freqSel.value = 'YEARLY';
  }

  if (data.expected_return && rateInput) {
    rateInput.value = parseFloat(data.expected_return).toFixed(2);
  }

  if (data.duration && durInput) {
    durInput.value = data.duration;
  }

  // Recalculate
  recalculateInvestment();

  // Scroll to section 5 smoothly
  const sec = document.getElementById('section-future-projection');
  if (sec) {
    sec.scrollIntoView({ behavior: 'smooth', block: 'start' });
    sec.style.outline = '2px solid var(--brand-lime)';
    setTimeout(() => { sec.style.outline = 'none'; }, 1200);
  }
}

// ============================================================================
// 11. CLICK DELEGATION FOR ALL CARDS
// ============================================================================
function initCardDelegation() {
  document.addEventListener('click', (e) => {
    // 1. Details Modal
    const btnDetails = e.target.closest('.action-view-details');
    if (btnDetails) {
      const id = btnDetails.getAttribute('data-id');
      if (id) openSchemeDetailsModal(id);
      return;
    }

    // 2. Project Scheme in Calculator
    const btnProject = e.target.closest('.action-project-scheme');
    if (btnProject) {
      const id = btnProject.getAttribute('data-id');
      const rate = btnProject.getAttribute('data-rate');
      const name = btnProject.getAttribute('data-name');
      const method = btnProject.getAttribute('data-method') || 'LUMPSUM';
      const amount = parseFloat(btnProject.getAttribute('data-amount') || 50000);

      transferToProjection({
        scheme_id: id,
        name: name,
        method: method,
        amount: amount,
        expected_return: rate
      });
      return;
    }

    // 3. Add to Portfolio
    const btnPort = e.target.closest('.action-add-portfolio');
    if (btnPort) {
      const id = btnPort.getAttribute('data-id');
      const name = btnPort.getAttribute('data-name');
      const cat = btnPort.getAttribute('data-category') || 'EQUITY_MUTUAL_FUNDS';
      const underlying = btnPort.getAttribute('data-underlying');
      const rate = parseFloat(btnPort.getAttribute('data-rate') || 12);
      const method = btnPort.getAttribute('data-method') || 'LUMPSUM';
      const amount = parseFloat(btnPort.getAttribute('data-amount') || 10000);

      addInvestmentToPortfolio({
        id: id,
        name: name,
        category: cat,
        underlying_scheme_id: underlying,
        method: method,
        amount: amount,
        expected_return_pct: rate
      });
      return;
    }

    // 4. Compare Add
    const btnComp = e.target.closest('.action-compare-add');
    if (btnComp) {
      const id = btnComp.getAttribute('data-id');
      if (id) addSchemeToCompare(id);
      return;
    }
  });
}

// ============================================================================
// 12. "WHAT IF I INVESTED EARLIER?" HISTORICAL CALCULATOR
// ============================================================================
function initWhatIfCalc() {
  const form = document.getElementById('what-if-form');
  if (!form) return;

  const schemeSel = document.getElementById('whatif-scheme');
  const methodSel = document.getElementById('whatif-method');
  const amountInput = document.getElementById('whatif-amount');

  if (schemeSel) schemeSel.addEventListener('change', recalculateWhatIf);
  if (methodSel) methodSel.addEventListener('change', recalculateWhatIf);
  if (amountInput) amountInput.addEventListener('input', debounce(recalculateWhatIf, 250));

  document.querySelectorAll('.duration-pill-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.duration-pill-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentWhatIfYears = parseInt(btn.getAttribute('data-years'));
      const txt = document.getElementById('whatif-duration-text');
      if (txt) txt.innerText = `${currentWhatIfYears} Years Ago`;
      recalculateWhatIf();
    });
  });
}

async function recalculateWhatIf() {
  const schemeId = document.getElementById('whatif-scheme')?.value || 'parag-parikh-flexi-cap';
  const method = document.getElementById('whatif-method')?.value || 'LUMPSUM';
  const amount = parseFloat(document.getElementById('whatif-amount')?.value || 50000);

  try {
    const res = await secureFetch('/api/schemes/what-if', {
      method: 'POST',
      body: JSON.stringify({
        scheme_id: schemeId,
        amount: amount,
        duration_years: currentWhatIfYears,
        method: method
      })
    });

    if (res && res.result) {
      updateWhatIfDOM(res.result);
    }
  } catch (err) {
    console.error('What-If calculation error:', err);
  }
}

function updateWhatIfDOM(result) {
  const sum = result.summary;
  const s = result.scheme;

  document.getElementById('whatif-invested-display').innerText = sum.original_investment_formatted;
  document.getElementById('whatif-current-display').innerText = sum.current_value_formatted;
  document.getElementById('whatif-profit-display').innerText = sum.profit_loss_formatted;
  document.getElementById('whatif-cagr-display').innerText = `${sum.annualized_return_pct}% p.a.`;
  document.getElementById('whatif-return-pct-display').innerText = `+${sum.total_return_pct}% total return`;

  const methodLabel = document.getElementById('whatif-method-label');
  if (methodLabel) {
    methodLabel.innerText = sum.method === 'SIP' ? 'Monthly SIP Compounded' : 'Lump Sum Compounded';
  }

  // Highlight card
  if (s) {
    document.getElementById('whatif-card-cat').innerText = s.category_label || s.category;
    document.getElementById('whatif-card-risk').innerText = `${s.risk_level} Risk`;
    document.getElementById('whatif-card-title').innerText = s.name;
    document.getElementById('whatif-card-obj').innerText = s.objective;
    document.getElementById('whatif-1y').innerText = s.cagr_1y ? `${s.cagr_1y}%` : 'N/A';
    document.getElementById('whatif-3y').innerText = s.cagr_3y ? `${s.cagr_3y}%` : 'N/A';
    document.getElementById('whatif-5y').innerText = s.cagr_5y ? `${s.cagr_5y}%` : 'N/A';
  }

  // Schedule table
  const tbody = document.getElementById('whatif-schedule-tbody');
  if (tbody && result.timeline) {
    tbody.innerHTML = result.timeline.map(row => `
      <tr>
        <td style="font-weight:700;">Year ${row.year}</td>
        <td>${row.invested_formatted}</td>
        <td style="font-weight:800;color:var(--text-primary);">${row.value_formatted}</td>
        <td style="color:#16a34a;font-weight:700;">+${row.profit_formatted}</td>
      </tr>
    `).join('');
  }

  // Chart
  updateWhatIfChart(result.timeline);
}

function updateWhatIfChart(timeline) {
  const canvas = document.getElementById('whatIfChart');
  if (!canvas || !window.Chart) return;

  const labels = timeline.map(r => `Year ${r.year}`);
  const investedData = timeline.map(r => r.invested);
  const valData = timeline.map(r => r.value);

  if (whatIfChart) {
    whatIfChart.data.labels = labels;
    whatIfChart.data.datasets[0].data = investedData;
    whatIfChart.data.datasets[1].data = valData;
    whatIfChart.update();
    return;
  }

  const ctx = canvas.getContext('2d');
  whatIfChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Original Capital Deposited',
          data: investedData,
          borderColor: '#0284c7',
          backgroundColor: 'rgba(2, 132, 199, 0.08)',
          fill: true,
          tension: 0.3,
          borderWidth: 2,
          pointRadius: 3
        },
        {
          label: 'Historical Valuation Today',
          data: valData,
          borderColor: '#16a34a',
          backgroundColor: 'rgba(22, 163, 74, 0.15)',
          fill: true,
          tension: 0.35,
          borderWidth: 3,
          pointRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'top', labels: { boxWidth: 12, font: { size: 11, weight: '600' } } },
        tooltip: {
          callbacks: {
            label: function(context) {
              return `${context.dataset.label}: ${formatINR(context.parsed.y)}`;
            }
          }
        }
      },
      scales: {
        y: {
          ticks: {
            callback: function(val) {
              if (val >= 10000000) return '₹' + (val / 10000000).toFixed(1) + ' Cr';
              if (val >= 100000) return '₹' + (val / 100000).toFixed(1) + ' L';
              if (val >= 1000) return '₹' + (val / 1000).toFixed(0) + 'k';
              return '₹' + val;
            }
          }
        }
      }
    }
  });
}

// ============================================================================
// 13. SCHEME DETAILS MODAL
// ============================================================================
function initSchemeModal() {
  const modal = document.getElementById('scheme-details-modal');
  const closeBtn = document.getElementById('btn-close-scheme-modal');

  if (closeBtn && modal) {
    closeBtn.addEventListener('click', () => modal.classList.remove('active'));
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.classList.remove('active');
    });
  }

  document.getElementById('modal-act-whatif')?.addEventListener('click', () => {
    if (activeModalScheme) {
      const schemeSel = document.getElementById('whatif-scheme');
      if (schemeSel) schemeSel.value = activeModalScheme.id;
      modal.classList.remove('active');
      switchTopTab('tab-what-if');
      recalculateWhatIf();
    }
  });

  document.getElementById('modal-act-future')?.addEventListener('click', () => {
    if (activeModalScheme) {
      modal.classList.remove('active');
      transferToProjection({
        scheme_id: activeModalScheme.id,
        name: activeModalScheme.name,
        method: activeModalScheme.category === 'SIP_INVESTMENTS' ? 'SIP' : 'LUMPSUM',
        amount: activeModalScheme.category === 'SIP_INVESTMENTS' ? (activeModalScheme.min_sip || 5000) : 50000,
        expected_return: activeModalScheme.cagr_5y || activeModalScheme.expected_annual_return || 12
      });
    }
  });

  document.getElementById('modal-act-compare')?.addEventListener('click', () => {
    if (activeModalScheme) {
      modal.classList.remove('active');
      addSchemeToCompare(activeModalScheme.id);
    }
  });
}

async function openSchemeDetailsModal(schemeId) {
  const modal = document.getElementById('scheme-details-modal');
  if (!modal) return;

  let scheme = cachedSchemes.find(s => s.id === schemeId);

  if (!scheme) {
    try {
      const res = await secureFetch(`/api/schemes/${schemeId}`);
      if (res && res.scheme) scheme = res.scheme;
    } catch (err) {
      console.error('Failed to load scheme details:', err);
      return;
    }
  }

  if (!scheme) return;
  activeModalScheme = scheme;

  document.getElementById('modal-category').innerText = scheme.category_label || scheme.category;
  document.getElementById('modal-risk').innerText = `${scheme.risk_level} Risk`;
  document.getElementById('modal-title').innerText = scheme.name;
  document.getElementById('modal-provider').innerText = `${scheme.provider} • ${scheme.category_label || scheme.category}`;
  document.getElementById('modal-objective').innerText = scheme.objective;
  document.getElementById('modal-how-it-works').innerText = scheme.how_it_works || 'Investments in this asset follow SEBI/AMFI regulatory guidelines.';
  document.getElementById('modal-eligibility').innerText = scheme.eligibility || 'KYC-compliant Indian investors';
  document.getElementById('modal-min-invest').innerText = scheme.min_investment_formatted;
  document.getElementById('modal-lock-in').innerText = scheme.lock_in;
  document.getElementById('modal-expense').innerText = scheme.expense_ratio;
  document.getElementById('modal-liquidity').innerText = scheme.liquidity;
  document.getElementById('modal-tax-treatment').innerText = scheme.tax_treatment;

  document.getElementById('modal-1y').innerText = scheme.cagr_1y ? `${scheme.cagr_1y}%` : 'N/A';
  document.getElementById('modal-3y').innerText = scheme.cagr_3y ? `${scheme.cagr_3y}%` : 'N/A';
  document.getElementById('modal-5y').innerText = scheme.cagr_5y ? `${scheme.cagr_5y}%` : (scheme.current_interest_rate ? `${scheme.current_interest_rate}%` : 'N/A');
  document.getElementById('modal-10y').innerText = scheme.cagr_10y ? `${scheme.cagr_10y}%` : 'N/A';

  const prosUl = document.getElementById('modal-pros');
  if (prosUl) {
    prosUl.innerHTML = (scheme.advantages || []).map(p => `<li>${p}</li>`).join('');
  }

  const consUl = document.getElementById('modal-cons');
  if (consUl) {
    consUl.innerHTML = (scheme.disadvantages || []).map(c => `<li>${c}</li>`).join('');
  }

  const srcEl = document.getElementById('modal-source');
  if (srcEl) srcEl.innerText = scheme.data_source || 'Official Disclosures';
  const updEl = document.getElementById('modal-updated');
  if (updEl) updEl.innerText = scheme.last_updated || 'October 2026';

  modal.classList.add('active');
}

async function loadSchemesCache() {
  try {
    const res = await secureFetch('/api/schemes');
    if (res && res.schemes) {
      cachedSchemes = res.schemes;
    }
  } catch (err) {
    console.error('Failed to load schemes cache:', err);
  }
}

// ============================================================================
// UTILITIES
// ============================================================================
function formatINR(val) {
  if (val === null || val === undefined || isNaN(val)) return '₹0';
  return '₹' + Math.round(val).toLocaleString('en-IN');
}

function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}
