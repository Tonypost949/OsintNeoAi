/**
 * Nav Polish — auto-collapse panels, keep globe visible, compact HUD
 */
(function() {
  const PANEL_IDS = ['data-panel','cctv-panel','scene-panel','global-context-panel','radio-panel','control-panel','location-bar','pp-toggles'];
  const LEFT_IDS = new Set(['data-panel','cctv-panel','scene-panel']);
  const RIGHT_IDS = new Set(['global-context-panel','radio-panel']);
  const BOTTOM_IDS = new Set(['control-panel','location-bar']);

  function collapseAllExcept(keepId) {
    for (const id of PANEL_IDS) {
      if (id === keepId) continue;
      const el = document.getElementById(id);
      if (!el) continue;
      // Left/right/bottom: collapse if open
      if (!el.classList.contains('collapsed')) {
        // Only auto-collapse if it's in same rail as keepId, or if keepId is a data/context panel that would obscure globe
        const isSameRail = (LEFT_IDS.has(keepId) && LEFT_IDS.has(id)) || (RIGHT_IDS.has(keepId) && RIGHT_IDS.has(id)) || (BOTTOM_IDS.has(keepId) && BOTTOM_IDS.has(id));
        const shouldCollapse = isSameRail || LEFT_IDS.has(keepId) || RIGHT_IDS.has(keepId);
        if (shouldCollapse) {
          el.classList.add('collapsed');
          el.classList.remove('auto-expanded');
          // Also try to click its collapse button to sync state
          const btn = el.querySelector('.panel-collapse-btn, [data-collapse-target]');
          if (btn && !el.classList.contains('collapsed')) {
            // fallback
          }
        }
      }
    }
  }

  // Observe class changes to detect manual expands
  const observer = new MutationObserver((mutations) => {
    for (const m of mutations) {
      if (m.type === 'attributes' && m.attributeName === 'class') {
        const el = m.target;
        if (el.id && PANEL_IDS.includes(el.id) && !el.classList.contains('collapsed')) {
          collapseAllExcept(el.id);
        }
      }
    }
  });

  function init() {
    for (const id of PANEL_IDS) {
      const el = document.getElementById(id);
      if (el) observer.observe(el, { attributes: true, attributeFilter: ['class'] });
      // Also listen to toggle buttons
      if (el) {
        const toggles = el.querySelectorAll('.panel-header, .panel-collapse-btn, [data-dock-toggle-target], [data-collapse-target]');
        toggles.forEach(btn => {
          btn.addEventListener('click', () => {
            setTimeout(() => {
              if (el && !el.classList.contains('collapsed')) collapseAllExcept(id);
            }, 60);
          }, { capture: true });
        });
      }
    }

    // Also handle bottom dock toggles
    document.querySelectorAll('[data-dock-toggle-target]').forEach(btn => {
      btn.addEventListener('click', () => {
        const target = btn.getAttribute('data-dock-toggle-target');
        if (target) setTimeout(() => collapseAllExcept(target), 80);
      });
    });

    // Move stray large telemetry popups to top-right if they appear centered
    const movePopups = () => {
      const overlay = document.getElementById('world-overlay-root');
      if (overlay && overlay.children.length > 0) {
        // Ensure it's compact and top-right via CSS, but also ensure pointer-events only on cards
        overlay.style.pointerEvents = 'none';
        Array.from(overlay.children).forEach(ch => ch.style.pointerEvents = 'auto');
      }
      const intelHud = document.getElementById('intel-hud');
      if (intelHud && intelHud.textContent.trim().length > 0) {
        intelHud.style.display = 'block';
      }
    };
    setInterval(movePopups, 1500);

    // Compact the title bar slightly after load
    const titleBar = document.getElementById('title-bar');
    if (titleBar) {
      // No extra JS needed, CSS handles it
    }

    console.log('[Nav Polish] Auto-collapse + compact HUD active');
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
