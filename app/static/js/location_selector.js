/**
 * MoneyLeak Searchable Dependent Location Dropdown Component
 * Hierarchy: Country -> State / Union Territory -> District -> City / Town
 * Features:
 * - Searchable with debounced and client-side filtering
 * - Keyboard navigation (Up/Down, Enter, Esc)
 * - Clear button
 * - Loading indicators
 * - Disambiguation labels: City (District, State)
 * - Tier badges (Metro, Urban, Town, Rural)
 * - Custom locality fallback
 * - Full mobile responsiveness and theme harmony
 */

class SearchableDropdown {
  constructor(container, options = {}) {
    this.container = typeof container === 'string' ? document.querySelector(container) : container;
    this.options = Object.assign({
      placeholder: 'Search or select...',
      disabledPlaceholder: 'Select parent first...',
      noResultsText: 'No matches found.',
      allowCustom: false,
      customPrompt: 'Use custom locality: "{query}"',
      searchDebounceMs: 150,
      onSelect: null,
      onClear: null,
      fetchItems: null,
      items: [],
      disabled: false,
      initialValue: null,
      idPrefix: 'sd_' + Math.random().toString(36).substr(2, 6)
    }, options);

    this.selectedItem = null;
    this.items = [...this.options.items];
    this.filteredItems = [];
    this.isOpen = false;
    this.activeIndex = -1;
    this.debounceTimer = null;
    this.isLoading = false;

    if (this.container) {
      this.init();
    }
  }

  init() {
    this.container.classList.add('searchable-dropdown-wrap');
    this.container.innerHTML = `
      <div class="sd-control ${this.options.disabled ? 'is-disabled' : ''}">
        <div class="sd-icon-search">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
        </div>
        <input type="text" class="sd-input form-control" 
               placeholder="${this.options.disabled ? this.options.disabledPlaceholder : this.options.placeholder}" 
               autocomplete="off" 
               spellcheck="false"
               ${this.options.disabled ? 'disabled' : ''}>
        <div class="sd-spinner" style="display:none;"></div>
        <button type="button" class="sd-clear-btn" title="Clear selection" style="display:none;">&times;</button>
        <div class="sd-chevron">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </div>
      </div>
      <div class="sd-menu" style="display:none;" role="listbox">
        <div class="sd-menu-content"></div>
      </div>
    `;

    this.controlEl = this.container.querySelector('.sd-control');
    this.inputEl = this.container.querySelector('.sd-input');
    this.menuEl = this.container.querySelector('.sd-menu');
    this.menuContentEl = this.container.querySelector('.sd-menu-content');
    this.clearBtn = this.container.querySelector('.sd-clear-btn');
    this.spinnerEl = this.container.querySelector('.sd-spinner');

    this.bindEvents();

    if (this.options.initialValue) {
      this.setValue(this.options.initialValue);
    }
  }

  bindEvents() {
    this.inputEl.addEventListener('focus', () => {
      if (!this.options.disabled) this.open();
    });

    this.inputEl.addEventListener('click', () => {
      if (!this.options.disabled && !this.isOpen) this.open();
    });

    this.inputEl.addEventListener('input', (e) => {
      const q = e.target.value.trim();
      if (this.selectedItem && q !== this.selectedItem.name) {
        this.selectedItem = null;
        this.updateClearBtn();
      }
      this.clearBtn.style.display = q.length > 0 ? 'flex' : 'none';

      clearTimeout(this.debounceTimer);
      this.debounceTimer = setTimeout(() => {
        this.filterAndRender(q);
      }, this.options.searchDebounceMs);
    });

    this.inputEl.addEventListener('keydown', (e) => {
      if (this.options.disabled) return;

      if (!this.isOpen && (e.key === 'ArrowDown' || e.key === 'Enter')) {
        e.preventDefault();
        this.open();
        return;
      }

      if (!this.isOpen) return;

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          this.moveActive(1);
          break;
        case 'ArrowUp':
          e.preventDefault();
          this.moveActive(-1);
          break;
        case 'Enter':
          e.preventDefault();
          if (this.activeIndex >= 0 && this.activeIndex < this.filteredItems.length) {
            this.selectItem(this.filteredItems[this.activeIndex]);
          } else if (this.options.allowCustom && this.inputEl.value.trim().length > 0) {
            const customVal = this.inputEl.value.trim();
            this.selectItem({
              id: 'OTHER',
              name: customVal,
              isCustom: true,
              badge: 'Custom Locality',
              tier: 'UNCLASSIFIED'
            });
          }
          break;
        case 'Escape':
          e.preventDefault();
          this.close();
          break;
        case 'Tab':
          this.close();
          break;
      }
    });

    this.clearBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      this.clear();
      this.inputEl.focus();
    });

    document.addEventListener('click', (e) => {
      if (!this.container.contains(e.target)) {
        this.close();
      }
    });
  }

  setDisabled(disabled, placeholder = null) {
    this.options.disabled = disabled;
    if (disabled) {
      this.controlEl.classList.add('is-disabled');
      this.inputEl.disabled = true;
      this.inputEl.placeholder = placeholder || this.options.disabledPlaceholder;
      this.clear();
      this.close();
    } else {
      this.controlEl.classList.remove('is-disabled');
      this.inputEl.disabled = false;
      this.inputEl.placeholder = placeholder || this.options.placeholder;
    }
  }

  setItems(items) {
    this.items = items ? [...items] : [];
    if (this.isOpen) {
      this.filterAndRender(this.inputEl.value.trim());
    }
  }

  setLoading(isLoading) {
    this.isLoading = isLoading;
    if (isLoading) {
      this.spinnerEl.style.display = 'block';
      this.clearBtn.style.display = 'none';
    } else {
      this.spinnerEl.style.display = 'none';
      this.updateClearBtn();
    }
  }

  async filterAndRender(query = '') {
    const cleanQ = (query || '').toLowerCase().trim();

    if (this.options.fetchItems && typeof this.options.fetchItems === 'function') {
      this.setLoading(true);
      try {
        const fetched = await this.options.fetchItems(cleanQ);
        this.items = fetched || [];
      } catch (err) {
        console.error('[SearchableDropdown] fetch error:', err);
      } finally {
        this.setLoading(false);
      }
    }

    if (!cleanQ) {
      this.filteredItems = [...this.items];
    } else {
      this.filteredItems = this.items.filter(item => {
        const nameMatch = (item.name || '').toLowerCase().includes(cleanQ);
        const subMatch = (item.subtext || item.district_name || '').toLowerCase().includes(cleanQ);
        const codeMatch = (item.code || '').toLowerCase().includes(cleanQ);
        return nameMatch || subMatch || codeMatch;
      });
    }

    this.activeIndex = this.filteredItems.length > 0 ? 0 : -1;
    this.renderMenu(cleanQ);
  }

  renderMenu(query = '') {
    if (this.filteredItems.length === 0) {
      if (this.options.allowCustom && query.length > 0) {
        const customPrompt = this.options.customPrompt.replace('{query}', this.escapeHtml(query));
        this.menuContentEl.innerHTML = `
          <div class="sd-empty-state">
            <div style="margin-bottom:8px;color:var(--text-muted);font-size:12px;">${this.options.noResultsText}</div>
            <div class="sd-item sd-custom-action" data-custom="true" role="option">
              <span class="sd-custom-icon">＋</span>
              <div>
                <div style="font-weight:700;color:var(--text-primary);font-size:13px;">${customPrompt}</div>
                <div style="font-size:11px;color:var(--text-muted);">Unverified locality — submitted as manual location request</div>
              </div>
            </div>
          </div>
        `;
        const customEl = this.menuContentEl.querySelector('[data-custom="true"]');
        if (customEl) {
          customEl.addEventListener('click', () => {
            this.selectItem({
              id: 'CUSTOM_REQUEST',
              name: query,
              isCustom: true,
              badge: 'Unverified Locality (Manual Request)',
              subtext: 'Unverified locality — submitted as manual location request',
              settlement_type: 'Unverified Manual Request',
              tier: 'UNCLASSIFIED'
            });
          });
        }
      } else {
        this.menuContentEl.innerHTML = `
          <div class="sd-empty-state">
            <span style="font-size:12px;color:var(--text-muted);">${this.options.noResultsText}</span>
          </div>
        `;
      }
      return;
    }

    const hasGroups = this.filteredItems.some(i => i.group);
    let html = '';

    if (hasGroups) {
      const grouped = {};
      this.filteredItems.forEach(item => {
        const grp = item.group || 'Other';
        if (!grouped[grp]) grouped[grp] = [];
        grouped[grp].push(item);
      });

      let overallIdx = 0;
      for (const [groupName, grpItems] of Object.entries(grouped)) {
        html += `<div class="sd-group-header">${this.escapeHtml(groupName)} (${grpItems.length})</div>`;
        grpItems.forEach(item => {
          html += this.renderItemHtml(item, overallIdx, query);
          overallIdx++;
        });
      }
    } else {
      this.filteredItems.forEach((item, idx) => {
        html += this.renderItemHtml(item, idx, query);
      });
    }

    if (this.options.allowCustom && query.length > 0) {
      html += `
        <div class="sd-divider"></div>
        <div class="sd-item sd-custom-action" data-custom="true" role="option">
          <span class="sd-custom-icon">＋</span>
          <div>
            <div style="font-size:12px;font-weight:700;color:var(--text-primary);">Submit manual location request for "${this.escapeHtml(query)}"</div>
            <div style="font-size:11px;color:var(--text-muted);">Unverified locality (Villages excluded from official directory)</div>
          </div>
        </div>
      `;
    }

    this.menuContentEl.innerHTML = html;

    const itemEls = this.menuContentEl.querySelectorAll('.sd-item:not([data-custom="true"])');
    itemEls.forEach((el, index) => {
      el.addEventListener('click', () => {
        this.selectItem(this.filteredItems[index]);
      });
      el.addEventListener('mouseenter', () => {
        this.setActiveIndex(index);
      });
    });

    const customEl = this.menuContentEl.querySelector('[data-custom="true"]');
    if (customEl) {
      customEl.addEventListener('click', () => {
        this.selectItem({
          id: 'CUSTOM_REQUEST',
          name: query,
          isCustom: true,
          badge: 'Unverified Locality (Manual Request)',
          subtext: 'Unverified locality — submitted as manual location request',
          settlement_type: 'Unverified Manual Request',
          tier: 'UNCLASSIFIED'
        });
      });
    }
  }

  renderItemHtml(item, index, query) {
    const isSelected = this.selectedItem && this.selectedItem.id === item.id;
    const isActive = index === this.activeIndex;
    const nameHighlighted = this.highlightMatch(item.name, query);

    let badgeHtml = '';
    if (item.badge) {
      let badgeClass = 'sd-badge-neutral';
      const b = (item.badge || '').toLowerCase();
      if (b.includes('municipal corporation') || b.includes('mcorp')) badgeClass = 'sd-badge-mcorp';
      else if (b.includes('cantonment')) badgeClass = 'sd-badge-cantt';
      else if (b.includes('census town')) badgeClass = 'sd-badge-ct';
      else if (b.includes('municipality') || b.includes('urban')) badgeClass = 'sd-badge-urban';
      else if (b.includes('nagar panchayat') || b.includes('town')) badgeClass = 'sd-badge-town';
      else if (b.includes('state')) badgeClass = 'sd-badge-state';
      else if (b.includes('union') || b.includes('ut')) badgeClass = 'sd-badge-ut';
      else if (b.includes('unverified') || b.includes('custom') || b.includes('manual')) badgeClass = 'sd-badge-unverified';
      else if (b.includes('metro')) badgeClass = 'sd-badge-metro';
      badgeHtml = `<span class="sd-badge ${badgeClass}">${this.escapeHtml(item.badge)}</span>`;
    }

    let subtextHtml = '';
    if (item.subtext || item.display_label) {
      subtextHtml = `<span class="sd-item-subtext">${this.escapeHtml(item.subtext || item.display_label)}</span>`;
    }

    return `
      <div class="sd-item ${isSelected ? 'is-selected' : ''} ${isActive ? 'is-active' : ''}" 
           data-index="${index}" 
           role="option" 
           aria-selected="${isSelected}">
        <div class="sd-item-main">
          <div class="sd-item-title-row">
            <span class="sd-item-name">${nameHighlighted}</span>
            ${badgeHtml}
          </div>
          ${subtextHtml}
        </div>
        ${isSelected ? '<span class="sd-check-icon">✓</span>' : ''}
      </div>
    `;
  }

  highlightMatch(text, query) {
    if (!query) return this.escapeHtml(text);
    const escapedText = this.escapeHtml(text);
    const cleanQ = this.escapeRegex(query);
    const regex = new RegExp(`(${cleanQ})`, 'gi');
    return escapedText.replace(regex, '<mark class="sd-mark">$1</mark>');
  }

  moveActive(direction) {
    if (this.filteredItems.length === 0) return;
    let next = this.activeIndex + direction;
    if (next < 0) next = this.filteredItems.length - 1;
    if (next >= this.filteredItems.length) next = 0;
    this.setActiveIndex(next);
  }

  setActiveIndex(index) {
    this.activeIndex = index;
    const items = this.menuContentEl.querySelectorAll('.sd-item:not([data-custom="true"])');
    items.forEach((el, idx) => {
      el.classList.toggle('is-active', idx === index);
      if (idx === index) {
        el.scrollIntoView({ block: 'nearest' });
      }
    });
  }

  selectItem(item) {
    this.selectedItem = item;
    this.inputEl.value = item.name;
    this.controlEl.classList.add('has-value');
    this.updateClearBtn();
    this.close();

    if (this.options.onSelect) {
      this.options.onSelect(item);
    }
  }

  setValue(val) {
    if (!val) {
      this.clear();
      return;
    }

    if (typeof val === 'object') {
      this.selectedItem = val;
      this.inputEl.value = val.name || '';
      this.controlEl.classList.add('has-value');
      this.updateClearBtn();
      if (this.options.onSelect) this.options.onSelect(val);
    } else {
      const found = this.items.find(i => i.id === val || i.name === val);
      if (found) {
        this.selectItem(found);
      } else {
        this.inputEl.value = val;
        this.selectedItem = { id: val, name: val };
        this.controlEl.classList.add('has-value');
        this.updateClearBtn();
        if (this.options.onSelect) this.options.onSelect(this.selectedItem);
      }
    }
  }

  getValue() {
    return this.selectedItem;
  }

  clear() {
    this.selectedItem = null;
    this.inputEl.value = '';
    this.controlEl.classList.remove('has-value');
    this.updateClearBtn();
    if (this.isOpen) {
      this.filterAndRender('');
    }
    if (this.options.onClear) {
      this.options.onClear();
    }
  }

  updateClearBtn() {
    this.clearBtn.style.display = (this.inputEl.value.trim().length > 0 && !this.options.disabled) ? 'flex' : 'none';
  }

  open() {
    if (this.isOpen || this.options.disabled) return;
    this.isOpen = true;
    this.menuEl.style.display = 'block';
    this.controlEl.classList.add('is-open');
    this.filterAndRender(this.inputEl.value.trim());
  }

  close() {
    if (!this.isOpen) return;
    this.isOpen = false;
    this.menuEl.style.display = 'none';
    this.controlEl.classList.remove('is-open');

    if (this.selectedItem) {
      this.inputEl.value = this.selectedItem.name;
    } else {
      this.inputEl.value = '';
      this.updateClearBtn();
    }
  }

  escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
}

class IndiaLocationCoordinator {
  constructor(config = {}) {
    this.config = Object.assign({
      countrySelector: '#s2-country',
      stateSelector: '#s2-state-wrap',
      districtSelector: '#s2-district-wrap',
      citySelector: '#s2-city-wrap',
      pincodeInput: '#s2-pincode',
      pincodeFeedback: '#pincode-feedback',
      tierPill: '#tier-pill',
      tierLabel: '#tier-name-label',
      hiddenInputs: {
        stateId: 'input[name="state_id"]',
        stateName: 'input[name="state_name"]',
        districtId: 'input[name="district_id"]',
        districtName: 'input[name="district_name"]',
        cityId: 'input[name="city_id"]',
        cityName: 'input[name="city_name"]',
        settlementType: 'input[name="settlement_type"]',
        isCustomCity: 'input[name="is_custom_city"]',
        locationTier: 'input[name="location_tier"]'
      },
      initialStateId: null,
      initialDistrictId: null,
      initialCityId: null,
      initialCityName: null,
      initialCountry: 'India',
      onChange: null
    }, config);

    this.stateDropdown = null;
    this.districtDropdown = null;
    this.cityDropdown = null;
    this.currentCountry = this.config.initialCountry || 'India';
    this.currentStateId = this.config.initialStateId;
    this.currentDistrictId = this.config.initialDistrictId;
    this.currentCityItem = null;

    this.init();
  }

  async init() {
    await this.setupStateDropdown();
    this.setupDistrictDropdown();
    this.setupCityDropdown();
    this.setupCountryListener();
    this.setupPincodeListener();

    if (this.config.initialStateId) {
      await this.hydrateInitialSelection();
    }
  }

  setupCountryListener() {
    const countryEl = document.querySelector(this.config.countrySelector);
    if (!countryEl) return;

    countryEl.addEventListener('change', (e) => {
      this.currentCountry = e.target.value;
      const isIndia = this.currentCountry === 'India';

      if (!isIndia) {
        if (this.stateDropdown) this.stateDropdown.setDisabled(true, 'Not applicable for ' + this.currentCountry);
        if (this.districtDropdown) this.districtDropdown.setDisabled(true, 'Not applicable for ' + this.currentCountry);
        if (this.cityDropdown) {
          this.cityDropdown.setDisabled(false, 'Enter city / locality name');
          this.cityDropdown.options.allowCustom = true;
        }
        this.updateTierBadge('UNCLASSIFIED');
      } else {
        if (this.stateDropdown) this.stateDropdown.setDisabled(false, 'Search State or Union Territory...');
        if (this.districtDropdown) this.districtDropdown.setDisabled(!this.currentStateId, 'Select State first...');
        if (this.cityDropdown) this.cityDropdown.setDisabled(!this.currentDistrictId, 'Select District first...');
      }

      this.updateHiddenFields();
      this.notifyChange();
    });
  }

  async setupStateDropdown() {
    const wrap = document.querySelector(this.config.stateSelector);
    if (!wrap) return;

    let states = [];
    try {
      const res = await fetch('/api/locations/states');
      const data = await res.json();
      if (data.success) {
        states = data.states.map(s => ({
          id: s.id,
          name: s.name,
          code: s.code,
          group: s.type === 'State' ? 'States (28)' : 'Union Territories (8)',
          badge: s.type,
          type: s.type
        }));
      }
    } catch (e) {
      console.error('[LocationCoordinator] Failed to fetch states:', e);
    }

    this.stateDropdown = new SearchableDropdown(wrap, {
      placeholder: 'Search State or Union Territory...',
      items: states,
      onSelect: (state) => {
        this.currentStateId = state.id;
        this.onStateChanged(state.id);
      },
      onClear: () => {
        this.currentStateId = null;
        this.onStateChanged(null);
      }
    });
  }

  setupDistrictDropdown() {
    const wrap = document.querySelector(this.config.districtSelector);
    if (!wrap) return;

    this.districtDropdown = new SearchableDropdown(wrap, {
      placeholder: 'Search District...',
      disabledPlaceholder: 'Select State / UT first...',
      disabled: !this.currentStateId,
      items: [],
      onSelect: (district) => {
        this.currentDistrictId = district.id;
        this.onDistrictChanged(district.id);
      },
      onClear: () => {
        this.currentDistrictId = null;
        this.onDistrictChanged(null);
      }
    });
  }

  setupCityDropdown() {
    const wrap = document.querySelector(this.config.citySelector);
    if (!wrap) return;

    this.cityDropdown = new SearchableDropdown(wrap, {
      placeholder: 'Search City or Town (Villages excluded)...',
      disabledPlaceholder: 'Select District first...',
      disabled: !this.currentDistrictId,
      allowCustom: true,
      customPrompt: 'Submit manual location request for "{query}" (Unverified Locality)',
      noResultsText: 'No recognized city or town found in this district. Note: Villages are excluded from this directory.',
      items: [],
      onSelect: (city) => {
        this.currentCityItem = city;
        this.updateTierBadge(city.tier || 'UNCLASSIFIED');
        this.updateHiddenFields();
        this.notifyChange();
      },
      onClear: () => {
        this.currentCityItem = null;
        this.updateTierBadge('UNCLASSIFIED');
        this.updateHiddenFields();
        this.notifyChange();
      }
    });
  }

  async onStateChanged(stateId) {
    if (this.districtDropdown) {
      this.districtDropdown.clear();
      this.currentDistrictId = null;
    }
    if (this.cityDropdown) {
      this.cityDropdown.clear();
      this.currentCityItem = null;
      this.cityDropdown.setDisabled(true, 'Select District first...');
    }
    this.updateTierBadge('UNCLASSIFIED');

    if (!stateId) {
      if (this.districtDropdown) this.districtDropdown.setDisabled(true, 'Select State / UT first...');
      this.updateHiddenFields();
      this.notifyChange();
      return;
    }

    if (this.districtDropdown) {
      this.districtDropdown.setDisabled(false, 'Search District...');
      this.districtDropdown.setLoading(true);
      try {
        const res = await fetch(`/api/locations/districts?state_id=${encodeURIComponent(stateId)}`);
        const data = await res.json();
        if (data.success) {
          const formatted = data.districts.map(d => ({
            id: d.id,
            name: d.name,
            code: d.code,
            subtext: `${d.name} District`,
            badge: d.name.startsWith('Other') ? 'Custom' : 'District'
          }));
          this.districtDropdown.setItems(formatted);
        }
      } catch (e) {
        console.error('[LocationCoordinator] Failed to fetch districts:', e);
      } finally {
        this.districtDropdown.setLoading(false);
      }
    }

    this.updateHiddenFields();
    this.notifyChange();
  }

  async onDistrictChanged(districtId) {
    if (this.cityDropdown) {
      this.cityDropdown.clear();
      this.currentCityItem = null;
    }
    this.updateTierBadge('UNCLASSIFIED');

    if (!districtId) {
      if (this.cityDropdown) this.cityDropdown.setDisabled(true, 'Select District first...');
      this.updateHiddenFields();
      this.notifyChange();
      return;
    }

    if (this.cityDropdown && this.currentStateId) {
      this.cityDropdown.setDisabled(false, 'Search City or Town (Villages excluded)...');
      this.cityDropdown.setLoading(true);
      try {
        const res = await fetch(`/api/locations/cities?state_id=${encodeURIComponent(this.currentStateId)}&district_id=${encodeURIComponent(districtId)}&limit=150`);
        const data = await res.json();
        if (data.success) {
          const formatted = data.cities.map(c => ({
            id: c.id,
            name: c.name,
            district_id: c.district_id,
            district_name: c.district_name,
            state_id: c.state_id,
            tier: c.tier,
            settlement_type: c.settlement_type,
            official_code: c.official_code,
            badge: c.settlement_type || c.badge || c.tier,
            subtext: c.display_label || `${c.name} — ${c.district_name || 'District'}, ${c.state_name || ''}`,
            isCustom: false
          }));
          this.cityDropdown.setItems(formatted);
        }
      } catch (e) {
        console.error('[LocationCoordinator] Failed to fetch cities:', e);
      } finally {
        this.cityDropdown.setLoading(false);
      }
    }

    this.updateHiddenFields();
    this.notifyChange();
  }

  setupPincodeListener() {
    const pinEl = document.querySelector(this.config.pincodeInput);
    const feedbackEl = document.querySelector(this.config.pincodeFeedback);
    if (!pinEl) return;

    pinEl.addEventListener('input', async (e) => {
      const val = e.target.value.trim();
      if (val.length === 6) {
        const stateId = this.currentStateId || '';
        try {
          const res = await fetch(`/api/locations/validate-pincode?pincode=${encodeURIComponent(val)}&state_id=${encodeURIComponent(stateId)}`);
          const data = await res.json();
          if (feedbackEl) {
            if (data.valid && data.matches_state) {
              feedbackEl.innerHTML = `<span style="color:#16a34a;font-weight:700;">✓ Valid PIN (${data.clean_pincode})</span>`;
            } else if (data.valid && !data.matches_state) {
              feedbackEl.innerHTML = `<span style="color:#d97706;font-size:11px;">⚠️ ${data.warning || 'Postal circle does not match selected state.'}</span>`;
            } else {
              feedbackEl.innerHTML = `<span style="color:#ef4444;font-size:11px;">✗ ${data.error || 'Invalid 6-digit PIN code.'}</span>`;
            }
          }
        } catch (err) {}
      } else if (feedbackEl) {
        feedbackEl.innerHTML = '';
      }
    });
  }

  updateTierBadge(tier) {
    const pill = document.querySelector(this.config.tierPill);
    const label = document.querySelector(this.config.tierLabel);
    if (!pill || !label) return;

    if (tier === 'METRO') {
      pill.innerText = 'Metro Tier-1';
      pill.style.background = 'rgba(203,244,50,0.3)';
      pill.style.color = '#121614';
      label.innerText = 'Major Metropolitan Area (Higher Living Baseline)';
    } else if (tier === 'URBAN') {
      pill.innerText = 'Urban Tier-2';
      pill.style.background = 'rgba(56,189,248,0.2)';
      pill.style.color = '#0284c7';
      label.innerText = 'Urban Area (Balanced Living Costs)';
    } else if (tier === 'TOWN') {
      pill.innerText = 'Town Tier-3';
      pill.style.background = 'rgba(168,85,247,0.2)';
      pill.style.color = '#9333ea';
      label.innerText = 'Smaller City / District Headquarters';
    } else if (tier === 'RURAL') {
      pill.innerText = 'Rural / Semi-Urban';
      pill.style.background = 'rgba(34,197,94,0.2)';
      pill.style.color = '#15803d';
      label.innerText = 'Semi-Urban / Rural Locality';
    } else {
      pill.innerText = 'General Baseline';
      pill.style.background = 'rgba(156,163,175,0.2)';
      pill.style.color = 'var(--text-secondary)';
      label.innerText = 'Standard 50/30/20 Baseline';
    }
  }

  async hydrateInitialSelection() {
    if (this.stateDropdown && this.config.initialStateId) {
      this.stateDropdown.setValue(this.config.initialStateId);
      await this.onStateChanged(this.config.initialStateId);

      if (this.districtDropdown && this.config.initialDistrictId) {
        this.districtDropdown.setValue(this.config.initialDistrictId);
        await this.onDistrictChanged(this.config.initialDistrictId);

        if (this.cityDropdown) {
          if (this.config.initialCityId && this.config.initialCityId !== 'OTHER') {
            this.cityDropdown.setValue(this.config.initialCityId);
          } else if (this.config.initialCityName) {
            this.cityDropdown.setValue({
              id: 'OTHER',
              name: this.config.initialCityName,
              isCustom: true,
              badge: 'Custom Locality',
              tier: 'UNCLASSIFIED'
            });
          }
        }
      }
    }
    this.updateHiddenFields();
  }

  updateHiddenFields() {
    const data = this.getLocationData();
    const map = this.config.hiddenInputs || {};

    const setInput = (sel, val) => {
      if (!sel) return;
      const el = document.querySelector(sel);
      if (el) el.value = (val !== null && val !== undefined) ? val : '';
    };

    setInput(map.stateId, data.state_id);
    setInput(map.stateName, data.state_name);
    setInput(map.districtId, data.district_id);
    setInput(map.districtName, data.district_name);
    setInput(map.cityId, data.city_id);
    setInput(map.cityName, data.city_name);
    setInput(map.settlementType, data.settlement_type);
    setInput(map.isCustomCity, data.is_custom_city ? 'true' : 'false');
    setInput(map.locationTier, data.location_tier);
  }

  getLocationData() {
    const state = this.stateDropdown ? this.stateDropdown.getValue() : null;
    const district = this.districtDropdown ? this.districtDropdown.getValue() : null;
    const city = this.cityDropdown ? this.cityDropdown.getValue() : null;
    const pinEl = document.querySelector(this.config.pincodeInput);

    return {
      country: this.currentCountry,
      state_id: state ? state.id : null,
      state_name: state ? state.name : null,
      district_id: district ? district.id : null,
      district_name: district ? district.name : null,
      city_id: city ? (city.isCustom ? 'CUSTOM_REQUEST' : city.id) : null,
      city_name: city ? city.name : null,
      is_custom_city: city ? Boolean(city.isCustom) : false,
      settlement_type: city ? (city.settlement_type || (city.isCustom ? 'Unverified Manual Request' : null)) : null,
      official_code: city ? (city.official_code || null) : null,
      location_tier: city ? (city.tier || 'UNCLASSIFIED') : 'UNCLASSIFIED',
      pincode: pinEl ? pinEl.value.trim() : null
    };
  }

  notifyChange() {
    if (this.config.onChange) {
      this.config.onChange(this.getLocationData());
    }
  }
}

window.SearchableDropdown = SearchableDropdown;
window.IndiaLocationCoordinator = IndiaLocationCoordinator;
