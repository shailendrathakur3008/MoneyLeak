/**
 * TripWise — Smart Trip Budget Planner
 * Frontend Controller for trip planning, category overrides, scenario views,
 * transaction linking, and real-time affordability updates.
 */

(function () {
  'use strict';

  let editingTripId = null;

  // Initialize event listeners when DOM is loaded
  document.addEventListener('DOMContentLoaded', () => {
    initTripPlanForm();
    initCategoryEditForm();
    initLinkTransactionForm();
    initLogTripExpenseForm();
    initDateAutoFill();
  });

  /**
   * Automatically adjust return date when departure date changes if return date is empty or earlier.
   */
  function initDateAutoFill() {
    const depInput = document.getElementById('trip-dep-date');
    const retInput = document.getElementById('trip-ret-date');
    if (!depInput || !retInput) return;

    depInput.addEventListener('change', () => {
      if (!retInput.value || retInput.value < depInput.value) {
        retInput.value = depInput.value;
      }
    });
  }

  /**
   * Reset the Plan Trip modal to clean "New Trip" creation mode.
   */
  window.resetPlanTripModal = function () {
    editingTripId = null;
    const form = document.getElementById('plan-trip-form');
    if (form) form.reset();

    const titleEl = document.querySelector('#plan-trip-modal .modal-header h3');
    if (titleEl) titleEl.textContent = 'TripWise — Plan a Trip';

    const saveBtn = document.getElementById('btn-save-trip');
    if (saveBtn) {
      saveBtn.innerHTML = '<i data-lucide="check" style="width:14px;height:14px;"></i> Generate & Save Trip';
    }

    // Default dates
    const depInput = document.getElementById('trip-dep-date');
    const retInput = document.getElementById('trip-ret-date');
    const today = new Date().toISOString().split('T')[0];
    if (depInput && !depInput.value) depInput.value = today;
    if (retInput && !retInput.value) retInput.value = today;

    window.refreshIcons();
  };

  /**
   * Open the Plan Trip modal populated with active trip data for editing.
   */
  window.openEditTripModal = function () {
    const cfg = window.TripWiseConfig;
    if (!cfg || !cfg.activeTrip) {
      showToast('No active trip to edit.', 'warning');
      return;
    }

    const trip = cfg.activeTrip;
    editingTripId = trip.id;

    document.getElementById('trip-origin').value = trip.starting_city || '';
    document.getElementById('trip-destination').value = trip.destination || '';
    document.getElementById('trip-dep-date').value = trip.departure_date ? trip.departure_date.split('T')[0] : '';
    document.getElementById('trip-ret-date').value = trip.return_date ? trip.return_date.split('T')[0] : '';
    document.getElementById('trip-travellers').value = trip.travellers_count || 1;
    document.getElementById('trip-nature').value = trip.trip_nature || 'PLANNED';
    document.getElementById('trip-transport').value = trip.transport_mode || 'TRAIN';
    document.getElementById('trip-style').value = trip.travel_style || 'STANDARD';
    document.getElementById('trip-accommodation').value = trip.accommodation_type || 'STANDARD_HOTEL';

    const customBudgetInput = document.getElementById('trip-custom-budget');
    if (customBudgetInput) {
      customBudgetInput.value = trip.custom_budget_target_minor_units ? (trip.custom_budget_target_minor_units / 100) : '';
    }

    const titleEl = document.querySelector('#plan-trip-modal .modal-header h3');
    if (titleEl) titleEl.textContent = 'Edit Trip Details';

    const saveBtn = document.getElementById('btn-save-trip');
    if (saveBtn) {
      saveBtn.innerHTML = '<i data-lucide="check" style="width:14px;height:14px;"></i> Update Trip';
    }

    window.refreshIcons();
    openModal('plan-trip-modal');
  };

  /**
   * Handle Plan / Edit Trip Form submission
   */
  function initTripPlanForm() {
    const form = document.getElementById('plan-trip-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const origin = document.getElementById('trip-origin').value.trim();
      const destination = document.getElementById('trip-destination').value.trim();
      const depDate = document.getElementById('trip-dep-date').value;
      const retDate = document.getElementById('trip-ret-date').value || depDate;
      const travellers = parseInt(document.getElementById('trip-travellers').value, 10) || 1;
      const nature = document.getElementById('trip-nature').value;
      const transport = document.getElementById('trip-transport').value;
      const style = document.getElementById('trip-style').value;
      const accommodation = document.getElementById('trip-accommodation').value;
      const customBudgetValue = document.getElementById('trip-custom-budget').value;

      if (!origin || !destination) {
        showToast('Please provide both starting city and destination.', 'danger');
        return;
      }

      if (retDate < depDate) {
        showToast('Return date cannot be earlier than departure date.', 'danger');
        return;
      }

      const payload = {
        starting_city: origin,
        destination: destination,
        departure_date: depDate,
        return_date: retDate,
        travellers_count: travellers,
        trip_nature: nature,
        transport_mode: transport,
        travel_style: style,
        accommodation_type: accommodation,
        target_budget: customBudgetValue ? parseFloat(customBudgetValue) : null
      };

      const saveBtn = document.getElementById('btn-save-trip');
      const originalText = saveBtn.innerHTML;
      saveBtn.disabled = true;
      saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Calculating...';

      try {
        let res;
        if (editingTripId) {
          res = await secureFetch(`/api/trips/${editingTripId}`, {
            method: 'PUT',
            body: JSON.stringify(payload)
          });
          showToast('Trip itinerary updated successfully!', 'success');
        } else {
          res = await secureFetch('/api/trips', {
            method: 'POST',
            body: JSON.stringify(payload)
          });
          showToast('Trip created and budget estimated!', 'success');
        }

        closeModal('plan-trip-modal');
        const targetTripId = res.trip ? res.trip.id : (res.id || editingTripId);
        window.location.href = `/trips?trip_id=${targetTripId}`;
      } catch (err) {
        showToast(err.message || 'Failed to save trip. Please try again.', 'danger');
        saveBtn.disabled = false;
        saveBtn.innerHTML = originalText;
        window.refreshIcons();
      }
    });
  }

  /**
   * Category Overrides
   */
  window.openEditCategoryModal = function (catKey, catName, currentAmountMinor) {
    document.getElementById('edit-cat-key').value = catKey;
    document.getElementById('edit-cat-title').textContent = `Edit: ${catName}`;
    document.getElementById('edit-cat-amount').value = (currentAmountMinor / 100).toFixed(2);
    openModal('edit-category-modal');
  };

  function initCategoryEditForm() {
    const form = document.getElementById('edit-category-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const catKey = document.getElementById('edit-cat-key').value;
      const amountVal = parseFloat(document.getElementById('edit-cat-amount').value);

      if (isNaN(amountVal) || amountVal < 0) {
        showToast('Please enter a valid positive amount.', 'danger');
        return;
      }

      const cfg = window.TripWiseConfig;
      if (!cfg || !cfg.activeTrip) {
        showToast('No active trip to update.', 'danger');
        return;
      }

      const trip = cfg.activeTrip;
      const estimates = trip.category_estimates || {};
      const newMinor = Math.round(amountVal * 100);

      // Update or create entry
      const existing = estimates[catKey] || {};
      estimates[catKey] = {
        ...existing,
        category: catKey,
        name: existing.name || catKey,
        estimated_cost_minor: newMinor,
        estimate_type: 'user_assumption',
        data_source: 'User Entered Assumption',
        calculation_basis: 'Custom manual budget override',
        last_updated: new Date().toISOString()
      };

      // Recalculate total budget
      let newTotal = 0;
      for (const k in estimates) {
        newTotal += estimates[k].estimated_cost_minor || 0;
      }

      try {
        await secureFetch(`/api/trips/${trip.id}`, {
          method: 'PUT',
          body: JSON.stringify({
            category_estimates: estimates,
            total_budget_minor_units: newTotal
          })
        });

        showToast('Category estimate updated!', 'success');
        closeModal('edit-category-modal');
        window.location.reload();
      } catch (err) {
        showToast(err.message || 'Failed to update category amount.', 'danger');
      }
    });
  }

  /**
   * Link Existing Ledger Transaction
   */
  function initLinkTransactionForm() {
    const form = document.getElementById('link-transaction-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const txnId = document.getElementById('link-txn-select').value;
      if (!txnId) {
        showToast('Please select a transaction to link.', 'warning');
        return;
      }

      const cfg = window.TripWiseConfig;
      if (!cfg || !cfg.activeTripId) {
        showToast('No active trip found.', 'danger');
        return;
      }

      try {
        await secureFetch(`/api/trips/${cfg.activeTripId}/transactions`, {
          method: 'POST',
          body: JSON.stringify({
            transaction_id: parseInt(txnId, 10)
          })
        });

        showToast('Transaction linked to trip successfully!', 'success');
        closeModal('link-transaction-modal');
        window.location.reload();
      } catch (err) {
        showToast(err.message || 'Failed to link transaction.', 'danger');
      }
    });
  }

  /**
   * Log New Trip Expense
   */
  function initLogTripExpenseForm() {
    const form = document.getElementById('log-trip-expense-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const amount = parseFloat(document.getElementById('new-txn-amount').value);
      const description = document.getElementById('new-txn-desc').value.trim();
      const categoryId = document.getElementById('new-txn-cat').value;
      const txnDate = document.getElementById('new-txn-date').value;

      if (!amount || amount <= 0 || !description) {
        showToast('Please provide a valid amount and description.', 'warning');
        return;
      }

      const cfg = window.TripWiseConfig;
      if (!cfg || !cfg.activeTripId) {
        showToast('No active trip found.', 'danger');
        return;
      }

      try {
        await secureFetch(`/api/trips/${cfg.activeTripId}/transactions`, {
          method: 'POST',
          body: JSON.stringify({
            amount: amount,
            description: description,
            category_id: categoryId ? parseInt(categoryId, 10) : null,
            transaction_date: txnDate
          })
        });

        showToast('Trip expense recorded and ledger updated!', 'success');
        closeModal('log-trip-expense-modal');
        window.location.reload();
      } catch (err) {
        showToast(err.message || 'Failed to record expense.', 'danger');
      }
    });
  }

  /**
   * Unlink a transaction from a trip
   */
  window.unlinkTripTransaction = async function (tripId, txnId) {
    if (!confirm('Unlink this transaction from the trip? The original ledger record will remain intact.')) {
      return;
    }

    try {
      await secureFetch(`/api/trips/${tripId}/transactions/${txnId}`, {
        method: 'DELETE'
      });

      showToast('Transaction unlinked from trip.', 'info');
      window.location.reload();
    } catch (err) {
      showToast(err.message || 'Failed to unlink transaction.', 'danger');
    }
  };

  /**
   * Delete an active trip
   */
  window.deleteActiveTrip = async function (tripId) {
    if (!confirm('Are you sure you want to delete this trip plan? Any linked transactions will simply be unlinked and preserved.')) {
      return;
    }

    try {
      await secureFetch(`/api/trips/${tripId}`, {
        method: 'DELETE'
      });

      showToast('Trip plan removed.', 'info');
      window.location.href = '/trips';
    } catch (err) {
      showToast(err.message || 'Failed to delete trip.', 'danger');
    }
  };

})();
