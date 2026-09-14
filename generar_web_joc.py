import json
import re
import os

sortida = "vortaro_paraulogic.txt"
alfabet_eo = set("abcĉdefgĝhĥijĵklmnoprsŝtuŭvz")

# 1. Terminacions nominals i adjectivals legítimes
terminacions_nominals = ["o", "oj", "on", "ojn", "a", "aj", "an", "ajn", "e", "en"]

# 2. Formes verbals acceptades segons el Paraulògic:
# Només infinitiu (-i). Cap forma conjugada personal (-as, -is, -os, -us, -u queda fora).
terminacio_infinitiu = ["i"]

# Participis actius i passius (que funcionen com a formes adjectivals/nominals derivades)
sufixos_participis = ["ant", "int", "ont", "at", "it", "ot"]
terminacions_participi = ["a", "aj", "an", "ajn", "o", "oj", "on", "ojn", "e"]

# Sufixos derivatius comuns
sufixos_derivacio = ["in", "et", "eg", "ec", "aĵ", "il", "ej", "ul", "ist"]

# 3. Paraules invariables / funcionals legítimes de diccionari
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

# 4. Extracció d'arrels vàlides des del corpus
arrels = set()

if os.path.exists("dataset_esperanto_master.jsonl"):
    with open("dataset_esperanto_master.jsonl", "r", encoding="utf-8") as f:
        for linia in f:
            if not linia.strip():
                continue
            try:
                d = json.loads(linia)
                text = d.get("text", "")
                if d.get("tipus") == "leksikono" and "Vorto:" in text:
                    parts = text.split("\nDifino:")
                    k = parts[0].replace("Vorto:", "").strip().lower()
                    k = k.split("/")[0].split("'")[0].split("|")[0]
                    k = re.sub(r'[^a-zĉĝĥĵŝŭ]', '', k)
                    if len(k) >= 2 and set(k).issubset(alfabet_eo):
                        arrels.add(k)
            except Exception:
                continue

arrels_clau = [
    "sent", "pens", "dir", "far", "vid", "ir", "ven", "don", "pren", "hav",
    "star", "sid", "kuŝ", "viv", "mort", "sci", "kon", "vol", "pov", "dev",
    "bon", "bel", "grand", "malgrand", "nov", "malnov", "long", "alt", "jun",
    "hom", "vir", "infan", "patr", "frat", "amik", "dom", "urb", "land", "mond",
    "libr", "vort", "lingv", "akv", "aer", "fajr", "ter", "sun", "lun", "stel",
    "temp", "jar", "tag", "nokt", "hor", "labor", "voj", "part", "lok", "man"
]
for a in arrels_clau:
    arrels.add(a)

print(f"Arrels identificades: {len(arrels)}")

# 5. Generació de lemes vàlids
for r in arrels:
    # A) Formes nominals i adjectivals (sento, sentoj, senton, sentojn, senta, sentaj...)
    for t in terminacions_nominals:
        w = r + t
        if len(w) >= 3 and set(w).issubset(alfabet_eo):
            paraules_totals.add(w)

    # B) Verbs: ÚNICAMENT infinitiu (-i)
    for t in terminacio_infinitiu:
        w = r + t
        if len(w) >= 3 and set(w).issubset(alfabet_eo):
            paraules_totals.add(w)

    # C) Participis (-anta, -into, -atojn...)
    for part in sufixos_participis:
        for t in terminacions_participi:
            w = r + part + t
            if len(w) >= 3 and set(w).issubset(alfabet_eo):
                paraules_totals.add(w)

    # D) Derivacions sufixals legítimes de diccionari
    for suf in sufixos_derivacio:
        for t in ["o", "oj", "on", "ojn", "a", "aj", "an", "ajn", "e", "i"]:
            w = r + suf + t
            if len(w) >= 3 and set(w).issubset(alfabet_eo):
                paraules_totals.add(w)

llista_final = sorted(list(paraules_totals))

print(f"Vocabulari depurat segons regles Paraulògic: {len(llista_final)} lemes.")
print("Formes conjugades (-as, -is, -os, -us, -u) i paraules truncades completament excloses.")

with open(sortida, "w", encoding="utf-8") as f:
    for p in llista_final:
        f.write(p + "\n")

print(f"Desat a '{sortida}' amb èxit!")