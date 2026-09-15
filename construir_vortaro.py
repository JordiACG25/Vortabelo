import json
import re
import os

print("Llegint dataset_esperanto_master.jsonl per extreure el vocabulari canònic...")

mots_trobats = set()

# 1. Extracció directa de lemes i derivats del dataset
if os.path.exists("dataset_esperanto_master.jsonl"):
    with open("dataset_esperanto_master.jsonl", "r", encoding="utf-8") as f:
        for linia in f:
            if not linia.strip():
                continue
            try:
                dada = json.loads(linia)
                text = dada.get("text", "")
                
                # Entrades de tipus leksikono
                if dada.get("tipus") == "leksikono" and "Vorto:" in text:
                    parts = text.split("\nDifino:")
                    if len(parts) >= 1:
                        w = re.sub(r'[^a-zĉĝĥĵŝŭ]', '', parts[0].replace("Vorto:", "").strip().lower())
                        if len(w) >= 3:
                            mots_trobats.add(w)
                
                # Entrades d'instruccions / preguntes
                elif dada.get("tipus") == "instrukcio" and "Demando:" in text:
                    m = re.search(r'Demando:\s*(.*?)\s*\nRespondo:', text)
                    if m:
                        w = re.sub(r'[^a-zĉĝĥĵŝŭ]', '', m.group(1).lower())
                        if len(w) >= 3:
                            mots_trobats.add(w)
            except Exception:
                continue

print(f"Lemes bàsics extrets: {len(mots_trobats)}")

# 2. Afegir partícules, numerals i correlatius essencials
particules_i_correlatius = [
    "jen", "en", "antaŭ", "post", "apud", "inter", "sub", "sur", "tra", "trans",
    "por", "per", "kun", "sen", "pri", "pro", "kontraŭ", "dum", "ĝis", "ekster",
    "ĉirkaŭ", "malgraŭ", "anstataŭ", "laŭ", "po",
    "unu", "du", "tri", "kvar", "kvin", "ses", "sep", "ok", "naŭ", "dek", "cent", "mil",
    "tuj", "nun", "jam", "tro", "tre", "plu", "for", "mem", "preskaŭ", "apenaŭ"
]
for p in particules_i_correlatius:
    mots_trobats.add(p)

for pref in ["k", "t", "", "ĉ", "nen"]:
    for suf in ["io", "iu", "ia", "ie", "iel", "ial", "iam", "iom", "ies"]:
        m = pref + suf
        if len(m) >= 3:
            mots_trobats.add(m)

# 3. Generar les flexions regulars legítimes (plurals, acusatius, ordinals)
vortaro_final = set()
terminacions_prohibides = ("as", "is", "os", "us")

for mot in mots_trobats:
    if len(mot) < 3 or any(c in mot for c in "qwx"):
        continue

    if mot.endswith(terminacions_prohibides):
        continue

    vortaro_final.add(mot)

    # Flexions de substantius (-o)
    if mot.endswith("o"):
        vortaro_final.add(mot + "j")
        vortaro_final.add(mot + "n")
        vortaro_final.add(mot + "jn")

    # Flexions d'adjectius (-a)
    elif mot.endswith("a"):
        vortaro_final.add(mot + "j")
        vortaro_final.add(mot + "n")
        vortaro_final.add(mot + "jn")

    # Adverbis amb acusatiu de direcció (-en)
    elif mot.endswith("e"):
        vortaro_final.add(mot + "n")

    # Derivats d'adjectiu i substantiu per a numerals i partícules
    elif mot in particules_i_correlatius:
        for t in ["o", "oj", "on", "ojn", "a", "aj", "an", "ajn", "e"]:
            vortaro_final.add(mot + t)

llista_ordenada = sorted(list(vortaro_final))

with open("vortaro_paraulogic.txt", "w", encoding="utf-8") as f:
    for w in llista_ordenada:
        f.write(w + "\n")

print(f"Fitxer 'vortaro_paraulogic.txt' generat amb èxit!")
print(f"Total de paraules vàlides: {len(llista_ordenada)}")
