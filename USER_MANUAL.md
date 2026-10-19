# 🎬 Animated Explainer Video Generator — User Manual

> **Next-Gen YouTube Explainer & Documentary Video Engine**  
> Generate high-retention animated videos across **Tech & Wealth**, **Psychology & Mind**, **Prehistory & Science**, and **World History** with synchronized AI voiceovers, dynamic 2D character puppets, Ken Burns camera motion, and sound effects.

---

## 📑 Table of Contents
1. [Quick Start (3-Step Guide)](#1-quick-start)
2. [Generator Modes](#2-generator-modes)
   - [Mode A: 1-Click Auto Pipeline (Recommended)](#mode-a-1-click-auto-pipeline)
   - [Mode B: Manual Assets Mode](#mode-b-manual-assets-mode)
   - [Mode C: Scene & Grid Studio (Script, Semantic SRT & Auto-Slicer)](#mode-c-scene--grid-studio)
3. [Character Action PNG Puppet System](#3-character-action-png-puppet-system)
   - [How It Works](#how-it-works)
   - [Where to Put Your Character PNGs](#where-to-put-your-character-pngs)
   - [Naming Guide & Action Keywords](#naming-guide--action-keywords)
   - [Dynamic Character Motion Curves](#dynamic-character-motion-curves)
4. [Video Types & Niche Prompts](#4-video-types--niche-prompts)
   - [Tech & Wealth (e.g. Elon Musk, Startups, Crypto)](#tech--wealth)
   - [Psychology & Mind (e.g. Overthinking, Habits, Brain)](#psychology--mind)
   - [Prehistory & Anthropology (e.g. Ancient Humans, Fire)](#prehistory--anthropology)
   - [History & Civilization (e.g. Rome, Revolutions)](#history--civilization)
5. [Audio, SFX & Volume Controls](#5-audio-sfx--volume-controls)
6. [Visual, Framing & Subtitle Controls](#6-visual-framing--subtitle-controls)
7. [Folder Structure & Asset Locations](#7-folder-structure--asset-locations)
8. [Troubleshooting & FAQ](#8-troubleshooting--faq)

---

## 1. Quick Start

1. **Start the Engine**: Double-click `SRT_Video_Generator.bat` (or run `python\python.exe -m uvicorn server:app --host 127.0.0.1 --port 8765`).
2. **Open the Studio**: Open your web browser and go to:
   ```
   http://127.0.0.1:8765/studio.html
   ```
3. **Generate Your Video**:
   - Enter your topic (e.g., *"Why You Overthink"* or *"How Elon Musk Got That Much Money"*).
   - Select your preferred Neural Voice.
   - Click **🚀 Launch Studio Render**.
   - Your MP4 video is rendered and automatically downloaded to your `output/` folder!

---

## 2. Generator Modes

### Mode A: 1-Click Auto Pipeline
Everything is automated from a single prompt:
1. **AI Scriptwriter**: Researches the topic, crafts a high-retention hook, sensory narration, and natural character quotes.
2. **Neural TTS Voiceover**: Synthesizes human-like narration (via Microsoft Edge Neural TTS voices: Christopher, Guy, Ryan, Jenny, Sonia).
3. **Synchronized SRT Timings**: Generates frame-accurate sentence subtitles.
4. **Visual Slides**: Automatically downloads high-resolution encyclopedic artwork/diagrams or renders modern procedural backdrops.
5. **Sound Effects**: AI analyzes dialogue and inserts synchronized sound effects (whooshes, dings, cash registers, tension hits).
6. **Animated Characters**: AI matches each subtitle cue to a character action PNG and animates it on screen.

### Mode B: Manual Assets Mode
For creators who already have their own images and audio:
1. Switch the mode selector at the top to **📁 Manual Assets Mode**.
2. Select your folder of images (sorted alphabetically or numerically: `01.jpg`, `02.jpg`, etc.).
3. Upload your `.srt` subtitle file.
4. Upload your voiceover `.mp3` or `.wav` audio.
5. Choose your subtitle styling and camera motion settings, then render!

### Mode C: Scene & Grid Studio (Script, Semantic SRT & Auto-Slicer)
Access via the top navigation bar or directly at `http://127.0.0.1:8765/scene_studio.html`.
Designed specifically for narrative video creation with Midjourney/Flux grids:
1. **Semantic Dialogue Segmentation (Clause-Aware SRT)**:
   - Paste any narrative text.
   - The engine automatically divides your script into logical visual scenes (treating each cue as a complete grammatical thought and splitting at punctuation and emotional shifts like smiles or shocks, never slicing mid-phrase).
   - Generates synchronized Edge-TTS narration audio and downloadable `.srt`.
2. **AI Scene Director & 2x2 Grid Prompt Generator**:
   - Analyzes each cue to extract emotion tags, subject actions, and visual scene prompts.
   - Automatically groups consecutive scenes into **2x2 Grid Prompts** ready to copy/paste into Midjourney, Flux, Google Flow, or Stable Diffusion.
3. **1-Click Auto-Grid Splitter**:
   - Upload your 2x2 (4-panel) or 3x3 (9-panel) generated grid sheets.
   - Click **✂️ Split & Package ZIP**.
   - The engine automatically crops each panel into numbered scene images (`image_00000.jpg`, `image_00001.jpg`, etc.) and downloads a ZIP file, instantly ready for your video renderer!

---

## 3. Character Action PNG Puppet System

### How It Works
The engine uses an **AI Animation Director** that reads your dialogue cues line-by-line (the same way it reads dialogue for SFX). Whenever a line describes an action, emotion, or speaker, the AI automatically selects the best matching character PNG and animates it with bespoke movement curves.

- **Multimodal Vision AI Reader**: When you upload a folder of custom popup PNGs (even with numbered or raw filenames like `character_001.png` or sprite sheets), Vision AI (`Llama 3.2 Vision` / `Gemini` / `GPT-4o`) visually inspects each image to understand its exact pose, emotion, and props (e.g. *holding coins*, *stressed head in hands*, *rocket ship*, *walking*). It then matches each image to the subtitle dialogue where that specific action or concept is spoken.
- **Strict Single-Use (Zero Looping)**: Every PNG in your upload box is used **at most once** in the entire video. Once placed at a dialogue moment, that image is never repeated or looped.
- **Full Folder Utilization**: All uploaded PNGs in your popup upload box are placed across the video at the most relevant dialogue moments so your entire collection is showcased.

### Where to Put Your Character PNGs
You can add characters in two easy ways:
- **Upload via Web UI**: In the web UI under **"Upload custom popup PNGs (Select a folder)"**, select your folder of transparent PNGs.
- **Direct Folder Drop**: Place transparent `.png` files into:
  - `characters/` *(Recommended)*
  - or `custom_channel_assets/`

### Naming Guide & Action Keywords
Name your PNG files with the character name and action. The AI reads the filename and automatically links it to the spoken dialogue:

| Action Category | Recommended Filename Examples | Dialogue Triggers |
| :--- | :--- | :--- |
| **Thinking / Mind** | `person_thinking.png`, `brain.png`, `thinking.png` | overthinking, thoughts, brain, ponder, wonder, question, doubt |
| **Stress & Panic** | `stress.png`, `anxious.png`, `panic.png` | stress, anxiety, panic, nervous, fear, insomnia, worry |
| **Eureka / Idea** | `idea.png`, `lightbulb.png`, `eureka.png` | idea, eureka, breakthrough, solution, realized, genius |
| **Wealth & Money** | `elon_rich.png`, `money.png`, `wealth.png` | billionaire, millionaire, cash, dollars, fortune, profit, stocks |
| **Tech & Rockets** | `elon_rocket.png`, `tesla_car.png`, `laptop.png` | rocket, spacex, launch, mars, tesla, electric car, coding |
| **Prehistory / Caveman** | `caveman_hunter.png`, `mammoth.png` | ancient human, hunter, gatherer, stone age, spear, tribe |
| **Fire & Warmth** | `fire.png`, `caveman_fire.png`, `torch.png` | fire, flame, cooking, warmth, burned, sparked |
| **Speech / Explaining** | `elon_talking.png`, `speaker.png`, `speech.png` | said, explained, declared, announced, told, speech |
| **Battle / Clash** | `soldier_attack.png`, `swords.png`, `battle.png` | clash, swords, attack, fight, strike, charge, war |
| **Defeat / Fall** | `defeat.png`, `dead.png`, `tombstone.png` | dead, died, defeat, fallen, collapsed, grief, lost |
| **Shock / Surprise** | `shocked.png`, `surprise.png` | suddenly, unexpected, surprise, shock, twist, gasp |
| **Cheer / Triumph** | `victory.png`, `cheer.png`, `gold.png` | victory, cheered, celebrate, triumph, won, glory |

> **Pro-Tip**: You can create multi-character variations! E.g.:  
> `elon_talking.png`, `elon_rich.png`, `elon_rocket.png`, `elon_thinking.png`  
> When the voiceover says *"Elon thought about bankruptcy"*, `elon_thinking.png` animates. When it says *"SpaceX launched the rocket"*, `elon_rocket.png` launches into the sky!

### Dynamic Character Motion Curves
Characters do not sit statically on screen. Each action executes mathematical movement curves:
- **Thinking**: Gentle contemplative pacing float and head hover.
- **Stress**: Rapid nervous shivering and tense heart-pulse tremors.
- **Eureka / Idea**: High-energy spring hop with enlightenment settling.
- **Wealth / Money**: Upward float with rhythmic celebration coin tosses.
- **Rocket**: Acceleration launch curve ascending smoothly off the top of the canvas.
- **Battle**: Forward lunge, weapon impact recoil, and subtle screen impact shake.
- **Defeat**: Stumble backward and slump down to the ground.
- **Speech**: Organic speaking body bobbing synchronized to the duration of the line.
- **Automatic Inward Facing (`hflip`)**: Characters placed on the right side of the screen are automatically mirrored so they always face inward toward the center and subtitles.

---

## 4. Video Types & Niche Prompts

The engine automatically detects the domain of your topic and tailors the script style, image search, and visual canvases accordingly:

### 💼 Tech & Wealth
- **Example Prompts**:
  - `How Elon Musk Got That Much Money`
  - `The Rise and Fall of WeWork`
  - `How Steve Jobs Saved Apple From Bankruptcy`
  - `The Hidden Mechanics of the Stock Market`
- **Visuals**: Modern dark cyber-slate canvas (`#0b0f19`), financial grid lines, and cyan accent horizon. Wikipedia search fetches real Tesla, SpaceX, and executive photos.

### 🧠 Psychology & Mind
- **Example Prompts**:
  - `Why You Overthink and How to Stop`
  - `The Neuroscience of Why We Procrastinate`
  - `How Dopamine Controls Your Daily Habits`
  - `Why You Wake Up at 3 AM Stressed`
- **Visuals**: Deep cerebral midnight violet/indigo backdrop (`#0d0c1d`) with glowing neural synapse nodes and purple glow.

### 🏹 Prehistory & Anthropology
- **Example Prompts**:
  - `What Did Ancient Humans Do All Day?`
  - `How the Discovery of Fire Changed the Human Brain`
  - `The Epic Mammoth Hunts of the Ice Age`
  - `Why Neanderthals Disappeared`
- **Visuals**: Earthy stone-cave and savanna amber tones (`#1a1412`), primal horizon terrain, and warm campfire lighting.

### ⚔️ History & Civilization
- **Example Prompts**:
  - `1000 Years of the Roman Empire Explained`
  - `The 1066 Battle of Hastings in 60 Seconds`
  - `How the French Revolution Changed the World`
- **Visuals**: Authentic vintage aged parchment map with compass rose and antique borders.

---

## 5. Audio, SFX & Volume Controls

- **Emotion SFX Volume Slider**: Located in the sidebar under **Audio & Sound Effects Master Suite**.
  - Default: `15%` (smooth, non-intrusive background accents).
  - Adjust freely between `0%` (silent) and `100%` (loud punchy hits).
- **Dialogue-Driven SFX**: AI automatically maps sounds to your dialogue:
  - Cash register / coins on wealth or money lines.
  - Whooshes on transitions and fast movement.
  - Dings on ideas and solutions.
  - Dramatic impacts and booms on tension, battles, or shocks.
  - Clock ticking on deadlines or time passing.
- **No Annoying Beeps**: Outdated click sounds have been removed in favor of clean cinematic accents.

---

## 6. Visual, Framing & Subtitle Controls

- **Canvas Aspect Ratio**:
  - **16:9 Landscape**: For standard YouTube long-form, desktop, and TV.
  - **9:16 Portrait**: For YouTube Shorts, Instagram Reels, and TikTok.
- **Camera Motion**:
  - `Smart Dynamic`: Auto-alternates smooth zoom-ins, zoom-outs, and horizontal pans.
  - `Cinematic Push-In`: Slow, steady documentary zoom-in.
  - `Dramatic Pull-Out`: Reveals full scene context.
  - `Static`: Clean still frames.
- **Framing & Mismatch Fill Mode**:
  - `Pro Glassmorphic Blur`: Perfect for photos that don't match 16:9/9:16. Sharp foreground centered with a softly blurred background. No cropped heads or cut-off text!
  - `Direct Center Crop`: Full bleed filling the entire canvas.
- **Subtitle Styling**:
  - `Hormozi Yellow`: High-contrast yellow text with bold black outline (proven highest retention).
  - `Cinematic White`: Elegant minimalist white documentary subtitles.
  - `Neon Glow`: Vibrant cyan/neon aesthetic for tech and modern explainers.

---

## 7. Folder Structure & Asset Locations

```
SRT Video Generator/
├── characters/               <-- 💡 DROP YOUR CHARACTER ACTION PNGs HERE
│   ├── elon_talking.png
│   ├── person_thinking.png
│   ├── brain.png
│   └── soldier_attack.png
│
├── custom_channel_assets/    <-- Alternative custom sticker/asset folder
├── sfx/                      <-- Shutter, whoosh, and transition audio files
├── intensity_sfx/            <-- Dialogue emotion sound effects library
├── output/                   <-- 🎬 ALL GENERATED MP4 VIDEOS ARE SAVED HERE
├── web/                      <-- Studio Web Interface
├── auto_generator.py         <-- Multi-genre script & visual slide generator
├── video_generator.py        <-- FFmpeg rendering & motion animation engine
└── server.py                 <-- Local server & API backend
```

---

## 8. Troubleshooting & FAQ

**Q: Where is my rendered video?**  
A: Your finished video is saved in the `output/` folder and will also download automatically in your web browser.

**Q: Can I use my own voice recording instead of AI voice?**  
A: Yes! Switch the generator to **Manual Assets Mode**, upload your images, your `.srt` subtitle file, and your voiceover `.mp3`/`.wav`.

**Q: How do I make characters appear more frequently?**  
A: Ensure you have PNGs in `characters/` or `custom_channel_assets/`. The AI matches character actions to relevant dialogue lines automatically.

**Q: Can I run this completely offline without API keys?**  
A: Yes! The system contains built-in studio fallback scripts, heuristic dialogue analyzers, and procedural visual canvas generators that run 100% offline. Adding an OpenAI or Gemini API key unlocks dynamic LLM script generation on any arbitrary topic.

---
*Happy Video Creating!* 🚀
