const studioForm = document.querySelector('#studio-form');
const autoPipelineCard = document.querySelector('#auto-pipeline-card');
const manualPipelineCard = document.querySelector('#manual-pipeline-card');

// Mode selectors
const genmodeAuto = document.querySelector('#genmode-auto');
const genmodeManual = document.querySelector('#genmode-manual');

// Auto mode elements
const autoTopic = document.querySelector('#auto-topic');
const autoVoice = document.querySelector('#auto-voice');
const autoDuration = document.querySelector('#auto-duration');
const autoScript = document.querySelector('#auto-script');
const btnGenerateScript = document.querySelector('#btn-generate-script');
const autovisAuto = document.querySelector('#autovis-auto');
const autovisCustom = document.querySelector('#autovis-custom');
const autoCustomImagesContainer = document.querySelector('#auto-custom-images-container');
const autoImageFolder = document.querySelector('#auto-image-folder');
const autoImageSummary = document.querySelector('#auto-image-summary');

// Manual mode elements
const imageFolder = document.querySelector('#pro-image-folder');
const srtFile = document.querySelector('#pro-srt-file');
const audioFile = document.querySelector('#pro-audio-file');
const imageSummary = document.querySelector('#pro-image-summary');
const srtSummary = document.querySelector('#pro-srt-summary');
const audioSummary = document.querySelector('#pro-audio-summary');
const bundledSfxContainer = document.querySelector('#pro-bundled-sfx');
const emotionSfxVolSlider = document.querySelector('#emotion-sfx-volume');
const emotionSfxVolLabel = document.querySelector('#emotion-sfx-vol-label');
if (emotionSfxVolSlider && emotionSfxVolLabel) {
  emotionSfxVolSlider.addEventListener('input', () => {
    const val = parseFloat(emotionSfxVolSlider.value);
    const pct = Math.round(val * 100);
    let desc = 'Quiet & Subtle';
    if (pct === 0) desc = 'Muted';
    else if (pct <= 10) desc = 'Very Quiet';
    else if (pct <= 20) desc = 'Quiet & Subtle';
    else if (pct <= 40) desc = 'Balanced';
    else desc = 'Loud';
    emotionSfxVolLabel.textContent = `${pct}% (${desc})`;
  });
}

const popupSfxVolSlider = document.querySelector('#popup-sfx-volume');
const popupSfxVolLabel = document.querySelector('#popup-sfx-vol-label');
if (popupSfxVolSlider && popupSfxVolLabel) {
  popupSfxVolSlider.addEventListener('input', () => {
    const val = parseFloat(popupSfxVolSlider.value);
    const pct = Math.round(val * 100);
    let desc = 'Standard';
    if (pct === 0) desc = 'Muted';
    else if (pct <= 15) desc = 'Very Quiet';
    else if (pct <= 30) desc = 'Subtle';
    else if (pct <= 55) desc = 'Standard';
    else desc = 'Loud';
    popupSfxVolLabel.textContent = `${pct}% (${desc})`;
  });
}

// Deck buttons & monitors
const btnRender = document.querySelector('#btn-render-master');
const btnCancel = document.querySelector('#btn-cancel-render');
const btnDownload = document.querySelector('#btn-download-master');
const btnClearCache = document.querySelector('#btn-clear-cache');

const monitorDot = document.querySelector('#monitor-dot');
const monitorStatusText = document.querySelector('#monitor-status-text');
const monitorResolution = document.querySelector('#monitor-resolution');
const monitorContainer = document.querySelector('#monitor-container');
const monitorEmpty = document.querySelector('#monitor-empty');
const videoPreview = document.querySelector('#pro-video-preview');

const statImages = document.querySelector('#stat-images');
const statCues = document.querySelector('#stat-cues');
const statDuration = document.querySelector('#stat-duration');

const hudPanel = document.querySelector('#hud-panel');
const hudBar = document.querySelector('#hud-bar');
const hudPhase = document.querySelector('#hud-phase');
const hudPercent = document.querySelector('#hud-percent');
const hudDetail = document.querySelector('#hud-detail');
const statusMessage = document.querySelector('#status-message');

const enableSubtitles = document.querySelector('#enable-subtitles');
const subtitlePanel = document.querySelector('#subtitle-options-panel');
const enablePopups = document.querySelector('#enable-popups');
const popupPanel = document.querySelector('#popup-options-panel');
const aiProvider = document.querySelector('#ai-provider');
const bytezBox = document.querySelector('#bytez-box');

let activeJobId = null;
let pollInterval = null;
let currentCuesCount = 0;
const supportedImageExtensions = new Set(['.jpg', '.jpeg', '.png', '.webp', '.bmp']);

// 1. Pipeline Mode Switcher
function updatePipelineMode() {
  const isAuto = genmodeAuto.checked;
  if (isAuto) {
    autoPipelineCard.style.display = 'block';
    manualPipelineCard.style.display = 'none';
    btnRender.innerHTML = '<span>🚀</span><span>Generate 1-Click Auto Video</span>';
  } else {
    autoPipelineCard.style.display = 'none';
    manualPipelineCard.style.display = 'block';
    btnRender.innerHTML = '<span>🚀</span><span>Render Pro Video</span>';
  }
}

genmodeAuto.addEventListener('change', updatePipelineMode);
genmodeManual.addEventListener('change', updatePipelineMode);

// Visual mode in auto pipeline
autovisAuto.addEventListener('change', () => {
  autoCustomImagesContainer.style.display = 'none';
});
autovisCustom.addEventListener('change', () => {
  autoCustomImagesContainer.style.display = 'block';
});

// Auto image folder change
autoImageFolder.addEventListener('change', () => {
  const files = [...(autoImageFolder.files || [])].filter(f => supportedImageExtensions.has(f.name.slice(f.name.lastIndexOf('.')).toLowerCase()));
  if (files.length > 0) {
    autoImageSummary.textContent = `✓ ${files.length} custom images selected`;
    autoImageSummary.classList.add('ready');
  } else {
    autoImageSummary.textContent = 'Cycles images across generated cues';
    autoImageSummary.classList.remove('ready');
  }
});

// 2. Fetch Curated Neural Voices
fetch('/api/voices', { cache: 'no-store' })
  .then(res => res.json())
  .then(voices => {
    if (Array.isArray(voices) && voices.length > 0) {
      autoVoice.innerHTML = '';
      voices.forEach(v => {
        const opt = document.createElement('option');
        opt.value = v.id;
        opt.textContent = `${v.name} • ${v.desc}`;
        if (v.id === 'en-US-ChristopherNeural') opt.selected = true;
        autoVoice.appendChild(opt);
      });
    }
  })
  .catch(() => {});

// 3. Preview AI Script Generator
btnGenerateScript.addEventListener('click', async () => {
  const topic = autoTopic.value.trim();
  if (!topic) {
    showStatus('Please enter a topic or title first.');
    return;
  }

  btnGenerateScript.disabled = true;
  btnGenerateScript.textContent = '⏳ Researching & Writing...';

  try {
    const res = await fetch('/api/auto-script', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: topic,
        duration_minutes: parseFloat(autoDuration.value) || 1.0,
        provider: aiProvider.value,
        api_key: document.querySelector('#api-key').value.trim(),
        api_model: document.querySelector('#api-model').value.trim(),
      })
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to write script' }));
      throw new Error(err.detail);
    }

    const data = await res.json();
    autoScript.value = data.script;
    showStatus('AI script generated successfully! You can review or edit it above.', 'success');
  } catch (err) {
    showStatus('Error generating script: ' + err.message, 'error');
  } finally {
    btnGenerateScript.disabled = false;
    btnGenerateScript.textContent = '✍️ Preview AI Script';
  }
});

// 4. Natural Sort Helper
function naturalFileOrder(left, right) {
  const leftParts = left.name.split(/(\d+)/);
  const rightParts = right.name.split(/(\d+)/);
  for (let index = 0; index < Math.max(leftParts.length, rightParts.length); index += 1) {
    const leftPart = leftParts[index] || '';
    const rightPart = rightParts[index] || '';
    const leftNumber = Number(leftPart);
    const rightNumber = Number(rightPart);
    if (!Number.isNaN(leftNumber) && !Number.isNaN(rightNumber)) {
      if (leftNumber !== rightNumber) return leftNumber - rightNumber;
    } else if (leftPart.toLowerCase() !== rightPart.toLowerCase()) {
      return leftPart.toLowerCase().localeCompare(rightPart.toLowerCase());
    }
  }
  return left.name.localeCompare(right.name);
}

function getSupportedImages(inputEl = imageFolder) {
  if (!inputEl.files) return [];
  return [...inputEl.files].filter((file) => {
    const extension = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();
    return supportedImageExtensions.has(extension);
  });
}

// 5. Aspect Ratio Sync
function updateAspectRatio() {
  const ratio = document.querySelector('input[name="aspect_ratio"]:checked').value;
  if (ratio === '9:16') {
    monitorContainer.style.aspectRatio = '9 / 16';
    monitorContainer.style.maxWidth = '360px';
    monitorContainer.style.margin = '0 auto';
    monitorResolution.textContent = '1080x1920 (9:16)';
  } else {
    monitorContainer.style.aspectRatio = '16 / 9';
    monitorContainer.style.maxWidth = '100%';
    monitorContainer.style.margin = '0';
    monitorResolution.textContent = '1920x1080 (16:9)';
  }
}

document.querySelectorAll('input[name="aspect_ratio"]').forEach(radio => {
  radio.addEventListener('change', updateAspectRatio);
});

// UI Toggles
enableSubtitles.addEventListener('change', () => {
  subtitlePanel.style.display = enableSubtitles.checked ? 'flex' : 'none';
});

enablePopups.addEventListener('change', () => {
  popupPanel.style.display = enablePopups.checked ? 'flex' : 'none';
});

aiProvider.addEventListener('change', () => {
  bytezBox.style.display = aiProvider.value === 'bytez' ? 'block' : 'none';
});

// Manual File listeners
imageFolder.addEventListener('change', () => {
  const validImages = getSupportedImages(imageFolder);
  if (validImages.length === 0) {
    imageSummary.textContent = 'No supported images found in folder.';
    imageSummary.classList.remove('ready');
    statImages.textContent = '0';
  } else {
    imageSummary.textContent = `✓ ${validImages.length} images loaded & sorted`;
    imageSummary.classList.add('ready');
    statImages.textContent = validImages.length.toString();
  }
});

srtFile.addEventListener('change', async () => {
  const file = srtFile.files?.[0];
  if (!file) return;
  try {
    const text = await file.text();
    const timestampPattern = /(\d{2}:\d{2}:\d{2}[,.]\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2}[,.]\d{3})/g;
    const matches = [...text.matchAll(timestampPattern)];
    currentCuesCount = matches.length;
    statCues.textContent = currentCuesCount.toString();
    srtSummary.textContent = `✓ ${file.name} (${currentCuesCount} cues)`;
    srtSummary.classList.add('ready');

    if (matches.length > 0) {
      const lastMatch = matches[matches.length - 1];
      const endTimestamp = lastMatch[2];
      const parts = endTimestamp.replace(',', '.').split(':');
      const totalSec = Math.round(Number(parts[0]) * 3600 + Number(parts[1]) * 60 + Number(parts[2]));
      const mins = Math.floor(totalSec / 60);
      const secs = totalSec % 60;
      statDuration.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;
    }
  } catch (e) {
    srtSummary.textContent = 'Error parsing SRT file.';
  }
});

audioFile.addEventListener('change', () => {
  const file = audioFile.files?.[0];
  if (file) {
    audioSummary.textContent = `✓ ${file.name} ready`;
    audioSummary.classList.add('ready');
  } else {
    audioSummary.textContent = 'Audio loops to video duration or trims cleanly';
    audioSummary.classList.remove('ready');
  }
});

// Fetch SFX List
fetch('/api/sfx', { cache: 'no-store' })
  .then(res => res.json())
  .then(sfxFiles => {
    bundledSfxContainer.innerHTML = '';
    if (!sfxFiles || sfxFiles.length === 0) {
      bundledSfxContainer.innerHTML = '<span style="color: var(--text-dim); font-size: 0.75rem;">No built-in sounds found.</span>';
      return;
    }
    sfxFiles.forEach((file, index) => {
      const row = document.createElement('label');
      row.style.display = 'flex';
      row.style.alignItems = 'center';
      row.style.gap = '8px';
      row.style.fontSize = '0.78rem';
      row.style.color = '#cbd5e1';
      row.style.cursor = 'pointer';

      const input = document.createElement('input');
      input.type = 'checkbox';
      input.name = 'bundled_sfx_files';
      input.value = file;
      input.style.accentColor = 'var(--accent-cyan)';
      const isCamera = file.toLowerCase().includes('camera') || file.toLowerCase().includes('shutter');
      input.checked = isCamera;

      row.appendChild(input);
      const icon = isCamera ? '📷 ' : '🔊 ';
      row.appendChild(document.createTextNode(icon + file));
      bundledSfxContainer.appendChild(row);
    });
  })
  .catch(() => {});

// Clear AI Cache
btnClearCache.addEventListener('click', async () => {
  try {
    const res = await fetch('/api/clear-cache', { method: 'POST' });
    if (res.ok) {
      showStatus('AI response cache cleared successfully.', 'success');
    }
  } catch (e) {
    showStatus('Failed to clear cache: ' + e.message, 'error');
  }
});

function showStatus(msg, type = 'error') {
  statusMessage.textContent = msg;
  statusMessage.className = `status-banner ${type}`;
  statusMessage.style.display = 'flex';
  if (type === 'success') {
    setTimeout(() => { statusMessage.style.display = 'none'; }, 4000);
  }
}

// 6. Submit Master Video (Auto or Manual)
btnRender.addEventListener('click', async (e) => {
  e.preventDefault();
  const isAuto = genmodeAuto.checked;
  const ratio = document.querySelector('input[name="aspect_ratio"]:checked').value;
  const formData = new FormData();

  formData.append('aspect_ratio', ratio);
  formData.append('motion_style', document.querySelector('#motion-style').value);
  formData.append('zoom_intensity', document.querySelector('#zoom-intensity').value);
  formData.append('bg_mode', document.querySelector('#bg-mode').value);
  formData.append('enable_subtitles', enableSubtitles.checked ? 'true' : 'false');
  formData.append('subtitle_style', document.querySelector('#subtitle-style').value);
  formData.append('subtitle_position', document.querySelector('#subtitle-position').value);
  formData.append('subtitle_font_size', document.querySelector('#subtitle-font-size').value);
  formData.append('gpu_accel', document.querySelector('#gpu-accel').value);
  formData.append('parallel_workers', document.querySelector('#parallel-workers').value);

  document.querySelectorAll('input[name="bundled_sfx_files"]:checked').forEach(cb => {
    formData.append('bundled_sfx', cb.value);
  });

  formData.append('ai_provider', aiProvider.value);
  formData.append('api_key', document.querySelector('#api-key').value.trim());
  formData.append('api_model', document.querySelector('#api-model').value.trim());
  formData.append('enable_popups', enablePopups.checked ? 'true' : 'false');
  formData.append('popup_prompt', document.querySelector('#popup-prompt').value.trim());
  const emotionSfxVol = emotionSfxVolSlider ? emotionSfxVolSlider.value : '0.15';
  formData.append('emotion_sfx_volume', emotionSfxVol);
  const popupSfxVol = popupSfxVolSlider ? popupSfxVolSlider.value : '0.40';
  formData.append('popup_sfx_volume', popupSfxVol);

  let targetEndpoint = '/api/generate';

  if (isAuto) {
    const topic = autoTopic.value.trim();
    const script = autoScript.value.trim();
    if (!topic && !script) {
      showStatus('Please enter a story topic or paste a script in the auto pipeline box.');
      return;
    }

    targetEndpoint = '/api/generate-auto';
    formData.append('topic', topic);
    formData.append('script_text', script);
    formData.append('voice', autoVoice.value);
    formData.append('duration_minutes', autoDuration.value);

    // Optional custom images
    if (autovisCustom.checked) {
      const customImages = getSupportedImages(autoImageFolder);
      customImages.sort(naturalFileOrder);
      customImages.forEach(img => formData.append('custom_images', img));
    }
  } else {
    // Manual Mode Validation
    const validImages = getSupportedImages(imageFolder);
    if (validImages.length === 0) {
      showStatus('Please select an image folder.');
      return;
    }
    const srt = srtFile.files?.[0];
    if (!srt) {
      showStatus('Please select an SRT subtitle file.');
      return;
    }

    validImages.sort(naturalFileOrder);
    formData.append('srt_file', srt);
    validImages.forEach(img => formData.append('images', img));

    if (audioFile.files?.[0]) {
      formData.append('audio_file', audioFile.files[0]);
    }
    formData.append('apply_zoom', 'true');
  }

  // UI State: Starting Render
  statusMessage.style.display = 'none';
  btnRender.disabled = true;
  btnRender.innerHTML = '<span>⏳</span><span>Starting Generation...</span>';
  btnCancel.style.display = 'block';
  btnDownload.style.display = 'none';

  hudPanel.style.display = 'flex';
  hudBar.style.width = '3%';
  hudPercent.textContent = '3%';
  hudPhase.textContent = isAuto ? 'Initiating 1-Click Story Engine...' : 'Connecting to Render Engine...';
  hudDetail.textContent = isAuto ? 'Generating voiceover, timing cues & visuals...' : 'Uploading media assets...';

  monitorDot.className = 'live-dot rendering';
  monitorStatusText.textContent = 'RENDERING IN PROGRESS...';
  monitorEmpty.style.display = 'flex';
  videoPreview.hidden = true;

  try {
    const res = await fetch(targetEndpoint, {
      method: 'POST',
      body: formData
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Server error' }));
      throw new Error(err.detail || 'Could not start generation.');
    }

    const data = await res.json();
    activeJobId = data.job_id;
    startPolling(activeJobId);
  } catch (err) {
    resetRenderUI();
    showStatus('Error starting generation: ' + err.message, 'error');
  }
});

// 7. Polling Job Progress
function startPolling(jobId) {
  if (pollInterval) clearInterval(pollInterval);

  pollInterval = setInterval(async () => {
    try {
      const res = await fetch(`/api/jobs/${jobId}`, { cache: 'no-store' });
      if (!res.ok) throw new Error('Job lost');

      const job = await res.json();
      const progress = job.progress || 0;
      hudBar.style.width = `${progress}%`;
      hudPercent.textContent = `${progress}%`;
      hudPhase.textContent = job.phase || 'Rendering...';

      if (job.total_images > 0) {
        statImages.textContent = job.total_images.toString();
        statCues.textContent = job.total_images.toString();
      }
      
      if (job.current_filename) {
        hudDetail.textContent = `Processing image ${job.current_image} of ${job.total_images}: ${job.current_filename}`;
      } else {
        hudDetail.textContent = job.phase;
      }

      if (job.state === 'complete') {
        clearInterval(pollInterval);
        handleComplete(jobId);
      } else if (job.state === 'error') {
        clearInterval(pollInterval);
        resetRenderUI();
        showStatus('Render Error: ' + (job.error || 'Unknown failure'), 'error');
      } else if (job.state === 'canceled') {
        clearInterval(pollInterval);
        resetRenderUI();
        showStatus('Render canceled by user.', 'error');
      }
    } catch (e) {
      // Continue polling
    }
  }, 750);
}

function handleComplete(jobId) {
  btnRender.disabled = false;
  btnRender.innerHTML = genmodeAuto.checked
    ? '<span>🚀</span><span>Generate 1-Click Auto Video</span>'
    : '<span>🚀</span><span>Render Pro Video</span>';
  btnCancel.style.display = 'none';

  hudBar.style.width = '100%';
  hudPercent.textContent = '100%';
  hudPhase.textContent = 'Master Render Complete!';
  hudDetail.textContent = 'Video successfully generated and encoded.';

  monitorDot.className = 'live-dot active';
  monitorStatusText.textContent = 'MASTER READY FOR PLAYBACK';

  const downloadUrl = `/api/jobs/${jobId}/download?t=${Date.now()}`;
  videoPreview.src = downloadUrl;
  videoPreview.hidden = false;
  monitorEmpty.style.display = 'none';

  btnDownload.style.display = 'flex';
  btnDownload.onclick = () => {
    window.location.href = downloadUrl;
  };
}

// 8. Cancel Render
btnCancel.addEventListener('click', async () => {
  if (!activeJobId) return;
  btnCancel.disabled = true;
  btnCancel.textContent = 'Aborting...';
  try {
    await fetch(`/api/jobs/${activeJobId}/cancel`, { method: 'POST' });
  } catch (e) {}
  setTimeout(() => {
    resetRenderUI();
  }, 1000);
});

function resetRenderUI() {
  btnRender.disabled = false;
  btnRender.innerHTML = genmodeAuto.checked
    ? '<span>🚀</span><span>Generate 1-Click Auto Video</span>'
    : '<span>🚀</span><span>Render Pro Video</span>';
  btnCancel.style.display = 'none';
  btnCancel.disabled = false;
  btnCancel.textContent = '⏹️ Abort Generation';
  monitorDot.className = 'live-dot';
  monitorStatusText.textContent = 'STUDIO MONITOR READY';
}

updateAspectRatio();
updatePipelineMode();

// 9. Stickman & Channel Assets Management
const channelAssetsGrid = document.querySelector('#channel-assets-grid');
const channelAssetCount = document.querySelector('#channel-asset-count');
const customAssetUpload = document.querySelector('#custom-asset-upload');

async function loadChannelAssets() {
  if (!channelAssetsGrid) return;
  try {
    const res = await fetch('/api/channel-assets', { cache: 'no-store' });
    if (!res.ok) return;
    const data = await res.json();
    channelAssetsGrid.innerHTML = '';
    channelAssetCount.textContent = `${data.count} Characters Active`;

    data.assets.forEach(asset => {
      const card = document.createElement('div');
      card.style.cssText = 'background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 6px; padding: 6px; display: flex; flex-direction: column; align-items: center; gap: 4px; text-align: center;';

      const img = document.createElement('img');
      img.src = asset.url;
      img.alt = asset.name;
      img.style.cssText = 'width: 44px; height: 44px; object-fit: contain; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.4));';
      img.loading = 'lazy';

      const label = document.createElement('span');
      label.textContent = asset.name.replace('stickman_', '');
      label.style.cssText = 'font-size: 0.62rem; color: #e2e8f0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 68px; font-weight: 500;';

      if (asset.is_custom) {
        const customBadge = document.createElement('span');
        customBadge.textContent = 'CUSTOM';
        customBadge.style.cssText = 'font-size: 0.55rem; color: #10b981; background: rgba(16, 185, 129, 0.2); padding: 1px 4px; border-radius: 3px; font-weight: 700;';
        card.appendChild(customBadge);
      }

      card.appendChild(img);
      card.appendChild(label);
      channelAssetsGrid.appendChild(card);
    });
  } catch (e) {
    console.error('Error loading channel assets:', e);
  }
}

if (customAssetUpload) {
  customAssetUpload.addEventListener('change', async () => {
    const files = [...(customAssetUpload.files || [])];
    if (files.length === 0) return;

    for (const file of files) {
      const formData = new FormData();
      formData.append('asset_file', file);
      try {
        const res = await fetch('/api/upload-channel-asset', {
          method: 'POST',
          body: formData
        });
        if (res.ok) {
          showStatus(`✓ Uploaded custom asset: ${file.name}`, 'success');
        }
      } catch (err) {
        showStatus(`Upload failed for ${file.name}: ${err.message}`, 'error');
      }
    }
    loadChannelAssets();
  });
}

loadChannelAssets();

// 10. Interactive User Manual Modal
const btnOpenManual = document.querySelector('#btn-open-manual');
const manualModal = document.querySelector('#manual-modal');
const btnCloseManual = document.querySelector('#btn-close-manual');
const btnCloseManualFooter = document.querySelector('#btn-close-manual-footer');

function toggleManualModal(show) {
  if (!manualModal) return;
  manualModal.style.display = show ? 'flex' : 'none';
  document.body.style.overflow = show ? 'hidden' : '';
}

if (btnOpenManual) {
  btnOpenManual.addEventListener('click', (e) => {
    e.preventDefault();
    toggleManualModal(true);
  });
}

[btnCloseManual, btnCloseManualFooter].forEach((btn) => {
  if (btn) {
    btn.addEventListener('click', () => toggleManualModal(false));
  }
});

if (manualModal) {
  manualModal.addEventListener('click', (e) => {
    if (e.target === manualModal) toggleManualModal(false);
  });
}

window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && manualModal && manualModal.style.display === 'flex') {
    toggleManualModal(false);
  }
});
