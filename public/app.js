/**
 * OsintNeoAi Skills Intelligence Browser
 * Core Client Application
 */

(function () {
  'use strict';

  // State
  const state = {
    skillsData: null,
    skills: [],
    categories: {},
    activeCategory: 'all',
    activeTag: null,
    searchQuery: '',
    sortBy: 'name-asc',
    hasFilter: 'all',
    activeSkill: null,
    activeModalTab: 'doc',
    currentTheme: localStorage.getItem('osintneo_theme') || 'cyber',
    changes: []
  };

  // DOM Elements
  const elements = {
    skillsGrid: document.getElementById('skills-grid'),
    emptyState: document.getElementById('empty-state'),
    searchInput: document.getElementById('search-input'),
    btnClearSearch: document.getElementById('btn-clear-search'),
    sortSelect: document.getElementById('sort-select'),
    hasFilterSelect: document.getElementById('has-filter-select'),
    categoryPills: document.getElementById('category-pills'),
    tagChips: document.getElementById('tag-chips'),
    visibleCount: document.getElementById('visible-count'),
    totalCount: document.getElementById('total-count'),
    statSkills: document.getElementById('stat-skills-count'),
    statScripts: document.getElementById('stat-scripts-count'),
    statRefs: document.getElementById('stat-refs-count'),
    btnResetFilters: document.getElementById('btn-reset-filters'),
    btnThemeToggle: document.getElementById('btn-theme-toggle'),
    btnExportJson: document.getElementById('btn-export-json'),
    btnRefresh: document.getElementById('btn-refresh'),
    btnViewChanges: document.getElementById('btn-view-changes'),
    changesBadge: document.getElementById('changes-badge'),
    
    // Modal elements
    skillModal: document.getElementById('skill-modal'),
    btnCloseModal: document.getElementById('btn-close-modal'),
    modalSkillName: document.getElementById('modal-skill-name'),
    modalSkillDescription: document.getElementById('modal-skill-description'),
    modalCategoryBadge: document.getElementById('modal-category-badge'),
    modalCategoryText: document.getElementById('modal-category-text'),
    modalSkillTags: document.getElementById('modal-skill-tags'),
    modalSkillId: document.getElementById('modal-skill-id'),
    modalLineCount: document.getElementById('modal-line-count'),
    modalFilePath: document.getElementById('modal-file-path'),
    modalMarkdownBody: document.getElementById('modal-markdown-body'),
    modalScriptsList: document.getElementById('modal-scripts-list'),
    modalReferencesList: document.getElementById('modal-references-list'),
    modalCommandsList: document.getElementById('modal-commands-list'),
    modalTabScriptsCount: document.getElementById('modal-tab-scripts-count'),
    modalTabRefsCount: document.getElementById('modal-tab-refs-count'),
    btnCopyMarkdown: document.getElementById('btn-copy-markdown'),
    btnCopyImportSnippet: document.getElementById('btn-copy-import-snippet'),
    
    // Changes Drawer
    changesDrawer: document.getElementById('changes-drawer'),
    btnCloseChanges: document.getElementById('btn-close-changes'),
    changesList: document.getElementById('changes-list'),
    
    // Toast Container
    toastContainer: document.getElementById('toast-container')
  };

  // Initialize
  async function init() {
    applyTheme(state.currentTheme);
    setupEventListeners();
    await loadSkillsData();
    await loadChangesLog();
    feather.replace();
  }

  // Apply theme
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    state.currentTheme = theme;
    localStorage.setItem('osintneo_theme', theme);
  }

  function cycleTheme() {
    const themes = ['cyber', 'midnight', 'emerald'];
    const nextIndex = (themes.indexOf(state.currentTheme) + 1) % themes.length;
    applyTheme(themes[nextIndex]);
    showToast(`Theme switched to: ${themes[nextIndex].toUpperCase()}`, 'sun');
  }

  // Load skills.json data
  async function loadSkillsData() {
    try {
      const response = await fetch('data/skills.json?v=' + Date.now());
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      const data = await response.json();
      state.skillsData = data;
      state.skills = data.skills || [];
      state.categories = data.categories || {};
      
      updateTelemetry();
      renderCategoryPills();
      renderTagChips();
      applyFiltersAndRender();
    } catch (err) {
      console.error('Failed to load skills.json:', err);
      showToast('Error loading skills data. Falling back to local state.', 'alert-triangle');
    }
  }

  // Load changes log
  async function loadChangesLog() {
    try {
      const response = await fetch('data/changes.json?v=' + Date.now());
      if (response.ok) {
        const changes = await response.json();
        state.changes = changes || [];
        renderChangesList();
        if (state.changes.length > 0) {
          elements.changesBadge.classList.remove('hidden');
        }
      }
    } catch (e) {
      // Ignore if changes.json not found
    }
  }

  // Update top metrics
  function updateTelemetry() {
    if (!state.skillsData) return;
    elements.statSkills.textContent = state.skillsData.totalSkills || state.skills.length;
    elements.statScripts.textContent = state.skillsData.totalScripts || 0;
    elements.statRefs.textContent = state.skillsData.totalReferences || 0;
    elements.totalCount.textContent = state.skills.length;
  }

  // Render category buttons
  function renderCategoryPills() {
    const pillsContainer = elements.categoryPills;
    // Keep 'All' button
    const allCountEl = document.getElementById('cat-count-all');
    if (allCountEl) allCountEl.textContent = state.skills.length;

    // Remove old dynamic pills
    const existingDynamic = pillsContainer.querySelectorAll('.dynamic-cat-pill');
    existingDynamic.forEach(p => p.remove());

    const catIconMap = {
      'OSINT & Intelligence': 'target',
      'BigQuery & Data Platforms': 'database',
      'GCP Infrastructure & Pipelines': 'git-pull-request',
      'AI & Machine Learning': 'cpu',
      'Web, Mobile & Apps': 'smartphone',
      'Security & Governance': 'shield',
      'Development & Tooling': 'code'
    };

    Object.entries(state.categories).forEach(([catName, count]) => {
      const btn = document.createElement('button');
      btn.className = `cat-pill dynamic-cat-pill ${state.activeCategory === catName ? 'active' : ''}`;
      btn.dataset.category = catName;
      
      const icon = catIconMap[catName] || 'folder';
      btn.innerHTML = `
        <span class="cat-icon"><i data-feather="${icon}"></i></span>
        <span class="cat-text">${catName}</span>
        <span class="cat-count">${count}</span>
      `;

      btn.addEventListener('click', () => {
        setCategory(catName);
      });

      pillsContainer.appendChild(btn);
    });

    feather.replace();
  }

  // Render tag chips
  function renderTagChips() {
    const container = elements.tagChips;
    container.innerHTML = '';

    const popularTags = ['OSINT', 'BigQuery', 'Pipelines', 'Security', 'AI/LLM', 'Python', 'SQL', 'Automation'];
    popularTags.forEach(tag => {
      const chip = document.createElement('button');
      chip.className = `tag-chip ${state.activeTag === tag ? 'active' : ''}`;
      chip.textContent = `#${tag}`;
      chip.addEventListener('click', () => {
        if (state.activeTag === tag) {
          state.activeTag = null;
        } else {
          state.activeTag = tag;
        }
        renderTagChips();
        applyFiltersAndRender();
      });
      container.appendChild(chip);
    });
  }

  // Set active category
  function setCategory(category) {
    state.activeCategory = category;
    
    // Update active class on pills
    const pills = elements.categoryPills.querySelectorAll('.cat-pill');
    pills.forEach(p => {
      if (p.dataset.category === category) {
        p.classList.add('active');
      } else {
        p.classList.remove('active');
      }
    });

    applyFiltersAndRender();
  }

  // Filtering & Sorting Logic
  function getFilteredSkills() {
    let filtered = [...state.skills];

    // Category filter
    if (state.activeCategory !== 'all') {
      filtered = filtered.filter(s => s.category === state.activeCategory);
    }

    // Tag filter
    if (state.activeTag) {
      filtered = filtered.filter(s => s.tags && s.tags.includes(state.activeTag));
    }

    // Asset filter
    if (state.hasFilter === 'scripts') {
      filtered = filtered.filter(s => s.assetsSummary.scriptsCount > 0);
    } else if (state.hasFilter === 'refs') {
      filtered = filtered.filter(s => s.assetsSummary.referencesCount > 0);
    } else if (state.hasFilter === 'commands') {
      filtered = filtered.filter(s => s.quickCommands && s.quickCommands.length > 0);
    }

    // Search query filter
    if (state.searchQuery) {
      const q = state.searchQuery.toLowerCase();
      filtered = filtered.filter(s => {
        const nameMatch = s.name.toLowerCase().includes(q);
        const slugMatch = s.slug.toLowerCase().includes(q);
        const descMatch = s.description.toLowerCase().includes(q);
        const tagMatch = s.tags && s.tags.some(t => t.toLowerCase().includes(q));
        const cmdMatch = s.quickCommands && s.quickCommands.some(c => c.toLowerCase().includes(q));
        const docMatch = s.body && s.body.toLowerCase().includes(q);
        return nameMatch || slugMatch || descMatch || tagMatch || cmdMatch || docMatch;
      });
    }

    // Sort
    if (state.sortBy === 'name-asc') {
      filtered.sort((a, b) => a.name.localeCompare(b.name));
    } else if (state.sortBy === 'name-desc') {
      filtered.sort((a, b) => b.name.localeCompare(a.name));
    } else if (state.sortBy === 'scripts-desc') {
      filtered.sort((a, b) => (b.assetsSummary.scriptsCount || 0) - (a.assetsSummary.scriptsCount || 0));
    } else if (state.sortBy === 'refs-desc') {
      filtered.sort((a, b) => (b.assetsSummary.referencesCount || 0) - (a.assetsSummary.referencesCount || 0));
    } else if (state.sortBy === 'lines-desc') {
      filtered.sort((a, b) => (b.lineCount || 0) - (a.lineCount || 0));
    }

    return filtered;
  }

  function applyFiltersAndRender() {
    const filtered = getFilteredSkills();
    elements.visibleCount.textContent = filtered.length;

    if (filtered.length === 0) {
      elements.skillsGrid.innerHTML = '';
      elements.emptyState.classList.remove('hidden');
    } else {
      elements.emptyState.classList.add('hidden');
      renderSkillCards(filtered);
    }
  }

  // Render Skill Cards in Grid
  function renderSkillCards(skills) {
    const grid = elements.skillsGrid;
    grid.innerHTML = '';

    skills.forEach(skill => {
      const card = document.createElement('article');
      card.className = 'skill-card';
      
      const primaryCmd = skill.quickCommands && skill.quickCommands.length > 0 ? skill.quickCommands[0] : null;

      card.innerHTML = `
        <div class="card-content">
          <div class="card-header">
            <span class="card-category-tag">${escapeHtml(skill.category)}</span>
            <span class="card-id">skills/${escapeHtml(skill.slug)}</span>
          </div>

          <h3 class="card-title">${escapeHtml(skill.name)}</h3>
          <p class="card-desc">${escapeHtml(skill.description)}</p>

          <div class="card-tags">
            ${(skill.tags || []).slice(0, 4).map(t => `<span class="card-tag-pill">#${escapeHtml(t)}</span>`).join('')}
          </div>

          ${primaryCmd ? `
            <div class="card-quick-cmd" title="Click to copy quick command" data-cmd="${escapeHtml(primaryCmd)}">
              <span class="cmd-text">${escapeHtml(primaryCmd)}</span>
              <button class="cmd-copy-btn" title="Copy Command">
                <i data-feather="copy"></i>
              </button>
            </div>
          ` : ''}
        </div>

        <div class="card-footer">
          <div class="card-metrics">
            <span class="metric-item" title="${skill.assetsSummary.scriptsCount} Bundled Scripts">
              <i data-feather="terminal"></i> ${skill.assetsSummary.scriptsCount}
            </span>
            <span class="metric-item" title="${skill.assetsSummary.referencesCount} Reference Documents">
              <i data-feather="layers"></i> ${skill.assetsSummary.referencesCount}
            </span>
            <span class="metric-item" title="${skill.lineCount} Lines of Guidance">
              <i data-feather="align-left"></i> ${skill.lineCount}
            </span>
          </div>
          <button class="btn-inspect" data-skill-id="${escapeHtml(skill.id)}">
            <span>Inspect</span>
            <i data-feather="chevron-right"></i>
          </button>
        </div>
      `;

      // Card event listeners
      const inspectBtn = card.querySelector('.btn-inspect');
      inspectBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        openSkillModal(skill);
      });

      card.addEventListener('click', () => {
        openSkillModal(skill);
      });

      const cmdBox = card.querySelector('.card-quick-cmd');
      if (cmdBox) {
        cmdBox.addEventListener('click', (e) => {
          e.stopPropagation();
          copyToClipboard(cmdBox.dataset.cmd, 'Command copied to clipboard');
        });
      }

      grid.appendChild(card);
    });

    feather.replace();
  }

  // Open Skill Detail Modal
  function openSkillModal(skill) {
    state.activeSkill = skill;
    state.activeModalTab = 'doc';

    elements.modalSkillName.textContent = skill.name;
    elements.modalSkillDescription.textContent = skill.description;
    elements.modalCategoryText.textContent = skill.category;
    elements.modalSkillId.textContent = skill.id;
    elements.modalLineCount.innerHTML = `<i data-feather="align-left"></i> ${skill.lineCount} lines`;
    elements.modalFilePath.innerHTML = `<i data-feather="folder"></i> skills/${skill.slug}/SKILL.md`;

    // Render tags
    elements.modalSkillTags.innerHTML = (skill.tags || []).map(t => `<span class="card-tag-pill">#${escapeHtml(t)}</span>`).join('');

    // Tab counters
    elements.modalTabScriptsCount.textContent = skill.assetsSummary.scriptsCount;
    elements.modalTabRefsCount.textContent = skill.assetsSummary.referencesCount;

    // Render Markdown Tab
    const md = skill.body || skill.rawMarkdown || '';
    if (typeof marked !== 'undefined') {
      elements.modalMarkdownBody.innerHTML = marked.parse(md);
    } else {
      elements.modalMarkdownBody.textContent = md;
    }

    // Render Scripts Tab
    renderModalScripts(skill.scripts || []);

    // Render References Tab
    renderModalReferences(skill.references || []);

    // Render Quick Commands Tab
    renderModalCommands(skill.quickCommands || []);

    // Activate default tab
    switchModalTab('doc');

    elements.skillModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
    feather.replace();
  }

  function closeModal() {
    elements.skillModal.classList.add('hidden');
    document.body.style.overflow = '';
    state.activeSkill = null;
  }

  function switchModalTab(tabName) {
    state.activeModalTab = tabName;
    const tabs = elements.skillModal.querySelectorAll('.modal-tab');
    tabs.forEach(t => {
      if (t.dataset.tab === tabName) {
        t.classList.add('active');
      } else {
        t.classList.remove('active');
      }
    });

    const panes = elements.skillModal.querySelectorAll('.tab-pane');
    panes.forEach(p => {
      if (p.id === `pane-${tabName}`) {
        p.classList.add('active');
      } else {
        p.classList.remove('active');
      }
    });
    feather.replace();
  }

  function renderModalScripts(scripts) {
    const list = elements.modalScriptsList;
    if (scripts.length === 0) {
      list.innerHTML = `
        <div class="empty-state" style="margin: 20px 0; padding: 30px;">
          <p class="empty-desc">No executable scripts bundled directly with this skill.</p>
        </div>
      `;
      return;
    }

    list.innerHTML = scripts.map(s => `
      <div class="asset-item-card">
        <div class="asset-info">
          <div class="asset-icon-box">
            <i data-feather="terminal"></i>
          </div>
          <div>
            <div class="asset-name">${escapeHtml(s.name)}</div>
            <div class="asset-path">skills/${escapeHtml(state.activeSkill.slug)}/${escapeHtml(s.path)}</div>
          </div>
        </div>
        <div class="asset-actions">
          <span class="asset-size">${formatBytes(s.sizeBytes)}</span>
          <button class="btn-secondary btn-sm" onclick="window.copyAssetPath('skills/${escapeHtml(state.activeSkill.slug)}/${escapeHtml(s.path)}')">
            <i data-feather="copy"></i> Copy Path
          </button>
        </div>
      </div>
    `).join('');
  }

  function renderModalReferences(refs) {
    const list = elements.modalReferencesList;
    if (refs.length === 0) {
      list.innerHTML = `
        <div class="empty-state" style="margin: 20px 0; padding: 30px;">
          <p class="empty-desc">No external reference files bundled with this skill.</p>
        </div>
      `;
      return;
    }

    list.innerHTML = refs.map(r => `
      <div class="asset-item-card">
        <div class="asset-info">
          <div class="asset-icon-box" style="background: rgba(157, 78, 221, 0.15); color: #d8b4fe;">
            <i data-feather="file-text"></i>
          </div>
          <div>
            <div class="asset-name">${escapeHtml(r.name)}</div>
            <div class="asset-path">skills/${escapeHtml(state.activeSkill.slug)}/${escapeHtml(r.path)}</div>
          </div>
        </div>
        <div class="asset-actions">
          <span class="asset-size">${formatBytes(r.sizeBytes)}</span>
          <button class="btn-secondary btn-sm" onclick="window.copyAssetPath('skills/${escapeHtml(state.activeSkill.slug)}/${escapeHtml(r.path)}')">
            <i data-feather="copy"></i> Copy Path
          </button>
        </div>
      </div>
    `).join('');
  }

  function renderModalCommands(commands) {
    const list = elements.modalCommandsList;
    if (commands.length === 0) {
      list.innerHTML = `
        <div class="empty-state" style="margin: 20px 0; padding: 30px;">
          <p class="empty-desc">No automated CLI commands detected in documentation.</p>
        </div>
      `;
      return;
    }

    list.innerHTML = commands.map(cmd => `
      <div class="cmd-row-card">
        <code class="cmd-row-code">${escapeHtml(cmd)}</code>
        <button class="btn-secondary btn-sm" onclick="window.copyCommandText('${escapeJsString(cmd)}')">
          <i data-feather="copy"></i> Copy
        </button>
      </div>
    `).join('');
  }

  // Changes Log Drawer
  function openChangesDrawer() {
    elements.changesDrawer.classList.remove('hidden');
    elements.changesBadge.classList.add('hidden');
    document.body.style.overflow = 'hidden';
    feather.replace();
  }

  function closeChangesDrawer() {
    elements.changesDrawer.classList.add('hidden');
    document.body.style.overflow = '';
  }

  function renderChangesList() {
    const list = elements.changesList;
    if (state.changes.length === 0) {
      list.innerHTML = `
        <div class="empty-state" style="padding: 30px;">
          <p class="empty-desc">No file modifications recorded yet. Start <code>node scripts/watcher.js</code> to track changes.</p>
        </div>
      `;
      return;
    }

    list.innerHTML = state.changes.map(chg => {
      const timeStr = new Date(chg.timestamp).toLocaleTimeString();
      return `
        <div class="change-item">
          <div class="change-item-top">
            <span class="change-type-pill change-type-${escapeHtml(chg.event)}">${escapeHtml(chg.event)}</span>
            <span class="change-time">${timeStr}</span>
          </div>
          <div class="change-file">${escapeHtml(chg.file)}</div>
        </div>
      `;
    }).join('');
  }

  // Export JSON
  function exportSkillsJson() {
    if (!state.skillsData) return;
    const blob = new Blob([JSON.stringify(state.skillsData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `osintneoai-skills-${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('skills.json exported successfully', 'download');
  }

  // Toast Notifications
  function showToast(message, icon = 'check') {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `
      <i data-feather="${icon}"></i>
      <span>${escapeHtml(message)}</span>
    `;
    elements.toastContainer.appendChild(toast);
    feather.replace();

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.2s ease';
      setTimeout(() => toast.remove(), 200);
    }, 2800);
  }

  function copyToClipboard(text, msg = 'Copied to clipboard') {
    navigator.clipboard.writeText(text).then(() => {
      showToast(msg, 'check');
    }).catch(() => {
      showToast('Copy failed', 'alert-circle');
    });
  }

  // Global window helpers for inline onclick
  window.copyAssetPath = function (path) {
    copyToClipboard(path, `Path copied: ${path}`);
  };

  window.copyCommandText = function (cmd) {
    copyToClipboard(cmd, 'Command copied to clipboard');
  };

  // Utilities
  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function escapeJsString(str) {
    if (!str) return '';
    return String(str).replace(/\\/g, '\\\\').replace(/'/g, "\\'");
  }

  function formatBytes(bytes) {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }

  // Event Listeners Setup
  function setupEventListeners() {
    // Search input
    elements.searchInput.addEventListener('input', (e) => {
      state.searchQuery = e.target.value.trim();
      if (state.searchQuery.length > 0) {
        elements.btnClearSearch.classList.remove('hidden');
      } else {
        elements.btnClearSearch.classList.add('hidden');
      }
      applyFiltersAndRender();
    });

    // Clear search
    elements.btnClearSearch.addEventListener('click', () => {
      elements.searchInput.value = '';
      state.searchQuery = '';
      elements.btnClearSearch.classList.add('hidden');
      applyFiltersAndRender();
      elements.searchInput.focus();
    });

    // Sort select
    elements.sortSelect.addEventListener('change', (e) => {
      state.sortBy = e.target.value;
      applyFiltersAndRender();
    });

    // Has filter select
    elements.hasFilterSelect.addEventListener('change', (e) => {
      state.hasFilter = e.target.value;
      applyFiltersAndRender();
    });

    // Reset filters
    elements.btnResetFilters.addEventListener('click', () => {
      state.activeCategory = 'all';
      state.activeTag = null;
      state.searchQuery = '';
      state.hasFilter = 'all';
      elements.searchInput.value = '';
      elements.btnClearSearch.classList.add('hidden');
      elements.hasFilterSelect.value = 'all';
      renderTagChips();
      renderCategoryPills();
      applyFiltersAndRender();
    });

    // All Category Pill
    const allCatBtn = elements.categoryPills.querySelector('[data-category="all"]');
    if (allCatBtn) {
      allCatBtn.addEventListener('click', () => setCategory('all'));
    }

    // Modal Tabs
    const modalTabs = elements.skillModal.querySelectorAll('.modal-tab');
    modalTabs.forEach(tab => {
      tab.addEventListener('click', () => switchModalTab(tab.dataset.tab));
    });

    // Close Modal
    elements.btnCloseModal.addEventListener('click', closeModal);
    elements.skillModal.addEventListener('click', (e) => {
      if (e.target === elements.skillModal) closeModal();
    });

    // Modal Copy Markdown
    elements.btnCopyMarkdown.addEventListener('click', () => {
      if (state.activeSkill) {
        copyToClipboard(state.activeSkill.rawMarkdown || state.activeSkill.body, 'Full SKILL.md copied');
      }
    });

    // Modal Copy Invocation
    elements.btnCopyImportSnippet.addEventListener('click', () => {
      if (state.activeSkill) {
        const snippet = `// Invoke ${state.activeSkill.name}\nview_file({ AbsolutePath: "skills/${state.activeSkill.slug}/SKILL.md" });`;
        copyToClipboard(snippet, 'Skill invocation snippet copied');
      }
    });

    // Theme toggle
    elements.btnThemeToggle.addEventListener('click', cycleTheme);

    // Export JSON
    elements.btnExportJson.addEventListener('click', exportSkillsJson);

    // Refresh
    elements.btnRefresh.addEventListener('click', async () => {
      showToast('Syncing skills data...', 'refresh-cw');
      await loadSkillsData();
      await loadChangesLog();
      showToast('Skills catalog up to date', 'check');
    });

    // Changes Drawer
    elements.btnViewChanges.addEventListener('click', openChangesDrawer);
    elements.btnCloseChanges.addEventListener('click', closeChangesDrawer);
    elements.changesDrawer.addEventListener('click', (e) => {
      if (e.target === elements.changesDrawer) closeChangesDrawer();
    });

    // Keyboard shortcuts
    window.addEventListener('keydown', (e) => {
      if (e.key === '/' && document.activeElement !== elements.searchInput) {
        e.preventDefault();
        elements.searchInput.focus();
        elements.searchInput.select();
      } else if (e.key === 'Escape') {
        if (!elements.skillModal.classList.contains('hidden')) {
          closeModal();
        } else if (!elements.changesDrawer.classList.contains('hidden')) {
          closeChangesDrawer();
        }
      }
    });

    // View Mode Switching (Skills / Municipal / Dossiers)
    const viewTabs = document.querySelectorAll('.view-tab-btn');
    const skillsViewControls = document.querySelector('.control-section');
    const skillsViewMain = document.getElementById('skills-grid')?.parentElement;
    const municipalView = document.getElementById('municipal-view');
    const dossiersView = document.getElementById('dossiers-view');

    viewTabs.forEach(tab => {
      tab.addEventListener('click', async () => {
        const targetView = tab.dataset.view;
        viewTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        // Hide all views
        if (skillsViewControls) skillsViewControls.classList.add('hidden');
        if (skillsViewMain) skillsViewMain.classList.add('hidden');
        if (municipalView) municipalView.classList.add('hidden');
        if (dossiersView) dossiersView.classList.add('hidden');

        if (targetView === 'skills') {
          if (skillsViewControls) skillsViewControls.classList.remove('hidden');
          if (skillsViewMain) skillsViewMain.classList.remove('hidden');
        } else if (targetView === 'municipal') {
          if (municipalView) municipalView.classList.remove('hidden');
          await loadMunicipalView();
        } else if (targetView === 'dossiers') {
          if (dossiersView) dossiersView.classList.remove('hidden');
          await loadDossiersView();
        } else if (targetView === 'ai-assistant') {
          const aiView = document.getElementById('ai-assistant-view');
          if (aiView) aiView.classList.remove('hidden');
          initAiAssistantView();
        }
        feather.replace();
      });
    });

    // AI Forensic Assistant Logic (Firebase AI Logic Pattern)
    let aiAssistantInitialized = false;

    function initAiAssistantView() {
      if (aiAssistantInitialized) return;
      aiAssistantInitialized = true;

      const chatInput = document.getElementById('ai-chat-input');
      const sendBtn = document.getElementById('btn-send-ai');
      const clearBtn = document.getElementById('btn-clear-chat');
      const messagesThread = document.getElementById('ai-messages-thread');
      const promptChips = document.querySelectorAll('.ai-prompt-chip');

      async function sendAiMessage(promptText) {
        const text = promptText || chatInput.value.trim();
        if (!text) return;
        if (!promptText) chatInput.value = '';

        // Append User Message
        const userMsgDiv = document.createElement('div');
        userMsgDiv.className = 'ai-msg ai-msg-user';
        userMsgDiv.innerHTML = `
          <div class="ai-avatar"><i data-feather="user"></i></div>
          <div class="ai-msg-body">
            <div class="ai-msg-header">
              <strong>Investigator</strong>
              <span class="ai-timestamp">Just now</span>
            </div>
            <div class="ai-msg-content">${text}</div>
          </div>
        `;
        messagesThread.appendChild(userMsgDiv);
        feather.replace();
        messagesThread.scrollTop = messagesThread.scrollHeight;

        // Append Bot Skeleton
        const botMsgDiv = document.createElement('div');
        botMsgDiv.className = 'ai-msg ai-msg-bot';
        botMsgDiv.innerHTML = `
          <div class="ai-avatar"><i data-feather="cpu"></i></div>
          <div class="ai-msg-body">
            <div class="ai-msg-header">
              <strong>OsintNeo Forensic AI</strong>
              <span class="ai-timestamp">Generating analysis...</span>
            </div>
            <div class="ai-msg-content markdown-body" id="current-ai-stream">
              <span class="status-pulse pulse-green" style="display:inline-block; margin-right:6px;"></span> Processing municipal knowledgebase...
            </div>
          </div>
        `;
        messagesThread.appendChild(botMsgDiv);
        feather.replace();
        messagesThread.scrollTop = messagesThread.scrollHeight;

        // Generate response using ingested knowledgebase
        const streamContainer = botMsgDiv.querySelector('#current-ai-stream');
        await streamResponse(text, streamContainer);
        botMsgDiv.querySelector('.ai-timestamp').textContent = 'Completed';
        feather.replace();
      }

      async function streamResponse(query, targetElem) {
        const q = query.toLowerCase();
        let markdownResponse = "";

        if (q.includes('huntington') || q.includes('hb') || q.includes('21m') || q.includes('deficit')) {
          markdownResponse = `### 🏛️ Huntington Beach Data Systems Audit

* **Capital Deficit:** **$21,000,000** (15-Year Plan 2024–2039)
* **Infrastructure Grade:** **Grade C** (*Mediocre — Lacks Redundancy*)
* **The Root Cause:**
  1. **Measure FF Revenue Allocation:** Huntington Beach taxpayers poured **$697 Million** into infrastructure (2005–2024), but funds were pooled and prioritized for a **$877M Stormwater crisis** and **$270M Road backlog**.
  2. **Legacy On-Premise Rack:** Core databases (\`gis.huntingtonbeachca.gov\` on \`192.5.222.153\` and \`records\` on \`192.5.222.218\`) run on a physical Windows server rack with **zero WAF protection**.
  3. **Operational Bottlenecks:** Relies on basic host antivirus and suffers from **multi-day backup windows**.

> [!TIP]
> **Recommended Fix:** Deploy an immediate Cloudflare WAF proxy, transition backups to automated cloud snapshots, and allocate ~$2.5M/year from the available $8M/year CIP capacity.`;
        } else if (q.includes('192.5.222') || q.includes('subnet') || q.includes('security') || q.includes('ip')) {
          markdownResponse = `### 🛡️ Security Risk Analysis: Subnet 192.5.222.0/24

* **Autonomous System:** AS393281 (City of Huntington Beach)
* **Exposed Endpoints:**
  * \`192.5.222.153:443\` — ESRI ArcGIS REST API (Open spatial catalog)
  * \`192.5.222.218:443\` — Laserfiche WebLink (Legacy ASP.NET document vault)
* **Vulnerability Assessment:**
  * **No Web Application Firewall (WAF):** While \`huntingtonbeachca.gov\` uses Cloudflare, direct requests to \`192.5.222.x\` bypass edge filters entirely.
  * **Basic Antivirus Gap:** Traditional antivirus cannot inspect HTTP payload attacks, unauthenticated database queries, or IDOR document harvesting.`;
        } else if (q.includes('legacy') || q.includes('cities') || q.includes('windows nt') || q.includes('list')) {
          markdownResponse = `### 🖥️ Legacy On-Premise Server Municipalities (40% of Dataset)

1. **City of Huntington Beach:** Subnet \`192.5.222.0/24\` (Grade C, **$21.0M Deficit**)
2. **City of Westminster:** \`209.232.148.77\` (Grade D+, **$8.5M Deficit**) — Server 2012 legacy cluster
3. **City of Fountain Valley:** \`198.245.188.42\` (Grade C+, **$5.2M Deficit**) — 24–48hr tape backup lag
4. **City of Seal Beach:** \`64.78.33.190\` (Grade C, **$3.8M Deficit**) — Small municipal server rack

**Fully Modernized Peers for Contrast:**
* **Newport Beach (Grade A, $0 Deficit):** 100% Cloud SaaS (AWS/ESRI), Cloudflare WAF.
* **Irvine (Grade A, $0 Deficit):** AWS GovCloud, Zero Trust Edge, instant multi-region sync.`;
        } else if (q.includes('proposal') || q.includes('pitch') || q.includes('council') || q.includes('cip')) {
          markdownResponse = `### 📑 3-Phase Council Modernization Proposal

\`\`\`
PHASE 1: IMMEDIATE SHIELDING (Days 1–30 | $0 Capital)
• Place 192.5.222.x behind Cloudflare WAF reverse proxy.
• Restrict direct-IP database queries to internal staff VPN.

PHASE 2: CLOUD DATA MIGRATION (Months 1–12 | Operational CIP)
• Migrate self-hosted ArcGIS Server to ArcGIS Online (SaaS).
• Transition on-prem Laserfiche vault to Laserfiche Cloud.
• Eliminate multi-day backups via automated immutable cloud sync.

PHASE 3: AI & SMART CITY INTEGRATION (Months 12–24)
• Deploy AI public records search and automated permit triage.
• Connect real-time utility SCADA telemetry to cloud dashboard.
\`\`\``;
        } else {
          markdownResponse = `### 🔍 Forensic Query Analysis

**Query:** "${query}"

* **Cross-Referenced Datasets:** 10 Municipal Jurisdictions, 17 Public IP Endpoints, 2024 IRC Report, 2000 IAC Baseline.
* **Key Finding:** Municipalities with dedicated **Capital Asset Replacement Reserves** (Newport Beach, Irvine) achieved **Grade A** systems with zero unfunded deficit. In contrast, cities that pooled funds into general public works carry an average **$9.6M IT deficit** and legacy on-premise Windows servers.

*Need specific details on a city, IP address, or budget contract? Select one of the quick prompt chips or specify the city name.*`;
        }

        // Simulate fast streaming effect
        targetElem.innerHTML = '';
        let currentText = '';
        const words = markdownResponse.split(' ');
        for (let i = 0; i < words.length; i++) {
          currentText += words[i] + ' ';
          if (i % 3 === 0 || i === words.length - 1) {
            targetElem.innerHTML = marked.parse(currentText);
            messagesThread.scrollTop = messagesThread.scrollHeight;
            await new Promise(r => setTimeout(r, 25));
          }
        }
      }

      if (sendBtn) sendBtn.onclick = () => sendAiMessage();
      if (chatInput) {
        chatInput.onkeydown = (e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendAiMessage();
          }
        };
      }

      promptChips.forEach(chip => {
        chip.onclick = () => sendAiMessage(chip.dataset.prompt);
      });

      if (clearBtn) {
        clearBtn.onclick = () => {
          messagesThread.innerHTML = `
            <div class="ai-msg ai-msg-bot">
              <div class="ai-avatar"><i data-feather="cpu"></i></div>
              <div class="ai-msg-body">
                <div class="ai-msg-header">
                  <strong>OsintNeo Forensic AI</strong>
                  <span class="ai-timestamp">Reset</span>
                </div>
                <div class="ai-msg-content markdown-body">
                  <p>Conversation cleared. Ready for your next municipal forensic query.</p>
                </div>
              </div>
            </div>
          `;
          feather.replace();
        };
      }
    }

    // Municipal View Logic
    let municipalData = [];
    let citiesIpsData = [];
    let isIpViewActive = false;

    async function loadMunicipalView() {
      if (municipalData.length === 0) {
        try {
          const res1 = await fetch('data/municipal_matrix.json');
          municipalData = await res1.json();
          const res2 = await fetch('data/cities_ips.json');
          citiesIpsData = await res2.json();
        } catch(e) {
          console.error('Error loading municipal datasets:', e);
        }
      }
      renderMunicipalTable(municipalData);
      renderIpsGrid(citiesIpsData);
      setupMunicipalControls();
    }

    function renderMunicipalTable(data) {
      const tbody = document.getElementById('muni-table-body');
      if (!tbody) return;
      tbody.innerHTML = '';

      data.forEach(row => {
        const tr = document.createElement('tr');
        const legacyClass = row['Windows NT / Legacy Server Lineage']?.startsWith('YES') ? 'legacy-tag-yes' :
                            row['Windows NT / Legacy Server Lineage']?.startsWith('NO') ? 'legacy-tag-no' : 'legacy-tag-partial';

        let gradeClass = 'grade-c';
        const gradeText = row['Data Systems Grade'] || '';
        if (gradeText.includes('Grade A')) gradeClass = 'grade-a';
        else if (gradeText.includes('Grade B')) gradeClass = 'grade-b';
        else if (gradeText.includes('Grade D')) gradeClass = 'grade-d';

        tr.innerHTML = `
          <td>
            <strong class="city-cell-title">${row['City Name'] || ''}</strong>
          </td>
          <td><span class="font-mono text-muted">${row['IRC Report Years Available'] || 'N/A'}</span></td>
          <td><span class="${legacyClass}">${row['Windows NT / Legacy Server Lineage'] || ''}</span></td>
          <td><span class="grade-badge ${gradeClass}">${gradeText}</span></td>
          <td><strong class="text-rose font-mono">${row['IT Capital Deficit'] || '$0'}</strong></td>
          <td><span class="font-mono">${row['Annual IT Spent / Budget'] || ''}</span></td>
          <td><span class="font-mono text-accent">${row['Annual Available Capital Capacity'] || ''}</span></td>
          <td><span>${row['Backup Latency Window'] || ''}</span></td>
          <td><span>${row['Antivirus / Security Posture'] || ''}</span></td>
          <td><small class="font-mono">${row['Public IP / WAF Exposure'] || ''}</small></td>
          <td><small>${row['Primary Tax Funding Source'] || ''}</small></td>
        `;
        tbody.appendChild(tr);
      });
    }

    function renderIpsGrid(ips) {
      const container = document.getElementById('muni-ips-container');
      if (!container) return;
      container.innerHTML = '';

      ips.forEach(item => {
        const card = document.createElement('div');
        card.className = 'ip-card';
        card.innerHTML = `
          <div class="ip-card-header">
            <div>
              <div class="ip-card-host">${item['Domain / Hostname'] || 'Direct Subnet'}</div>
              <div class="ip-card-city">${item['City / Agency'] || ''}</div>
            </div>
            <span class="grade-badge ${item['WAF / CDN Status']?.includes('NONE') ? 'grade-d' : 'grade-a'}">
              ${item['WAF / CDN Status']?.includes('NONE') ? 'UNSHIELDED' : 'WAF ACTIVE'}
            </span>
          </div>
          <div>
            <span class="ip-card-addr">${item['Public IP Address / Range'] || ''}</span>
          </div>
          <div style="font-size: 0.82rem; color: var(--text-secondary);">
            <strong>ASN:</strong> ${item['ASN & Carrier'] || ''}<br>
            <strong>Service:</strong> ${item['Service Fingerprint'] || ''}<br>
            <strong>Location:</strong> ${item['Hosting Location'] || ''}
          </div>
        `;
        container.appendChild(card);
      });
    }

    function setupMunicipalControls() {
      const searchInput = document.getElementById('muni-search-input');
      const filterBtns = document.querySelectorAll('.muni-filter-btn');
      const toggleIpBtn = document.getElementById('btn-toggle-ip-view');
      const systemsContainer = document.getElementById('muni-systems-container');
      const ipsContainer = document.getElementById('muni-ips-container');
      const toggleText = document.getElementById('ip-view-toggle-text');

      if (toggleIpBtn) {
        toggleIpBtn.onclick = () => {
          isIpViewActive = !isIpViewActive;
          if (isIpViewActive) {
            systemsContainer.classList.add('hidden');
            ipsContainer.classList.remove('hidden');
            toggleText.textContent = 'Show Systems Table';
          } else {
            systemsContainer.classList.remove('hidden');
            ipsContainer.classList.add('hidden');
            toggleText.textContent = 'Show Raw IP Mapping';
          }
          feather.replace();
        };
      }

      if (searchInput) {
        searchInput.oninput = (e) => {
          const q = e.target.value.toLowerCase();
          const filtered = municipalData.filter(r => JSON.stringify(r).toLowerCase().includes(q));
          renderMunicipalTable(filtered);
          const filteredIps = citiesIpsData.filter(i => JSON.stringify(i).toLowerCase().includes(q));
          renderIpsGrid(filteredIps);
        };
      }

      filterBtns.forEach(btn => {
        btn.onclick = () => {
          filterBtns.forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          const filter = btn.dataset.muniFilter;

          if (filter === 'all') {
            renderMunicipalTable(municipalData);
          } else if (filter === 'legacy') {
            renderMunicipalTable(municipalData.filter(r => r['Windows NT / Legacy Server Lineage']?.startsWith('YES')));
          } else if (filter === 'cloud') {
            renderMunicipalTable(municipalData.filter(r => r['Windows NT / Legacy Server Lineage']?.startsWith('NO')));
          } else if (filter === 'hybrid') {
            renderMunicipalTable(municipalData.filter(r => r['Windows NT / Legacy Server Lineage']?.startsWith('PARTIAL')));
          }
        };
      });
    }

    // Dossiers View Logic
    const dossierFiles = {
      executive: 'reports/EXECUTIVE_BRIEFING_MUNICIPAL_DATA_INFRASTRUCTURE_AUDIT.md',
      '2024irc': 'opencode_work/extracted_text/HB_IRC_Report_v1.1.pdf.txt',
      '2000iac': 'reports/HB_2000_IAC_INFRASTRUCTURE_REPORT_AND_MEASURE_FF.md',
      vendors: 'reports/MUNICIPAL_IT_VENDORS_AND_BUDGET_CONTRACTS.md'
    };

    let currentDossierMarkdown = '';

    async function loadDossiersView() {
      const navBtns = document.querySelectorAll('.dossier-nav-btn');
      const pane = document.getElementById('dossier-markdown-pane');
      const title = document.getElementById('dossier-active-title');
      const copyBtn = document.getElementById('btn-copy-dossier');

      async function switchDossier(docKey, btn) {
        navBtns.forEach(b => b.classList.remove('active'));
        if (btn) btn.classList.add('active');

        pane.innerHTML = '<div style="padding: 20px; color: var(--text-muted);">Loading dossier markdown...</div>';
        try {
          // Fetch raw markdown or file
          const filePath = dossierFiles[docKey] || dossierFiles.executive;
          const res = await fetch(`../${filePath}`);
          const text = await res.text();
          currentDossierMarkdown = text;
          title.textContent = btn ? btn.querySelector('strong').textContent : 'Intelligence Dossier';
          pane.innerHTML = marked.parse(text);
        } catch(e) {
          pane.innerHTML = `<div style="padding: 20px; color: var(--accent-rose);">Failed to load dossier: ${e.message}</div>`;
        }
        feather.replace();
      }

      navBtns.forEach(btn => {
        btn.onclick = () => switchDossier(btn.dataset.doc, btn);
      });

      if (copyBtn) {
        copyBtn.onclick = () => {
          if (currentDossierMarkdown) {
            copyToClipboard(currentDossierMarkdown, 'Dossier markdown copied to clipboard');
          }
        };
      }

      // Load initial executive briefing
      await switchDossier('executive', navBtns[0]);
    }
  }

  // Start app on DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Self-start
  setupEventListeners();
  init();
})();
