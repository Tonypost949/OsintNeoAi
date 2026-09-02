/**
 * Native Voice Control — Zero-API Fallback for God's Eye View
 * Uses Web Speech API (webkitSpeechRecognition) with no token required.
 * Works in Chrome, Edge, Safari, Brave, Opera, mobile browsers.
 * Provides glowing MIC at bottom-center + Spacebar push-to-talk + live transcript + speech synthesis.
 */
(function() {
  const MIC_ID = 'native-voice-control';
  if (document.getElementById(MIC_ID)) return;

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const hasNativeSpeech = !!SpeechRecognition;

  // Create UI
  const root = document.createElement('div');
  root.id = MIC_ID;
  root.innerHTML = `
    <div id="native-mic-wrap" style="position:fixed; bottom:18px; left:50%; transform:translateX(-50%); z-index:9999; display:flex; flex-direction:column; align-items:center; gap:8px; pointer-events:auto;">
      <div id="native-transcript" style="background:rgba(0,0,0,0.85); color:#7ee8ff; font-family:'JetBrains Mono', monospace; font-size:12px; letter-spacing:0.08em; padding:6px 14px; border-radius:20px; border:1px solid rgba(126,232,255,0.35); backdrop-filter:blur(10px); display:none; max-width:92vw; text-align:center; box-shadow:0 4px 20px rgba(0,0,0,0.5);"></div>
      <button id="native-mic-btn" type="button" aria-label="Native voice control — click to speak" title="Click to speak or hold Space" style="width:62px; height:62px; border-radius:50%; background:radial-gradient(circle at 30% 30%, #1a2a4a, #0a0f1e); border:2px solid rgba(126,232,255,0.45); color:#7ee8ff; font-size:26px; cursor:pointer; display:flex; align-items:center; justify-content:center; box-shadow:0 0 24px rgba(56,189,248,0.45), 0 0 48px rgba(56,189,248,0.18), inset 0 1px 0 rgba(255,255,255,0.12); transition:all 0.2s ease; backdrop-filter:blur(12px);">
        <span style="filter:drop-shadow(0 0 8px rgba(126,232,255,0.9));">🎙️</span>
      </button>
      <div style="font-family:'Inter',sans-serif; font-size:9px; letter-spacing:0.18em; color:rgba(180,210,235,0.7); text-transform:uppercase; background:rgba(0,0,0,0.6); padding:2px 8px; border-radius:10px; border:1px solid rgba(255,255,255,0.08);">VOICE • HOLD SPACE</div>
    </div>
  `;
  document.body.appendChild(root);

  const btn = document.getElementById('native-mic-btn');
  const transcriptEl = document.getElementById('native-transcript');
  let recognition = null;
  let isListening = false;
  let holdSpace = false;

  function speak(text) {
    try {
      if (!window.speechSynthesis) return;
      window.speechSynthesis.cancel();
      const utter = new SpeechSynthesisUtterance(text);
      utter.rate = 1.05;
      utter.pitch = 1.0;
      utter.volume = 0.85;
      window.speechSynthesis.speak(utter);
    } catch {}
  }

  function showTranscript(text, isFinal) {
    transcriptEl.textContent = (isFinal ? '✓ ' : '… ') + text;
    transcriptEl.style.display = 'block';
    transcriptEl.style.borderColor = isFinal ? 'rgba(52,211,153,0.6)' : 'rgba(126,232,255,0.35)';
    transcriptEl.style.color = isFinal ? '#6ee7b7' : '#7ee8ff';
    if (isFinal) setTimeout(() => { transcriptEl.style.display = 'none'; }, 3200);
  }

  function setMicListening(listening) {
    isListening = listening;
    if (listening) {
      btn.style.background = 'radial-gradient(circle at 30% 30%, #ff3b5c, #9f1239)';
      btn.style.borderColor = 'rgba(251,113,133,0.9)';
      btn.style.boxShadow = '0 0 32px rgba(244,63,94,0.65), 0 0 64px rgba(244,63,94,0.3)';
      btn.style.transform = 'scale(1.08)';
      btn.querySelector('span').textContent = '🔴';
    } else {
      btn.style.background = 'radial-gradient(circle at 30% 30%, #1a2a4a, #0a0f1e)';
      btn.style.borderColor = 'rgba(126,232,255,0.45)';
      btn.style.boxShadow = '0 0 24px rgba(56,189,248,0.45), 0 0 48px rgba(56,189,248,0.18)';
      btn.style.transform = 'scale(1.0)';
      btn.querySelector('span').textContent = '🎙️';
    }
  }

  function getGEV() { return window.__godsEyeView || null; }

  async function executeVoiceCommand(raw) {
    const text = raw.toLowerCase().trim();
    if (!text) return;
    const gev = getGEV();
    if (!gev) { speak('System not ready'); return; }
    const { viewer, styleManager, dataManager } = gev;
    const runner = gev.voiceCommands?.runner || null;

    // Helper to use runner if available, else direct
    async function runAction(name, args) {
      if (runner) {
        try { return await runner(name, args); } catch (e) { console.warn('runner', e); }
      }
      // Fallback direct handling for common commands
      if (name === 'fly_to_location' && args.query) {
        try {
          const { searchAndFlyTo } = await import('/assets/index-B30cPkKk.js').catch(() => ({}));
        } catch {}
        // Use dataManager/styleManager direct
        if (styleManager && typeof styleManager.runImmediateLocationNavigation === 'function') {
          // ignore
        }
      }
      return null;
    }

    // Parse locations
    const locMatch = text.match(/(?:fly to|go to|show|take me to)\s+(.+)/) || text.match(/^(austin|new york|tokyo|paris|london|dubai|san francisco|washington|berlin|moscow|sydney|los angeles|chicago|miami|seattle|boston|denver|houston|atlanta)$/);
    let targetLocation = null;
    if (locMatch) targetLocation = (locMatch[1] || locMatch[0]).trim();

    // Visual presets
    const styleMap = {
      'thermal': 'thermal', 'flir': 'thermal', 'heat': 'thermal',
      'night vision': 'surveillance', 'nvg': 'surveillance', 'night': 'surveillance',
      'retro': 'retro', 'crt': 'retro',
      'noir': 'noir', 'black and white': 'noir',
      'anime': 'anime',
      'snow': 'snow',
      'normal': 'normal', 'default': 'normal', 'clear style': 'normal'
    };
    for (const [key, style] of Object.entries(styleMap)) {
      if (text.includes(key)) {
        if (gev.styleManager) gev.styleManager.setStyle(style);
        speak(`${style} enabled`);
        showTranscript(`→ ${style.toUpperCase()}`, true);
        return;
      }
    }

    // Layer toggles
    const layerMap = {
      'flights': 'flights', 'planes': 'flights', 'aircraft': 'flights', 'air traffic': 'flights',
      'military': 'military', 'military planes': 'military',
      'satellites': 'satellites', 'starlink': 'satellites', 'space station': 'satellites',
      'earthquakes': 'earthquakes', 'quakes': 'earthquakes',
      'traffic': 'traffic', 'street traffic': 'traffic',
      'cctv': 'cctv', 'cameras': 'cctv',
      'wildfires': 'local-firms', 'fires': 'local-firms', 'firms': 'local-firms',
      'ships': 'ais-live-vessels', 'vessels': 'ais-live-vessels', 'boats': 'ais-live-vessels',
      'radio': 'radio'
    };
    for (const [key, layerId] of Object.entries(layerMap)) {
      if (text.includes(`show ${key}`) || text.includes(`enable ${key}`) || text.includes(`turn on ${key}`)) {
        if (dataManager) await dataManager.setEnabled(layerId, true, { origin: 'voice-native' }).catch(()=>{});
        speak(`Showing ${key}`);
        showTranscript(`→ SHOW ${key.toUpperCase()}`, true);
        return;
      }
      if (text.includes(`hide ${key}`) || text.includes(`disable ${key}`) || text.includes(`turn off ${key}`) || text.includes(`clear ${key}`)) {
        if (dataManager) await dataManager.setEnabled(layerId, false, { origin: 'voice-native' }).catch(()=>{});
        speak(`Hiding ${key}`);
        showTranscript(`→ HIDE ${key.toUpperCase()}`, true);
        return;
      }
    }
    if (text.includes('clear all') || text.includes('clear layers') || text.includes('hide all')) {
      if (dataManager) {
        for (const lid of ['flights','military','satellites','earthquakes','traffic','cctv','ais-live-vessels']) {
          await dataManager.setEnabled(lid, false, { origin: 'voice-native' }).catch(()=>{});
        }
      }
      speak('Cleared all layers');
      showTranscript('→ CLEAR ALL', true);
      return;
    }

    // Camera
    if (text.includes('zoom in')) {
      if (runner) await runner('adjust_camera_zoom', { direction: 'in', amount: 'medium' }).catch(()=>{});
      else if (viewer) viewer.camera.zoomIn(50000);
      speak('Zooming in'); return;
    }
    if (text.includes('zoom out')) {
      if (runner) await runner('adjust_camera_zoom', { direction: 'out', amount: 'medium' }).catch(()=>{});
      else if (viewer) viewer.camera.zoomOut(50000);
      speak('Zooming out'); return;
    }
    if (text.includes('reset globe') || text.includes('reset view') || text.includes('globe view')) {
      if (runner) await runner('zoom_to_globe', {}).catch(()=>{});
      else if (gev.styleManager?.resetToGlobeView) gev.styleManager.resetToGlobeView();
      speak('Resetting globe'); return;
    }
    if (text.includes('orbit')) {
      speak('Orbit view'); return;
    }

    // Location fly - must be after style/layer checks
    if (targetLocation) {
      const needsFeedback = true;
      showTranscript(`→ FLY TO ${targetLocation.toUpperCase()}`, true);
      speak(`Flying to ${targetLocation}`);
      if (runner) {
        try {
          // Try location search via gevActions
          await runner('fly_to_location', { query: targetLocation, waitForArrival: false });
          return;
        } catch (e) { console.warn(e); }
      }
      // Fallback: use location search input
      const searchInput = document.getElementById('location-search');
      if (searchInput) {
        searchInput.value = targetLocation;
        searchInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }));
        // Try to click search
        setTimeout(() => {
          const firstPill = document.querySelector('.location-city-row button, #location-pills button');
          if (firstPill) firstPill.click();
        }, 400);
      }
      return;
    }

    // Generic fallback - try as location
    if (text.length > 2 && text.length < 40) {
      showTranscript(`→ TRY ${text.toUpperCase()}`, true);
      if (runner) {
        try { await runner('fly_to_location', { query: text }); speak(`Trying ${text}`); return; } catch {}
      }
      speak(`Heard ${text}`);
      return;
    }

    speak(`Heard ${text}`);
  }

  function startListening() {
    if (!hasNativeSpeech) {
      transcriptEl.textContent = '⚠️ Voice not supported in this browser — use Chrome, Edge, or Safari';
      transcriptEl.style.display = 'block';
      transcriptEl.style.borderColor = 'rgba(251,113,133,0.6)';
      transcriptEl.style.color = '#fca5a5';
      speak('Voice not supported');
      return;
    }
    if (isListening) return;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 1;

    recognition.onstart = () => { setMicListening(true); showTranscript('Listening…', false); };
    recognition.onresult = (event) => {
      let interim = '';
      let final = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const res = event.results[i];
        if (res.isFinal) final += res[0].transcript;
        else interim += res[0].transcript;
      }
      if (interim) showTranscript(interim, false);
      if (final) {
        showTranscript(final, true);
        executeVoiceCommand(final);
      }
    };
    recognition.onerror = (event) => {
      setMicListening(false);
      const err = event.error || 'unknown';
      if (err === 'not-allowed' || err === 'service-not-allowed') {
        transcriptEl.textContent = '🎤 Microphone blocked — allow mic permission';
        transcriptEl.style.display = 'block';
        speak('Microphone blocked');
      } else if (err !== 'aborted' && err !== 'no-speech') {
        transcriptEl.textContent = `Voice error: ${err}`;
        transcriptEl.style.display = 'block';
      }
      setTimeout(() => transcriptEl.style.display = 'none', 3000);
    };
    recognition.onend = () => { setMicListening(false); };
    try { recognition.start(); } catch (e) { setMicListening(false); }
  }

  function stopListening() {
    if (recognition) {
      try { recognition.stop(); } catch {}
      recognition = null;
    }
    setMicListening(false);
  }

  // Button click toggles
  btn.addEventListener('click', () => {
    if (isListening) stopListening();
    else startListening();
  });

  // Spacebar push-to-talk (hold Space)
  let spaceHeld = false;
  document.addEventListener('keydown', (e) => {
    if (e.code === 'Space' && !e.repeat && !spaceHeld && !e.ctrlKey && !e.metaKey && !e.altKey) {
      const activeEl = document.activeElement;
      const isTyping = activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'TEXTAREA' || activeEl.isContentEditable);
      if (isTyping) return;
      spaceHeld = true;
      e.preventDefault();
      startListening();
    }
  });
  document.addEventListener('keyup', (e) => {
    if (e.code === 'Space' && spaceHeld) {
      spaceHeld = false;
      e.preventDefault();
      // Keep listening until result, but visual held state off
      // Native recognition will auto-stop on pause; we keep it listening
    }
  });
  window.addEventListener('blur', () => { spaceHeld = false; });

  // Also watch for OpenAI voice failure and show native as fallback hint
  const checkOpenAIFail = setInterval(() => {
    const gevVoice = document.getElementById('gev-voice-control');
    if (gevVoice && gevVoice.dataset.status === 'error') {
      const errDetail = document.getElementById('gev-voice-error-detail');
      if (errDetail && !errDetail.textContent.includes('native')) {
        // Append hint
        const hint = document.createElement('div');
        hint.style.cssText = 'margin-top:8px; padding:8px; background:rgba(6,182,212,0.12); border:1px solid rgba(6,182,212,0.3); border-radius:8px; font-size:11px; color:#7dd3fc;';
        hint.textContent = '💡 Try the native MIC at bottom center — works without any API key (Web Speech).';
        if (!errDetail.querySelector('#native-hint')) {
          hint.id = 'native-hint';
          errDetail.appendChild(hint);
        }
      }
    }
  }, 3000);
  setTimeout(() => clearInterval(checkOpenAIFail), 60000);

  console.log('[Native Voice] Ready — click MIC or hold Space');
})();
