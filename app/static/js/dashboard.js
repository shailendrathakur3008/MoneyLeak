/**
 * MoneyLeak Dashboard Interactive Visualizations
 * Renders Chart.js Donut breakdown and Progress Area Trend Chart.
 */

document.addEventListener('DOMContentLoaded', () => {
  initMacroRings();
  initDonutChart();
  initTrendsChart();
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
