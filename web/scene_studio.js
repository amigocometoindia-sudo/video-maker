document.addEventListener("DOMContentLoaded", () => {
  const scriptInput = document.getElementById("script-input");
  const voiceSelect = document.getElementById("voice-select");
  const styleSelect = document.getElementById("style-select");
  const btnGenerateSrt = document.getElementById("btn-generate-srt");
  const btnAutoGenerateScenes = document.getElementById("btn-auto-generate-scenes");
  const btnAutoGenFromTable = document.getElementById("btn-auto-gen-from-table");
  const btnLoadSample = document.getElementById("btn-load-sample");
  const genStatus = document.getElementById("gen-status");

  const sceneTableCard = document.getElementById("scene-table-card");
  const sceneTableBody = document.getElementById("scene-table-body");
  const sceneMetaDesc = document.getElementById("scene-meta-desc");
  const audioPreview = document.getElementById("audio-preview");
  const btnDownloadSrt = document.getElementById("btn-download-srt");
  const btnCopyGridPrompts = document.getElementById("btn-copy-grid-prompts");
  const gridPromptsContainer = document.getElementById("grid-prompts-container");

  const gridFilesInput = document.getElementById("grid-files-input");
  const gridTypeSelect = document.getElementById("grid-type-select");
  const btnSplitGrids = document.getElementById("btn-split-grids");
  const autoGridsGallery = document.getElementById("auto-grids-gallery");
  const autoGridsList = document.getElementById("auto-grids-list");
  const splitResultsCard = document.getElementById("split-results-card");
  const splitSummaryTitle = document.getElementById("split-summary-title");
  const splitSummaryDesc = document.getElementById("split-summary-desc");
  const btnDownloadZip = document.getElementById("btn-download-zip");

  let currentSrtText = "";
  let currentGridPrompts = [];
  let currentScenes = [];
  let currentGeneratedSlices = [];

  // Sample Script
  const sampleScript = `Have you ever caught your brain spinning in an endless loop at 2 AM?
You replay a conversation from three years ago, terrified that you made a complete fool of yourself.
Psychologists call this cognitive rumination, an ancient survival mechanism where the brain scans for imaginary danger.
In the Stone Age, hyper-vigilance kept your ancestors alive against predators.
Suddenly, your heart begins to race, flooding your veins with adrenaline and stress.
You try to force your thoughts to stop, but the mental tension only intensifies.
Then, with a gentle breath and a quiet smile, you realize that thoughts are merely passing clouds.
By stepping back into the present moment, calm focus is finally restored.`;

  btnLoadSample.addEventListener("click", () => {
    scriptInput.value = sampleScript;
  });

  // 1. Generate Semantic SRT & Audio
  async function generateSemanticSrt() {
    const text = scriptInput.value.trim();
    if (!text) {
      alert("Please enter a script or dialogue text.");
      return false;
    }

    btnGenerateSrt.disabled = true;
    btnGenerateSrt.innerHTML = `<span>⏳ Synthesizing Voice & Semantic Cues...</span>`;
    genStatus.style.display = "block";
    genStatus.textContent = "Analyzing complete grammatical sentences and spoken timings...";

    try {
      const formData = new FormData();
      formData.append("script_text", text);
      formData.append("voice", voiceSelect.value);
      formData.append("topic", text.slice(0, 60));

      const res = await fetch("/api/generate-semantic-srt", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to generate SRT.");
      }

      const data = await res.json();
      currentSrtText = data.srt_text;

      if (data.audio_url) {
        audioPreview.src = data.audio_url;
      }

      currentScenes = data.scenes || [];
      currentGridPrompts = data.grid_prompts_2x2 || [];

      renderSceneTable(currentScenes);
      renderGridPrompts(currentGridPrompts);

      sceneTableCard.style.display = "block";
      sceneTableCard.scrollIntoView({ behavior: "smooth" });
      genStatus.style.display = "none";
      return true;
    } catch (e) {
      alert("Notice: " + e.message);
      genStatus.style.display = "none";
      return false;
    } finally {
      btnGenerateSrt.disabled = false;
      btnGenerateSrt.innerHTML = `<span>⚡ Generate Semantic SRT & Audio</span>`;
    }
  }

  btnGenerateSrt.addEventListener("click", generateSemanticSrt);

  // 2. Fetch Scene Director Breakdown
  async function fetchSceneBreakdown(srtText, style) {
    const formData = new FormData();
    formData.append("cues_text", srtText);
    formData.append("topic", scriptInput.value.slice(0, 60));
    formData.append("style", style);

    const res = await fetch("/api/scene-director-breakdown", {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to get scene breakdown.");
    }

    const data = await res.json();
    currentScenes = data.scenes;
    renderSceneTable(currentScenes);
    renderGridPrompts(data.grid_prompts_2x2);
  }

  styleSelect.addEventListener("change", () => {
    if (currentSrtText) {
      fetchSceneBreakdown(currentSrtText, styleSelect.value).catch(console.error);
    }
  });

  function renderSceneTable(scenes, imageMap = {}) {
    sceneTableBody.innerHTML = "";
    let totalDur = 0;

    scenes.forEach((sc, idx) => {
      totalDur += sc.duration_s;
      const tr = document.createElement("tr");

      const emotionClass = `emotion-${sc.emotion}`;
      const emotionLabel = sc.emotion.replace("_", " ");

      const imgInfo = imageMap[idx] || (currentGeneratedSlices && currentGeneratedSlices[idx]);
      const imgHtml = imgInfo
        ? `<div style="position: relative; width: 88px; height: 50px; border-radius: 6px; overflow: hidden; border: 1px solid var(--border-subtle); box-shadow: 0 2px 6px rgba(0,0,0,0.4); cursor: pointer;" onclick="window.open('${imgInfo.url}', '_blank')">
             <img src="${imgInfo.url}" alt="Scene ${idx + 1}" style="width: 100%; height: 100%; object-fit: cover;">
             <span style="position: absolute; bottom: 2px; right: 4px; background: rgba(0,0,0,0.7); color: #fff; font-size: 0.65rem; padding: 1px 4px; border-radius: 3px; font-family: monospace;">${imgInfo.filename}</span>
           </div>`
        : `<div style="width: 88px; height: 50px; border-radius: 6px; background: rgba(255,255,255,0.03); border: 1px dashed var(--border-subtle); display: flex; align-items: center; justify-content: center; color: var(--text-dim); font-size: 0.68rem; text-align: center;">
             Pending
           </div>`;

      tr.innerHTML = `
        <td style="color: var(--text-dim); font-family: 'DM Mono', monospace; font-size: 0.85rem;">${idx + 1}</td>
        <td>${imgHtml}</td>
        <td style="font-family: 'DM Mono', monospace; font-size: 0.8rem; color: #38bdf8;">
          ${(sc.start_ms / 1000).toFixed(1)}s - ${(sc.end_ms / 1000).toFixed(1)}s<br>
          <span style="color: var(--text-dim); font-size: 0.75rem;">(${sc.duration_s}s scene)</span>
        </td>
        <td style="font-weight: 500;">
          <textarea class="dialogue-cell" style="width: 100%; background: transparent; border: 1px solid transparent; color: #fff; font-family: inherit; font-size: 0.88rem; resize: vertical;" rows="2">${sc.text}</textarea>
        </td>
        <td>
          <span class="emotion-pill ${emotionClass}">${emotionLabel}</span>
        </td>
        <td style="font-size: 0.82rem; color: #cbd5e1; font-family: 'DM Mono', monospace; background: rgba(0,0,0,0.2); border-radius: 4px; padding: 6px 10px;">
          ${sc.scene_prompt}
        </td>
      `;
      sceneTableBody.appendChild(tr);
    });

    sceneMetaDesc.textContent = `${scenes.length} complete narrative scenes | Total spoken time: ${totalDur.toFixed(1)}s`;
  }

  function renderGridPrompts(gridPrompts) {
    gridPromptsContainer.innerHTML = "";
    currentGridPrompts = gridPrompts;

    if (!gridPrompts || gridPrompts.length === 0) {
      gridPromptsContainer.innerHTML = `<p style="color: var(--text-dim); font-size: 0.85rem;">No grid prompts available.</p>`;
      return;
    }

    gridPrompts.forEach((g) => {
      const box = document.createElement("div");
      box.className = "grid-prompt-box";
      box.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
          <strong style="color: var(--accent-cyan); font-size: 0.88rem;">Grid #${g.grid_number} (Scenes ${g.scene_range})</strong>
          <button type="button" class="btn-copy-one" style="padding: 3px 8px; font-size: 0.75rem; background: rgba(255,255,255,0.1); border: 1px solid var(--border-subtle); color: #fff; border-radius: 4px; cursor: pointer;">Copy Prompt</button>
        </div>
        <p style="color: #94a3b8; line-height: 1.4;">${g.prompt}</p>
      `;

      box.querySelector(".btn-copy-one").addEventListener("click", () => {
        navigator.clipboard.writeText(g.prompt);
        alert(`Grid #${g.grid_number} prompt copied to clipboard!`);
      });

      gridPromptsContainer.appendChild(box);
    });
  }

  // 3. Automated AI Scene & Grid Generation
  async function triggerAutoSceneGeneration() {
    if (!currentScenes || currentScenes.length === 0) {
      const ok = await generateSemanticSrt();
      if (!ok) return;
    }

    const triggerBtn = btnAutoGenerateScenes;
    triggerBtn.disabled = true;
    triggerBtn.innerHTML = `<span>⏳ Synthesizing AI Grids & Slices...</span>`;
    genStatus.style.display = "block";
    genStatus.textContent = "Compositing 2x2 narrative grid sheets and slicing scenes according to dialogue...";

    try {
      const payload = {
        cues: currentScenes.map((s, i) => ({
          index: i,
          text: s.text,
          start_ms: s.start_ms,
          end_ms: s.end_ms,
          emotion: s.emotion,
        })),
        topic: scriptInput.value.slice(0, 60),
        style: styleSelect.value,
        grid_type: gridTypeSelect.value || "2x2",
      };

      const res = await fetch("/api/auto-generate-scenes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to auto-generate scenes.");
      }

      const data = await res.json();
      currentGeneratedSlices = data.scenes;

      // 1. Update Scene Table with image previews
      const imageMap = {};
      data.scenes.forEach((s) => {
        imageMap[s.cue_index] = s;
      });
      renderSceneTable(currentScenes, imageMap);

      // 2. Populate Auto-Grid Gallery
      if (data.grids && data.grids.length > 0) {
        autoGridsGallery.style.display = "block";
        autoGridsList.innerHTML = "";
        data.grids.forEach((g, gIdx) => {
          const item = document.createElement("div");
          item.style.cssText = "flex-shrink: 0; width: 210px; border-radius: 8px; overflow: hidden; border: 1px solid var(--border-subtle); background: #07090e; box-shadow: 0 4px 12px rgba(0,0,0,0.5); cursor: pointer;";
          item.innerHTML = `
            <div style="position: relative; width: 100%; height: 160px; overflow: hidden;">
              <img src="${g.url}" alt="Grid #${gIdx + 1}" style="width: 100%; height: 100%; object-fit: cover; transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
              <span style="position: absolute; top: 6px; left: 6px; background: rgba(0,0,0,0.75); color: #38bdf8; font-size: 0.72rem; padding: 2px 6px; border-radius: 4px; font-weight: 600;">Grid #${gIdx + 1} (${data.grid_type})</span>
            </div>
            <div style="padding: 8px 10px; display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 0.75rem; color: #94a3b8; font-family: monospace;">${g.filename}</span>
              <a href="${g.url}" target="_blank" style="font-size: 0.75rem; color: var(--accent-cyan); text-decoration: none;">View ➔</a>
            </div>
          `;
          autoGridsList.appendChild(item);
        });
      }

      // 3. Show Split Results card with instant ZIP download
      splitResultsCard.style.display = "block";
      splitSummaryTitle.textContent = `🎨 Successfully generated & sliced ${data.total_scenes} scenes matching dialogue!`;
      splitSummaryDesc.textContent = `All scenes formatted as image_00000.jpg ... image_${String(data.total_scenes - 1).padStart(5, "0")}.jpg and packaged into ZIP.`;
      btnDownloadZip.href = data.zip_url;
      splitResultsCard.scrollIntoView({ behavior: "smooth" });

      genStatus.style.display = "none";
    } catch (e) {
      alert("Notice: " + e.message);
      genStatus.style.display = "none";
    } finally {
      triggerBtn.disabled = false;
      triggerBtn.innerHTML = `<span>🎨 Auto-Generate Images & Grids Live</span>`;
    }
  }

  btnAutoGenerateScenes.addEventListener("click", triggerAutoSceneGeneration);
  if (btnAutoGenFromTable) {
    btnAutoGenFromTable.addEventListener("click", triggerAutoSceneGeneration);
  }

  // Copy All Grid Prompts
  btnCopyGridPrompts.addEventListener("click", () => {
    if (!currentGridPrompts || currentGridPrompts.length === 0) {
      alert("No grid prompts generated yet.");
      return;
    }
    const allText = currentGridPrompts.map((g) => `// GRID #${g.grid_number} (Scenes ${g.scene_range})\n${g.prompt}\n`).join("\n");
    navigator.clipboard.writeText(allText);
    alert(`Copied all ${currentGridPrompts.length} grid prompts to clipboard!`);
  });

  // Download .SRT
  btnDownloadSrt.addEventListener("click", () => {
    if (!currentSrtText) {
      alert("No SRT generated yet.");
      return;
    }
    const blob = new Blob([currentSrtText], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "scene_subtitles.srt";
    a.click();
    URL.revokeObjectURL(url);
  });

  // Manual Grid Slicer Button
  btnSplitGrids.addEventListener("click", async () => {
    const files = gridFilesInput.files;
    if (!files || files.length === 0) {
      alert("Please select one or more grid images to slice.");
      return;
    }

    btnSplitGrids.disabled = true;
    btnSplitGrids.innerHTML = `<span>✂️ Slicing Panels...</span>`;

    try {
      const formData = new FormData();
      for (let i = 0; i < files.length; i++) {
        formData.append("grid_files", files[i]);
      }
      formData.append("grid_type", gridTypeSelect.value);

      const res = await fetch("/api/split-grids", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to split grids.");
      }

      const data = await res.json();
      splitResultsCard.style.display = "block";
      splitSummaryTitle.textContent = `Successfully sliced ${data.total_sliced_scenes} individual scenes from ${data.input_grid_count} grid images!`;
      splitSummaryDesc.textContent = `Formatted as image_00000.jpg ... image_${String(data.total_sliced_scenes - 1).padStart(5, "0")}.jpg.`;
      btnDownloadZip.href = data.zip_url;
      splitResultsCard.scrollIntoView({ behavior: "smooth" });
    } catch (e) {
      alert("Error: " + e.message);
    } finally {
      btnSplitGrids.disabled = false;
      btnSplitGrids.innerHTML = `<span>✂️ Slice All Grids</span>`;
    }
  });
});
