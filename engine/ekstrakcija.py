"""Korak 2 — izvlačenje veština iz teksta.

Dve tehnike (profesor je tražio da se tehnika izvlačenja preispita, pa ih poredimo):

1. recnik — traži ESCO nazive i sinonime direktno u tekstu.
   + jednostavno, besplatno, ne izmišlja
   − nalazi samo ono što je napisano istim rečima kao u ESCO-u (ESCO nema srpski!)

2. llm — LLM pročita tekst i vrati listu veština, uz citat iz teksta za svaku.
   + razume parafraze i srpski tekst
   − košta, može da izmisli (zato proveravamo citat)

Obe tehnike vraćaju isti oblik: lista rečnika {"vestina": ..., "citat": ...}.
"""

import re

import pandas as pd

from .llm import LLM
from .tekst import normalizuj

NAJKRACI_NAZIV = 2   # nazive od 1 slova (npr. "C", "R") rečnik preskače jer daju previše lažnih pogodaka


def _recenica_oko(tekst: str, pocetak: int, kraj: int) -> str:
    """Rečenica ili red teksta u kom se nalazi pogodak (služi kao citat)."""
    levo = max(tekst.rfind(z, 0, pocetak) for z in ".\n;") + 1
    desni = [tekst.find(z, kraj) for z in ".\n;"]
    desno = min([d for d in desni if d != -1], default=len(tekst))
    return tekst[levo:desno].strip()


class RecnikEkstraktor:
    def __init__(self, esco: pd.DataFrame):
        # Svi nazivi (zvanični + sinonimi), duži prvo, da „SQL Server“ ima prednost nad „SQL“.
        nazivi = set()
        for _, red in esco.iterrows():
            for naziv in [red["preferredLabel"], *red["altLabels"].split("\n")]:
                naziv = normalizuj(naziv)
                if len(naziv) >= NAJKRACI_NAZIV:
                    nazivi.add(naziv)
        self.nazivi = sorted(nazivi, key=len, reverse=True)

    def izvuci(self, tekst: str) -> list[dict]:
        norm = normalizuj(tekst)
        zauzeto = [False] * len(norm)          # da se isti deo teksta ne broji dvaput
        rezultat = []
        for naziv in self.nazivi:
            for m in re.finditer(r"(?<!\w)" + re.escape(naziv) + r"(?!\w)", norm):
                if any(zauzeto[m.start():m.end()]):
                    continue
                zauzeto[m.start():m.end()] = [True] * (m.end() - m.start())
                rezultat.append({"vestina": naziv, "citat": _recenica_oko(norm, m.start(), m.end())})
                break                          # dovoljan je jedan pogodak po nazivu
        return rezultat


PROMPT_LLM = """Iz sledećeg teksta izvuci sve veštine i znanja (tehnička znanja, alate, jezike, meke veštine).
Za svaku veštinu navedi i deo teksta iz kog si je izvukao, doslovno prepisan.
Ne dodaji veštine kojih nema u tekstu.

Odgovori samo JSON listom u obliku:
[{{"vestina": "...", "citat": "..."}}]

Tekst:
\"\"\"
{tekst}
\"\"\""""


class LlmEkstraktor:
    def __init__(self, llm: LLM):
        if not llm.ukljucen:
            raise ValueError("Za ekstrakciju 'llm' treba podesiti llm.provider u config.yaml.")
        self.llm = llm
        self.odbaceno = 0                      # koliko veština je odbačeno jer citat nije iz teksta

    def izvuci(self, tekst: str) -> list[dict]:
        odgovor = self.llm.pitaj_json(PROMPT_LLM.format(tekst=tekst))
        norm = normalizuj(tekst)
        rezultat = []
        for stavka in odgovor:
            citat = normalizuj(stavka.get("citat", ""))
            # Provera da LLM nije izmislio: citat mora stvarno da postoji u tekstu.
            if citat and citat in norm:
                rezultat.append({"vestina": stavka["vestina"].strip(), "citat": stavka["citat"]})
            else:
                self.odbaceno += 1
        return rezultat


def napravi_ekstraktor(tehnika: str, esco: pd.DataFrame, llm: LLM):
    if tehnika == "recnik":
        return RecnikEkstraktor(esco)
    if tehnika == "llm":
        return LlmEkstraktor(llm)
    raise ValueError(f"Nepoznata tehnika izvlačenja: {tehnika}")
