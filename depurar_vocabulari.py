import json
import re
import os

sortida = "vortaro_paraulogic.txt"
alfabet_eo = set("abcĉdefgĝhĥijĵklmnoprsŝtuŭvz")

# Terminacions vàlides segons les regles del Paraulògic (Sense verbs conjugats en -as, -is, -os, -us, -u)
terminacions_nominals = ["o", "oj", "on", "ojn", "a", "aj", "an", "ajn", "e", "en"]
terminacions_infinitiu = ["i"]
sufixos_participis = ["ant", "int", "ont", "at", "it", "ot"]
terminacions_participi = ["a", "aj", "an", "ajn", "o", "oj", "on", "ojn", "e"]
sufixos_derivacio = ["in", "et", "eg", "ec", "aĵ", "il", "ej", "ul", "ist", "an"]

# Paraules invariables / funcionals bàsiques
invariables_base = [
    "kaj", "sed", "ke", "ĉu", "en", "de", "al", "kun", "per", "por", "pri", "sub", "super", 
    "sur", "dum", "ĝis", "inter", "tra", "ĉe", "kontraŭ", "anstataŭ", "krom", "sen",
    "mi", "vi", "li", "ŝi", "ĝi", "si", "ni", "ili", "oni", "ci",
    "kio", "kiu", "kia", "kies", "kiel", "kiam", "kiom", "kial", "kie",
    "tio", "tiu", "tia", "ties", "tiel", "tiam", "tiom", "tial", "tie",
    "io", "iu", "ia", "ies", "iel", "iam", "iom", "ial", "ie",
    "ĉio", "ĉiu", "ĉia", "ĉies", "ĉiel", "ĉiam", "ĉiom", "ĉial", "ĉie",
    "nenio", "neniu", "nenia", "nenies", "neniel", "neniam", "neniom", "nenial", "nenie",
    "unu", "du", "tri", "kvar", "kvin", "ses", "sep", "ok", "naŭ", "dek", "cent", "mil",
    "tuj", "jam", "ankoraŭ", "nur", "tre", "tro", "pli", "plej", "for", "jen", "nek", "ja", "do"
]

paraules_totals = set()
for inv in invariables_base:
    if len(inv) >= 3 and set(inv).issubset(alfabet_eo):
        paraules_totals.add(inv)

arrels = set()

# 1. Extracció directa de les 5.081 entrades de npiv_complet.jsonl
if os.path.exists("npiv_complet.jsonl"):
    print("Llegint arrels de 'npiv_complet.jsonl'...")
    with open("npiv_complet.jsonl", "r", encoding="utf-8") as f:
        for linia in f:
            if not linia.strip():
                continue
            try:
                d = json.loads(linia)
                # El cap de mot pot venir a "kapvorto" o dins de text
                k = d.get("kapvorto", "")
                if not k and "text" in d:
                    m = re.match(r'^(.*?)[,|]', d["text"])
                    if m:
                        k = m.group(1)
                
                # Neteja de caràcters auxiliars del diccionari (ex: bon', libr/, k|o)
                k = k.split("/")[0].split("'")[0].split("|")[0].strip().lower()
                k = re.sub(r'[^a-zĉĝĥĵŝŭ]', '', k)
                if len(k) >= 2 and set(k).issubset(alfabet_eo):
                    arrels.add(k)
            except Exception:
                continue

print(f"Arrels extretes de npiv_complet: {len(arrels)}")

# 2. Extracció d'arrels addicionals del fitxer mestre
if os.path.exists("dataset_esperanto_master.jsonl"):
    print("Processant el dataset mestre...")
    with open("dataset_esperanto_master.jsonl", "r", encoding="utf-8") as f:
        for linia in f:
            if not linia.strip():
                continue
            try:
                d = json.loads(linia)
                txt = d.get("text", "")
                if d.get("tipus") == "leksikono":
                    # Busca qualsevol línia inicial amb la paraula o terme
                    linies = txt.split("\n")
                    terme = linies[0].replace("Vorto:", "").strip().lower()
                    terme = terme.split("/")[0].split("'")[0].split("|")[0].split(",")[0]
                    terme = re.sub(r'[^a-zĉĝĥĵŝŭ]', '', terme)
                    if len(terme) >= 2 and set(terme).issubset(alfabet_eo):
                        arrels.add(terme)
            except Exception:
                continue

print(f"Total d'arrels vàlides consolidades: {len(arrels)}")

# 3. Generació estricta segons regles del Paraulògic
for r in arrels:
    # A) Formes nominals i adjectivals
    for t in terminacions_nominals:
        w = r + t
        if len(w) >= 3 and set(w).issubset(alfabet_eo):
            paraules_totals.add(w)

    # B) Verbs: ÚNICAMENT infinitiu (-i)
    for t in terminacions_infinitiu:
        w = r + t
        if len(w) >= 3 and set(w).issubset(alfabet_eo):
            paraules_totals.add(w)

    # C) Participis (-anta, -intoj, -ata, -itojn...)
    for part in sufixos_participis:
        for t in terminacions_participi:
            w = r + part + t
            if len(w) >= 3 and set(w).issubset(alfabet_eo):
                paraules_totals.add(w)

    # D) Derivacions sufixades clàssiques
    for suf in sufixos_derivacio:
        for t in ["o", "oj", "on", "ojn", "a", "aj", "an", "ajn", "e", "i"]:
            w = r + suf + t
            if len(w) >= 3 and set(w).issubset(alfabet_eo):
                paraules_totals.add(w)

llista_final = sorted(list(paraules_totals))

print("-" * 50)
print(f"Total de lemes Paraulògic generats: {len(llista_final)}")
print("Exclosos tots els conjugats (-as, -is, -os, -us, -u) i caràcters truncats.")

with open(sortida, "w", encoding="utf-8") as f:
    for p in llista_final:
        f.write(p + "\n")

print(f"Fitxer '{sortida}' actualitzat correctament!")