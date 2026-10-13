/**
 * Savings Simulator Interactive Engine
 * Interactive sliders for category expense trims and scenario saving.
 */

let simulationChart = null;

document.addEventListener('DOMContentLoaded', () => {
  initSimulatorEvents();
  initSimulationChart();
  triggerRecalculation();
});

function initSimulatorEvents() {
  const inputs = document.querySelectorAll('.sim-reduction-input');
  inputs.forEach(input => {
    input.addEventListener('input', () => {
      const catId = input.getAttribute('data-cat-id');
      const val = parseFloat(input.value || 0);
      const valDisplay = document.getElementById(`reduction-val-${catId}`);
      if (valDisplay) valDisplay.innerText = val.toLocaleString();

      triggerRecalculation();
    });
  });

  const saveForm = document.getElementById('save-scenario-form');
  if (saveForm) {
    saveForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = document.getElementById('scenario-name').value.trim();
      if (!name) return;

      const reductions = {};
      inputs.forEach(input => {
        const catId = input.getAttribute('data-cat-id');
        const val = parseFloat(input.value || 0);
        if (val > 0) reductions[catId] = val;
      });

      try {
        await secureFetch('/api/simulations', {
          method: 'POST',
          body: JSON.stringify({
            name: name,
            scenario_data: reductions
          })
        });
        showToast(`Scenario "${name}" saved!`, 'success');
        setTimeout(() => window.location.reload(), 600);
      } catch (err) {
        showToast(err.message, 'danger');
      }
    });
  }
}

async function triggerRecalculation() {
  const inputs = document.querySelectorAll('.sim-reduction-input');
  const reductions = {};
  inputs.forEach(input => {
    const catId = input.getAttribute('data-cat-id');
    const val = parseFloat(input.value || 0);
    if (val > 0) reductions[catId] = val;
  });

  try {
    const res = await secureFetch('/api/simulations/calculate', {
      method: 'POST',
      body: JSON.stringify({
        reductions: reductions,
        is_minor_units: false
      })
    });

    const sim = res.simulation;
    updateSimulatorDOM(sim);
  } catch (err) {
    console.error('Simulation calculation failed:', err);
  }
}

function updateSimulatorDOM(sim) {
  // Update KPI displays
  document.getElementById('sim-total-reduction').innerText = sim.proposed.total_reduction_formatted;
  document.getElementById('sim-revised-expenses').innerText = sim.proposed.revised_expenses_formatted;
  document.getElementById('sim-revised-surplus').innerText = sim.proposed.revised_surplus_formatted;
  document.getElementById('sim-annualized-savings').innerText = sim.proposed.annualized_savings_formatted;
  document.getElementById('sim-revised-rate').innerText = `${sim.proposed.revised_savings_rate}%`;

  // Update chart
  if (simulationChart) {
    const origExp = sim.baseline.expenses_minor / 100;
    const revExp = sim.proposed.revised_expenses_minor / 100;
    const origSurplus = sim.baseline.surplus_minor / 100;
    const revSurplus = sim.proposed.revised_surplus_minor / 100;

    simulationChart.data.datasets[0].data = [origExp, revExp];
    simulationChart.data.datasets[1].data = [origSurplus, revSurplus];
    simulationChart.update();
  }
}

function initSimulationChart() {
  const canvas = document.getElementById('simulationComparisonChart');
  if (!canvas) return;

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

// Live update simulation chart on themechange
window.addEventListener('themechange', (e) => {
  if (simulationChart) {
    const isDarkNow = e.detail.theme === 'dark';
    simulationChart.data.datasets[0].backgroundColor = isDarkNow ? '#f87171' : '#161917';
    if (simulationChart.options.scales && simulationChart.options.scales.y) {
      simulationChart.options.scales.y.grid.color = isDarkNow ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.04)';
    }
    simulationChart.update();
  }
});

function loadScenario(reductionsJson) {
  try {
    const reductions = typeof reductionsJson === 'string' ? JSON.parse(reductionsJson) : reductionsJson;
    const inputs = document.querySelectorAll('.sim-reduction-input');
    inputs.forEach(input => {
      const catId = input.getAttribute('data-cat-id');
      const val = reductions[catId] || 0;
      input.value = val;
      const valDisplay = document.getElementById(`reduction-val-${catId}`);
      if (valDisplay) valDisplay.innerText = Number(val).toLocaleString();
    });
    triggerRecalculation();
    showToast('Loaded scenario assumptions!', 'info');
  } catch (e) {
    console.error('Error loading scenario', e);
  }
}
