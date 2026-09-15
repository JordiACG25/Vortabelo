import json
import re
import os

print("Reconstruint vocabulari oficial per a Vortabelo...")

mots_base = set()

# 1. Base fonamental d'arrels d'esperanto 100% garantides
arrels_fonamentals = [
    # Temps i calendari
    "lund", "mard", "merkred", "ĵaŭd", "vendred", "sabat", "dimanĉ",
    "januar", "februar", "mart", "april", "maj", "juni", "juli", "aŭgust", "septembr", "oktobr", "novembr", "decembr",
    "printemp", "somer", "aŭtun", "vintr", "temp", "hor", "minut", "sekund", "tag", "nokt", "maten", "vesper", "jar", "semajn",
    # Menjar i cuina
    "melon", "pom", "pan", "lakt", "fromaĝ", "viand", "karn", "ov", "suker", "sal", "akv", "vin", "bier", "kaf", "te",
    "manĝ", "trink", "kuir", "frukt", "legom", "sup",
    # Colors
    "nigr", "blank", "ruĝ", "verd", "blu", "flav", "griz", "brun",
    # Persones i família
    "knab", "vir", "hom", "infan", "patr", "edz", "fil", "frat", "amik", "sinjor", "person",
    # Natura i animals
    "arb", "flor", "best", "hund", "kat", "bird", "fiŝ", "ĉeval", "bov", "pork",
    "fajr", "ter", "aer", "sun", "lun", "stel", "nub", "vent", "pluv", "mar", "mont", "river",
    # Casa i objectes quotidians
    "dom", "ĉambr", "pord", "fenestr", "tabl", "seĝ", "lit", "lig", "libr", "paper", "plum", "horloĝ", "vest",
    # Verbs clàssics
    "est", "hav", "far", "dir", "vid", "ir", "ven", "pren", "don", "sci", "vol", "pov", "dev",
    "pens", "kred", "kompren", "leg", "skrib", "parol", "dorm", "star", "sid", "viv", "mort",
    "labor", "lud", "kur", "marŝ", "port", "met", "trov", "pet", "demand", "respond",
    "aŭd", "rigard", "sent", "am", "tim", "help", "ŝanĝ", "montr", "esper",
    # Qualitats / Adjectius
    "bon", "bel", "nov", "jun", "malnov", "grand", "malgrand", "alt", "long", "vast", "plen", "facil", "grav",
    "fort", "san", "varm", "ver", "cert", "pur", "klar", "feliĉ", "liber", "pret",
    # Conceptes i llengua
    "vort", "liter", "lingv", "nom", "mond", "lok", "part", "voj", "urb", "land", "ŝtat"
]

for arrel in arrels_fonamentals:
    for f in ["o", "a", "e", "i"]:
        mots_base.add(arrel + f)

# 2. Extracció des de dataset_esperanto_master.jsonl si existeix
if os.path.exists("dataset_esperanto_master.jsonl"):
    try:
        with open("dataset_esperanto_master.jsonl", "r", encoding="utf-8") as f:
            for linia in f:
                if not linia.strip():
                    continue
                try:
                    dada = json.loads(linia)
                    txt = dada.get("text", "")
                    if "Vorto:" in txt:
                        m = txt.split("\nDifino:")[0].replace("Vorto:", "").strip().lower()
                        w = re.sub(r'[^a-zĉĝĥĵŝŭ]', '', m)
                        if len(w) >= 3:
                            mots_base.add(w)
                except Exception:
                    continue
    except Exception as e:
        print(f"Avís llegint el dataset: {e}")

# 3. Partícules invariables fonamentals
particules_invariables = [
    "jes", "ne", "jen", "jam", "tuj", "nun", "tro", "tre", "plu", "for",
    "mem", "dum", "por", "per", "kun", "sen", "pri", "pro", "ĝis", "tra",
    "sur", "sub", "apud", "laŭ", "anstataŭ", "malgraŭ", "ĉirkaŭ", "ekster",
    "unu", "du", "tri", "kvar", "kvin", "ses", "sep", "ok", "naŭ", "dek", "cent", "mil"
]

for p in particules_invariables:
    mots_base.add(p)
    # jes -> jeso, jesa, jese, jesi...
    if p in ["jes", "unu", "ne", "mem"]:
        for f in ["o", "a", "e", "i"]:
            mots_base.add(p + f)

# 4. Correlatius de l'esperanto
for pr in ["k", "t", "", "ĉ", "nen"]:
    for sf in ["io", "iu", "ia", "ie", "iel", "ial", "iam", "iom", "ies"]:
        base = pr + sf
        if len(base) >= 3:
            mots_base.add(base)
            if sf == "io":
                mots_base.add(base + "n")
            elif sf in ["iu", "ia"]:
                mots_base.add(base + "j")
                mots_base.add(base + "n")
                mots_base.add(base + "jn")
            elif sf == "ie":
                mots_base.add(base + "n")

# 5. Afixos comuns i derivacions reals (-il-, -ej-, -in-, -ist-, -ar-, -ec-)
afixos = ["il", "ej", "in", "ist", "ar", "ec", "aĵ"]
troncs_per_afixos = [
    "manĝ", "trink", "dorm", "lern", "kuir", "labor", "lud", "preg", "preĝ", "kaf", "pan", "drink", "bov", "pork",
    "lig", "lit", "nov", "bel", "bon", "grand", "san", "hom", "amik", "patr", "frat", "fil", "edz", "kat", "hund"
]
for tr in troncs_per_afixos:
    for af in afixos:
        base_af = tr + af
        for f in ["o", "a", "e"]:
            mots_base.add(base_af + f)

# 6. Flexió regular completa (plurals i acusatius)
vortaro_final = set()
terminacions_conjugades = ("as", "is", "os", "us")

for w in mots_base:
    if len(w) < 3 or any(c in w for c in "qwx"):
        continue
    
    # Si és partícula invariable aprovada, entra directe
    if w in particules_invariables:
        vortaro_final.add(w)
        continue

    # Rebutgem verbs conjugats
    if w.endswith(terminacions_conjugades):
        continue

    vortaro_final.add(w)

    if w.endswith("o"):
        vortaro_final.add(w + "j")
        vortaro_final.add(w + "n")
        vortaro_final.add(w + "jn")
    elif w.endswith("a"):
        vortaro_final.add(w + "j")
        vortaro_final.add(w + "n")
        vortaro_final.add(w + "jn")
    elif w.endswith("e"):
        vortaro_final.add(w + "n")

llista_neta = sorted(list(vortaro_final))

with open("vortaro_paraulogic.txt", "w", encoding="utf-8") as f:
    for mot in llista_neta:
        f.write(mot + "\n")

print(f"Completat! Total paraules consolidades: {len(llista_neta)}")
