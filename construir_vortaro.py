import json
import re
import os

print("Llegint dataset_esperanto_master.jsonl per extreure el vocabulari canònic...")

mots_trobats = set()

# 1. Extracció directa i exhaustiva de lemes del dataset
if os.path.exists("dataset_esperanto_master.jsonl"):
    with open("dataset_esperanto_master.jsonl", "r", encoding="utf-8") as f:
        for linia in f:
            if not linia.strip():
                continue
            try:
                dada = json.loads(linia)
                text = dada.get("text", "")
                
                # Extracció per camp leksikono clàssic
                if "Vorto:" in text:
                    parts = text.split("\nDifino:")
                    if len(parts) >= 1:
                        w = re.sub(r'[^a-zĉĝĥĵŝŭ]', '', parts[0].replace("Vorto:", "").strip().lower())
                        if len(w) >= 3:
                            mots_trobats.add(w)

                # Si hi ha contingut lliure en esperanto al bloc, n'extreiem paraules candidates
                tokens = re.findall(r'[a-zĉĝĥĵŝŭ]+', text.lower())
                for t in tokens:
                    if len(t) >= 3 and not any(c in t for c in "qwx"):
                        # Acceptem lemes acabats en terminacions normatives
                        if t.endswith(("o", "a", "e", "i", "oj", "aj", "on", "an", "ojn", "ajn", "en")):
                            mots_trobats.add(t)
            except Exception:
                continue

print(f"Mots i formes extrets del dataset: {len(mots_trobats)}")

# 2. Arrels fonamentals bàsiques garantides (menjar, natura, dies, etc.)
arrels_fonamentals = [
    "melon", "pom", "pan", "lakto", "fromaĝ", "viand", "karn", "ov", "suker", "sal",
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
for af in arrels_fonamentals:
    mots_trobats.add(af + "o")
    mots_trobats.add(af + "a")
    mots_trobats.add(af + "e")
    mots_trobats.add(af + "i")

# 3. Partícules, preposicions, nombres i 'jes'
particules_i_correlatius = [
    "jes", "jen", "en", "antaŭ", "post", "apud", "inter", "sub", "sur", "tra", "trans",
    "por", "per", "kun", "sen", "pri", "pro", "kontraŭ", "dum", "ĝis", "ekster",
    "ĉirkaŭ", "malgraŭ", "anstataŭ", "laŭ", "po", "ne",
    "unu", "du", "tri", "kvar", "kvin", "ses", "sep", "ok", "naŭ", "dek", "cent", "mil",
    "tuj", "nun", "jam", "tro", "tre", "plu", "for", "mem", "preskaŭ", "apenaŭ"
]
for p in particules_i_correlatius:
    mots_trobats.add(p)
    # jes -> jeso, jesa, jese, jesi...
    for t in ["o", "oj", "on", "ojn", "a", "aj", "an", "ajn", "e", "i"]:
        mots_trobats.add(p + t)

# Correlatius
for pref in ["k", "t", "", "ĉ", "nen"]:
    for suf in ["io", "iu", "ia", "ie", "iel", "ial", "iam", "iom", "ies"]:
        m = pref + suf
        if len(m) >= 3:
            mots_trobats.add(m)
            if suf == "io":
                mots_trobats.add(m + "n")
            elif suf in ["iu", "ia"]:
                mots_trobats.add(m + "j")
                mots_trobats.add(m + "n")
                mots_trobats.add(m + "jn")
            elif suf == "ie":
                mots_trobats.add(m + "n")

# 4. Generació de flexions legítimes i filtratge ferm de verbs conjugats
vortaro_final = set()
terminacions_prohibides = ("as", "is", "os", "us")

for mot in mots_trobats:
    if len(mot) < 3 or any(c in mot for c in "qwx"):
        continue

    if mot.endswith(terminacions_prohibides):
        continue

    vortaro_final.add(mot)

    if mot.endswith("o"):
        vortaro_final.add(mot + "j")
        vortaro_final.add(mot + "n")
        vortaro_final.add(mot + "jn")
    elif mot.endswith("a"):
        vortaro_final.add(mot + "j")
        vortaro_final.add(mot + "n")
        vortaro_final.add(mot + "jn")
    elif mot.endswith("e"):
        vortaro_final.add(mot + "n")

llista_ordenada = sorted(list(vortaro_final))

with open("vortaro_paraulogic.txt", "w", encoding="utf-8") as f:
    for w in llista_ordenada:
        f.write(w + "\n")

print(f"Fitxer 'vortaro_paraulogic.txt' actualitzat amb èxit!")
print(f"Total de paraules vàlides: {len(llista_ordenada)}")
