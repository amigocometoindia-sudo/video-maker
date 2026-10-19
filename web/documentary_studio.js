/**
 * Auto Documentary Cinema Studio — Client Controller
 * Powers 1-click long-form animated historical video generation.
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const presetGrid = document.getElementById('presetGrid');
  const topicInput = document.getElementById('topicInput');
  const btnResearchOutline = document.getElementById('btnResearchOutline');
  const voiceSelect = document.getElementById('voiceSelect');
  const styleSelect = document.getElementById('styleSelect');
  const subtitleStyle = document.getElementById('subtitleStyle');
  const sfxSlider = document.getElementById('sfxSlider');
  const sfxVal = document.getElementById('sfxVal');
  const muteSfxCheckbox = document.getElementById('muteSfxCheckbox');
  const toggleDatePill = document.getElementById('toggleDatePill');
  const toggleArchiveArt = document.getElementById('toggleArchiveArt');
  const toggleCountryballs = document.getElementById('toggleCountryballs');
  const btnToggleScriptEditor = document.getElementById('btnToggleScriptEditor');
  const scriptEditorContainer = document.getElementById('scriptEditorContainer');
  const overrideCustomScriptCheckbox = document.getElementById('overrideCustomScriptCheckbox');
  const customScriptInput = document.getElementById('customScriptInput');
  const chaptersPreview = document.getElementById('chaptersPreview');
  const btnLaunchDocumentary = document.getElementById('btnLaunchDocumentary');
  const statusBanner = document.getElementById('statusBanner');

  // Monitor & HUD Elements
  const liveDot = document.getElementById('liveDot');
  const monitorStatusText = document.getElementById('monitorStatusText');
  const cinemaVideo = document.getElementById('cinemaVideo');
  const monitorPlaceholder = document.getElementById('monitorPlaceholder');
  const hudCard = document.getElementById('hudCard');
  const hudPhaseLabel = document.getElementById('hudPhaseLabel');
  const hudDetailLabel = document.getElementById('hudDetailLabel');
  const hudPct = document.getElementById('hudPct');
  const hudProgressBar = document.getElementById('hudProgressBar');
  const hudStatStage = document.getElementById('hudStatStage');
  const hudStatElapsed = document.getElementById('hudStatElapsed');
  const hudStatEst = document.getElementById('hudStatEst');
  const btnCancelJob = document.getElementById('btnCancelJob');
  const btnDownloadVideo = document.getElementById('btnDownloadVideo');
  const sceneStripCard = document.getElementById('sceneStripCard');
  const sceneStrip = document.getElementById('sceneStrip');
  const sceneCountBadge = document.getElementById('sceneCountBadge');

  // AI Image Engine & Aspect Elements
  const aiImageProviderSelect = document.getElementById('aiImageProviderSelect');
  const aiProviderSelect = document.getElementById('aiProviderSelect');
  const imageStyleSelect = document.getElementById('imageStyleSelect');
  const apiKeyInput = document.getElementById('apiKeyInput');
  const apiModelInput = document.getElementById('apiModelInput');
  const keyTypeHint = document.getElementById('keyTypeHint');
  const btnTestApiKey = document.getElementById('btnTestApiKey');
  const apiKeyStatusBox = document.getElementById('apiKeyStatusBox');
  const btnAspect169 = document.getElementById('btnAspect169');
  const btnAspect916 = document.getElementById('btnAspect916');
  const monitorScreen = document.getElementById('monitorScreen');

  // State
  let activePreset = 'israel_history';
  let activeJobId = null;
  let pollInterval = null;
  let elapsedTimer = null;
  let jobStartTime = null;
  let currentAspectRatio = '16:9';

  // NVIDIA NIM Auto-Detection
  if (apiKeyInput) {
    apiKeyInput.addEventListener('input', () => {
      const val = apiKeyInput.value.trim();
      if (val.startsWith('nvapi-')) {
        if (aiProviderSelect) aiProviderSelect.value = 'nvidia';
        if (aiImageProviderSelect) aiImageProviderSelect.value = 'nvidia';
        if (keyTypeHint) {
          keyTypeHint.textContent = '⚡ NVIDIA NIM Active (FLUX.1 + Llama 3.3)';
          keyTypeHint.style.color = '#10b981';
        }
        if (apiModelInput && !apiModelInput.value) {
          apiModelInput.placeholder = 'meta/llama-3.3-70b-instruct';
        }
      } else if (val.startsWith('sk-')) {
        if (aiProviderSelect) aiProviderSelect.value = 'openai';
        if (aiImageProviderSelect) aiImageProviderSelect.value = 'openai';
        if (keyTypeHint) {
          keyTypeHint.textContent = 'OpenAI Active';
          keyTypeHint.style.color = '#38bdf8';
        }
      } else {
        if (keyTypeHint) {
          keyTypeHint.textContent = 'nvapi-... or sk-...';
          keyTypeHint.style.color = '#94a3b8';
        }
      }
    });
  }

  // NVIDIA NIM Key Test Button
  if (btnTestApiKey) {
    btnTestApiKey.addEventListener('click', async () => {
      const key = apiKeyInput ? apiKeyInput.value.trim() : '';
      if (!key) {
        if (apiKeyStatusBox) {
          apiKeyStatusBox.style.display = 'block';
          apiKeyStatusBox.style.background = 'rgba(239, 68, 68, 0.15)';
          apiKeyStatusBox.style.border = '1px solid rgba(239, 68, 68, 0.4)';
          apiKeyStatusBox.style.color = '#f87171';
          apiKeyStatusBox.textContent = '⚠️ Please paste your NVIDIA NIM API key (nvapi-...) to test.';
        }
        return;
      }

      btnTestApiKey.disabled = true;
      btnTestApiKey.textContent = '⏳ Testing...';
      if (apiKeyStatusBox) {
        apiKeyStatusBox.style.display = 'block';
        apiKeyStatusBox.style.background = 'rgba(56, 189, 248, 0.1)';
        apiKeyStatusBox.style.border = '1px solid rgba(56, 189, 248, 0.3)';
        apiKeyStatusBox.style.color = '#38bdf8';
        apiKeyStatusBox.textContent = 'Connecting to NVIDIA NIM cloud endpoint...';
      }

      try {
        const resp = await fetch('/api/documentary/test_nvidia_key', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ api_key: key }),
        });
        const data = await resp.json();
        if (data.success) {
          if (apiKeyStatusBox) {
            apiKeyStatusBox.style.background = 'rgba(16, 185, 129, 0.15)';
            apiKeyStatusBox.style.border = '1px solid rgba(16, 185, 129, 0.4)';
            apiKeyStatusBox.style.color = '#34d399';
            apiKeyStatusBox.innerHTML = `✅ <strong>${data.message}</strong> (Model: ${data.model}) — Ready for ultra-fast FLUX.1 Dev/Schnell & Llama 3.3 70B generation!`;
          }
        } else {
          if (apiKeyStatusBox) {
            apiKeyStatusBox.style.background = 'rgba(239, 68, 68, 0.15)';
            apiKeyStatusBox.style.border = '1px solid rgba(239, 68, 68, 0.4)';
            apiKeyStatusBox.style.color = '#f87171';
            apiKeyStatusBox.textContent = `❌ Test Failed: ${data.message}`;
          }
        }
      } catch (err) {
        if (apiKeyStatusBox) {
          apiKeyStatusBox.style.background = 'rgba(239, 68, 68, 0.15)';
          apiKeyStatusBox.style.border = '1px solid rgba(239, 68, 68, 0.4)';
          apiKeyStatusBox.style.color = '#f87171';
          apiKeyStatusBox.textContent = `❌ Connection Error: ${err.message}`;
        }
      } finally {
        btnTestApiKey.disabled = false;
        btnTestApiKey.textContent = '⚡ Test Key';
      }
    });
  }

  // Aspect Ratio Toggles
  if (btnAspect169 && btnAspect916 && monitorScreen) {
    btnAspect169.addEventListener('click', () => {
      currentAspectRatio = '16:9';
      btnAspect169.classList.add('active');
      btnAspect916.classList.remove('active');
      monitorScreen.classList.remove('vertical-9-16');
    });

    btnAspect916.addEventListener('click', () => {
      currentAspectRatio = '9:16';
      btnAspect916.classList.add('active');
      btnAspect169.classList.remove('active');
      monitorScreen.classList.add('vertical-9-16');
    });
  }

  // Sound effects slider & mute handling
  sfxSlider.addEventListener('input', () => {
    if (muteSfxCheckbox && muteSfxCheckbox.checked) {
      muteSfxCheckbox.checked = false;
    }
    const val = parseInt(sfxSlider.value);
    let desc = 'Subtle Ambience';
    if (val === 0) desc = 'Muted';
    else if (val >= 70) desc = 'Punchy SFX';
    else if (val >= 35) desc = 'Balanced SFX';
    sfxVal.textContent = `${val}% (${desc})`;
  });

  if (muteSfxCheckbox) {
    muteSfxCheckbox.addEventListener('change', () => {
      if (muteSfxCheckbox.checked) {
        sfxVal.textContent = 'Muted (0 SFX)';
      } else {
        const val = parseInt(sfxSlider.value);
        sfxVal.textContent = `${val}% (Subtle Ambience)`;
      }
    });
  }

  // Toggle Script Editor
  btnToggleScriptEditor.addEventListener('click', () => {
    const isHidden = scriptEditorContainer.style.display === 'none';
    scriptEditorContainer.style.display = isHidden ? 'block' : 'none';
    btnToggleScriptEditor.textContent = isHidden ? '✕ Close Editor' : '✏️ Edit Script';
  });

  // Get selected duration in minutes
  function getSelectedDuration() {
    const checked = document.querySelector('input[name="duration"]:checked');
    return checked ? parseInt(checked.value) : 3;
  }

  // Handle Preset Clicks
  const presetCards = document.querySelectorAll('.preset-card');
  presetCards.forEach(card => {
    card.addEventListener('click', () => {
      presetCards.forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      activePreset = card.dataset.preset;

      const nameEl = card.querySelector('.preset-name');
      if (nameEl) {
        topicInput.value = nameEl.textContent;
      }
      customScriptInput.value = '';
      customScriptInput.dataset.presetSync = activePreset;

      // Auto-fetch researched outline for this preset
      fetchOutline();
    });
  });

  // Research Outline Button
  btnResearchOutline.addEventListener('click', () => {
    fetchOutline();
  });

  // Duration pill changes trigger fresh outline preview if topic set
  document.querySelectorAll('input[name="duration"]').forEach(radio => {
    radio.addEventListener('change', () => {
      fetchOutline();
    });
  });

  // Fetch or preview the chapter outline from the backend
  async function fetchOutline() {
    btnResearchOutline.disabled = true;
    btnResearchOutline.textContent = '⏳ Researching...';
    chaptersPreview.innerHTML = `
      <div style="padding: 16px; text-align: center; color: var(--text-muted); font-size: 0.85rem;">
        <span>🔍 AI Historian researching deep multi-chapter outline...</span>
      </div>
    `;

    try {
      const resp = await fetch('/api/documentary/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: topicInput.value.trim(),
          duration_minutes: getSelectedDuration(),
          preset: activePreset,
          api_key: apiKeyInput ? apiKeyInput.value.trim() : "",
          ai_provider: aiProviderSelect ? aiProviderSelect.value : "nvidia",
          api_model: apiModelInput ? apiModelInput.value.trim() : ""
        })
      });

      const data = await resp.json();
      if (data.success && data.outline && data.outline.chapters) {
        if (data.script && (!customScriptInput.value || customScriptInput.dataset.presetSync === activePreset)) {
          customScriptInput.value = data.script;
          customScriptInput.dataset.presetSync = activePreset;
        }
        renderChaptersOutline(data.outline);
      } else {
        showOutlineFallback(data.message || 'Could not retrieve outline');
      }
    } catch (err) {
      console.warn('Research outline error:', err);
      showOutlineFallback('Network or server error while generating outline');
    } finally {
      btnResearchOutline.disabled = false;
      btnResearchOutline.textContent = '🔍 Research Outline';
    }
  }

  function renderChaptersOutline(outline) {
    const chapters = outline.chapters || [];
    let html = '';

    chapters.forEach((ch, idx) => {
      const eraBadge = ch.era ? `<span class="preset-tag" style="font-size:0.65rem;">${escapeHtml(ch.era)}</span>` : '';
      const sceneBadge = ch.scene_type ? `<span style="font-size:0.7rem; color:var(--accent-gold); font-family:monospace;">[Scene: ${escapeHtml(ch.scene_type)}]</span>` : '';
      const snippet = ch.narration ? ch.narration.substring(0, 140) + '...' : (ch.summary || '');

      html += `
        <div style="background: rgba(10, 14, 23, 0.7); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 10px 14px; display: flex; flex-direction: column; gap: 4px;">
          <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px;">
            <strong style="font-size: 0.88rem; color: #ffffff;">${idx + 1}. ${escapeHtml(ch.title || 'Chapter ' + (idx + 1))}</strong>
            <div style="display: flex; align-items: center; gap: 6px;">
              ${eraBadge}
              ${sceneBadge}
            </div>
          </div>
          <p style="font-size: 0.78rem; color: var(--text-muted); line-height: 1.4; margin: 0;">
            ${escapeHtml(snippet)}
          </p>
        </div>
      `;
    });

    chaptersPreview.innerHTML = html;

    // Also populate the scene strip on the right
    populateSceneStrip(chapters);
  }

  function showOutlineFallback(msg) {
    chaptersPreview.innerHTML = `
      <div style="padding: 12px; background: rgba(244, 63, 94, 0.1); border: 1px solid rgba(244, 63, 94, 0.3); border-radius: 8px; font-size: 0.82rem; color: #fda4af;">
        <span>ℹ️ Note: ${escapeHtml(msg)}. Direct 1-Click Launch will synthesize all chapters on the fly!</span>
      </div>
    `;
  }

  function populateSceneStrip(chapters) {
    if (!chapters || chapters.length === 0) return;
    sceneStripCard.style.display = 'block';
    sceneCountBadge.textContent = `${chapters.length} Scenes Directed`;

    const sceneIcons = {
      bastille_fortress: '🏰',
      guillotine_square: '⚖️',
      versailles_palace: '👑',
      french_assembly: '🏛️',
      roman_forum: '🏛️',
      roman_colosseum: '🏟️',
      hastings_battlefield: '⚔️',
      trench_battlefield: '🪖',
      prehistoric_savanna: '🦣',
      masada_fortress: '⛰️',
      fortress_plateau: '⛰️',
      caesarea_harbor: '⚓',
      coastal_harbor: '⚓',
      roman_tent: '⛺',
      military_tent: '⛺',
      cathedral_square: '⛪',
      church_town_square: '⛪',
      burning_ruins: '🔥',
      family_cabin: '🏠',
      countryballs: '🌐',
      countryballs_war: '🌐',
      map: '🗺️',
      ancient_map: '🗺️',
      desert_plains: '🏜️',
      ancient_village: '🏜️',
      throne_room: '👑'
    };

    let stripHtml = '';
    chapters.forEach((ch, idx) => {
      const icon = sceneIcons[ch.scene_type] || '🎬';
      stripHtml += `
        <div class="scene-thumb-card">
          <div style="display: flex; align-items: center; justify-content: space-between;">
            <span>Scene ${idx + 1}</span>
            <span>${icon}</span>
          </div>
          <strong>${escapeHtml(ch.title || 'Act ' + (idx + 1))}</strong>
          <span>${escapeHtml(ch.era || 'Era Pill')}</span>
        </div>
      `;
    });
    sceneStrip.innerHTML = stripHtml;
  }

  // 1-Click Master Launch Button
  btnLaunchDocumentary.addEventListener('click', async () => {
    const topic = topicInput.value.trim();
    if (!topic) {
      showStatus('Please enter a documentary topic or select a preset.', 'error');
      return;
    }

    const isMuted = muteSfxCheckbox && muteSfxCheckbox.checked;
    const computedSfxVol = isMuted ? 0.0 : (parseInt(sfxSlider.value) / 100);
    const useOverrideScript = overrideCustomScriptCheckbox && overrideCustomScriptCheckbox.checked;

    // Prepare Request Payload
    const payload = {
      topic: topic,
      duration_minutes: getSelectedDuration(),
      preset: activePreset,
      voice: voiceSelect ? voiceSelect.value : "en-US-ChristopherNeural",
      aspect_ratio: currentAspectRatio,
      ai_image_provider: aiImageProviderSelect ? aiImageProviderSelect.value : "flux",
      image_style: imageStyleSelect ? imageStyleSelect.value : "cinematic_oil",
      subtitle_style: subtitleStyle ? subtitleStyle.value : "gold_pill",
      sfx_volume: computedSfxVol,
      stamp_dates: toggleDatePill ? toggleDatePill.checked : true,
      include_archive_art: toggleArchiveArt ? toggleArchiveArt.checked : true,
      countryballs: toggleCountryballs ? toggleCountryballs.checked : true,
      custom_script: useOverrideScript ? customScriptInput.value.trim() : "",
      api_key: apiKeyInput ? apiKeyInput.value.trim() : "",
      ai_provider: aiProviderSelect ? aiProviderSelect.value : "nvidia",
      api_model: apiModelInput ? apiModelInput.value.trim() : "",
    };

    // UI Updates to "Producing" State
    btnLaunchDocumentary.disabled = true;
    btnLaunchDocumentary.innerHTML = `<span>⏳ Synthesizing & Rendering Cinema Documentary...</span>`;
    showStatus('', ''); // clear banner

    hudCard.classList.add('active');
    btnDownloadVideo.style.display = 'none';
    hudProgressBar.style.width = '3%';
    hudPct.textContent = '3%';
    hudPhaseLabel.textContent = 'Submitting production order to engine...';
    hudDetailLabel.textContent = 'Initializing Edge Neural Speech & Vector Scene Pipeline...';
    hudStatStage.textContent = 'Initializing';

    liveDot.className = 'live-dot rendering';
    monitorStatusText.textContent = 'CINEMA MONITOR — PRODUCING DOCUMENTARY';

    jobStartTime = Date.now();
    startElapsedTimer();

    try {
      const resp = await fetch('/api/documentary/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await resp.json();
      if (!resp.ok || !data.success) {
        throw new Error(data.error || data.message || 'Failed to start generation job');
      }

      activeJobId = data.job_id;
      showStatus(`Production started (Job ID: ${activeJobId}). Automated engine running...`, 'success');

      // Start polling
      startPolling(activeJobId);

    } catch (err) {
      console.error('Launch documentary error:', err);
      showStatus(`Error starting generation: ${err.message}`, 'error');
      resetLaunchButton();
      stopTimers();
      liveDot.className = 'live-dot';
      monitorStatusText.textContent = 'CINEMA MONITOR — ERROR';
    }
  });

  // Polling Job Status
  function startPolling(jobId) {
    if (pollInterval) clearInterval(pollInterval);

    pollInterval = setInterval(async () => {
      try {
        const resp = await fetch(`/api/jobs/${jobId}`);
        if (!resp.ok) return;

        const job = await resp.json();
        updateHUDWithJob(job);

        if (job.status === 'done' || job.status === 'completed') {
          handleJobComplete(job);
        } else if (job.status === 'error' || job.status === 'failed') {
          handleJobError(job);
        }
      } catch (err) {
        console.warn('Poll error:', err);
      }
    }, 1000);
  }

  // Update HUD elements
  function updateHUDWithJob(job) {
    const pct = Math.min(100, Math.max(0, Math.round(job.progress || 0)));
    hudProgressBar.style.width = `${pct}%`;
    hudPct.textContent = `${pct}%`;

    const stageNames = {
      'starting': 'Starting Production Engine',
      'researching': 'AI Historian: Writing Chapter Scripts & Prompts',
      'scripting': 'Synthesizing Dialogues & Dialogue Hooks',
      'voice_synthesis': 'Generating Edge Neural TTS & Viseme Sync',
      'synthesizing_audio': 'Synthesizing Neural Narration & SFX',
      'directing_scenes': 'Directing Scene Staging & Character Visemes',
      'rendering_frames': 'Rendering 1080p Vector Backgrounds & Puppets',
      'compositing': 'Compositing Subtitles, Date Badges & Visuals',
      'muxing_video': 'FFmpeg Multi-Track Assembly (Video + Speech + SFX)',
      'finalizing': 'Finalizing MP4 Master Export',
      'done': 'Production Master Complete',
      'completed': 'Production Master Complete'
    };

    const friendlyStage = stageNames[job.stage] || job.stage || 'Processing...';
    hudPhaseLabel.textContent = friendlyStage;
    hudDetailLabel.textContent = job.message || 'Executing automated video synthesis pipeline...';
    hudStatStage.textContent = job.stage || 'Processing';

    // Calculate Estimated Remaining Time
    if (jobStartTime && pct > 5 && pct < 100) {
      const elapsedSec = (Date.now() - jobStartTime) / 1000;
      const totalEstimatedSec = elapsedSec / (pct / 100);
      const remainingSec = Math.max(0, Math.round(totalEstimatedSec - elapsedSec));
      hudStatEst.textContent = formatTime(remainingSec);
    }
  }

  // Handle Successful Generation
  function handleJobComplete(job) {
    stopTimers();
    resetLaunchButton();

    hudProgressBar.style.width = '100%';
    hudPct.textContent = '100%';
    hudPhaseLabel.textContent = '✨ 100% Complete — Full Cinema Master Ready';
    hudDetailLabel.textContent = 'Video, audio, subtitles and lip-sync puppet tracks assembled cleanly.';
    hudStatEst.textContent = 'Done!';

    liveDot.className = 'live-dot ready';
    monitorStatusText.textContent = 'CINEMA MONITOR — PLAYBACK READY';

    // Determine Video URL
    let videoUrl = job.video_url;
    if (!videoUrl && job.video_filename) {
      videoUrl = `/api/video/${job.video_filename}`;
    }
    if (!videoUrl && job.output_video) {
      const fname = job.output_video.replace(/\\/g, '/').split('/').pop();
      videoUrl = `/api/video/${fname}`;
    }

    if (videoUrl) {
      monitorPlaceholder.style.display = 'none';
      cinemaVideo.style.display = 'block';
      cinemaVideo.src = videoUrl;
      cinemaVideo.load();
      cinemaVideo.play().catch(e => console.log('Autoplay deferred:', e));

      btnDownloadVideo.href = videoUrl;
      btnDownloadVideo.style.display = 'inline-flex';
      btnDownloadVideo.download = job.video_filename || 'animated_history_documentary.mp4';
    }

    showStatus('🎉 Full Long-form Documentary generated successfully! Ready to watch & download.', 'success');
  }

  // Handle Job Failure
  function handleJobError(job) {
    stopTimers();
    resetLaunchButton();

    liveDot.className = 'live-dot';
    monitorStatusText.textContent = 'CINEMA MONITOR — GENERATION FAILED';
    hudPhaseLabel.textContent = '❌ Generation Stopped';
    hudDetailLabel.textContent = job.error || 'An error occurred during video rendering.';
    showStatus(`Generation failed: ${job.error || 'Unknown error'}`, 'error');
  }

  // Cancel Job Button
  btnCancelJob.addEventListener('click', async () => {
    if (!activeJobId) return;
    if (!confirm('Are you sure you want to cancel the documentary generation?')) return;

    try {
      await fetch(`/api/jobs/${activeJobId}/cancel`, { method: 'POST' });
    } catch (e) {
      console.warn('Cancel fetch failed:', e);
    }

    stopTimers();
    resetLaunchButton();
    hudPhaseLabel.textContent = 'Production Cancelled';
    hudDetailLabel.textContent = 'Job was cancelled by the user.';
    showStatus('Generation was cancelled.', 'error');
  });

  // Timers and Helpers
  function startElapsedTimer() {
    if (elapsedTimer) clearInterval(elapsedTimer);
    hudStatElapsed.textContent = '00:00';
    elapsedTimer = setInterval(() => {
      if (!jobStartTime) return;
      const sec = Math.round((Date.now() - jobStartTime) / 1000);
      hudStatElapsed.textContent = formatTime(sec);
    }, 1000);
  }

  function stopTimers() {
    if (pollInterval) {
      clearInterval(pollInterval);
      pollInterval = null;
    }
    if (elapsedTimer) {
      clearInterval(elapsedTimer);
      elapsedTimer = null;
    }
  }

  function resetLaunchButton() {
    btnLaunchDocumentary.disabled = false;
    btnLaunchDocumentary.innerHTML = `<span>🚀 Generate Full Documentary Video (1-Click)</span>`;
  }

  function formatTime(totalSec) {
    const mins = Math.floor(totalSec / 60);
    const secs = totalSec % 60;
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  }

  function showStatus(msg, type) {
    if (!msg) {
      statusBanner.style.display = 'none';
      return;
    }
    statusBanner.style.display = 'flex';
    statusBanner.className = `status-banner ${type}`;
    statusBanner.textContent = msg;
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // On page load, fetch initial outline for default preset
  fetchOutline();
});
