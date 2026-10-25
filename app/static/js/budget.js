/**
 * 50/30/20 Budget Configuration Interactive Logic
 * Live slider calibration, sum-to-100% enforcement, and target previews.
 */

document.addEventListener('DOMContentLoaded', () => {
  initBudgetSliders();
});

function initBudgetSliders() {
  const needsInput = document.getElementById('budget-needs-range');
  const wantsInput = document.getElementById('budget-wants-range');
  const savingsInput = document.getElementById('budget-savings-range');

  if (!needsInput || !wantsInput || !savingsInput) return;

  function updateSumPreview() {
    const needs = parseFloat(needsInput.value);
    const wants = parseFloat(wantsInput.value);
    const savings = parseFloat(savingsInput.value);

    document.getElementById('needs-val-preview').innerText = `${needs}%`;
    document.getElementById('wants-val-preview').innerText = `${wants}%`;
    document.getElementById('savings-val-preview').innerText = `${savings}%`;

    const total = Math.round((needs + wants + savings) * 10) / 10;
    const sumEl = document.getElementById('budget-sum-preview');
    const saveBtn = document.getElementById('save-budget-btn');

    sumEl.innerText = `${total}%`;
    if (total === 100.0) {
      sumEl.style.color = '#16a34a';
      if (saveBtn) saveBtn.disabled = false;
    } else {
      sumEl.style.color = '#dc2626';
      if (saveBtn) saveBtn.disabled = true;
    }
  }

  needsInput.addEventListener('input', updateSumPreview);
  wantsInput.addEventListener('input', updateSumPreview);
  savingsInput.addEventListener('input', updateSumPreview);

  const form = document.getElementById('budget-config-form');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const needs = parseFloat(needsInput.value);
      const wants = parseFloat(wantsInput.value);
      const savings = parseFloat(savingsInput.value);

      const incomeInput = document.getElementById('budget-income-input');
      const monthlyIncome = incomeInput ? incomeInput.value.replace(/,/g, '').trim() : '';

      const budgetInput = document.getElementById('budget-amount-input');
      const monthlyBudget = budgetInput ? budgetInput.value.replace(/,/g, '').trim() : '';

      try {
        await secureFetch('/api/budget', {
          method: 'PUT',
          body: JSON.stringify({
            needs_percentage: needs,
            wants_percentage: wants,
            savings_percentage: savings,
            monthly_budget: monthlyBudget,
            monthly_income: monthlyIncome
          })
        });
        showToast('50/30/20 framework & persistent monthly budget updated successfully!', 'success');
        setTimeout(() => window.location.reload(), 600);
      } catch (err) {
        showToast(err.message, 'danger');
      }
    });
  }

  const resetBtn = document.getElementById('reset-budget-btn');
  if (resetBtn) {
    resetBtn.addEventListener('click', async () => {
      if (!confirm('Reset back to standard 50% Needs, 30% Wants, 20% Savings?')) return;
      try {
        await secureFetch('/api/budget/reset', { method: 'POST' });
        showToast('Reset to default 50/30/20!', 'success');
        setTimeout(() => window.location.reload(), 500);
      } catch (err) {
        showToast(err.message, 'danger');
      }
    });
  }
}
