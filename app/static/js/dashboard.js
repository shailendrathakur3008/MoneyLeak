/**
 * MoneyLeak Dashboard Interactive Visualizations
 * Renders Chart.js Donut breakdown and Progress Area Trend Chart.
 */

document.addEventListener('DOMContentLoaded', () => {
  initMacroRings();
  initDonutChart();
  initTrendsChart();
  initMonthlyBudgetPrompt();
});

// Animate the 3 SVG Macro Rings (Needs, Wants, Savings)
function initMacroRings() {
  const circles = document.querySelectorAll('.macro-circle-val');
  circles.forEach(circle => {
    const pct = parseFloat(circle.getAttribute('data-pct') || '0');
    // Circumference = 2 * PI * r = 2 * 3.14159 * 28 ≈ 175.9
    const circumference = 175.9;
    circle.style.strokeDasharray = circumference;
    const offset = circumference - (Math.min(pct, 100) / 100) * circumference;
    circle.style.strokeDashoffset = offset;
  });
}

// Donut Chart: 50/30/20 Distribution & Outflows
function initDonutChart() {
  const canvas = document.getElementById('budgetDonutChart');
  if (!canvas) return;

  const needsMinor = parseFloat(canvas.getAttribute('data-needs') || '0');
  const wantsMinor = parseFloat(canvas.getAttribute('data-wants') || '0');
  const savingsMinor = parseFloat(canvas.getAttribute('data-savings') || '0');

  const total = needsMinor + wantsMinor + savingsMinor;
  const dataVals = total > 0 ? [needsMinor, wantsMinor, savingsMinor] : [50, 30, 20];

  const ctx = canvas.getContext('2d');
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Needs (50%)', 'Wants (30%)', 'Savings (20%)'],
      datasets: [{
        data: dataVals,
        backgroundColor: [
          '#cbf432', // Vibrant Lime
          '#38bdf8', // Sky Blue
          '#a78bfa'  // Soft Lavender
        ],
        borderWidth: 0,
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '76%',
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#161917',
          titleColor: '#ffffff',
          bodyColor: '#cbf432',
          padding: 12,
          cornerRadius: 12,
          displayColors: true,
          callbacks: {
            label: function(context) {
              const val = context.parsed;
              const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
              return ` ${context.label}: ${pct}%`;
            }
          }
        }
      }
    }
  });
}

// Trends Area Chart: 6-Month Income vs Expenses
async function initTrendsChart() {
  const canvas = document.getElementById('progressTrendChart');
  if (!canvas) return;

  try {
    const res = await secureFetch('/api/dashboard/trends?months=6');
    const trends = res.trends || [];

    const labels = trends.map(t => t.label);
    const currency = res.currency || 'INR';

    // Convert minor units to major for chart
    const decimals = currency === 'JPY' ? 0 : 2;
    const divisor = Math.pow(10, decimals);

    const incomeData = trends.map(t => t.income_minor / divisor);
    const expenseData = trends.map(t => t.expenses_minor / divisor);
    const savingsData = trends.map(t => t.savings_minor / divisor);

    const ctx = canvas.getContext('2d');

    // Create subtle gradients
    const gradIncome = ctx.createLinearGradient(0, 0, 0, 200);
    gradIncome.addColorStop(0, 'rgba(203, 244, 50, 0.35)');
    gradIncome.addColorStop(1, 'rgba(203, 244, 50, 0.0)');

    const gradExpense = ctx.createLinearGradient(0, 0, 0, 200);
    gradExpense.addColorStop(0, 'rgba(22, 25, 23, 0.2)');
    gradExpense.addColorStop(1, 'rgba(22, 25, 23, 0.0)');

    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const expenseColor = isDark ? '#f87171' : '#161917';
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.04)';

    window.trendChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Income',
            data: incomeData,
            borderColor: '#84cc16',
            backgroundColor: gradIncome,
            fill: true,
            tension: 0.35,
            borderWidth: 2.5,
            pointBackgroundColor: '#84cc16',
            pointRadius: 4,
            pointHoverRadius: 6
          },
          {
            label: 'Expenses',
            data: expenseData,
            borderColor: expenseColor,
            backgroundColor: gradExpense,
            fill: true,
            tension: 0.35,
            borderWidth: 2.5,
            pointBackgroundColor: expenseColor,
            pointRadius: 4,
            pointHoverRadius: 6
          },
          {
            label: 'Savings',
            data: savingsData,
            borderColor: '#38bdf8',
            backgroundColor: 'transparent',
            fill: false,
            tension: 0.35,
            borderWidth: 2,
            borderDash: [5, 5],
            pointBackgroundColor: '#38bdf8',
            pointRadius: 3
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false
        },
        plugins: {
          legend: {
            position: 'top',
            labels: {
              boxWidth: 10,
              usePointStyle: true,
              font: { weight: '600', size: 11 }
            }
          },
          tooltip: {
            backgroundColor: '#161917',
            titleColor: '#ffffff',
            bodyColor: '#ffffff',
            padding: 12,
            cornerRadius: 12
          }
        },
        scales: {
          x: {
            grid: { display: false }
          },
          y: {
            grid: { color: gridColor },
            ticks: {
              callback: function(value) {
                return value >= 1000 ? `${(value / 1000).toFixed(0)}k` : value;
              }
            }
          }
        }
      }
    });
  } catch (err) {
    console.error('Failed to load trend chart data:', err);
  }
}

// Update trend chart live when theme changes
window.addEventListener('themechange', (e) => {
  if (window.trendChart) {
    const isDarkNow = e.detail.theme === 'dark';
    window.trendChart.data.datasets[1].borderColor = isDarkNow ? '#f87171' : '#161917';
    window.trendChart.data.datasets[1].pointBackgroundColor = isDarkNow ? '#f87171' : '#161917';
    if (window.trendChart.options.scales && window.trendChart.options.scales.y) {
      window.trendChart.options.scales.y.grid.color = isDarkNow ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.04)';
    }
    window.trendChart.update();
  }
});

// ============================================================================
// MONTHLY BUDGET CONFIRMATION LOGIC
// ============================================================================

function getPromptMetadata() {
  const el = document.getElementById('budget-prompt-data');
  if (!el) return null;
  return {
    year: parseInt(el.getAttribute('data-year') || '0', 10),
    month: parseInt(el.getAttribute('data-month') || '0', 10),
    monthName: el.getAttribute('data-month-name') || '',
    shouldPrompt: el.getAttribute('data-should-prompt') === 'true',
    needsPct: parseFloat(el.getAttribute('data-needs-pct') || '50'),
    wantsPct: parseFloat(el.getAttribute('data-wants-pct') || '30'),
    savingsPct: parseFloat(el.getAttribute('data-savings-pct') || '20'),
    currencySymbol: el.getAttribute('data-currency-symbol') || '₹',
    prevFormatted: el.getAttribute('data-prev-formatted') || ''
  };
}

function initMonthlyBudgetPrompt() {
  const meta = getPromptMetadata();
  if (!meta) return;

  // Initialize live preview for modal input if present
  const inputEl = document.getElementById('modal-new-budget-amount');
  if (inputEl && inputEl.value) {
    updateModalBudgetPreview(inputEl.value);
  }

  // Check if eligible to prompt and not dismissed during this browser session
  const sessionKey = `budget_prompt_dismissed_${meta.year}_${meta.month}`;
  const alreadyDismissedThisSession = sessionStorage.getItem(sessionKey) === 'true';

  if (meta.shouldPrompt && !alreadyDismissedThisSession) {
    // Delay slightly for smooth page entrance
    setTimeout(() => {
      openMonthlyBudgetModal();
    }, 400);
  }
}

window.openMonthlyBudgetModal = function() {
  openModal('monthly-budget-modal');
  const inputEl = document.getElementById('modal-new-budget-amount');
  if (inputEl) {
    updateModalBudgetPreview(inputEl.value);
    inputEl.focus();
  }
};

window.handleCloseBudgetModal = function() {
  const meta = getPromptMetadata();
  if (meta) {
    sessionStorage.setItem(`budget_prompt_dismissed_${meta.year}_${meta.month}`, 'true');
    // Notify server of dismissal without changing budget
    secureFetch('/api/budget/confirm-action', {
      method: 'POST',
      body: JSON.stringify({ action: 'dismiss', year: meta.year, month: meta.month })
    }).catch(() => {});
  }
  closeModal('monthly-budget-modal');
};

window.handlePostponePrompt = function() {
  const meta = getPromptMetadata();
  if (meta) {
    sessionStorage.setItem(`budget_prompt_dismissed_${meta.year}_${meta.month}`, 'true');
    secureFetch('/api/budget/confirm-action', {
      method: 'POST',
      body: JSON.stringify({ action: 'remind_later', year: meta.year, month: meta.month })
    }).then(() => {
      showToast('Reminder postponed. You can set or confirm your budget anytime from this dashboard or Settings.', 'info');
      const banner = document.getElementById('monthly-budget-banner');
      if (banner) banner.style.opacity = '0.7';
    }).catch(err => {
      showToast(err.message || 'Action failed', 'danger');
    });
  }
  closeModal('monthly-budget-modal');
};

window.handleKeepPreviousBudget = function() {
  const meta = getPromptMetadata();
  if (!meta) return;

  secureFetch('/api/budget/confirm-action', {
    method: 'POST',
    body: JSON.stringify({ action: 'keep_previous', year: meta.year, month: meta.month })
  }).then(res => {
    closeModal('monthly-budget-modal');
    const banner = document.getElementById('monthly-budget-banner');
    if (banner) banner.remove();
    showToast(res.message || 'Previous budget retained.', 'success');
    setTimeout(() => window.location.reload(), 450);
  }).catch(err => {
    showToast(err.message || 'Failed to confirm budget.', 'danger');
  });
};

window.handleSetNewBudget = async function(e) {
  if (e) e.preventDefault();
  const meta = getPromptMetadata();
  if (!meta) return;

  const inputEl = document.getElementById('modal-new-budget-amount');
  const rawVal = (inputEl ? inputEl.value : '').replace(/,/g, '').trim();
  const amount = parseFloat(rawVal);

  if (isNaN(amount) || amount <= 0) {
    showToast('Please enter a valid positive budget amount.', 'danger');
    if (inputEl) inputEl.focus();
    return;
  }

  const btn = document.getElementById('btn-confirm-new-budget');
  if (btn) btn.disabled = true;

  try {
    const res = await secureFetch('/api/budget/confirm-action', {
      method: 'POST',
      body: JSON.stringify({
        action: 'set_new',
        amount: amount,
        year: meta.year,
        month: meta.month,
        month_name: meta.monthName
      })
    });
    closeModal('monthly-budget-modal');
    const banner = document.getElementById('monthly-budget-banner');
    if (banner) banner.remove();
    showToast(res.message || 'New monthly budget confirmed!', 'success');
    setTimeout(() => window.location.reload(), 450);
  } catch (err) {
    showToast(err.message || 'Failed to save new budget.', 'danger');
    if (btn) btn.disabled = false;
  }
};

window.updateModalBudgetPreview = function(val) {
  const meta = getPromptMetadata();
  if (!meta) return;

  const num = parseFloat((val || '').replace(/,/g, '').trim());
  const needsEl = document.getElementById('modal-preview-needs');
  const wantsEl = document.getElementById('modal-preview-wants');
  const savingsEl = document.getElementById('modal-preview-savings');

  if (isNaN(num) || num <= 0) {
    if (needsEl) needsEl.innerText = '-';
    if (wantsEl) wantsEl.innerText = '-';
    if (savingsEl) savingsEl.innerText = '-';
    return;
  }

  const sym = meta.currencySymbol;
  const needsAmt = Math.round(num * (meta.needsPct / 100)).toLocaleString('en-IN');
  const wantsAmt = Math.round(num * (meta.wantsPct / 100)).toLocaleString('en-IN');
  const savingsAmt = Math.round(num * (meta.savingsPct / 100)).toLocaleString('en-IN');

  if (needsEl) needsEl.innerText = `${sym}${needsAmt}`;
  if (wantsEl) wantsEl.innerText = `${sym}${wantsAmt}`;
  if (savingsEl) savingsEl.innerText = `${sym}${savingsAmt}`;
};

