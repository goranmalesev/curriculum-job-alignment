"""Korak 1 — učitavanje predmeta i oglasa.

Predmeti se čitaju iz JSON fajla, oglasi iz CSV fajla. Kako su ti fajlovi nastali
(ručno, krouler, Ivanin dataset...) nije bitno: engine radi sa ovim formatom.

Ovde se određuje i KOLIKO teksta sistem vidi (nivoi V0–V3 iz koraka 7).
"""

import json

import pandas as pd

from .tekst import u_latinicu

# Koja polja predmeta ulaze u tekst na kom nivou (korak 7 u dnevniku).
NIVOI = {
    "V0": ["naziv", "opis"],
    "V1": ["naziv", "opis", "ishodi"],
    "V2": ["naziv", "opis", "ishodi", "sadrzaj"],
    "V3": ["naziv", "opis", "ishodi", "sadrzaj", "materijali"],
}


def ucitaj_predmete(putanja: str) -> list[dict]:
    """Lista predmeta. Svaki predmet: id, naziv, opis, ishodi, sadrzaj, materijali."""
    with open(putanja, encoding="utf-8") as f:
        return json.load(f)


def tekst_predmeta(predmet: dict, nivo: str) -> str:
    """Spaja polja predmeta koja pripadaju zadatom nivou u jedan tekst."""
    delovi = []
    for polje in NIVOI[nivo]:
        vrednost = predmet.get(polje) or ""
        if isinstance(vrednost, list):          # npr. lista ishoda
            vrednost = "\n".join(vrednost)
        if vrednost:
            delovi.append(vrednost)
    return u_latinicu("\n".join(delovi))


def ucitaj_oglase(putanja: str) -> pd.DataFrame:
    """Tabela oglasa: id, naziv, firma, izvor, link, datum, tekst, opis_firme."""
    oglasi = pd.read_csv(putanja, dtype=str).fillna("")
    return oglasi


def tekst_oglasa(oglas: pd.Series, sa_opisom_firme: bool) -> str:
    """Tekst oglasa; po izboru se dodaje i opis firme (obogaćivanje na strani oglasa)."""
    tekst = oglas["tekst"]
    if sa_opisom_firme and oglas.get("opis_firme"):
        tekst += "\n" + oglas["opis_firme"]
    return u_latinicu(tekst)


def pdf_u_tekst(putanja: str) -> str:
    """Pomoćna funkcija: vadi tekst iz PDF-a (knjiga predmeta, slajdovi)."""
    import pdfplumber

    with pdfplumber.open(putanja) as pdf:
        return "\n".join(strana.extract_text() or "" for strana in pdf.pages)
