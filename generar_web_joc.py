import json
import random
import re
import os
import datetime

print("Carregant dades i reconstruint vocabulari oficial per a Vortabelo v1.2.2...")

definicions_raw = {}
arrels_lexic = set()

# 1. Extreure lemes i definicions de dataset_esperanto_master.jsonl
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
                        if k:
                            arrels_lexic.add(k)
                            if k not in definicions_raw:
                                definicions_raw[k] = parts[1].strip()
                elif dada.get("tipus") == "instrukcio" and "Demando:" in text:
                    m = re.search(r'Demando:\s*(.*?)\s*\nRespondo:\s*(.*)', text)
                    if m:
                        k = re.sub(r'[^a-zĉĝĥĵŝŭ]', '', m.group(1).lower())
                        if k:
                            arrels_lexic.add(k)
                            if k not in definicions_raw:
                                definicions_raw[k] = m.group(2).strip()
            except Exception:
                continue

# 2. Carregar vortaro_paraulogic.txt com a suport
paraules_set = set()
if os.path.exists("vortaro_paraulogic.txt"):
    with open("vortaro_paraulogic.txt", "r", encoding="utf-8") as f:
        for l in f:
            w = l.strip().lower()
            if len(w) >= 3 and not any(c in w for c in "qwx"):
                paraules_set.add(w)

# 3. Troncs de lemes per a flexio i derivacio
terminacions_nominals = ["o", "oj", "on", "ojn", "a", "aj", "an", "ajn", "e", "en", "i"]
troncs_extrets = set()

for mot in arrels_lexic.union(paraules_set):
    tronc = mot
    for t_lema in ["ojn", "ajn", "oj", "aj", "on", "an", "en", "o", "a", "i", "e"]:
        if mot.endswith(t_lema) and len(mot) > len(t_lema) + 1:
            tronc = mot[:-len(t_lema)]
            break
    if len(tronc) >= 2:
        troncs_extrets.add(tronc)

# AFEGIR ARRELS FONAMENTALS GARANTIDES (dies, mesos, colors, vocabulari base)
arrels_basiques = [
    "lund", "mard", "merkred", "ĵaŭd", "vendred", "sabat", "dimanĉ",
    "januar", "februar", "mart", "april", "maj", "juni", "juli", "aŭgust", "septembr", "oktobr", "novembr", "decembr",
    "printemp", "somer", "aŭtun", "vintr",
    "nigr", "blank", "ruĝ", "verd", "blu", "flav", "griz", "brun",
    "knab", "vir", "hom", "infan", "patr", "edz", "fil", "frat", "amik",
    "arb", "flor", "best", "hund", "kat", "bird", "fiŝ",
    "akv", "fajr", "ter", "aer", "sun", "lun", "stel", "nub", "vent",
    "dom", "ĉambr", "pord", "fenestr", "tabl", "seĝ", "lit", "lig",
    "manĝ", "trink", "dorm", "pens", "sci", "kompren", "leg", "skrib",
    "grand", "bon", "bel", "nov", "jun", "alt", "long", "fort", "san",
    "vort", "liter", "lingv", "nom", "temp", "tag", "nokt", "maten", "vesper"
]
for ab in arrels_basiques:
    troncs_extrets.add(ab)

# Generem totes les flexions directes
for tr in troncs_extrets:
    for t in terminacions_nominals:
        derivat = tr + t
        if len(derivat) >= 3:
            paraules_set.add(derivat)

# 4. Prefixos essencials de l'esperanto (mal-, re-, ge-, ek-, dis-)
prefixos_comuns = ["mal", "re", "ge", "ek", "dis"]
for tr in troncs_extrets:
    if 2 <= len(tr) <= 5:
        for pref in prefixos_comuns:
            base_pref = pref + tr
            for t in ["o", "oj", "on", "ojn", "a", "aj", "an", "ajn", "e", "i"]:
                paraules_set.add(base_pref + t)

# 5. Afixos productius del PIV i Fundamento (sense caracters espuris com 'x')
afixos_productius = [
    "il", "ej", "in", "ist", "ar", "ec", "ebl", "et", "eg", "ig", "iĝ", "ad", "ul", "aĵ"
]

for tr in troncs_extrets:
    if 2 <= len(tr) <= 5:
        for af in afixos_productius:
            base_af = tr + af
            for t in ["o", "oj", "on", "ojn", "a", "aj", "an", "ajn", "e", "i"]:
                paraules_set.add(base_af + t)

# 6. Particules, preposicions i numerals canonics amb derivats
particules_preposicions = [
    "jen", "en", "antaŭ", "post", "apud", "inter", "sub", "sur", "tra", "trans",
    "por", "per", "kun", "sen", "pri", "pro", "kontraŭ", "dum", "ĝis", "ekster",
    "ĉirkaŭ", "malgraŭ", "anstataŭ", "laŭ", "po",
    "unu", "du", "tri", "kvar", "kvin", "ses", "sep", "ok", "naŭ", "dek", "cent", "mil",
    "tuj", "nun", "jam", "tro", "tre", "plu", "for", "mem", "preskaŭ", "apenaŭ"
]

for base in particules_preposicions:
    for t in ["", "o", "oj", "on", "ojn", "a", "aj", "an", "ajn", "e", "en", "i"]:
        mot = base + t
        if len(mot) >= 3:
            paraules_set.add(mot)
    for af in ["il", "ej", "ec", "ar", "ig", "iĝ", "in", "ist"]:
        for t in ["o", "oj", "on", "ojn", "a", "aj", "an", "ajn", "e", "i"]:
            paraules_set.add(base + af + t)

# 7. Correlatius de la llengua (Tabelvortoj)
pref_tabel = ["k", "t", "", "ĉ", "nen"]
suf_tabel = ["io", "iu", "ia", "ie", "iel", "ial", "iam", "iom", "ies"]

for p in pref_tabel:
    for s in suf_tabel:
        base = p + s
        if len(base) >= 3:
            paraules_set.add(base)
        if s == "io":
            paraules_set.add(base + "n")
        elif s in ["iu", "ia"]:
            paraules_set.add(base + "j")
            paraules_set.add(base + "n")
            paraules_set.add(base + "jn")
        elif s == "ie":
            paraules_set.add(base + "n")

# 8. Participis basics
verbs_arrels_comuns = ["est", "vid", "ir", "far", "dir", "hav", "don", "pren", "sci", "ven", "pas", "star", "viv"]
afixos_participi = ["ant", "int", "ont", "at", "it", "ot"]
terminacions_part = ["a", "aj", "an", "ajn", "o", "oj", "on", "ojn", "e"]

for v in verbs_arrels_comuns:
    for af in afixos_participi:
        for t in terminacions_part:
            mot = v + af + t
            if len(mot) >= 3:
                paraules_set.add(mot)

# Neteja final: només paraules d'esperanto valides (sense x, q, w)
paraules = sorted(list(p for p in paraules_set if not any(c in p for c in "qwx")))

# 9. Determinisme diari i seleccio equilibrada del tauler
avui_str = datetime.date.today().isoformat()
rng = random.Random(avui_str)

candidats_tuti = [p for p in paraules if len(set(p)) == 7 and len(p) >= 7]
rng.shuffle(candidats_tuti)

vocals_esperanto = set("aeiou")
centre = "l"
corones = ["m", "o", "n", "t", "e", "r"]
solucions = []

for base_cand in candidats_tuti:
    lletres_cand = list(set(base_cand))
    rng.shuffle(lletres_cand)
    c_cand = lletres_cand[0]
    conjunt_cand = set(lletres_cand)
    
    # Exigir minim 2 vocals al panell
    num_vocals = len(conjunt_cand.intersection(vocals_esperanto))
    if num_vocals < 2:
        continue
        
    sols_cand = sorted([
        p for p in paraules
        if c_cand in p and set(p).issubset(conjunt_cand)
    ])
    
    inicials = set(w[0] for w in sols_cand)
    if len(sols_cand) >= 35 and len(inicials) >= 3:
        centre = c_cand
        corones = lletres_cand[1:]
        solucions = sols_cand
        break

if not solucions:
    lletres = list("lmonter")
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

longituds_possibles = sorted(list(set(len(w) for w in solucions)))
lletres_inicials = sorted(list(set(w[0].upper() for w in solucions)))

graella_pistes = {}
for ini in lletres_inicials:
    graella_pistes[ini] = {l: 0 for l in longituds_possibles}

for w in solucions:
    graella_pistes[w[0].upper()][len(w)] += 1

json_lletres = json.dumps([centre] + corones, ensure_ascii=False)
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

  .brand-banner {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 8px;
  }
  .brand-logo-wrap {
    display: flex;
    align-items: center;
    gap: 12px;
    background: var(--card-bg);
    border: 1px solid var(--border);
    padding: 6px 16px;
    border-radius: 999px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.06);
  }
  .star-svg {
    width: 32px;
    height: 32px;
  }
  .crocodile-svg {
    width: 46px;
    height: 46px;
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

  .player-greeting {
    width: 100%;
    max-width: 380px;
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--primary);
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .player-greeting span.change-link {
    font-size: 0.75rem;
    color: var(--text-muted);
    cursor: pointer;
    text-decoration: underline;
  }

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

  .user-input-field {
    width: 100%;
    padding: 10px;
    font-size: 1rem;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--bg);
    color: var(--text);
    box-sizing: border-box;
    margin-bottom: 14px;
  }

  .hints-table-wrapper {
    width: 100%;
    overflow-x: auto;
  }

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
    font-size: 0.85rem;
    color: var(--text-muted);
    border-top: 1px solid var(--border);
    padding-top: 14px;
    width: 100%;
    max-width: 380px;
  }
  .creator-tag {
    font-weight: 600;
    font-size: 0.95rem;
    color: var(--primary);
  }
  .version-tag {
    font-size: 0.78rem;
    color: var(--text-muted);
    margin-top: 2px;
  }
  footer a { color: var(--primary); text-decoration: none; }
</style>
</head>
<body>

<div class="brand-banner">
  <div class="brand-logo-wrap">
    <svg class="star-svg" viewBox="0 0 100 100">
      <rect width="100" height="100" fill="#ffffff" stroke="#22c55e" stroke-width="6" rx="14"/>
      <polygon points="50,12 61,38 89,38 66,54 75,80 50,64 25,80 34,54 11,38 39,38" fill="#16a34a"/>
    </svg>
    <svg class="crocodile-svg" viewBox="0 0 64 64" fill="none">
      <path d="M8 38 C 12 24, 26 22, 38 22 C 49 22, 59 26, 61 35 C 61 40, 52 44, 40 44 C 28 44, 16 46, 10 44 Z" fill="#22c55e"/>
      <path d="M16 42 C 28 42, 55 41, 59 37 C 55 45, 42 47, 26 47 C 18 47, 14 45, 16 42 Z" fill="#15803d"/>
      <circle cx="26" cy="22" r="6" fill="#facc15"/>
      <circle cx="26" cy="22" r="3" fill="#0f172a"/>
      <polygon points="32,38 35,43 38,38" fill="#ffffff"/>
      <polygon points="42,37 45,42 48,37" fill="#ffffff"/>
      <polygon points="14,26 17,19 20,26" fill="#15803d"/>
      <polygon points="20,25 23,18 26,24" fill="#15803d"/>
      <circle cx="57" cy="33" r="2" fill="#0f172a"/>
    </svg>
  </div>
</div>

<header>
  <div class="title-wrap">
    <h1>Vortabelo</h1>
    <div class="subtitle">Taga defio - __DATA__</div>
  </div>
  <div class="header-actions">
    <button class="icon-btn" onclick="toggleModal('user-modal')" title="Uzanto">👤</button>
    <button class="icon-btn" onclick="toggleModal('rules-modal')" title="Reguloj">ℹ️</button>
    <button class="icon-btn" id="theme-btn" onclick="toggleTheme()" title="Reĝimo">🌙</button>
  </div>
</header>

<div class="player-greeting" id="player-banner" style="display: none;">
  <span>Saluton, <span id="display-username">Ludanto</span>!</span>
  <span class="change-link" onclick="toggleModal('user-modal')">ŝanĝi</span>
</div>

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
  <div class="creator-tag">Kreita de Esperantulo de la VA</div>
  <div class="version-tag">Versio 1.2.2</div>
  <div style="margin-top:4px;">Bazita sur Fundamento kaj ReVo • <a href="https://github.com/JordiACG25/Vortabelo" target="_blank">Fontkodo ĉe GitHub</a></div>
</footer>

<div id="rules-modal" class="modal-overlay" onclick="closeOnOverlay(event, 'rules-modal')">
  <div class="modal-content">
    <div class="modal-header">
      <h2>Kiel ludi? (Reguloj)</h2>
      <button class="close-btn" onclick="toggleModal('rules-modal')">×</button>
    </div>
    <div class="rule-item">• Trovu kiom eble plej multajn Esperantajn vortojn uzante la 7 proponitajn literojn.</div>
    <div class="rule-item">• Ĉiu vorto devas havi almenaŭ 3 literojn.</div>
    <div class="rule-item">• Ĉiu vorto nepre devas enhavi la centran literon (flavan).</div>
    <div class="rule-item">• Vi rajtas uzi la samajn literojn plurfoje en la sama vorto.</div>
    <div class="rule-item">• Permesitaj formoj: Substantivoj (-o, -oj, -on), adjektivoj (-a, -aj, -an), adverboj (-e, -en), infinitivoj (-i), partikloj, numeraloj, tabelvortoj, participoj kaj derivitaj formoj (mal-, re-, ge-, -il-, -ej-, -in-...).</div>
    <div class="rule-item">• Malpermesitaj formoj: Konjugaciitaj verboj (-as, -is, -os, -us, -u) kaj mallongigoj.</div>
    <div class="rule-item">• Tuti / Pangeromo: Vorto kiu uzas ĉiujn 7 literojn de la tago donas 10 kromajn poentojn!</div>
    <div class="rule-item">• Klavaro: Tajpu 'cx', 'gx', 'hx', 'jx', 'sx', 'ux' por ricevi la ĉapelajn literojn aŭtomate.</div>
  </div>
</div>

<div id="user-modal" class="modal-overlay" onclick="closeOnOverlay(event, 'user-modal')">
  <div class="modal-content">
    <div class="modal-header">
      <h2>Profilo de Ludanto</h2>
      <button class="close-btn" onclick="toggleModal('user-modal')">×</button>
    </div>
    <div style="font-size: 0.9rem; margin-bottom: 12px; color: var(--text-muted);">
      Enigu vian nomon aŭ kromnomon por konservi viajn personajn lud-rezultojn:
    </div>
    <input type="text" id="username-input" class="user-input-field" placeholder="Ekz: Jordi, VerdaStelo..." maxlength="20" />
    <div style="display:flex; justify-content:flex-end; gap:8px;">
      <button class="action-btn btn-secondary" onclick="toggleModal('user-modal')">Nuligi</button>
      <button class="action-btn" onclick="saveUsername()">Konservi</button>
    </div>
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
    if (id === 'user-modal') {
      const current = localStorage.getItem('vortabelo_username') || '';
      document.getElementById('username-input').value = current;
    }
  }

  function closeOnOverlay(e, id) {
    if (e.target.id === id) toggleModal(id);
  }

  function saveUsername() {
    const val = document.getElementById('username-input').value.trim();
    if (val) {
      localStorage.setItem('vortabelo_username', val);
    } else {
      localStorage.removeItem('vortabelo_username');
    }
    updateUserDisplay();
    toggleModal('user-modal');
  }

  function updateUserDisplay() {
    const name = localStorage.getItem('vortabelo_username');
    const banner = document.getElementById('player-banner');
    const disp = document.getElementById('display-username');
    if (name) {
      disp.innerText = name;
      banner.style.display = 'flex';
    } else {
      banner.style.display = 'none';
    }
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

  const eoAlphabet = "abcĉdefgĝhĥijĵklmnoprsŝtuŭvz";
  function compareEo(a, b) {
    const lowerA = a.toLowerCase();
    const lowerB = b.toLowerCase();
    const minLen = Math.min(lowerA.length, lowerB.length);
    for (let i = 0; i < minLen; i++) {
      const idxA = eoAlphabet.indexOf(lowerA[i]);
      const idxB = eoAlphabet.indexOf(lowerB[i]);
      const posA = idxA === -1 ? 999 : idxA;
      const posB = idxB === -1 ? 999 : idxB;
      if (posA !== posB) return posA - posB;
    }
    return lowerA.length - lowerB.length;
  }

  function renderFoundWordsList() {
    const listContainer = document.getElementById("words-list");
    listContainer.innerHTML = "";
    const sortedWords = Array.from(foundWords).sort(compareEo);
    for (const w of sortedWords) {
      const isTuti = new Set(w).size === 7;
      const tag = document.createElement("span");
      tag.className = "word-tag" + (isTuti ? " tuti" : "");
      tag.innerText = w + (isTuti ? " ★" : "");
      tag.onclick = () => displayDef(w);
      listContainer.appendChild(tag);
    }
  }

  function loadProgress() {
    const saved = localStorage.getItem("vortabelo_" + gameDate);
    if (saved) {
      const arr = JSON.parse(saved);
      for (let w of arr) {
        if (solutions.has(w)) {
          foundWords.add(w);
          score += getWordPoints(w);
        }
      }
      document.getElementById("found-count").innerText = foundWords.size;
      updateRankAndScore();
      renderFoundWordsList();
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

    vibrate([40, 30, 40]);
    foundWords.add(w);
    score += getWordPoints(w);
    document.getElementById("found-count").innerText = foundWords.size;
    updateRankAndScore();
    renderFoundWordsList();
    displayDef(w);
    saveProgress();
    currentInput = "";
    updateInput();
  }

  function renderHintsTable() {
    const container = document.getElementById("hints-table-container");
    let html = '<div class="hints-table-wrapper"><table class="hints-table"><thead><tr><th>Lit</th>';
    for (let l of lengthsList) {
      html += '<th>' + l + '</th>';
    }
    html += '<th>Σ</th></tr></thead><tbody>';

    const sortedInitials = Object.keys(hintsMatrix).sort(compareEo);
    for (let ini of sortedInitials) {
      let rowSum = 0;
      html += '<tr><td>' + ini + '</td>';
      for (let l of lengthsList) {
        let val = hintsMatrix[ini][l] || 0;
        rowSum += val;
        html += '<td>' + (val > 0 ? val : '-') + '</td>';
      }
      html += '<td>' + rowSum + '</td></tr>';
    }
    html += '</tbody></table></div>';
    container.innerHTML = html;
  }

  function shareResults() {
    const rank = document.getElementById("user-rank").innerText;
    const user = localStorage.getItem("vortabelo_username");
    const userStr = user ? ("Ludanto: " + user + "\\n") : "";
    const txt = "Vortabelo v1.2.2 (" + gameDate + ")\\n" +
                userStr +
                "Nivelo: " + rank + " | " + score + " pt\\n" +
                "Trovitaj vortoj: " + foundWords.size + "/" + solutions.size;
    navigator.clipboard.writeText(txt).then(() => {
      alert("Rezulto kopiita al la tondejo!");
    });
  }

  const surogatoMap = {
    "cx": "ĉ",
    "gx": "ĝ",
    "hx": "ĥ",
    "jx": "ĵ",
    "sx": "ŝ",
    "ux": "ŭ"
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
      if (k === "x" && currentInput.length > 0) {
        const lastChar = currentInput.slice(-1);
        const combo = lastChar + "x";
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
  updateUserDisplay();
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

print("Fitxer 'index.html' generat correctament amb la versio 1.2.2 i arrels garantides!")
