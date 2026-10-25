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
  initNeonModal();
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
  activeTab: 'ALL',
  searchQuery: '',
  riskFilter: 'ALL',
  assetTypeFilter: 'ALL',
  durationFilter: 'ALL',
  goalFilter: 'ALL',
  amountFilter: null,
  sortBy: 'relevance',
  returnPeriod: '5y',
  currentPage: 1,
  pageSize: 12
};

function initSchemeExplorer() {
  // 1. Tab buttons click listeners
  const tabBtns = document.querySelectorAll('#scheme-explorer-tabs .explorer-tab-btn');
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.getAttribute('data-tab');
      switchExplorerTab(tab);
    });
  });

  // 2. Search input listener
  const searchInput = document.getElementById('explorer-search');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      explorerState.searchQuery = e.target.value;
      explorerState.currentPage = 1;
      applySchemeExplorerFilters();
    });
  }

  // 3. Risk level filter
  const riskSelect = document.getElementById('explorer-risk');
  if (riskSelect) {
    riskSelect.addEventListener('change', (e) => {
      explorerState.riskFilter = e.target.value;
      explorerState.currentPage = 1;
      applySchemeExplorerFilters();
    });
  }

  // 4. Investment Type filter
  const assetTypeSelect = document.getElementById('explorer-asset-type');
  if (assetTypeSelect) {
    assetTypeSelect.addEventListener('change', (e) => {
      explorerState.assetTypeFilter = e.target.value;
      explorerState.currentPage = 1;
      applySchemeExplorerFilters();
    });
  }

  // 5. Investment Duration filter
  const durationSelect = document.getElementById('explorer-duration');
  if (durationSelect) {
    durationSelect.addEventListener('change', (e) => {
      explorerState.durationFilter = e.target.value;
      explorerState.currentPage = 1;
      applySchemeExplorerFilters();
    });
  }

  // 6. Investment Goal filter
  const goalSelect = document.getElementById('explorer-goal');
  if (goalSelect) {
    goalSelect.addEventListener('change', (e) => {
      explorerState.goalFilter = e.target.value;
      explorerState.currentPage = 1;
      applySchemeExplorerFilters();
    });
  }

  // 7. Investment Amount filter
  const amountInput = document.getElementById('explorer-amount');
  if (amountInput) {
    amountInput.addEventListener('input', (e) => {
      const val = parseFloat(e.target.value);
      explorerState.amountFilter = (!isNaN(val) && val > 0) ? val : null;
      explorerState.currentPage = 1;
      applySchemeExplorerFilters();
    });
  }

  // 8. Sort selector
  const sortSelect = document.getElementById('explorer-sort');
  if (sortSelect) {
    sortSelect.addEventListener('change', (e) => {
      explorerState.sortBy = e.target.value;
      explorerState.currentPage = 1;
      applySchemeExplorerFilters();
    });
  }

  // 9. Reset Filters buttons
  document.getElementById('btn-reset-filters')?.addEventListener('click', resetSchemeExplorerFilters);
  document.getElementById('btn-empty-reset')?.addEventListener('click', resetSchemeExplorerFilters);

  // 10. Pagination buttons
  document.getElementById('btn-page-prev')?.addEventListener('click', () => {
    if (explorerState.currentPage > 1) {
      explorerState.currentPage--;
      applySchemeExplorerFilters(false);
      document.getElementById('scheme-explorer-section')?.scrollIntoView({ behavior: 'smooth' });
    }
  });

  document.getElementById('btn-page-next')?.addEventListener('click', () => {
    const filtered = computeFilteredSchemes();
    const totalPages = Math.ceil(filtered.length / explorerState.pageSize) || 1;
    if (explorerState.currentPage < totalPages) {
      explorerState.currentPage++;
      applySchemeExplorerFilters(false);
      document.getElementById('scheme-explorer-section')?.scrollIntoView({ behavior: 'smooth' });
    }
  });

  // Initial render
  applySchemeExplorerFilters();
}

function switchExplorerTab(newTab) {
  if (explorerState.activeTab === newTab) return;
  explorerState.activeTab = newTab;
  explorerState.currentPage = 1;

  // Highlight active tab & update ARIA accessibility
  document.querySelectorAll('#scheme-explorer-tabs .explorer-tab-btn').forEach(btn => {
    const isActive = btn.getAttribute('data-tab') === newTab;
    btn.classList.toggle('active', isActive);
    btn.setAttribute('aria-selected', isActive ? 'true' : 'false');
  });

  applySchemeExplorerFilters();
}

function resetSchemeExplorerFilters() {
  explorerState.activeTab = 'ALL';
  explorerState.searchQuery = '';
  explorerState.riskFilter = 'ALL';
  explorerState.assetTypeFilter = 'ALL';
  explorerState.durationFilter = 'ALL';
  explorerState.goalFilter = 'ALL';
  explorerState.amountFilter = null;
  explorerState.sortBy = 'relevance';
  explorerState.currentPage = 1;

  document.querySelectorAll('#scheme-explorer-tabs .explorer-tab-btn').forEach(btn => {
    const isActive = btn.getAttribute('data-tab') === 'ALL';
    btn.classList.toggle('active', isActive);
    btn.setAttribute('aria-selected', isActive ? 'true' : 'false');
  });

  const searchInput = document.getElementById('explorer-search');
  if (searchInput) searchInput.value = '';

  const riskSelect = document.getElementById('explorer-risk');
  if (riskSelect) riskSelect.value = 'ALL';

  const assetTypeSelect = document.getElementById('explorer-asset-type');
  if (assetTypeSelect) assetTypeSelect.value = 'ALL';

  const durationSelect = document.getElementById('explorer-duration');
  if (durationSelect) durationSelect.value = 'ALL';

  const goalSelect = document.getElementById('explorer-goal');
  if (goalSelect) goalSelect.value = 'ALL';

  const amountInput = document.getElementById('explorer-amount');
  if (amountInput) amountInput.value = '';

  const sortSelect = document.getElementById('explorer-sort');
  if (sortSelect) sortSelect.value = 'relevance';

  applySchemeExplorerFilters();
}

function applySchemeExplorerFilters(resetPage = false) {
  if (resetPage) {
    explorerState.currentPage = 1;
  }
  const filtered = computeFilteredSchemes();
  const totalCount = filtered.length;
  const totalPages = Math.ceil(totalCount / explorerState.pageSize) || 1;

  // Guard current page bounds
  if (explorerState.currentPage > totalPages) {
    explorerState.currentPage = totalPages;
  }
  if (explorerState.currentPage < 1) {
    explorerState.currentPage = 1;
  }

  const startIdx = (explorerState.currentPage - 1) * explorerState.pageSize;
  const pageItems = filtered.slice(startIdx, startIdx + explorerState.pageSize);

  renderExplorerResults(pageItems);
  renderActiveFilterChips();
  updateResultsCount(totalCount, filtered.some(s => s.is_fallback));
  updatePaginationDOM(totalCount, totalPages);
}

function computeFilteredSchemes() {
  let baseItems = Array.isArray(window.__ALL_SCHEMES__) && window.__ALL_SCHEMES__.length > 0
    ? [...window.__ALL_SCHEMES__]
    : [...cachedSchemes];

  // Deduplicate by scheme ID
  const seenIds = new Set();
  let items = [];
  for (const item of baseItems) {
    if (!seenIds.has(item.id)) {
      seenIds.add(item.id);
      items.push(item);
    }
  }

  // 1. Tab Filtering
  if (explorerState.activeTab !== 'ALL') {
    const tab = explorerState.activeTab;
    items = items.filter(s => {
      const type = (s.assetType || '').toUpperCase();
      const cat = (s.category || '').toUpperCase();
      const code = (s.category_code || '').toUpperCase();

      if (tab === 'STOCKS' || tab === 'STOCKS_EQUITY') {
        return type === 'STOCKS' || cat === 'STOCKS' || cat === 'STOCKS_EQUITY' || code === 'STOCKS';
      }
      if (tab === 'MUTUAL_FUNDS' || tab === 'EQUITY_MUTUAL_FUNDS') {
        return type === 'MUTUAL FUNDS' || cat === 'MUTUAL_FUNDS' || cat === 'EQUITY_MUTUAL_FUNDS' || code === 'MUTUAL_FUNDS';
      }
      if (tab === 'ETFS') {
        return type === 'ETFS' || cat === 'ETFS' || code === 'ETFS';
      }
      if (tab === 'FIXED_DEPOSITS') {
        return type === 'FIXED DEPOSITS' || cat === 'FIXED_DEPOSITS' || code === 'FIXED_DEPOSITS';
      }
      if (tab === 'GOVT_SECURITIES') {
        return type.includes('GOVERNMENT') || cat === 'GOVT_SECURITIES' || code === 'GOVT_SECURITIES';
      }
      if (tab === 'SMALL_SAVINGS') {
        return type.includes('SMALL SAVINGS') || cat === 'SMALL_SAVINGS' || code === 'SMALL_SAVINGS';
      }
      if (tab === 'GOLD') {
        return type === 'GOLD' || cat === 'GOLD' || code === 'GOLD';
      }
      if (tab === 'OTHER') {
        return type.includes('OTHER') || cat === 'OTHER' || code === 'OTHER';
      }
      if (tab === 'SIP_INVESTMENTS') {
        return s.supports_sip === true || cat === 'SIP_INVESTMENTS' || code === 'SIP_INVESTMENTS';
      }
      return type.includes(tab) || cat.includes(tab) || code === tab;
    });
  }

  // 2. Risk Level Filter (Normalized)
  if (explorerState.riskFilter !== 'ALL') {
    const target = explorerState.riskFilter.toLowerCase();
    items = items.filter(s => {
      const rLevel = (s.riskLevel || s.risk_level || '').trim().toLowerCase();
      const score = s.riskScore || s.risk_score || 0;

      if (target === 'low') {
        return rLevel === 'low' || (score >= 1 && score <= 3);
      }
      if (target === 'medium' || target === 'moderate') {
        return rLevel === 'medium' || rLevel === 'moderate' || (score >= 4 && score <= 6);
      }
      if (target === 'high' || target === 'very high') {
        return rLevel === 'high' || rLevel === 'very high' || score >= 7;
      }
      return rLevel === target;
    });
  }

  // 3. Investment Type (Asset Type) Filter
  if (explorerState.assetTypeFilter !== 'ALL') {
    const targetType = explorerState.assetTypeFilter.toLowerCase();
    items = items.filter(s => (s.assetType || '').toLowerCase() === targetType);
  }

  // 4. Investment Duration Filter
  if (explorerState.durationFilter !== 'ALL') {
    const targetDur = explorerState.durationFilter;
    items = items.filter(s => {
      const durations = s.supported_durations || [];
      return durations.includes(targetDur) || (targetDur === 'MORE_THAN_5Y' && (durations.includes('5_TO_10Y') || durations.includes('MORE_THAN_10Y')));
    });
  }

  // 5. Investment Goal Filter
  if (explorerState.goalFilter !== 'ALL') {
    const targetGoal = explorerState.goalFilter.toLowerCase();
    items = items.filter(s => {
      const goals = (s.supported_goals || []).map(g => g.toLowerCase());
      const tags = (s.best_for_tags || []).map(t => t.toLowerCase());
      return goals.some(g => g.includes(targetGoal)) || tags.some(t => t.includes(targetGoal.replace(/\s+/g, '-')));
    });
  }

  // 6. Investment Amount Filter
  if (explorerState.amountFilter !== null && explorerState.amountFilter > 0) {
    const threshold = explorerState.amountFilter;
    items = items.filter(s => {
      const minVal = s.minimumInvestment !== undefined ? s.minimumInvestment : (s.min_investment || 0);
      return minVal <= threshold;
    });
  }

  // 7. Search Query Filter
  const q = (explorerState.searchQuery || '').trim().toLowerCase();
  if (q) {
    items = items.filter(s => {
      const name = (s.name || '').toLowerCase();
      const symbol = (s.symbol || s.ticker || '').toLowerCase();
      const comp = (s.company_name || s.provider || '').toLowerCase();
      const subcat = (s.investmentCategory || s.subcategory || '').toLowerCase();
      const assetType = (s.assetType || '').toLowerCase();
      const tags = (s.tags || s.best_for_tags || []).join(' ').toLowerCase();
      return name.includes(q) || symbol.includes(q) || comp.includes(q) || subcat.includes(q) || assetType.includes(q) || tags.includes(q);
    });
  }

  // 8. Sensible Fallback if strict filter yields 0 matches
  const fallbackBanner = document.getElementById('explorer-fallback-banner');
  const fallbackMsg = document.getElementById('explorer-fallback-message');

  if (items.length === 0 && explorerState.riskFilter !== 'ALL') {
    const targetRisk = explorerState.riskFilter.toLowerCase();
    let fallbacks = baseItems.filter(s => {
      const rLevel = (s.riskLevel || s.risk_level || '').trim().toLowerCase();
      const score = s.riskScore || s.risk_score || 0;
      if (targetRisk === 'low') return rLevel === 'low' || (score >= 1 && score <= 3);
      if (targetRisk === 'medium' || targetRisk === 'moderate') return rLevel === 'medium' || rLevel === 'moderate' || (score >= 4 && score <= 6);
      if (targetRisk === 'high' || targetRisk === 'very high') return rLevel === 'high' || rLevel === 'very high' || score >= 7;
      return rLevel === targetRisk;
    });

    if (q) {
      const queryFallbacks = fallbacks.filter(s => {
        return (s.name || '').toLowerCase().includes(q) || (s.symbol || s.ticker || '').toLowerCase().includes(q);
      });
      if (queryFallbacks.length > 0) fallbacks = queryFallbacks;
    }

    if (fallbacks.length > 0) {
      if (fallbackBanner) fallbackBanner.style.display = 'block';
      if (fallbackMsg) {
        fallbackMsg.innerText = `No exact matches for this specific combination. Displaying ${fallbacks.length} alternative investments within the ${explorerState.riskFilter} Risk category.`;
      }
      return fallbacks.map(f => ({ ...f, is_fallback: true }));
    }
  }

  if (fallbackBanner) fallbackBanner.style.display = 'none';

  // 9. Sorting
  const period = explorerState.returnPeriod || '5y';
  const cagrKey = `cagr_${period}`;

  if (explorerState.sortBy === 'name_asc') {
    items.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
  } else if (explorerState.sortBy === 'name_desc') {
    items.sort((a, b) => (b.name || '').localeCompare(a.name || ''));
  } else if (explorerState.sortBy === 'risk_asc') {
    items.sort((a, b) => (a.riskScore || a.risk_score || 5) - (b.riskScore || b.risk_score || 5));
  } else if (explorerState.sortBy === 'risk_desc') {
    items.sort((a, b) => (b.riskScore || b.risk_score || 5) - (a.riskScore || a.risk_score || 5));
  } else if (explorerState.sortBy === 'min_inv_asc') {
    items.sort((a, b) => (a.minimumInvestment ?? a.min_investment ?? 0) - (b.minimumInvestment ?? b.min_investment ?? 0));
  } else if (explorerState.sortBy === 'min_inv_desc') {
    items.sort((a, b) => (b.minimumInvestment ?? b.min_investment ?? 0) - (a.minimumInvestment ?? a.min_investment ?? 0));
  } else if (explorerState.sortBy === 'return_desc') {
    items.sort((a, b) => {
      const aVal = a[cagrKey] ?? a.expected_annual_return ?? 0;
      const bVal = b[cagrKey] ?? b.expected_annual_return ?? 0;
      return bVal - aVal;
    });
  } else if (explorerState.sortBy === 'liquidity') {
    items.sort((a, b) => {
      const aLiq = (a.liquidity || '').toLowerCase();
      const bLiq = (b.liquidity || '').toLowerCase();
      const aScore = aLiq.includes('instant') ? 3 : (aLiq.includes('high') ? 2 : 1);
      const bScore = bLiq.includes('instant') ? 3 : (bLiq.includes('high') ? 2 : 1);
      return bScore - aScore;
    });
  }

  return items;
}

function getFreshnessBadgeHtml(s) {
  const status = s.freshness_status || (s.assetType === 'STOCKS' ? 'LIVE' : (s.assetType === 'MUTUAL FUNDS' ? 'OFFICIAL_AMFI_NAV' : 'VERIFIED'));
  
  if (status === 'LIVE') {
    return `<span class="badge-pill" style="font-size:9px;font-weight:800;background:rgba(22,163,74,0.15);color:#16a34a;border:1px solid rgba(22,163,74,0.3);display:inline-flex;align-items:center;gap:3px;"><span style="display:inline-block;width:5px;height:5px;background:#22c55e;border-radius:50%;box-shadow:0 0 4px #22c55e;"></span> LIVE (NSE)</span>`;
  }
  if (status === 'LAST_TRADED') {
    return `<span class="badge-pill" style="font-size:9px;font-weight:800;background:rgba(2,132,199,0.12);color:#0284c7;border:1px solid rgba(2,132,199,0.3);">NSE Traded</span>`;
  }
  if (status === 'OFFICIAL_AMFI_NAV') {
    return `<span class="badge-pill" style="font-size:9px;font-weight:800;background:rgba(2,132,199,0.12);color:#0284c7;border:1px solid rgba(2,132,199,0.3);">AMFI NAV</span>`;
  }
  if (status === 'SPOT_BENCHMARK') {
    return `<span class="badge-pill" style="font-size:9px;font-weight:800;background:rgba(202,138,4,0.15);color:#ca8a04;border:1px solid rgba(202,138,4,0.3);">IBJA Spot</span>`;
  }
  if (status === 'STATUTORY_RATE') {
    return `<span class="badge-pill" style="font-size:9px;font-weight:800;background:rgba(99,102,241,0.12);color:#6366f1;border:1px solid rgba(99,102,241,0.3);">Sovereign</span>`;
  }
  if (status === 'CACHED_BASELINE') {
    return `<span class="badge-pill" style="font-size:9px;font-weight:800;background:rgba(100,116,139,0.12);color:#64748b;border:1px solid rgba(100,116,139,0.25);">Verified Cache</span>`;
  }
  return `<span class="badge-pill" style="font-size:9px;font-weight:800;background:rgba(22,163,74,0.12);color:#16a34a;border:1px solid rgba(22,163,74,0.25);">Verified</span>`;
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

  grid.innerHTML = items.map(s => {
    // Risk display & styling
    const riskLevel = s.riskLevel || s.risk_level || 'Medium';
    const riskScore = s.riskScore || s.risk_score || 5;
    let riskBadgeClass = 'badge-peach';
    let riskBadgeStyle = 'background:#fef3c7;color:#92400e;border:1px solid #fde68a;';

    if (riskLevel.toLowerCase() === 'low') {
      riskBadgeClass = 'badge-mint';
      riskBadgeStyle = 'background:#ecfdf5;color:#065f46;border:1px solid #a7f3d0;';
    } else if (riskLevel.toLowerCase() === 'high' || riskLevel.toLowerCase() === 'very high') {
      riskBadgeClass = 'badge-danger';
      riskBadgeStyle = 'background:#fef2f2;color:#991b1b;border:1px solid #fecaca;';
    }

    // Capital protection badge
    const capProtection = s.capitalProtection || 'Market-Linked';
    let capBadgeClass = 'badge-subtle';
    if (capProtection.includes('Sovereign')) {
      capBadgeClass = 'badge-mint';
    } else if (capProtection.includes('Guaranteed') || capProtection.includes('DICGC')) {
      capBadgeClass = 'badge-blue';
    }

    // Return display
    const returnDisplay = s.expectedReturnRange || (s.cagr_5y ? `+${s.cagr_5y}% CAGR` : `${s.expected_annual_return || 10}% p.a.`);
    const returnColor = '#16a34a';

    // Min investment display
    const minVal = s.minimumInvestment ?? s.min_investment ?? 500;
    const minDisplay = `₹${Number(minVal).toLocaleString('en-IN')}`;

    // Asset type & subcategory
    const assetTypeDisplay = s.assetType || s.category_label || 'Investment';
    const subcatDisplay = s.investmentCategory || s.subcategory || '';

    // Projection pre-fill parameters
    const projMethod = s.supports_sip ? 'SIP' : 'LUMPSUM';
    const projAmount = s.supports_sip ? (s.min_sip || 5000) : Math.max(minVal, 25000);
    const projRate = s.expected_annual_return || s.cagr_5y || 12.0;

    // Compounding pre-fill
    let compFreq = 'MONTHLY';
    if (assetTypeDisplay === 'Fixed Deposits' || s.id.includes('post-office') || s.id.includes('scss')) {
      compFreq = 'QUARTERLY';
    } else if (s.id.includes('ppf') || s.id.includes('ssy') || s.id.includes('nsc')) {
      compFreq = 'ANNUALLY';
    }

    const benefits = (s.investmentBenefits || s.advantages || []).slice(0, 2);
    const risks = (s.investmentLimitations || s.disadvantages || []).slice(0, 2);

    return `
      <div class="scheme-card explorer-card ${s.is_fallback ? 'fallback-card' : ''}" data-id="${s.id}" style="display:flex;flex-direction:column;justify-content:space-between;padding:18px;border-radius:var(--radius-sm);background:var(--bg-card);border:1px solid var(--border-card);position:relative;">
        
        ${s.is_fallback ? `
          <div style="position:absolute;top:0;right:0;background:#d97706;color:#fff;font-size:9px;font-weight:800;padding:2px 8px;border-bottom-left-radius:6px;text-transform:uppercase;">
            Alternative Match
          </div>
        ` : ''}

        <div>
          <!-- Header Badges -->
          <div style="display:flex;justify-content:space-between;align-items:center;gap:6px;margin-bottom:10px;flex-wrap:wrap;">
            <div style="display:flex;gap:5px;align-items:center;flex-wrap:wrap;">
              <span class="badge-pill" style="font-size:10px;font-weight:700;background:var(--bg-subtle);color:var(--text-primary);border:1px solid var(--border-subtle);">${assetTypeDisplay}</span>
              <span class="badge-pill ${capBadgeClass}" style="font-size:9px;font-weight:700;">${capProtection}</span>
              ${getFreshnessBadgeHtml(s)}
            </div>
            <span class="badge-pill ${riskBadgeClass}" style="font-size:10px;font-weight:800;${riskBadgeStyle}">
              ${riskLevel} Risk
            </span>
          </div>

          <!-- Title & Symbol -->
          <div class="scheme-title" style="font-size:15px;font-weight:800;color:var(--text-primary);margin-bottom:2px;line-height:1.3;">${s.name}</div>
          <div class="scheme-provider" style="font-size:11px;color:var(--text-muted);margin-bottom:10px;">
            ${s.dataSource || s.data_source || s.provider || ''} ${s.official_symbol || s.symbol ? `• Symbol: <strong>${s.official_symbol || s.symbol}</strong>` : ''}
          </div>

          <!-- Risk Score & Description Pill -->
          <div style="background:var(--bg-card-subtle);border:1px solid var(--border-subtle);border-radius:4px;padding:6px 10px;margin-bottom:12px;font-size:11px;line-height:1.4;">
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:2px;">
              <strong style="color:var(--text-primary);">Risk Score: ${riskScore}/10</strong>
              <span style="font-size:10px;color:var(--text-muted);">${subcatDisplay}</span>
            </div>
            <div style="font-size:10.5px;color:var(--text-secondary);">
              ${s.riskDescription ? s.riskDescription.substring(0, 95) + (s.riskDescription.length > 95 ? '...' : '') : ''}
            </div>
          </div>

          <!-- Metrics Grid -->
          <div class="scheme-meta-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px;">
            <div class="scheme-meta-item" style="background:var(--bg-subtle);padding:6px 8px;border-radius:4px;">
              <div class="scheme-meta-label" style="font-size:10px;color:var(--text-muted);font-weight:700;">Expected Return</div>
              <div class="scheme-meta-val" style="color:${returnColor};font-weight:800;font-size:12px;">${returnDisplay}</div>
            </div>
            <div class="scheme-meta-item" style="background:var(--bg-subtle);padding:6px 8px;border-radius:4px;">
              <div class="scheme-meta-label" style="font-size:10px;color:var(--text-muted);font-weight:700;">Min Investment</div>
              <div class="scheme-meta-val" style="font-weight:800;color:var(--text-primary);font-size:12px;">${minDisplay}</div>
            </div>
            <div class="scheme-meta-item" style="background:var(--bg-subtle);padding:6px 8px;border-radius:4px;">
              <div class="scheme-meta-label" style="font-size:10px;color:var(--text-muted);font-weight:700;">Horizon</div>
              <div class="scheme-meta-val" style="font-size:11px;font-weight:700;">${s.investmentHorizon || '3–5 Years'}</div>
            </div>
            <div class="scheme-meta-item" style="background:var(--bg-subtle);padding:6px 8px;border-radius:4px;">
              <div class="scheme-meta-label" style="font-size:10px;color:var(--text-muted);font-weight:700;">Liquidity</div>
              <div class="scheme-meta-val" style="font-size:10.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="${s.liquidity || 'High'}">${s.liquidity ? s.liquidity.substring(0, 24) + '...' : 'High Liquidity'}</div>
            </div>
          </div>

          <!-- Purpose -->
          ${s.investmentPurpose ? `
            <div style="font-size:11px;color:var(--text-secondary);margin-bottom:10px;line-height:1.4;">
              <strong style="color:var(--text-primary);">Purpose:</strong> ${s.investmentPurpose.substring(0, 95)}${s.investmentPurpose.length > 95 ? '...' : ''}
            </div>
          ` : ''}

          <!-- Highlights (Benefits vs Risks) -->
          <div style="font-size:10.5px;margin-bottom:12px;background:var(--bg-subtle);padding:8px 10px;border-radius:4px;">
            ${benefits.length > 0 ? `
              <div style="color:#15803d;display:flex;align-items:flex-start;gap:4px;margin-bottom:3px;">
                <span>✓</span> <span>${benefits[0]}</span>
              </div>
            ` : ''}
            ${risks.length > 0 ? `
              <div style="color:#b91c1c;display:flex;align-items:flex-start;gap:4px;">
                <span>⚠</span> <span>${risks[0]}</span>
              </div>
            ` : ''}
          </div>

          <!-- Footer Metadata -->
          <div style="display:flex;justify-content:space-between;align-items:center;font-size:10px;color:var(--text-muted);padding-top:8px;border-top:1px solid rgba(0,0,0,0.06);">
            <span>Price/NAV: <strong style="color:var(--text-primary);">${s.currentPrice || s.currentNAV || (s.price_numeric ? '₹' + Number(s.price_numeric).toLocaleString('en-IN') : 'Market')}</strong> ${s.day_change_pct ? `<span style="color:${s.day_change >= 0 ? '#16a34a' : '#dc2626'};font-weight:700;">(${s.day_change >= 0 ? '+' : ''}${s.day_change_pct}%)</span>` : ''}</span>
            <span>${s.price_date || s.lastUpdated || 'October 2026'}</span>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="scheme-card-actions" style="margin-top:14px;display:flex;gap:8px;">
          <button type="button" class="btn btn-secondary btn-sm action-view-details" data-id="${s.id}" style="flex:1;font-weight:700;">
            View Details
          </button>
          <button type="button" class="btn btn-primary btn-sm action-project-scheme" 
            data-id="${s.id}" 
            data-name="${s.name}" 
            data-category="${s.category || ''}"
            data-risk="${s.risk_level || s.riskLevel || ''}"
            data-rate="${projRate}" 
            data-method="${projMethod}" 
            data-amount="${projAmount}"
            data-comp="${compFreq}"
            style="flex:1;font-weight:800;background:#cbf432;color:#121614;border:none;box-shadow:0 0 10px rgba(203,244,50,0.3);display:inline-flex;align-items:center;justify-content:center;gap:4px;">
            <i data-lucide="sparkles" style="width:13px;height:13px;"></i> Add to Projection
          </button>
        </div>

      </div>
    `;
  }).join('');
}

function updatePaginationDOM(totalCount, totalPages) {
  const container = document.getElementById('explorer-pagination');
  const info = document.getElementById('explorer-pagination-info');
  const btnPrev = document.getElementById('btn-page-prev');
  const btnNext = document.getElementById('btn-page-next');

  if (!container) return;

  if (totalCount <= explorerState.pageSize) {
    container.style.display = 'none';
    return;
  }

  container.style.display = 'flex';
  if (info) {
    info.innerText = `Page ${explorerState.currentPage} of ${totalPages} (${totalCount} investments)`;
  }

  if (btnPrev) {
    btnPrev.disabled = (explorerState.currentPage <= 1);
  }
  if (btnNext) {
    btnNext.disabled = (explorerState.currentPage >= totalPages);
  }
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

  // Asset type chip
  if (explorerState.assetTypeFilter !== 'ALL') {
    chips.push({
      key: 'asset_type',
      label: `Type: ${explorerState.assetTypeFilter}`
    });
  }

  // Duration chip
  if (explorerState.durationFilter !== 'ALL') {
    const durLabels = {
      'UP_TO_1Y': '< 1 year',
      '1_TO_3Y': '1–3 years',
      '3_TO_5Y': '3–5 years',
      'MORE_THAN_5Y': '> 5 years'
    };
    chips.push({
      key: 'duration',
      label: `Duration: ${durLabels[explorerState.durationFilter] || explorerState.durationFilter}`
    });
  }

  // Goal chip
  if (explorerState.goalFilter !== 'ALL') {
    chips.push({
      key: 'goal',
      label: `Goal: ${explorerState.goalFilter}`
    });
  }

  // Amount threshold chip
  if (explorerState.amountFilter !== null && explorerState.amountFilter > 0) {
    chips.push({
      key: 'amount',
      label: `Amount: ≤ ₹${Number(explorerState.amountFilter).toLocaleString('en-IN')}`
    });
  }

  // Sort chip if not relevance
  if (explorerState.sortBy !== 'relevance') {
    const sortLabels = {
      'name_asc': 'Name: A–Z',
      'name_desc': 'Name: Z–A',
      'risk_asc': 'Risk: Low to High',
      'risk_desc': 'Risk: High to Low',
      'min_inv_asc': 'Min Inv: Low to High',
      'min_inv_desc': 'Min Inv: High to Low',
      'return_desc': 'Returns: High to Low',
      'liquidity': 'Highest Liquidity'
    };
    chips.push({
      key: 'sort',
      label: `Sort: ${sortLabels[explorerState.sortBy] || explorerState.sortBy}`
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

  // Click listeners to remove filter chip
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
  } else if (key === 'asset_type') {
    explorerState.assetTypeFilter = 'ALL';
    const select = document.getElementById('explorer-asset-type');
    if (select) select.value = 'ALL';
  } else if (key === 'duration') {
    explorerState.durationFilter = 'ALL';
    const select = document.getElementById('explorer-duration');
    if (select) select.value = 'ALL';
  } else if (key === 'goal') {
    explorerState.goalFilter = 'ALL';
    const select = document.getElementById('explorer-goal');
    if (select) select.value = 'ALL';
  } else if (key === 'amount') {
    explorerState.amountFilter = null;
    const input = document.getElementById('explorer-amount');
    if (input) input.value = '';
  } else if (key === 'sort') {
    explorerState.sortBy = 'relevance';
    const select = document.getElementById('explorer-sort');
    if (select) select.value = 'relevance';
  }
  explorerState.currentPage = 1;
  applySchemeExplorerFilters();
}

function updateResultsCount(count, isFallback = false) {
  const badge = document.getElementById('explorer-results-count-badge');
  if (badge) {
    const word = count === 1 ? 'investment' : 'investments';
    badge.innerText = `Showing ${count} ${word}${isFallback ? ' (Alternatives)' : ''}`;
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
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;flex-wrap:wrap;gap:4px;">
          <div style="display:flex;gap:4px;align-items:center;flex-wrap:wrap;">
            <span class="badge-pill badge-mint" style="font-size:10px;">${r.category_label || r.category}</span>
            ${getFreshnessBadgeHtml(r)}
          </div>
          <span class="badge-pill" style="background:#eef8ed;color:#166534;font-size:10px;font-weight:700;display:inline-flex;align-items:center;gap:4px;">
            <i data-lucide="star" style="width:12px;height:12px;"></i> ${r.match_score}% Match
          </span>
        </div>

        <div class="scheme-title" style="font-size:15px;font-weight:800;">${r.name}</div>
        <div class="scheme-provider" style="font-size:12px;color:var(--text-muted);margin-bottom:10px;">
          ${r.dataSource || r.data_source || r.provider || ''} ${r.official_symbol || r.symbol ? `• <strong>${r.official_symbol || r.symbol}</strong>` : ''}
        </div>

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
          <span>Price/NAV: <strong style="color:var(--text-primary);">${r.currentPrice || r.currentNAV || (r.price_numeric ? '₹' + Number(r.price_numeric).toLocaleString('en-IN') : 'Market')}</strong></span>
          <span>${r.price_date || r.last_updated || 'October 2026'}</span>
        </div>
      </div>

      <div class="scheme-card-actions" style="margin-top:12px;">
        <button type="button" class="btn btn-secondary btn-sm action-view-details" data-id="${r.id}">Details</button>
        <button type="button" class="btn btn-primary btn-sm action-project-scheme" 
          data-id="${r.id}" 
          data-rate="${r.cagr_5y || r.expected_annual_return}" 
          data-name="${r.name}" 
          data-category="${r.category || ''}"
          data-risk="${r.risk_level || ''}"
          data-method="${r.category === 'SIP_INVESTMENTS' ? 'SIP' : 'LUMPSUM'}" 
          data-amount="${r.category === 'SIP_INVESTMENTS' ? 5000 : 10000}"
          style="display:inline-flex;align-items:center;background:#cbf432;color:#121614;font-weight:800;border:none;box-shadow:0 0 10px rgba(203,244,50,0.35);">
          <i data-lucide="sparkles" style="width:13px;height:13px;margin-right:4px;"></i> Add to Projection
        </button>
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
                data-category="${s.category || ''}"
                data-risk="${s.risk_level || ''}"
                data-method="${comp.parameters?.method || 'LUMPSUM'}" 
                data-amount="${comp.parameters?.amount || 50000}"
                style="background:#cbf432;color:#121614;font-weight:800;border:none;box-shadow:0 0 10px rgba(203,244,50,0.35);display:inline-flex;align-items:center;gap:4px;">
                <i data-lucide="sparkles" style="width:13px;height:13px;"></i> Add to Projection
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

  const inputs = ['calc-initial', 'calc-periodic', 'calc-freq', 'calc-return', 'calc-duration', 'calc-step-up', 'calc-timing', 'calc-compounding-freq'];
  inputs.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('input', debounce(recalculateInvestment, 200));
      if (el.tagName === 'SELECT') {
        el.addEventListener('change', debounce(recalculateInvestment, 200));
      }
    }
  });

  document.getElementById('btn-reset-calc')?.addEventListener('click', () => {
    document.getElementById('calc-scheme-link').value = '';
    document.getElementById('calc-initial').value = '10000';
    document.getElementById('calc-periodic').value = '5000';
    document.getElementById('calc-freq').value = 'MONTHLY';
    document.getElementById('calc-return').value = '12.0';
    document.getElementById('calc-duration').value = '10';
    document.getElementById('calc-step-up').value = '0';
    const compSel = document.getElementById('calc-compounding-freq');
    if (compSel) compSel.value = 'MONTHLY';
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
  const compFreq = document.getElementById('calc-compounding-freq')?.value || 'MONTHLY';
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
        compounding_frequency: compFreq,
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
// 10. NEON PROJECTION BOX & TRANSFER HELPERS
// ============================================================================
let currentNeonData = {
  id: '',
  name: 'Selected Investment',
  category: 'EQUITY_MUTUAL_FUNDS',
  risk: 'Moderate',
  method: 'SIP',
  amount: 10000,
  duration: 10,
  expected_return: 14.0,
  step_up: 0,
  compounding: 'MONTHLY'
};

function initNeonModal() {
  const modal = document.getElementById('neon-projection-modal');
  if (!modal) return;
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal('neon-projection-modal');
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('active')) {
      closeModal('neon-projection-modal');
    }
  });
}

function openNeonProjectionBox(data) {
  if (!data) return;

  const schemeId = data.scheme_id || data.id;
  let scheme = null;
  if (schemeId && cachedSchemes.length) {
    scheme = cachedSchemes.find(s => s.id === schemeId);
  }
  if (!scheme && schemeId && window.__ALL_SCHEMES__?.length) {
    scheme = window.__ALL_SCHEMES__.find(s => s.id === schemeId);
  }

  currentNeonData.id = schemeId || (scheme ? scheme.id : 'custom-investment');
  currentNeonData.name = data.name || (scheme ? scheme.name : 'Selected Investment');
  currentNeonData.category = data.category || (scheme ? scheme.category : 'EQUITY_MUTUAL_FUNDS');
  currentNeonData.risk = data.risk || (scheme ? scheme.risk_level : 'Moderate');

  const rate = data.expected_return || (scheme ? (scheme.cagr_5y || scheme.expected_annual_return || 12.0) : 12.0);
  currentNeonData.expected_return = parseFloat(rate) || 12.0;

  if (data.method) {
    currentNeonData.method = data.method;
  } else if (currentNeonData.category === 'SIP_INVESTMENTS') {
    currentNeonData.method = 'SIP';
  } else {
    currentNeonData.method = 'LUMPSUM';
  }

  if (data.amount && parseFloat(data.amount) > 0) {
    currentNeonData.amount = parseFloat(data.amount);
  } else if (currentNeonData.method === 'SIP') {
    currentNeonData.amount = (scheme && scheme.min_sip) ? scheme.min_sip : 10000;
  } else {
    currentNeonData.amount = (scheme && scheme.min_investment) ? Math.max(50000, scheme.min_investment) : 50000;
  }

  currentNeonData.duration = data.duration ? parseInt(data.duration) : 10;
  currentNeonData.step_up = data.step_up ? parseFloat(data.step_up) : 0;
  currentNeonData.compounding = data.compounding_frequency || 'MONTHLY';

  const nameEl = document.getElementById('neon-scheme-name');
  if (nameEl) nameEl.innerText = currentNeonData.name;

  const catEl = document.getElementById('neon-scheme-cat');
  if (catEl) {
    const catLabels = {
      'STOCKS_EQUITY': 'Stocks & Equity',
      'EQUITY_MUTUAL_FUNDS': 'Equity Mutual Funds',
      'SIP_INVESTMENTS': 'SIP Investments',
      'GOLD': 'Gold'
    };
    catEl.innerText = catLabels[currentNeonData.category] || currentNeonData.category;
  }

  const riskEl = document.getElementById('neon-scheme-risk');
  if (riskEl) {
    riskEl.innerText = `${currentNeonData.risk} Risk`;
  }

  const cagrEl = document.getElementById('neon-scheme-cagr-badge');
  if (cagrEl) {
    cagrEl.innerText = `CAGR: ~${currentNeonData.expected_return.toFixed(1)}%`;
  }

  const returnInput = document.getElementById('neon-input-return');
  if (returnInput) returnInput.value = currentNeonData.expected_return.toFixed(2);

  const durationRange = document.getElementById('neon-range-duration');
  if (durationRange) durationRange.value = currentNeonData.duration;
  const durLabel = document.getElementById('neon-duration-label');
  if (durLabel) durLabel.innerText = `${currentNeonData.duration} Years`;

  const stepUpSel = document.getElementById('neon-select-stepup');
  if (stepUpSel) stepUpSel.value = String(currentNeonData.step_up);

  const compSel = document.getElementById('neon-select-compounding');
  if (compSel) compSel.value = currentNeonData.compounding;

  setNeonMethod(currentNeonData.method, false);
  setNeonAmount(currentNeonData.amount);
  syncNeonDuration(currentNeonData.duration);

  updateNeonProjection();

  openModal('neon-projection-modal');
  if (window.refreshIcons) {
    window.refreshIcons(document.getElementById('neon-projection-modal'));
  }
}

function setNeonMethod(method, recalculate = true) {
  currentNeonData.method = method;
  const btnSip = document.getElementById('neon-btn-method-sip');
  const btnLump = document.getElementById('neon-btn-method-lump');
  const amountLabel = document.getElementById('neon-amount-label');

  if (method === 'SIP') {
    if (btnSip) btnSip.classList.add('active');
    if (btnLump) btnLump.classList.remove('active');
    if (amountLabel) amountLabel.innerText = 'Monthly Contribution (₹)';
  } else {
    if (btnSip) btnSip.classList.remove('active');
    if (btnLump) btnLump.classList.add('active');
    if (amountLabel) amountLabel.innerText = 'One-Time Lump Sum Capital (₹)';
  }

  if (recalculate) {
    updateNeonProjection();
  }
}

function setNeonAmount(amt) {
  currentNeonData.amount = parseFloat(amt) || 10000;
  const input = document.getElementById('neon-input-amount');
  if (input) input.value = currentNeonData.amount;

  document.querySelectorAll('#neon-projection-modal .neon-chip').forEach(chip => {
    const fnStr = chip.getAttribute('onclick') || '';
    if (fnStr.includes(`(${currentNeonData.amount})`)) {
      chip.classList.add('active');
    } else {
      chip.classList.remove('active');
    }
  });

  updateNeonProjection();
}

function syncNeonDuration(years) {
  const y = parseInt(years) || 10;
  currentNeonData.duration = y;

  const range = document.getElementById('neon-range-duration');
  if (range) range.value = y;

  const label = document.getElementById('neon-duration-label');
  if (label) label.innerText = `${y} Years`;

  document.querySelectorAll('#neon-projection-modal .neon-mini-chip').forEach(chip => {
    const fnStr = chip.getAttribute('onclick') || '';
    if (fnStr.includes(`(${y})`)) {
      chip.classList.add('active');
    } else {
      chip.classList.remove('active');
    }
  });

  updateNeonProjection();
}

function updateNeonProjection() {
  const amtInput = document.getElementById('neon-input-amount');
  const returnInput = document.getElementById('neon-input-return');
  const rangeDur = document.getElementById('neon-range-duration');
  const stepUpSel = document.getElementById('neon-select-stepup');
  const compSel = document.getElementById('neon-select-compounding');

  if (amtInput) currentNeonData.amount = parseFloat(amtInput.value) || 0;
  if (returnInput) currentNeonData.expected_return = parseFloat(returnInput.value) || 0;
  if (rangeDur) currentNeonData.duration = parseInt(rangeDur.value) || 10;
  if (stepUpSel) currentNeonData.step_up = parseFloat(stepUpSel.value) || 0;
  if (compSel) currentNeonData.compounding = compSel.value || 'MONTHLY';

  const amountDisplay = document.getElementById('neon-amount-display');
  if (amountDisplay) {
    amountDisplay.innerText = formatINR(currentNeonData.amount);
  }

  const P = currentNeonData.amount;
  const N = currentNeonData.duration;
  const r = currentNeonData.expected_return / 100;
  const s = currentNeonData.step_up / 100;
  const isSip = currentNeonData.method === 'SIP';

  let totalInvested = 0;
  let futureValue = 0;

  if (!isSip) {
    totalInvested = P;
    let k = 12;
    if (currentNeonData.compounding === 'QUARTERLY') k = 4;
    else if (currentNeonData.compounding === 'ANNUALLY') k = 1;
    futureValue = P * Math.pow(1 + r / k, k * N);
  } else {
    const monthlyRate = r / 12;
    const totalMonths = N * 12;
    let balance = 0;

    for (let m = 1; m <= totalMonths; m++) {
      const yearIndex = Math.floor((m - 1) / 12);
      const monthlyContribution = P * Math.pow(1 + s, yearIndex);
      totalInvested += monthlyContribution;
      balance = (balance + monthlyContribution) * (1 + monthlyRate);
    }
    futureValue = balance;
  }

  const estimatedGain = Math.max(0, futureValue - totalInvested);
  const multiplier = totalInvested > 0 ? (futureValue / totalInvested) : 1;

  const fvEl = document.getElementById('neon-res-fv');
  const investedEl = document.getElementById('neon-res-invested');
  const gainEl = document.getElementById('neon-res-gain');
  const multEl = document.getElementById('neon-gain-multiplier');

  if (fvEl) fvEl.innerText = formatINR(futureValue);
  if (investedEl) investedEl.innerText = formatINR(totalInvested);
  if (gainEl) gainEl.innerText = `+${formatINR(estimatedGain)}`;
  if (multEl) multEl.innerText = `${multiplier.toFixed(2)}x Capital Growth`;
}

function applyNeonToMainCalculator() {
  const schemeSel = document.getElementById('calc-scheme-link');
  if (schemeSel && currentNeonData.id) {
    schemeSel.value = currentNeonData.id;
  }

  const badge = document.getElementById('active-linked-badge');
  if (badge) {
    badge.innerText = `Linked: ${currentNeonData.name}`;
  }

  const initialInput = document.getElementById('calc-initial');
  const periodicInput = document.getElementById('calc-periodic');
  const freqSel = document.getElementById('calc-freq');
  const rateInput = document.getElementById('calc-return');
  const durInput = document.getElementById('calc-duration');
  const stepUpInput = document.getElementById('calc-step-up');
  const compSel = document.getElementById('calc-compounding-freq');

  if (currentNeonData.method === 'SIP') {
    if (initialInput) initialInput.value = '0';
    if (periodicInput) periodicInput.value = currentNeonData.amount;
    if (freqSel) freqSel.value = 'MONTHLY';
  } else {
    if (initialInput) initialInput.value = currentNeonData.amount;
    if (periodicInput) periodicInput.value = '0';
    if (freqSel) freqSel.value = 'YEARLY';
  }

  if (rateInput) rateInput.value = currentNeonData.expected_return.toFixed(2);
  if (durInput) durInput.value = currentNeonData.duration;
  if (stepUpInput) stepUpInput.value = currentNeonData.step_up;
  if (compSel) compSel.value = currentNeonData.compounding;

  closeModal('neon-projection-modal');
  recalculateInvestment();
  switchTopTab('tab-future');

  const sec = document.getElementById('section-future-projection');
  if (sec) {
    sec.scrollIntoView({ behavior: 'smooth', block: 'start' });
    sec.classList.add('neon-section-highlight');
    setTimeout(() => {
      sec.classList.remove('neon-section-highlight');
    }, 2400);
  }
}

function neonAddToPortfolio() {
  addInvestmentToPortfolio({
    id: currentNeonData.id,
    name: currentNeonData.name,
    category: currentNeonData.category || 'EQUITY_MUTUAL_FUNDS',
    method: currentNeonData.method,
    amount: currentNeonData.amount,
    expected_return_pct: currentNeonData.expected_return
  });

  closeModal('neon-projection-modal');
  showToast(`Added ${currentNeonData.name} to Combined Portfolio!`, 'success');
}

function transferToProjection(data) {
  openNeonProjectionBox(data);
}

// Global exposure for inline events
window.openNeonProjectionBox = openNeonProjectionBox;
window.setNeonMethod = setNeonMethod;
window.setNeonAmount = setNeonAmount;
window.syncNeonDuration = syncNeonDuration;
window.updateNeonProjection = updateNeonProjection;
window.applyNeonToMainCalculator = applyNeonToMainCalculator;
window.neonAddToPortfolio = neonAddToPortfolio;

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

    // 2. Project Scheme in Neon Box & Calculator
    const btnProject = e.target.closest('.action-project-scheme');
    if (btnProject) {
      const id = btnProject.getAttribute('data-id');
      const rate = btnProject.getAttribute('data-rate');
      const name = btnProject.getAttribute('data-name');
      const category = btnProject.getAttribute('data-category') || '';
      const risk = btnProject.getAttribute('data-risk') || '';
      const method = btnProject.getAttribute('data-method') || 'LUMPSUM';
      const amount = parseFloat(btnProject.getAttribute('data-amount') || 50000);
      const comp = btnProject.getAttribute('data-comp') || 'MONTHLY';

      openNeonProjectionBox({
        scheme_id: id,
        id: id,
        name: name,
        category: category,
        risk: risk,
        method: method,
        amount: amount,
        expected_return: rate,
        compounding_frequency: comp
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

  // Calculation Basis & Data Source
  const basisEl = document.getElementById('whatif-calc-basis');
  if (basisEl) {
    if (sum.calculation_basis === 'OFFICIAL_HISTORICAL_SERIES') {
      basisEl.innerText = 'Official Historical NAV Series';
      basisEl.style.color = '#16a34a';
    } else {
      basisEl.innerText = 'Verified Regulatory CAGR Model';
      basisEl.style.color = '#0284c7';
    }
  }
  const sourceEl = document.getElementById('whatif-source-label');
  if (sourceEl) {
    sourceEl.innerText = sum.data_source || 'AMFI India / Verified';
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
      const s = activeModalScheme;
      modal.classList.remove('active');
      openNeonProjectionBox({
        scheme_id: s.id,
        id: s.id,
        name: s.name,
        category: s.category,
        risk: s.risk_level,
        method: s.category === 'SIP_INVESTMENTS' ? 'SIP' : 'LUMPSUM',
        amount: s.category === 'SIP_INVESTMENTS' ? (s.min_sip || 5000) : 50000,
        expected_return: s.cagr_5y || s.expected_annual_return || 12
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

  const riskScore = scheme.riskScore || scheme.risk_score || 5;
  const assetType = scheme.assetType || scheme.category_label || scheme.category;
  document.getElementById('modal-category').innerText = assetType;
  document.getElementById('modal-risk').innerText = `${scheme.riskLevel || scheme.risk_level} Risk (Score: ${riskScore}/10)`;
  document.getElementById('modal-title').innerText = scheme.name;

  // Provider and official identifier
  const provEl = document.getElementById('modal-provider');
  if (provEl) {
    const symbolStr = scheme.official_symbol || scheme.symbol ? ` • Symbol: ${scheme.official_symbol || scheme.symbol}` : '';
    provEl.innerText = `${scheme.dataSource || scheme.data_source || scheme.provider || 'SEBI Regulated'}${symbolStr}`;
  }

  // Market strip: price, date, and plan details
  const priceVal = scheme.currentPrice || scheme.currentNAV || (scheme.price_numeric ? '₹' + Number(scheme.price_numeric).toLocaleString('en-IN') : '-');
  const marketPriceEl = document.getElementById('modal-market-price');
  if (marketPriceEl) {
    if (scheme.day_change_pct) {
      marketPriceEl.innerHTML = `${priceVal} <span style="font-size:11px;color:${scheme.day_change >= 0 ? '#16a34a' : '#dc2626'};font-weight:700;">(${scheme.day_change >= 0 ? '+' : ''}${scheme.day_change_pct}%)</span>`;
    } else {
      marketPriceEl.innerText = priceVal;
    }
  }

  const marketDateEl = document.getElementById('modal-market-date');
  if (marketDateEl) marketDateEl.innerText = scheme.price_date || scheme.last_updated || 'Latest Session';

  const freshnessBadge = document.getElementById('modal-freshness-badge');
  if (freshnessBadge) {
    const status = scheme.freshness_status || 'VERIFIED';
    freshnessBadge.innerText = status.replace(/_/g, ' ');
    if (status === 'LIVE') {
      freshnessBadge.style.background = 'rgba(22,163,74,0.15)';
      freshnessBadge.style.color = '#16a34a';
      freshnessBadge.style.border = '1px solid rgba(22,163,74,0.3)';
    } else if (status.includes('AMFI')) {
      freshnessBadge.style.background = 'rgba(2,132,199,0.12)';
      freshnessBadge.style.color = '#0284c7';
      freshnessBadge.style.border = '1px solid rgba(2,132,199,0.3)';
    } else if (status.includes('SPOT')) {
      freshnessBadge.style.background = 'rgba(202,138,4,0.15)';
      freshnessBadge.style.color = '#ca8a04';
      freshnessBadge.style.border = '1px solid rgba(202,138,4,0.3)';
    } else {
      freshnessBadge.style.background = 'rgba(99,102,241,0.12)';
      freshnessBadge.style.color = '#6366f1';
      freshnessBadge.style.border = '1px solid rgba(99,102,241,0.3)';
    }
  }

  const planInfoEl = document.getElementById('modal-plan-info');
  if (planInfoEl) {
    const parts = [];
    if (scheme.amc) parts.push(`AMC: ${scheme.amc}`);
    if (scheme.plan_type) parts.push(`Plan: ${scheme.plan_type}`);
    if (scheme.option) parts.push(`Option: ${scheme.option}`);
    if (scheme.amfi_code) parts.push(`AMFI: ${scheme.amfi_code}`);
    planInfoEl.innerText = parts.length ? parts.join(' | ') : (scheme.sector ? `Sector: ${scheme.sector}` : '');
  }

  document.getElementById('modal-objective').innerText = scheme.investmentPurpose || scheme.objective || '';

  // How it works + evidence-based risk methodology
  const howEl = document.getElementById('modal-how-it-works');
  if (howEl) {
    let methodText = scheme.riskDescription || scheme.how_it_works || 'Investments in this asset follow regulatory guidelines.';
    if (scheme.risk_methodology) {
      methodText += `\n\nRisk Assessment Methodology: ${scheme.risk_methodology}`;
    }
    if (scheme.risk_classification_source) {
      methodText += ` (Source: ${scheme.risk_classification_source})`;
    }
    howEl.innerText = methodText;
  }

  document.getElementById('modal-eligibility').innerText = scheme.eligibilityRequirements || scheme.eligibility || 'KYC-compliant Indian investors';
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
  if (updEl) updEl.innerText = scheme.last_sync_time || scheme.price_date || scheme.last_updated || 'October 2026';

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
