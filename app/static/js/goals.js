/**
 * Financial Goals Planner Logic
 * Goal creation, contribution logging, and milestone tracking.
 */

document.addEventListener('DOMContentLoaded', () => {
  const goalForm = document.getElementById('create-goal-form');
  if (goalForm) {
    goalForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        name: document.getElementById('goal-name').value.trim(),
        target_amount: document.getElementById('goal-target-amount').value,
        target_date: document.getElementById('goal-target-date').value,
        category_type: document.getElementById('goal-category-type').value,
        icon: document.getElementById('goal-icon').value
      };

      try {
        await secureFetch('/api/goals', {
          method: 'POST',
          body: JSON.stringify(payload)
        });
        showToast('Financial goal created!', 'success');
        closeModal('create-goal-modal');
        setTimeout(() => window.location.reload(), 500);
      } catch (err) {
        showToast(err.message, 'danger');
      }
    });
  }

  const contribForm = document.getElementById('log-contrib-form');
  if (contribForm) {
    contribForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const goalId = document.getElementById('contrib-goal-id').value;
      const payload = {
        amount: document.getElementById('contrib-amount').value,
        contribution_date: document.getElementById('contrib-date').value,
        notes: document.getElementById('contrib-notes').value.trim()
      };

      try {
        const res = await secureFetch(`/api/goals/${goalId}/contributions`, {
          method: 'POST',
          body: JSON.stringify(payload)
        });
        showToast(res.message || 'Contribution logged!', 'success');
        closeModal('log-contrib-modal');
        setTimeout(() => window.location.reload(), 500);
      } catch (err) {
        showToast(err.message, 'danger');
      }
    });
  }
});

function openContributionModal(goalId, goalName) {
  document.getElementById('contrib-goal-id').value = goalId;
  document.getElementById('contrib-goal-title').innerText = goalName;
  openModal('log-contrib-modal');
}

async function deleteGoal(goalId) {
  if (!confirm('Are you sure you want to delete this financial goal?')) return;
  try {
    await secureFetch(`/api/goals/${goalId}`, { method: 'DELETE' });
    showToast('Goal removed.', 'success');
    setTimeout(() => window.location.reload(), 500);
  } catch (err) {
    showToast(err.message, 'danger');
  }
}
