import json, re

with open('build_voicetube_ui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Subtitle Stage CSS: Left alignment & Karaoke highlight classes
old_sub_stage_css = """.vt-sub-stage {
  background: #0b0b14;
  border: 1px solid #232338;
  border-top: none;
  border-radius: 0 0 14px 14px;
  padding: 16px 20px;
  min-height: 105px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  box-shadow: inset 0 2px 10px rgba(0,0,0,0.4);
}
.vt-sub-en-line {
  font-size: 21px;
  font-weight: 750;
  line-height: 1.45;
  color: #ffffff;
  letter-spacing: -0.2px;
  max-width: 95%;
  word-break: break-word;
}
.vt-sub-zh-line {
  font-size: 15px;
  font-weight: 500;
  line-height: 1.5;
  color: #a4a4c2;
  margin-top: 8px;
  max-width: 95%;
}
.vt-word-token {
  cursor: pointer;
  display: inline-block;
  padding: 1px 3px;
  border-radius: 4px;
  transition: all .15s;
}
.vt-word-token:hover {
  background: #6d5dfc3d;
  color: #a49aff;
  text-decoration: underline;
}"""

new_sub_stage_css = """.vt-sub-stage {
  background: #0d0d1a;
  border: 1px solid #232338;
  border-top: none;
  border-left: 5px solid #6d5dfc;
  border-radius: 0 0 14px 14px;
  padding: 18px 24px;
  min-height: 115px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  text-align: left;
  box-shadow: inset 0 2px 10px rgba(0,0,0,0.4);
}
.vt-sub-en-line {
  font-size: 23px;
  font-weight: 750;
  line-height: 1.6;
  color: #ffffff;
  letter-spacing: -0.2px;
  width: 100%;
  text-align: left;
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 3px 6px;
}
.vt-sub-zh-line {
  font-size: 15px;
  font-weight: 500;
  line-height: 1.5;
  color: #9ea0be;
  margin-top: 8px;
  width: 100%;
  text-align: left;
}
/* Word Token Base */
.vt-word-token {
  cursor: pointer;
  display: inline-block;
  padding: 2px 6px;
  border-radius: 5px;
  transition: background 0.1s ease, color 0.1s ease, transform 0.1s ease, box-shadow 0.1s ease;
  line-height: 1.25;
}
/* Unspoken word (尚未發音) */
.vt-word-token.future {
  color: #6b6b85;
}
/* Already spoken word (已發音) */
.vt-word-token.passed {
  color: #f0f0ff;
  font-weight: 700;
}
/* Current spoken word (隨影片聲音逐字反白移動) */
.vt-word-token.current {
  background: #ffffff !important;
  color: #0d0d1a !important;
  font-weight: 900 !important;
  box-shadow: 0 0 14px rgba(255, 255, 255, 0.75);
  transform: translateY(-1px) scale(1.06);
  display: inline-block;
}
.vt-word-token:hover {
  background: rgba(109, 93, 252, 0.35);
  color: #a49aff;
  text-decoration: underline;
}
.vt-punct {
  color: #6b6b85;
  margin-right: 2px;
}"""

content = content.replace(old_sub_stage_css, new_sub_stage_css)

# 2. Update Sync timer interval from 100ms to 50ms for ultra-smooth 20 FPS word tracking
content = content.replace(
    "syncTimer = setInterval(checkSubtitleSync, 100);",
    "syncTimer = setInterval(checkSubtitleSync, 50);"
)

# 3. Update checkSubtitleSync to call updateKaraokeWordHighlight
old_check_sync = """  if (matchIdx !== -1 && matchIdx !== activeCueIdx) {
    highlightVoiceTubeCue(matchIdx);
  }
}"""

new_check_sync = """  if (matchIdx !== -1) {
    if (matchIdx !== activeCueIdx) {
      highlightVoiceTubeCue(matchIdx);
    }
    // 字幕隨影片聲音逐字反白移動
    updateKaraokeWordHighlight(time, cues[matchIdx]);
  }
}"""

content = content.replace(
    """  if (matchIdx !== -1 && matchIdx !== activeCueIdx) {{
    highlightVoiceTubeCue(matchIdx);
  }}
}}""",
    """  if (matchIdx !== -1) {{
    if (matchIdx !== activeCueIdx) {{
      highlightVoiceTubeCue(matchIdx);
    }}
    // 字幕隨影片聲音逐字反白移動
    updateKaraokeWordHighlight(time, cues[matchIdx]);
  }}
}}"""
)

# 4. Add updateKaraokeWordHighlight and improve tokenizeWords
karaoke_logic = """
function updateKaraokeWordHighlight(time, cue) {
  const words = document.querySelectorAll('#vtActiveEn .vt-word-token');
  if (!words.length) return;

  const start = cue.start;
  const dur = cue.duration > 0 ? cue.duration : 4.5;
  const elapsed = Math.max(0, time - start);
  const ratio = Math.min(0.999, elapsed / dur);

  let totalChars = 0;
  const charWeights = [];
  words.forEach(w => {
    const len = parseInt(w.getAttribute('data-len') || '3', 10);
    charWeights.push(len);
    totalChars += len;
  });

  const targetPos = ratio * totalChars;
  let accumulated = 0;
  let activeWIdx = 0;
  for (let i = 0; i < charWeights.length; i++) {
    accumulated += charWeights[i];
    if (accumulated >= targetPos) {
      activeWIdx = i;
      break;
    }
  }

  words.forEach((w, i) => {
    if (i < activeWIdx) {
      if (w.className !== 'vt-word-token passed') w.className = 'vt-word-token passed';
    } else if (i === activeWIdx) {
      if (w.className !== 'vt-word-token current') w.className = 'vt-word-token current';
    } else {
      if (w.className !== 'vt-word-token future') w.className = 'vt-word-token future';
    }
  });
}

function tokenizeWords(sentence) {
  const parts = sentence.split(/(\\s+|[^\\w\\s'-]+)/);
  let wordCounter = 0;
  return parts.map(part => {
    if (/^[a-zA-Z0-9'-]{2,}$/.test(part)) {
      const clean = part.replace(/[^a-zA-Z]/g, '').toLowerCase();
      const idx = wordCounter++;
      return `<span class="vt-word-token future" data-word-idx="${idx}" data-len="${clean.length}" onclick="lookupWord('${clean}')">${escapeHTML(part)}</span>`;
    } else if (/^[a-zA-Z]$/.test(part)) {
      const clean = part.toLowerCase();
      const idx = wordCounter++;
      return `<span class="vt-word-token future" data-word-idx="${idx}" data-len="${clean.length}" onclick="lookupWord('${clean}')">${escapeHTML(part)}</span>`;
    } else {
      return `<span class="vt-punct">${escapeHTML(part)}</span>`;
    }
  }).join('');
}
"""

# Replace old tokenizeWords with karaoke_logic in build_voicetube_ui.py
old_tokenize = """function tokenizeWords(sentence) {{
  // Wrap every word token in an interactive clickable span
  return sentence.replace(/\\\\b([a-zA-Z'-]{2,})\\\\b/g, (match) => {{
    const clean = match.replace(/[^a-zA-Z]/g, '').toLowerCase();
    return `<span class="vt-word-token" onclick="lookupWord('${{clean}}')">${{match}}</span>`;
  }});
}}"""

new_tokenize = """function updateKaraokeWordHighlight(time, cue) {{
  const words = document.querySelectorAll('#vtActiveEn .vt-word-token');
  if (!words.length) return;

  const start = cue.start;
  const dur = cue.duration > 0 ? cue.duration : 4.5;
  const elapsed = Math.max(0, time - start);
  const ratio = Math.min(0.999, elapsed / dur);

  let totalChars = 0;
  const charWeights = [];
  words.forEach(w => {{
    const len = parseInt(w.getAttribute('data-len') || '3', 10);
    charWeights.push(len);
    totalChars += len;
  }});

  const targetPos = ratio * totalChars;
  let accumulated = 0;
  let activeWIdx = 0;
  for (let i = 0; i < charWeights.length; i++) {{
    accumulated += charWeights[i];
    if (accumulated >= targetPos) {{
      activeWIdx = i;
      break;
    }}
  }}

  words.forEach((w, i) => {{
    if (i < activeWIdx) {{
      if (w.className !== 'vt-word-token passed') w.className = 'vt-word-token passed';
    }} else if (i === activeWIdx) {{
      if (w.className !== 'vt-word-token current') w.className = 'vt-word-token current';
    }} else {{
      if (w.className !== 'vt-word-token future') w.className = 'vt-word-token future';
    }}
  }});
}}

function tokenizeWords(sentence) {{
  const parts = sentence.split(/(\\s+|[^\\w\\s'-]+)/);
  let wordCounter = 0;
  return parts.map(part => {{
    if (/^[a-zA-Z0-9'-]{{2,}}$/.test(part)) {{
      const clean = part.replace(/[^a-zA-Z]/g, '').toLowerCase();
      const idx = wordCounter++;
      return `<span class="vt-word-token future" data-word-idx="${{idx}}" data-len="${{clean.length}}" onclick="lookupWord('${{clean}}')">${{escapeHTML(part)}}</span>`;
    }} else if (/^[a-zA-Z]$/.test(part)) {{
      const clean = part.toLowerCase();
      const idx = wordCounter++;
      return `<span class="vt-word-token future" data-word-idx="${{idx}}" data-len="${{clean.length}}" onclick="lookupWord('${{clean}}')">${{escapeHTML(part)}}</span>`;
    }} else {{
      return `<span class="vt-punct">${{escapeHTML(part)}}</span>`;
    }}
  }}).join('');
}}"""

content = content.replace(old_tokenize, new_tokenize)

with open('build_voicetube_ui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("build_voicetube_ui.py updated with karaoke word-by-word reverse highlight & left alignment!")
