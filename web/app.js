const form = document.querySelector('#generator-form');
const imageFolder = document.querySelector('#image-folder');
const srtFile = document.querySelector('#srt-file');
const audioFile = document.querySelector('#audio-file');
const applyZoom = document.querySelector('#apply-zoom');
const bundledSfxContainer = document.querySelector('#bundled-sfx-container');
const customSfx = document.querySelector('#custom-sfx');
const customIntensity = document.querySelector('#custom-intensity');
const emotionSfxVolume = document.querySelector('#emotion-sfx-volume');
const emotionSfxVolLabel = document.querySelector('#emotion-sfx-vol-label');
if (emotionSfxVolume && emotionSfxVolLabel) {
  emotionSfxVolume.addEventListener('input', () => {
    const val = parseFloat(emotionSfxVolume.value);
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

const popupSfxVolume = document.querySelector('#popup-sfx-volume');
const popupSfxVolLabel = document.querySelector('#popup-sfx-vol-label');
if (popupSfxVolume && popupSfxVolLabel) {
  popupSfxVolume.addEventListener('input', () => {
    const val = parseFloat(popupSfxVolume.value);
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

const colorBoostSlider = document.querySelector('#color-boost-slider');
const colorBoostBadge = document.querySelector('#color-boost-badge');

function updateColorEnhanceUI() {
  if (!colorBoostSlider || !colorBoostBadge) return;
  const val = parseInt(colorBoostSlider.value, 10);
  let desc = 'Cinematic';
  if (val <= 75) desc = 'Soft / Muted';
  else if (val <= 95) desc = 'Natural';
  else if (val <= 125) desc = 'Cinematic';
  else if (val <= 160) desc = 'Vivid Film';
  else desc = 'Ultra Pop';
  colorBoostBadge.textContent = `${val}% (${desc})`;

  if (videoPreview) {
    const sat = val / 100;
    const con = 1 + (val - 100) * 0.003;
    videoPreview.style.filter = `saturate(${sat}) contrast(${con})`;
  }
}

if (colorBoostSlider) {
  colorBoostSlider.addEventListener('input', updateColorEnhanceUI);
  document.querySelectorAll('.btn-color-preset').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetVal = btn.getAttribute('data-val');
      if (targetVal) {
        colorBoostSlider.value = targetVal;
        updateColorEnhanceUI();
      }
    });
  });
}
const aiProvider = document.querySelector('#ai-provider');
const apiKey = document.querySelector('#api-key');
const bytezModelContainer = document.querySelector('#bytez-model-container');
const apiModel = document.querySelector('#api-model');
const enablePopups = document.querySelector('#enable-popups');
const popupPrompt = document.querySelector('#popup-prompt');
const customPopups = document.querySelector('#custom-popups');
const customPopupSfx = document.querySelector('#custom-popup-sfx');
const imageSummary = document.querySelector('#image-summary');
const srtSummary = document.querySelector('#srt-summary');
const audioSummary = document.querySelector('#audio-summary');
const button = document.querySelector('#generate-button');
const cancelButton = document.querySelector('#cancel-button');
const status = document.querySelector('#status');
const progressPanel = document.querySelector('#progress-panel');
const progressBar = document.querySelector('#progress-bar');
const progressPercent = document.querySelector('#progress-percent');
const progressLabel = document.querySelector('#progress-label');
const progressDetail = document.querySelector('#progress-detail');
const appName = document.querySelector('#app-name');
const appDescription = document.querySelector('#app-description');
const previewEmpty = document.querySelector('#preview-empty');
const videoPreview = document.querySelector('#video-preview');
const previewState = document.querySelector('#preview-state');
const downloadButton = document.querySelector('#download-button');
let activeJobId = null;
let previewUrl = null;
let previewFilename = 'generated_video.mp4';
const supportedImageExtensions = new Set(['.jpg', '.jpeg', '.png', '.webp', '.bmp']);

function getSupportedImages() {
  return [...imageFolder.files].filter((file) => {
    const extension = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();
    return supportedImageExtensions.has(extension);
  });
}

async function countSrtCues(file) {
  const text = await file.text();
  const timestampPattern = /\d{2}:\d{2}:\d{2}[,.]\d{3}\s+-->\s+\d{2}:\d{2}:\d{2}[,.]\d{3}/g;
  return text.match(timestampPattern)?.length || 0;
}

function updatePreviewAspectRatio() {
  const ratio = document.querySelector('input[name="aspect_ratio"]:checked').value;
  const cssRatio = ratio === '9:16' ? '1 / 1' : '16 / 9';
  videoPreview.style.aspectRatio = cssRatio;
  previewEmpty.style.aspectRatio = cssRatio;
}

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

fetch('/api/version', { cache: 'no-store' })
  .then((response) => response.json())
  .then(({ name, description, version }) => {
    appName.textContent = name;
    appDescription.textContent = description;
    document.title = name;
    document.querySelector('#app-version').textContent = `v${version}`;
  })
  .catch(() => {});

fetch('/api/sfx', { cache: 'no-store' })
  .then(res => res.json())
  .then(sfxFiles => {
    if (sfxFiles.length === 0) {
      bundledSfxContainer.innerHTML = '<span class="hint">No built-in sounds found.</span>';
      return;
    }
    sfxFiles.forEach((file, index) => {
      const label = document.createElement('label');
      label.className = 'checkbox-row';
      const input = document.createElement('input');
      input.type = 'checkbox';
      input.name = 'bundled_sfx_files';
      input.value = file;
      const isCamera = file.toLowerCase().includes('camera') || file.toLowerCase().includes('shutter');
      input.checked = isCamera;
      const span = document.createElement('span');
      const icon = isCamera ? '📷 ' : '';
      span.textContent = icon + file;
      label.appendChild(input);
      label.appendChild(span);
      bundledSfxContainer.appendChild(label);
    });
  })
  .catch(() => {});

const bundledPopupSfxContainer = document.querySelector('#bundled-popup-sfx-container');
const btnSelectAllPopups = document.querySelector('#btn-select-all-popups');
const btnDeselectAllPopups = document.querySelector('#btn-deselect-all-popups');

let activeAudio = null;
function playSoundPreview(url) {
  if (activeAudio) {
    activeAudio.pause();
    activeAudio.currentTime = 0;
  }
  activeAudio = new Audio(url);
  activeAudio.play().catch(() => {});
}

fetch('/api/popup-sfx', { cache: 'no-store' })
  .then(res => res.json())
  .then(items => {
    if (!bundledPopupSfxContainer) return;
    if (items.length === 0) {
      bundledPopupSfxContainer.innerHTML = '<span class="hint">No popup sounds found.</span>';
      return;
    }
    bundledPopupSfxContainer.innerHTML = '';
    items.forEach((item, index) => {
      const row = document.createElement('div');
      row.style.cssText = 'display: flex; align-items: center; justify-content: space-between; gap: 6px; padding: 3px 6px; background: rgba(255,255,255,0.03); border-radius: 4px;';

      const label = document.createElement('label');
      label.className = 'checkbox-row';
      label.style.cssText = 'cursor: pointer; display: flex; align-items: center; gap: 6px; margin: 0;';

      const input = document.createElement('input');
      input.type = 'checkbox';
      input.name = 'bundled_popup_sfx_files';
      input.value = item.filename;
      input.checked = true; // default enabled

      const span = document.createElement('span');
      span.style.fontSize = '12px';
      span.textContent = item.name;

      label.appendChild(input);
      label.appendChild(span);

      const playBtn = document.createElement('button');
      playBtn.type = 'button';
      playBtn.style.cssText = 'padding: 2px 6px; font-size: 11px; background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.3); color: #38bdf8; border-radius: 4px; cursor: pointer;';
      playBtn.textContent = '🔊';
      playBtn.title = `Preview ${item.name}`;
      playBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        playSoundPreview(item.url);
      });

      row.appendChild(label);
      row.appendChild(playBtn);
      bundledPopupSfxContainer.appendChild(row);
    });
  })
  .catch(() => {});

if (btnSelectAllPopups) {
  btnSelectAllPopups.addEventListener('click', () => {
    document.querySelectorAll('input[name="bundled_popup_sfx_files"]').forEach(cb => cb.checked = true);
  });
}
if (btnDeselectAllPopups) {
  btnDeselectAllPopups.addEventListener('click', () => {
    document.querySelectorAll('input[name="bundled_popup_sfx_files"]').forEach(cb => cb.checked = false);
  });
}

imageFolder.addEventListener('change', () => {
  const count = imageFolder.files.length;
  imageSummary.textContent = count ? `${count} image${count === 1 ? '' : 's'} selected.` : 'Choose a folder. Images are used in alphabetical order.';
});

srtFile.addEventListener('change', () => {
  srtSummary.textContent = srtFile.files[0]?.name || 'Select the SRT file whose cue times control the slideshow.';
});

audioFile.addEventListener('change', () => {
  audioSummary.textContent = audioFile.files[0]?.name || 'Add background music or narration to the generated video.';
});

document.querySelectorAll('input[name="aspect_ratio"]').forEach((input) => {
  input.addEventListener('change', updatePreviewAspectRatio);
});
updatePreviewAspectRatio();

aiProvider.addEventListener('change', () => {
  if (aiProvider.value === 'bytez') {
    bytezModelContainer.style.display = 'block';
  } else {
    bytezModelContainer.style.display = 'none';
  }
});

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const selectedImages = getSupportedImages().sort(naturalFileOrder);
  const selectedSrt = srtFile.files[0];
  if (selectedSrt) {
    const cueCount = await countSrtCues(selectedSrt);
    if (cueCount > selectedImages.length) {
      const confirmed = window.confirm(
        `The SRT contains ${cueCount} cues, but only ${selectedImages.length} images were provided. `
        + `Only the ${selectedImages.length} available images will be used. Do you want to continue?`,
      );
      if (!confirmed) {
        status.className = 'status';
        status.textContent = 'Video generation canceled.';
        return;
      }
    }
  }

  button.disabled = true;
  cancelButton.hidden = false;
  cancelButton.disabled = false;
  progressPanel.hidden = false;
  progressBar.style.width = '0%';
  progressBar.style.backgroundColor = '#4ecdc4';
  progressPercent.textContent = '0%';
  progressLabel.textContent = 'Preparing...';
  progressDetail.textContent = 'Uploading files...';
  status.className = 'status working';
  status.textContent = 'Rendering video. This can take a moment...';

  const data = new FormData();
  data.append('srt_file', srtFile.files[0]);
  data.append('apply_zoom', applyZoom.checked ? 'true' : 'false');
  document.querySelectorAll('input[name="bundled_sfx_files"]:checked').forEach(input => {
    data.append('bundled_sfx', input.value);
  });
  if (customSfx.files) {
    Array.from(customSfx.files).forEach(file => {
      data.append('custom_sfx', file, file.name);
    });
  }
  
  data.append('ai_provider', aiProvider.value);
  data.append('api_key', apiKey.value);
  if (apiModel) data.append('api_model', apiModel.value);
  if (customIntensity.files) {
    Array.from(customIntensity.files).forEach(file => {
      data.append('custom_intensity', file, file.name);
    });
  }
  if (emotionSfxVolume) {
    data.append('emotion_sfx_volume', emotionSfxVolume.value);
  }
  if (popupSfxVolume) {
    data.append('popup_sfx_volume', popupSfxVolume.value);
  }
  
  data.append('enable_popups', enablePopups.checked ? 'true' : 'false');
  data.append('popup_prompt', popupPrompt.value);

  if (customPopups && customPopups.files) {
    Array.from(customPopups.files).forEach(file => {
      data.append('custom_popups', file, file.name);
    });
  }
  
  if (customPopupSfx && customPopupSfx.files[0]) {
    data.append('custom_popup_sfx', customPopupSfx.files[0], customPopupSfx.files[0].name);
  }
  document.querySelectorAll('input[name="bundled_popup_sfx_files"]:checked').forEach(input => {
    data.append('bundled_popup_sfx', input.value);
  });

  data.append('aspect_ratio', document.querySelector('input[name="aspect_ratio"]:checked').value);
  if (colorBoostSlider) data.append('color_boost', colorBoostSlider.value);
  if (audioFile.files[0]) data.append('audio_file', audioFile.files[0], audioFile.files[0].name);
  selectedImages.forEach((file) => data.append('images', file, file.name));

  try {
    const response = await fetch('/api/generate', { method: 'POST', body: data, cache: 'no-store' });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'Video generation failed.');
    }
    const { job_id: jobId } = await response.json();
    activeJobId = jobId;
    let job;
    do {
      await new Promise((resolve) => setTimeout(resolve, 500));
      const progressResponse = await fetch(`/api/jobs/${jobId}`, { cache: 'no-store' });
      job = await progressResponse.json();
      if (!progressResponse.ok) throw new Error(job.detail || 'Could not read generation progress.');
      progressBar.style.width = `${job.progress}%`;
      progressPercent.textContent = `${job.progress}%`;
      progressLabel.textContent = job.phase || `Rendering image ${job.current_image} of ${job.total_images}`;
      progressDetail.textContent = job.current_filename || (job.state === 'complete' ? 'Video ready.' : 'Please wait...');
      if (job.state === 'error') throw new Error(job.error);
      if (job.state === 'canceled') throw new Error('Generation canceled.');
    } while (job.state !== 'complete');

    const downloadResponse = await fetch(`/api/jobs/${jobId}/download`, { cache: 'no-store' });
    if (!downloadResponse.ok) throw new Error('Video was created but could not be downloaded.');
    const blob = await downloadResponse.blob();
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    previewUrl = URL.createObjectURL(blob);
    videoPreview.src = previewUrl;
    videoPreview.hidden = false;
    previewEmpty.hidden = true;
    previewFilename = job.output_name || 'generated_video.mp4';
    downloadButton.hidden = false;
    previewState.textContent = 'Ready to play';
    status.className = 'status success';
    status.textContent = 'Video created and loaded in the preview.';
  } catch (error) {
    status.className = 'status error';
    status.textContent = error.message;
    progressLabel.textContent = 'Error during generation';
    progressDetail.textContent = error.message;
    progressBar.style.backgroundColor = '#ff6b6b';
    previewState.textContent = 'No video yet';
  } finally {
    activeJobId = null;
    cancelButton.hidden = true;
    button.disabled = false;
  }
});

cancelButton.addEventListener('click', async () => {
  if (!activeJobId) return;
  cancelButton.disabled = true;
  status.textContent = 'Canceling current FFmpeg process...';
  try {
    await fetch(`/api/jobs/${activeJobId}/cancel`, { method: 'POST', cache: 'no-store' });
  } catch {
    status.textContent = 'Could not contact the server to cancel the job.';
    cancelButton.disabled = false;
  }
});

downloadButton.addEventListener('click', () => {
  if (!previewUrl) return;
  const link = document.createElement('a');
  link.href = previewUrl;
  link.download = previewFilename;
  link.click();
});

const clearCacheButton = document.getElementById('clear-cache-button');
if (clearCacheButton) {
  clearCacheButton.addEventListener('click', async () => {
    try {
      clearCacheButton.disabled = true;
      clearCacheButton.textContent = 'Clearing...';
      const response = await fetch('/api/clear-cache', { method: 'POST', cache: 'no-store' });
      if (!response.ok) throw new Error('Failed to clear cache');
      alert('AI Cache successfully cleared! The AI will now re-analyze your text from scratch.');
    } catch (e) {
      alert('Error clearing cache: ' + e.message);
    } finally {
      clearCacheButton.disabled = false;
      clearCacheButton.textContent = 'Clear AI Cache';
    }
  });
}
