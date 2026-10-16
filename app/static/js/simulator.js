/**
 * Savings Simulator Interactive Engine
 * Interactive synchronized manual inputs and sliders for category expense trims,
 * real-time what-if live calculations, inline validation, and scenario management.
 */

let simulationChart = null;
let recalculationTimer = null;

function getConfig() {
  const fallback = {
    currency: 'INR',
    currencySymbol: '₹',
    currencyDecimals: 2,
    baselineExpensesMinor: 0,
    baselineExpensesFormatted: '₹0.00',
    baselineSurplusMinor: 0,
    baselineSurplusFormatted: '₹0.00'
  };
  return Object.assign({}, fallback, window.MoneyLeakSimulatorConfig || {});
}

/**
 * Format major amount into user's active currency representation.
 * Supports Indian numbering commas for INR and standard commas for other currencies.
 */
function formatCurrency(majorAmount, includeSymbol = true) {
  const config = getConfig();
  const symbol = includeSymbol ? (config.currencySymbol || '₹') + ' ' : '';
  const decimals = config.currencyDecimals !== undefined ? config.currencyDecimals : 2;
  const num = Number(majorAmount) || 0;
  const isNegative = num < 0;
  const absNum = Math.abs(num);

  const parts = absNum.toFixed(decimals).split('.');
  const integerPart = parts[0];
  const decimalPart = parts.length > 1 && decimals > 0 ? '.' + parts[1] : '';

  let formattedInteger;
  if ((config.currency || '').toUpperCase() === 'INR') {
    // Indian numbering format (1,00,000)
    if (integerPart.length > 3) {
      const lastThree = integerPart.slice(-3);
      const otherDigits = integerPart.slice(0, -3);
      const groupedOthers = otherDigits.replace(/\B(?=(\d{2})+(?!\d))/g, ',');
      formattedInteger = groupedOthers + ',' + lastThree;
    } else {
      formattedInteger = integerPart;
    }
  } else {
    // Standard thousands separator
    formattedInteger = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  }

  return (isNegative ? '-' : '') + symbol + formattedInteger + decimalPart;
}

document.addEventListener('DOMContentLoaded', () => {
  initSimulatorEvents();
  initSimulationChart();
  handleLiveUpdate(true);
});

/**
 * Initialize all interactive listeners for inputs, sliders, reset, and modals.
 */
function initSimulatorEvents() {
  const cards = document.querySelectorAll('.sim-cat-card');

  cards.forEach(card => {
    const catId = card.getAttribute('data-cat-id');
    const manualInput = document.getElementById(`manual-reduction-${catId}`);
    const sliderInput = document.getElementById(`slider-reduction-${catId}`);

    if (manualInput && sliderInput) {
      // 1. Slider input event -> synchronise manual input and recalculate
      sliderInput.addEventListener('input', () => {
        const val = parseFloat(sliderInput.value) || 0;
        const config = getConfig();
        const decimals = config.currencyDecimals !== undefined ? config.currencyDecimals : 2;
        
        // Update manual input without losing decimal cleanliness
        manualInput.value = decimals > 0 ? (Number.isInteger(val) ? val.toString() : val.toFixed(decimals)) : Math.round(val).toString();
        
        // Clear any error state since slider is bounded by max
        clearCategoryError(catId, manualInput);
        handleLiveUpdate(false);
      });

      // 2. Manual numeric input event -> validate, synchronise slider, recalculate
      manualInput.addEventListener('input', () => {
        const rawVal = manualInput.value.trim();
        const maxSpend = parseFloat(card.getAttribute('data-original-major') || '0');
        const validation = validateCategoryInput(catId, rawVal, maxSpend);

        if (validation.isValid) {
          clearCategoryError(catId, manualInput);
          if (validation.isEmpty) {
            sliderInput.value = 0;
          } else {
            sliderInput.value = Math.min(validation.value, maxSpend);
          }
        } else {
          showCategoryError(catId, manualInput, validation.errorMessage);
        }

        handleLiveUpdate(false);
      });

      // 3. Manual input blur event -> finalize empty or formatted inputs
      manualInput.addEventListener('blur', () => {
        const rawVal = manualInput.value.trim();
        const maxSpend = parseFloat(card.getAttribute('data-original-major') || '0');
        const validation = validateCategoryInput(catId, rawVal, maxSpend);

        if (validation.isEmpty) {
          manualInput.value = '0';
          sliderInput.value = 0;
          clearCategoryError(catId, manualInput);
          handleLiveUpdate(false);
        } else if (validation.isValid) {
          // Normalize clean numeric display
          const config = getConfig();
          const decimals = config.currencyDecimals !== undefined ? config.currencyDecimals : 2;
          const val = validation.value;
          manualInput.value = decimals > 0 ? (Number.isInteger(val) ? val.toString() : val.toFixed(decimals)) : Math.round(val).toString();
          sliderInput.value = Math.min(val, maxSpend);
          clearCategoryError(catId, manualInput);
        }
      });
    }
  });

  // Reset Reductions Button
  const resetBtn = document.getElementById('btn-reset-reductions');
  if (resetBtn) {
    resetBtn.addEventListener('click', handleResetReductions);
  }

  // Save Scenario Form
  const saveForm = document.getElementById('save-scenario-form');
  if (saveForm) {
    saveForm.addEventListener('submit', handleSaveScenario);
  }
}

/**
 * Validate a reduction input value against spending limits and rules.
 */
function validateCategoryInput(catId, rawVal, maxSpend) {
  // Graceful empty input while user is typing
  if (rawVal === '' || rawVal === null || rawVal === undefined) {
    return { isValid: true, isEmpty: true, value: 0, errorMessage: '' };
  }

  const val = Number(rawVal);
  if (isNaN(val)) {
    return { isValid: false, isEmpty: false, value: 0, errorMessage: 'Please enter a valid numeric amount.' };
  }

  if (val < 0) {
    return { isValid: false, isEmpty: false, value: 0, errorMessage: 'Reduction cannot be negative.' };
  }

  if (maxSpend <= 0 && val > 0) {
    return { isValid: false, isEmpty: false, value: 0, errorMessage: 'Category spending is zero. No reduction can be applied.' };
  }

  // Tolerance check for minor floating point imprecision
  if (val > maxSpend + 0.0001) {
    return {
      isValid: false,
      isEmpty: false,
      value: val,
      errorMessage: `Reduction cannot exceed current spending (${formatCurrency(maxSpend)}).`
    };
  }

  return { isValid: true, isEmpty: false, value: val, errorMessage: '' };
}

function showCategoryError(catId, inputEl, message) {
  inputEl.classList.add('is-invalid');
  const errEl = document.getElementById(`reduction-error-${catId}`);
  if (errEl) {
    errEl.innerText = message;
    errEl.style.display = 'block';
  }
}

function clearCategoryError(catId, inputEl) {
  inputEl.classList.remove('is-invalid');
  const errEl = document.getElementById(`reduction-error-${catId}`);
  if (errEl) {
    errEl.innerText = '';
    errEl.style.display = 'none';
  }
}

/**
 * Gather the current simulation state from the DOM.
 * Guarantees no duplicate counting by indexing strictly on unique catId.
 */
function collectSimulationState() {
  const cards = document.querySelectorAll('.sim-cat-card');
  const validReductions = {};
  let totalMonthlySavings = 0;
  let activeCategoriesCount = 0;
  let hasErrors = false;

  cards.forEach(card => {
    const catId = card.getAttribute('data-cat-id');
    const maxSpend = parseFloat(card.getAttribute('data-original-major') || '0');
    const manualInput = document.getElementById(`manual-reduction-${catId}`);

    if (!manualInput) return;

    const rawVal = manualInput.value.trim();
    const validation = validateCategoryInput(catId, rawVal, maxSpend);

    if (!validation.isValid) {
      hasErrors = true;
      // Do not corrupt calculations with invalid input
    } else {
      const reductionVal = validation.value;
      if (reductionVal > 0) {
        validReductions[catId] = reductionVal;
        totalMonthlySavings += reductionVal;
        activeCategoriesCount++;
        card.classList.add('has-reduction');
      } else {
        card.classList.remove('has-reduction');
      }

      // Update Proposed Monthly Spending for this category
      const proposedSpend = Math.max(0, maxSpend - reductionVal);
      const proposedEl = document.getElementById(`proposed-spend-${catId}`);
      if (proposedEl) {
        proposedEl.innerText = formatCurrency(proposedSpend);
      }

      // Update category reduction percentage badge
      const pctEl = document.getElementById(`reduction-pct-${catId}`);
      if (pctEl) {
        const pct = maxSpend > 0 ? Math.min(100, Math.round((reductionVal / maxSpend) * 100)) : 0;
        pctEl.innerText = `${pct}%`;
      }
    }
  });

  return {
    validReductions,
    totalMonthlySavings,
    activeCategoriesCount,
    hasErrors
  };
}

/**
 * Immediate, zero-lag client-side recalculation of KPIs and chart,
 * followed by debounced server-side synchronization for authoritative figures.
 */
function handleLiveUpdate(immediateServerSync = false) {
  const state = collectSimulationState();
  const config = getConfig();

  const decimals = config.currencyDecimals !== undefined ? config.currencyDecimals : 2;
  const divisor = 10 ** decimals;
  const baselineExpenses = (config.baselineExpensesMinor || 0) / divisor;
  const baselineSurplus = (config.baselineSurplusMinor || 0) / divisor;

  const totalMonthlySavings = state.totalMonthlySavings;
  const revisedExpenses = Math.max(0, baselineExpenses - totalMonthlySavings);
  const revisedSurplus = baselineSurplus + totalMonthlySavings;
  const estimatedAnnualSavings = totalMonthlySavings * 12;

  // 1. Immediately update top KPI summary cards
  const totalRedEl = document.getElementById('sim-total-reduction');
  if (totalRedEl) totalRedEl.innerText = formatCurrency(totalMonthlySavings);

  const revExpEl = document.getElementById('sim-revised-expenses');
  if (revExpEl) revExpEl.innerText = formatCurrency(revisedExpenses);

  const revSurplusEl = document.getElementById('sim-revised-surplus');
  if (revSurplusEl) revSurplusEl.innerText = formatCurrency(revSurplus);

  const annualEl = document.getElementById('sim-annualized-savings');
  if (annualEl) annualEl.innerText = formatCurrency(estimatedAnnualSavings);

  // 2. Update category meta bar
  const countEl = document.getElementById('sim-categories-count');
  if (countEl) countEl.innerText = state.activeCategoriesCount;

  const trimEl = document.getElementById('sim-category-total-trim');
  if (trimEl) trimEl.innerText = formatCurrency(totalMonthlySavings);

  // 3. Fast chart update
  if (simulationChart) {
    simulationChart.data.datasets[0].data = [baselineExpenses, revisedExpenses];
    simulationChart.data.datasets[1].data = [baselineSurplus, revisedSurplus];
    simulationChart.update('none');
  }

  // 4. Server synchronization (debounced by 150ms to prevent network churn while typing)
  clearTimeout(recalculationTimer);
  if (immediateServerSync) {
    syncWithServer(state.validReductions);
  } else {
    recalculationTimer = setTimeout(() => {
      syncWithServer(state.validReductions);
    }, 150);
  }
}

/**
 * Call the backend /api/simulations/calculate endpoint for authoritative figures.
 */
async function syncWithServer(validReductions) {
  try {
    const res = await secureFetch('/api/simulations/calculate', {
      method: 'POST',
      body: JSON.stringify({
        reductions: validReductions,
        is_minor_units: false
      })
    });

    if (res && res.simulation) {
      updateSimulatorDOM(res.simulation);
    }
  } catch (err) {
    console.error('Simulation calculation failed:', err);
  }
}

/**
 * Apply authoritative server values to DOM displays and chart.
 */
function updateSimulatorDOM(sim) {
  if (!sim || !sim.proposed) return;

  const totalRedEl = document.getElementById('sim-total-reduction');
  if (totalRedEl) totalRedEl.innerText = sim.proposed.total_reduction_formatted;

  const revExpEl = document.getElementById('sim-revised-expenses');
  if (revExpEl) revExpEl.innerText = sim.proposed.revised_expenses_formatted;

  const revSurplusEl = document.getElementById('sim-revised-surplus');
  if (revSurplusEl) revSurplusEl.innerText = sim.proposed.revised_surplus_formatted;

  const annualEl = document.getElementById('sim-annualized-savings');
  if (annualEl) annualEl.innerText = sim.proposed.annualized_savings_formatted;

  const rateEl = document.getElementById('sim-revised-rate');
  if (rateEl) rateEl.innerText = `${sim.proposed.revised_savings_rate}%`;

  const trimEl = document.getElementById('sim-category-total-trim');
  if (trimEl) trimEl.innerText = sim.proposed.total_reduction_formatted;

  // Synchronise chart with authoritative minor values
  if (simulationChart && sim.baseline) {
    const config = getConfig();
    const divisor = 10 ** (config.currencyDecimals || 2);
    const origExp = sim.baseline.expenses_minor / divisor;
    const revExp = sim.proposed.revised_expenses_minor / divisor;
    const origSurplus = sim.baseline.surplus_minor / divisor;
    const revSurplus = sim.proposed.revised_surplus_minor / divisor;

    simulationChart.data.datasets[0].data = [origExp, revExp];
    simulationChart.data.datasets[1].data = [origSurplus, revSurplus];
    simulationChart.update();
  }
}

/**
 * Reset all category reductions to zero with confirmation when active reductions exist.
 */
function handleResetReductions() {
  const state = collectSimulationState();
  const hasActiveReductions = state.totalMonthlySavings > 0 || state.activeCategoriesCount > 0;

  if (hasActiveReductions) {
    const confirmed = confirm('Reset all category reductions to zero?');
    if (!confirmed) return;
  }

  const cards = document.querySelectorAll('.sim-cat-card');
  cards.forEach(card => {
    const catId = card.getAttribute('data-cat-id');
    const manualInput = document.getElementById(`manual-reduction-${catId}`);
    const sliderInput = document.getElementById(`slider-reduction-${catId}`);
    const origMajor = parseFloat(card.getAttribute('data-original-major') || '0');

    if (manualInput) {
      manualInput.value = '0';
      clearCategoryError(catId, manualInput);
    }
    if (sliderInput) {
      sliderInput.value = 0;
    }

    card.classList.remove('has-reduction');

    const proposedEl = document.getElementById(`proposed-spend-${catId}`);
    if (proposedEl) {
      proposedEl.innerText = formatCurrency(origMajor);
    }

    const pctEl = document.getElementById(`reduction-pct-${catId}`);
    if (pctEl) {
      pctEl.innerText = '0%';
    }
  });

  handleLiveUpdate(true);
  showToast('All category reductions have been reset.', 'info');
}

/**
 * Handle saving the current scenario.
 */
async function handleSaveScenario(e) {
  e.preventDefault();
  const nameInput = document.getElementById('scenario-name');
  const name = nameInput ? nameInput.value.trim() : '';
  if (!name) return;

  const state = collectSimulationState();

  try {
    await secureFetch('/api/simulations', {
      method: 'POST',
      body: JSON.stringify({
        name: name,
        scenario_data: state.validReductions
      })
    });
    showToast(`Scenario "${name}" saved!`, 'success');
    closeModal('save-scenario-modal');
    setTimeout(() => window.location.reload(), 600);
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

/**
 * Load a previously saved scenario into both manual inputs and sliders.
 */
function loadScenario(reductionsJson) {
  try {
    const reductions = typeof reductionsJson === 'string' ? JSON.parse(reductionsJson) : reductionsJson;
    const cards = document.querySelectorAll('.sim-cat-card');
    const config = getConfig();
    const decimals = config.currencyDecimals !== undefined ? config.currencyDecimals : 2;

    cards.forEach(card => {
      const catId = card.getAttribute('data-cat-id');
      const maxSpend = parseFloat(card.getAttribute('data-original-major') || '0');
      const manualInput = document.getElementById(`manual-reduction-${catId}`);
      const sliderInput = document.getElementById(`slider-reduction-${catId}`);

      const savedVal = reductions[catId] !== undefined ? parseFloat(reductions[catId]) : 0;
      const effectiveVal = Math.min(Math.max(0, savedVal || 0), maxSpend);

      if (manualInput) {
        manualInput.value = decimals > 0 ? (Number.isInteger(effectiveVal) ? effectiveVal.toString() : effectiveVal.toFixed(decimals)) : Math.round(effectiveVal).toString();
        clearCategoryError(catId, manualInput);
      }

      if (sliderInput) {
        sliderInput.value = effectiveVal;
      }
    });

    handleLiveUpdate(true);
    showToast('Loaded scenario assumptions!', 'info');
  } catch (e) {
    console.error('Error loading scenario', e);
  }
}

/**
 * Initialize Comparison Bar Chart with theme responsiveness.
 */
function initSimulationChart() {
  const canvas = document.getElementById('simulationComparisonChart');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const expenseColor = isDark ? '#f87171' : '#161917';
  const gridColor = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.04)';

  simulationChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Current Baseline', 'Simulated Scenario'],
      datasets: [
        {
          label: 'Expenses',
          data: [0, 0],
          backgroundColor: expenseColor,
          borderRadius: 8
        },
        {
          label: 'Monthly Surplus',
          data: [0, 0],
          backgroundColor: '#cbf432',
          borderRadius: 8
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: { font: { weight: '700' } }
        }
      },
      scales: {
        x: { grid: { display: false } },
        y: { grid: { color: gridColor } }
      }
    }
  });
}

// Live update chart styling on themechange event
window.addEventListener('themechange', (e) => {
  if (simulationChart) {
    const isDarkNow = e.detail && e.detail.theme === 'dark';
    simulationChart.data.datasets[0].backgroundColor = isDarkNow ? '#f87171' : '#161917';
    if (simulationChart.options.scales && simulationChart.options.scales.y) {
      simulationChart.options.scales.y.grid.color = isDarkNow ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.04)';
    }
    simulationChart.update();
  }
});

