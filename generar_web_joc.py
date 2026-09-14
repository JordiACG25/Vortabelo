import json
import random
import re
import os
import datetime

print("Carregant dades per al generador complet de Vortabelo...")

# 1. Carregar definicions locals
definicions_raw = {}
if os.path.exists("dataset_esperanto_master.jsonl"):
    with open("dataset_esperanto_master.jsonl", "r", encoding="utf-8") as f:
        for linia in f:
            if not linia.strip():
                continue
            try:
                dada = json.loads(linia)
                text = dada.get("text", "")
                if dada.get("tipus") == "leksikono" and "Vorto:" in text:
                    parts = text.split("\nDifino:")
                    if len(parts) == 2:
                        k = re.sub(r'[^a-zĉĝĥĵŝŭ]', '', parts[0].replace("Vorto:", "").strip().lower())
                        if k and k not in definicions_raw:
                            definicions_raw[k] = parts[1].strip()
                elif dada.get("tipus") == "instrukcio" and "Demando:" in text:
                    m = re.search(r'Demando:\s*(.*?)\s*\nRespondo:\s*(.*)', text)
                    if m:
                        k = re.sub(r'[^a-zĉĝĥĵŝŭ]', '', m.group(1).lower())
                        if k and k not in definicions_raw:
                            definicions_raw[k] = m.group(2).strip()
            except Exception:
                continue

# 2. Carregar vocabulari
with open("vortaro_paraulogic.txt", "r", encoding="utf-8") as f:
    paraules = [l.strip().lower() for l in f if len(l.strip()) >= 3]

# 3. Determinisme diari basat en la data
avui_str = datetime.date.today().isoformat()
random.seed(avui_str)

candidats_tuti = [p for p in paraules if len(set(p)) == 7 and len(p) >= 7]
if candidats_tuti:
    base_tuti = random.choice(candidats_tuti)
    lletres = list(set(base_tuti))
else:
    lletres = list("lmonter")

random.shuffle(lletres)
centre = lletres[0]
corones = lletres[1:]
conjunt_lletres = set(lletres)

solucions = sorted([
    p for p in paraules
    if centre in p and set(p).issubset(conjunt_lletres)
])

def punts_de_paraula(p):
    l = len(p)
    pts = 1 if l == 3 else (2 if l == 4 else l)
    if len(set(p)) == 7:
        pts += 10
    return pts

total_punts_partida = sum(punts_de_paraula(p) for p in solucions)
total_tutis = sum(1 for p in solucions if len(set(p)) == 7)

# Lematitzacio basica
def cercar_definicio(w):
    if w in definicions_raw:
        return definicions_raw[w]
    sufixos = ["ojn", "ajn", "on", "an", "en", "oj", "aj", "as", "is", "os", "us", "ante", "inte", "o", "a", "e", "i"]
    for s in sufixos:
        if w.endswith(s) and len(w) - len(s) >= 2:
            stem = w[:-len(s)]
            if stem in definicions_raw:
                return f"[{w.upper()} el '{stem}'] " + definicions_raw[stem]
    return ""

dict_solucions = {w: cercar_definicio(w) for w in solucions}

# Generacio de matriu de pistes: lletres inicials x longituds
longituds_possibles = sorted(list(set(len(w) for w in solucions)))
lletres_inicials = sorted(list(set(w[0].upper() for w in solucions)))

graella_pistes = {}
for ini in lletres_inicials:
    graella_pistes[ini] = {l: 0 for l in longituds_possibles}

for w in solucions:
    graella_pistes[w[0].upper()][len(w)] += 1

json_lletres = json.dumps(lletres, ensure_ascii=False)
json_solucions = json.dumps(solucions, ensure_ascii=False)
json_definicions = json.dumps(dict_solucions, ensure_ascii=False)
json_graella = json.dumps(graella_pistes, ensure_ascii=False)
json_longituds = json.dumps(longituds_possibles, ensure_ascii=False)

html_template = """<!DOCTYPE html>
<html lang="eo">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vortabelo - Esperanta Paraulògic</title>
<style>
  :root {
    --primary: #0f766e;
    --primary-hover: #115e59;
    --primary-light: #ccfbf1;
    --center-color: #f59e0b;
    --bg: #f8fafc;
    --card-bg: #ffffff;
    --text: #0f172a;
    --text-muted: #64748b;
    --border: #e2e8f0;
    --error: #ef4444;
    --tag-bg: #f1f5f9;
  }

  body.dark-mode {
    --primary: #14b8a6;
    --primary-hover: #2dd4bf;
    --primary-light: #134e4a;
    --center-color: #fbbf24;
    --bg: #0f172a;
    --card-bg: #1e293b;
    --text: #f8fafc;
    --text-muted: #94a3b8;
    --border: #334155;
    --error: #f87171;
    --tag-bg: #334155;
  }

  body {
    font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    background: var(--bg);
    color: var(--text);
    margin: 0;
    padding: 12px;
    transition: background-color 0.2s, color 0.2s;
  }

  header {
    width: 100%;
    max-width: 400px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }
  .title-wrap h1 { margin: 0; font-size: 1.8rem; color: var(--primary); }
  .subtitle { font-size: 0.82rem; color: var(--text-muted); margin-top: 2px; }

  .header-actions { display: flex; gap: 8px; }
  .icon-btn {
    background: none;
    border: 1px solid var(--border);
    color: var(--text);
    border-radius: 50%;
    width: 36px;
    height: 36px;
    cursor: pointer;
    font-size: 1.1rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .icon-btn:hover { background: var(--border); }

  .rank-container {
    width: 100%;
    max-width: 380px;
    margin-bottom: 12px;
  }
  .rank-meta {
    display: flex;
    justify-content: space-between;
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 4px;
  }
  .progress-bar {
    width: 100%;
    height: 8px;
    background: var(--border);
    border-radius: 999px;
    overflow: hidden;
  }
  .progress-fill {
    height: 100%;
    width: 0%;
    background: var(--primary);
    transition: width 0.3s ease;
  }

  .input-wrapper {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    min-height: 50px;
    margin-bottom: 6px;
  }
  #error-toast {
    position: absolute;
    top: -12px;
    background: #1e293b;
    color: #ffffff;
    font-size: 0.8rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 999px;
    opacity: 0;
    transform: translateY(4px);
    transition: opacity 0.2s ease, transform 0.2s ease;
    pointer-events: none;
    z-index: 10;
  }
  #error-toast.show { opacity: 1; transform: translateY(0); }
  #input-box {
    height: 38px;
    font-size: 1.7rem;
    font-weight: bold;
    letter-spacing: 2px;
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 220px;
    border-bottom: 2px solid var(--primary);
    text-transform: uppercase;
    transition: color 0.15s ease, border-bottom-color 0.15s ease;
  }
  #input-box.error {
    color: var(--error) !important;
    border-bottom-color: var(--error) !important;
    animation: shake 0.35s ease-in-out;
  }
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    20%, 60% { transform: translateX(-6px); }
    40%, 80% { transform: translateX(6px); }
  }

  .hive {
    position: relative;
    width: 260px;
    height: 250px;
    margin-bottom: 14px;
  }
  .hex {
    position: absolute;
    width: 72px;
    height: 72px;
    background: var(--primary-light);
    color: var(--text);
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.8rem;
    font-weight: 700;
    cursor: pointer;
    user-select: none;
    transition: transform 0.08s ease;
  }
  .hex:active { transform: scale(0.92); }
  .hex.center { background: var(--center-color); color: #111827; }

  .pos-0 { top: 89px; left: 94px; }
  .pos-1 { top: 11px; left: 94px; }
  .pos-2 { top: 50px; left: 160px; }
  .pos-3 { top: 128px; left: 160px; }
  .pos-4 { top: 167px; left: 94px; }
  .pos-5 { top: 128px; left: 28px; }
  .pos-6 { top: 50px; left: 28px; }

  .controls { display: flex; gap: 8px; margin-bottom: 15px; }
  button.action-btn {
    padding: 8px 16px;
    font-size: 0.95rem;
    font-weight: 600;
    border: none;
    border-radius: 999px;
    background: var(--primary);
    color: white;
    cursor: pointer;
    transition: background-color 0.15s;
  }
  button.action-btn:hover { background: var(--primary-hover); }
  button.btn-secondary { background: var(--tag-bg); color: var(--text); }

  #definition-box {
    max-width: 380px;
    width: 100%;
    background: var(--card-bg);
    border: 2px solid var(--primary);
    border-left: 6px solid var(--primary);
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 15px;
    box-sizing: border-box;
  }
  #def-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
  #def-title { font-size: 1.1rem; font-weight: 700; color: var(--primary); text-transform: uppercase; }
  #def-link { font-size: 0.8rem; color: var(--primary); text-decoration: none; }
  #def-body { font-size: 0.9rem; line-height: 1.35; color: var(--text); }

  .section-card {
    max-width: 380px;
    width: 100%;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px;
    box-sizing: border-box;
    margin-bottom: 12px;
  }
  .card-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  #words-list { display: flex; flex-wrap: wrap; gap: 6px; }
  .word-tag {
    background: var(--tag-bg);
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 0.85rem;
    cursor: pointer;
  }
  .word-tag.tuti {
    background: #fef08a;
    font-weight: bold;
    color: #854d0e;
    animation: flash 0.8s ease;
  }
  @keyframes flash {
    0% { transform: scale(1.2); box-shadow: 0 0 10px #eab308; }
    100% { transform: scale(1); box-shadow: none; }
  }

  /* Modal de Normes */
  .modal-overlay {
    display: none;
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.6);
    z-index: 100;
    align-items: center;
    justify-content: center;
    padding: 16px;
  }
  .modal-overlay.open { display: flex; }
  .modal-content {
    background: var(--card-bg);
    color: var(--text);
    max-width: 440px;
    width: 100%;
    border-radius: 12px;
    padding: 20px;
    box-sizing: border-box;
    max-height: 85vh;
    overflow-y: auto;
  }
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
  }
  .modal-header h2 { margin: 0; font-size: 1.3rem; color: var(--primary); }
  .close-btn { background: none; border: none; font-size: 1.5rem; color: var(--text); cursor: pointer; }
  .rule-item { margin-bottom: 10px; font-size: 0.9rem; line-height: 1.4; }

  /* Taula de pistes */
  .hints-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8rem;
    text-align: center;
    margin-top: 8px;
  }
  .hints-table th, .hints-table td {
    border: 1px solid var(--border);
    padding: 4px;
  }
  .hints-table th { background: var(--tag-bg); }

  footer {
    margin-top: 20px;
    text-align: center;
    font-size: 0.8rem;
    color: var(--text-muted);
    border-top: 1px solid var(--border);
    padding-top: 14px;
    width: 100%;
    max-width: 380px;
  }
  footer a { color: var(--primary); text-decoration: none; }
</style>
</head>
<body>

<header>
  <div class="title-wrap">
    <h1>Vortabelo</h1>
    <div class="subtitle">Taga defio - __DATA__</div>
  </div>
  <div class="header-actions">
    <button class="icon-btn" onclick="toggleModal('rules-modal')" title="Reguloj">ℹ️</button>
    <button class="icon-btn" id="theme-btn" onclick="toggleTheme()" title="Reĝimo">🌙</button>
  </div>
</header>

<div class="rank-container">
  <div class="rank-meta">
    <span id="user-rank">Novulo</span>
    <span id="score-text">0 / __TOTAL_PUNTS__ pt</span>
  </div>
  <div class="progress-bar">
    <div id="progress-fill" class="progress-fill"></div>
  </div>
</div>

<div class="input-wrapper">
  <div id="error-toast"></div>
  <div id="input-box"></div>
</div>

<div class="hive">
  <div id="hex-0" class="hex center pos-0" onclick="addLetter(centerLetter)"></div>
  <div id="hex-1" class="hex pos-1" onclick="addLetter(outerLetters[0])"></div>
  <div id="hex-2" class="hex pos-2" onclick="addLetter(outerLetters[1])"></div>
  <div id="hex-3" class="hex pos-3" onclick="addLetter(outerLetters[2])"></div>
  <div id="hex-4" class="hex pos-4" onclick="addLetter(outerLetters[3])"></div>
  <div id="hex-5" class="hex pos-5" onclick="addLetter(outerLetters[4])"></div>
  <div id="hex-6" class="hex pos-6" onclick="addLetter(outerLetters[5])"></div>
</div>

<div class="controls">
  <button class="action-btn btn-secondary" onclick="deleteLetter()">Forigi</button>
  <button class="action-btn btn-secondary" onclick="shuffleLetters()">Miksi</button>
  <button class="action-btn" onclick="submitWord()">Enmeti</button>
</div>

<div id="definition-box" style="display: none;">
  <div id="def-header">
    <span id="def-title"></span>
    <a id="def-link" href="#" target="_blank">Vortaro.net ↗</a>
  </div>
  <div id="def-body"></div>
</div>

<div class="section-card">
  <div class="card-title">
    <span>Trovitaj vortoj (<span id="found-count">0</span>/__TOTAL_SOLS__)</span>
    <button class="action-btn btn-secondary" style="font-size:0.75rem; padding:3px 8px;" onclick="shareResults()">Kopii</button>
  </div>
  <div id="words-list"></div>
</div>

<div class="section-card">
  <div class="card-title">
    <span>Spuroj & Pangeromoj</span>
    <span id="tuti-counter" style="font-size:0.8rem; color:var(--primary);">0/__TOTAL_TUTIS__ tutis</span>
  </div>
  <div id="hints-table-container"></div>
</div>

<footer>
  <div>Kreita de Esperantulo Mataró 2026</div>
  <div style="margin-top:4px;">Bazita sur Fundamento kaj ReVo • <a href="https://github.com/JordiACG25/Vortabelo" target="_blank">Fontkodo ĉe GitHub</a></div>
</footer>

<!-- Modal Reguloj -->
<div id="rules-modal" class="modal-overlay" onclick="closeOnOverlay(event, 'rules-modal')">
  <div class="modal-content">
    <div class="modal-header">
      <h2>Kiel ludi? (Reguloj)</h2>
      <button class="close-btn" onclick="toggleModal('rules-modal')">×</button>
    </div>
    <div class="rule-item">• Trovu kiom eble plej multajn Esperantajn vortojn uzante la 7 proponitajn literojn.</div>
    <div class="rule-item">• Ĉiu vorto devas havi almenaŭ 3 literojn.</div>
    <div class="rule-item">• Ĉiu vorto <strong>nepre devas enhavi la centran literon</strong> (flavan).</div>
    <div class="rule-item">• Vi rajtas uzi la samajn literojn plurfoje en la sama vorto.</div>
    <div class="rule-item">• <strong>Permesitaj formoj:</strong> Substantivoj (-o, -oj, -on), adjektivoj (-a, -aj, -an), adverboj (-e, -en), infinitivoj (-i), participoj kaj ordinaraj vortfaradoj.</div>
    <div class="rule-item">• <strong>Malpermesitaj formoj:</strong> Konjugaciitaj verboj (-as, -is, -os, -us, -u) kaj mallongigoj.</div>
    <div class="rule-item">• <strong>Tuti / Pangeromo:</strong> Vorto kiu uzas ĉiujn 7 literojn de la tago donas 10 kromajn poentojn!</div>
    <div class="rule-item">• <strong>Klavaro:</strong> Vi povas tajpi 'cx', 'gx', 'hx', 'jx', 'sx', 'ux' aŭ per 'h' por ricevi la ĉapelajn literojn aŭtomate.</div>
  </div>
</div>

<script>
  const gameDate = '__DATA__';
  const centerLetter = '__CENTRE__';
  let outerLetters = __JSON_CORONES__;
  const solutions = new Set(__JSON_SOLUCIONS__);
  const dict = __JSON_DEFINICIONS__;
  const hintsMatrix = __JSON_GRAELLA__;
  const lengthsList = __JSON_LONGITUDS__;
  const maxScore = __TOTAL_PUNTS__;
  const totalTutis = __TOTAL_TUTIS__;
  
  let currentInput = "";
  let foundWords = new Set();
  let score = 0;
  let isShaking = false;

  const ranks = [
    { min: 0.85, name: "Zamenhof" },
    { min: 0.70, name: "Majstro" },
    { min: 0.50, name: "Flua" },
    { min: 0.35, name: "Progresanto" },
    { min: 0.20, name: "Lernanto" },
    { min: 0.08, name: "Komencanto" },
    { min: 0.00, name: "Novulo" }
  ];

  function vibrate(ms) {
    if (navigator.vibrate) {
      navigator.vibrate(ms);
    }
  }

  function toggleModal(id) {
    document.getElementById(id).classList.toggle('open');
  }

  function closeOnOverlay(e, id) {
    if (e.target.id === id) toggleModal(id);
  }

  function toggleTheme() {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    document.getElementById('theme-btn').innerText = isDark ? '☀️' : '🌙';
    localStorage.setItem('vortabelo_theme', isDark ? 'dark' : 'light');
  }

  if (localStorage.getItem('vortabelo_theme') === 'dark') {
    document.body.classList.add('dark-mode');
    document.getElementById('theme-btn').innerText = '☀️';
  }

  function renderHexes() {
    document.getElementById("hex-0").innerText = centerLetter.toUpperCase();
    for (let i = 0; i < 6; i++) {
      document.getElementById("hex-" + (i + 1)).innerText = outerLetters[i].toUpperCase();
    }
  }

  function shuffleLetters() {
    outerLetters.sort(() => Math.random() - 0.5);
    renderHexes();
  }

  function updateInput() {
    document.getElementById("input-box").innerText = currentInput;
  }

  function addLetter(ch) {
    if (isShaking) return;
    currentInput += ch;
    updateInput();
  }

  function deleteLetter() {
    if (isShaking) return;
    currentInput = currentInput.slice(0, -1);
    updateInput();
  }

  function getWordPoints(w) {
    let l = w.length;
    let pts = (l === 3 ? 1 : (l === 4 ? 2 : l));
    if (new Set(w).size === 7) pts += 10;
    return pts;
  }

  function updateRankAndScore() {
    document.getElementById("score-text").innerText = score + " / " + maxScore + " pt";
    let ratio = maxScore > 0 ? (score / maxScore) : 0;
    document.getElementById("progress-fill").style.width = Math.min(100, Math.round(ratio * 100)) + "%";

    for (let r of ranks) {
      if (ratio >= r.min) {
        document.getElementById("user-rank").innerText = r.name;
        break;
      }
    }
    
    let tutisFound = 0;
    for (let w of foundWords) {
      if (new Set(w).size === 7) tutisFound++;
    }
    document.getElementById("tuti-counter").innerText = tutisFound + "/" + totalTutis + " tutis";
  }

  function saveProgress() {
    localStorage.setItem("vortabelo_" + gameDate, JSON.stringify(Array.from(foundWords)));
  }

  function loadProgress() {
    const saved = localStorage.getItem("vortabelo_" + gameDate);
    if (saved) {
      const arr = JSON.parse(saved);
      for (let w of arr) {
        if (solutions.has(w)) {
          foundWords.add(w);
          score += getWordPoints(w);
          appendWordTag(w, false);
        }
      }
      document.getElementById("found-count").innerText = foundWords.size;
      updateRankAndScore();
    }
  }

  function cleanHtml(raw) {
    let txt = document.createElement("textarea");
    txt.innerHTML = raw.replace(/<[^>]*>/g, "");
    return txt.value;
  }

  async function fetchWiktionaryDef(word) {
    try {
      const url = "https://eo.wiktionary.org/api/rest_v1/page/definition/" + encodeURIComponent(word);
      const res = await fetch(url);
      if (!res.ok) return null;
      const data = await res.json();
      if (data.eo && data.eo.length > 0) {
        for (let item of data.eo) {
          if (item.definitions && item.definitions.length > 0) {
            let d = item.definitions[0].definition;
            d = cleanHtml(d).trim();
            if (d) return d;
          }
        }
      }
    } catch(e) {}
    return null;
  }

  async function displayDef(w) {
    const box = document.getElementById("definition-box");
    const t = document.getElementById("def-title");
    const l = document.getElementById("def-link");
    const b = document.getElementById("def-body");

    t.innerText = w;
    l.href = "https://vortaro.net/#" + encodeURIComponent(w);
    box.style.display = "block";

    if (dict[w] && dict[w].length > 0) {
      b.innerText = dict[w];
    } else {
      b.innerText = "Ŝarĝante difinon el Vikivortaro...";
      const wikDef = await fetchWiktionaryDef(w);
      if (wikDef) {
        dict[w] = wikDef;
        b.innerText = wikDef;
      } else {
        b.innerText = "Literatura vorto en Esperanto. Klaku supre por vidi ĝin en Vortaro.net.";
      }
    }
  }

  function appendWordTag(w, triggerDef = true) {
    const isTuti = new Set(w).size === 7;
    const tag = document.createElement("span");
    tag.className = "word-tag" + (isTuti ? " tuti" : "");
    tag.innerText = w + (isTuti ? " ★" : "");
    tag.onclick = () => displayDef(w);
    document.getElementById("words-list").appendChild(tag);
    if (triggerDef) displayDef(w);
  }

  function triggerError(msg) {
    vibrate(60);
    const inputEl = document.getElementById("input-box");
    const toast = document.getElementById("error-toast");
    
    isShaking = true;
    inputEl.classList.add("error");
    toast.innerText = msg;
    toast.classList.add("show");

    setTimeout(() => {
      inputEl.classList.remove("error");
      toast.classList.remove("show");
      currentInput = "";
      updateInput();
      isShaking = false;
    }, 700);
  }

  function submitWord() {
    if (isShaking) return;
    const w = currentInput.toLowerCase();
    
    if (w.length < 3) {
      triggerError("Tro mallonga!");
      return;
    }
    if (!w.includes(centerLetter)) {
      triggerError("Mankas la centra litero!");
      return;
    }
    if (foundWords.has(w)) {
      displayDef(w);
      triggerError("Jam trovita!");
      return;
    }
    if (!solutions.has(w)) {
      triggerError("Nekonata vorto!");
      return;
    }

    // Encis
    vibrate([40, 30, 40]);
    foundWords.add(w);
    score += getWordPoints(w);
    document.getElementById("found-count").innerText = foundWords.size;
    updateRankAndScore();
    appendWordTag(w, true);
    saveProgress();
    currentInput = "";
    updateInput();
  }

  function renderHintsTable() {
    const container = document.getElementById("hints-table-container");
    let html = '<table class="hints-table"><thead><tr><th>Lit</th>';
    for (let l of lengthsList) {
      html += '<th>' + l + '</th>';
    }
    html += '<th>Σ</th></tr></thead><tbody>';

    for (let ini of Object.keys(hintsMatrix).sort()) {
      let rowSum = 0;
      html += '<tr><td>' + ini + '</td>';
      for (let l of lengthsList) {
        let val = hintsMatrix[ini][l] || 0;
        rowSum += val;
        html += '<td>' + (val > 0 ? val : '-') + '</td>';
      }
      html += '<td>' + rowSum + '</td></tr>';
    }
    html += '</tbody></table>';
    container.innerHTML = html;
  }

  function shareResults() {
    const rank = document.getElementById("user-rank").innerText;
    const txt = "Vortabelo (" + gameDate + ")\\n" +
                "Nivelo: " + rank + " | " + score + " pt\\n" +
                "Trovitaj vortoj: " + foundWords.size + "/" + solutions.size;
    navigator.clipboard.writeText(txt).then(() => {
      alert("Rezulto kopiita al la tondejo!");
    });
  }

  const surogatoMap = {
    "cx": "ĉ", "ch": "ĉ",
    "gx": "ĝ", "gh": "ĝ",
    "hx": "ĥ", "hh": "ĥ",
    "jx": "ĵ", "jh": "ĵ",
    "sx": "ŝ", "sh": "ŝ",
    "ux": "ŭ", "uh": "ŭ"
  };

  window.addEventListener("keydown", (e) => {
    if (e.key === "Backspace") {
      deleteLetter();
    } else if (e.key === "Enter") {
      submitWord();
    } else if (e.key === " ") {
      e.preventDefault();
      shuffleLetters();
    } else {
      const k = e.key.toLowerCase();
      if (["x", "h"].includes(k) && currentInput.length > 0) {
        const lastChar = currentInput.slice(-1);
        const combo = lastChar + k;
        if (surogatoMap[combo]) {
          currentInput = currentInput.slice(0, -1) + surogatoMap[combo];
          updateInput();
          return;
        }
      }
      if ([centerLetter, ...outerLetters].includes(k)) {
        addLetter(k);
      }
    }
  });

  renderHexes();
  renderHintsTable();
  loadProgress();
</script>
</body>
</html>
"""

final_html = (
    html_template
    .replace("__DATA__", avui_str)
    .replace("__CENTRE__", centre)
    .replace("__JSON_CORONES__", json.dumps(corones, ensure_ascii=False))
    .replace("__JSON_SOLUCIONS__", json_solucions)
    .replace("__JSON_DEFINICIONS__", json_definicions)
    .replace("__JSON_GRAELLA__", json_graella)
    .replace("__JSON_LONGITUDS__", json_longituds)
    .replace("__TOTAL_PUNTS__", str(total_punts_partida))
    .replace("__TOTAL_SOLS__", str(len(solucions)))
    .replace("__TOTAL_TUTIS__", str(total_tutis))
)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(final_html)

print("Fitxer 'index.html' generat amb èxit amb totes les millores completes!")
