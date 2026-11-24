"""Korak 6 — koliko sistem greši.

Test skup (Ivanin dataset ili ručno označeni oglasi) treba da bude CSV sa kolonama:
    oglas_id   — ID oglasa (isti kao u oglasi.csv)
    vestina    — veština koju oglas traži (kako je čovek zapisao)
    pokriveno  — da / ne (da li je smer pokriva, po proceni čoveka)

Ivanin dataset verovatno ima drugačiji format; tada se napiše mala funkcija koja ga
pretvori u ovaj oblik, a ostatak evaluacije ostaje isti.

Mere:
- izvuceno:    od veština iz test skupa, koliko ih je sistem uopšte pronašao u oglasu (korak 2)
- preciznost:  kada sistem kaže „pokriveno“, koliko često je u pravu
- odziv:       od veština koje su stvarno pokrivene, koliko ih je sistem označio kao pokrivene
- F1:          jedan broj koji spaja preciznost i odziv
"""

import pandas as pd

from engine.tekst import normalizuj


def ucitaj_test_skup(putanja: str) -> pd.DataFrame:
    t = pd.read_csv(putanja, dtype=str).fillna("")
    t["pokriveno"] = t["pokriveno"].str.strip().str.lower().isin(["da", "1", "true", "yes"])
    return t


def _isti(a: str, b: str) -> bool:
    """Da li su dva naziva veštine ista: jednaki su, ili je jedan sadržan u drugom."""
    a, b = normalizuj(a), normalizuj(b)
    return bool(a and b) and (a == b or a in b or b in a)


def proceni(vestine_oglasa: pd.DataFrame, test: pd.DataFrame) -> dict:
    """Poredi odluke sistema sa test skupom. Vraća mere i tabelu po veštinama."""
    redovi = []
    for _, t in test.iterrows():
        sistem = vestine_oglasa[vestine_oglasa["oglas_id"] == t["oglas_id"]]
        pogodak = sistem[[_isti(t["vestina"], v) or _isti(t["vestina"], e)
                          for v, e in zip(sistem["vestina"], sistem["esco_naziv"])]]
        izvuceno = len(pogodak) > 0
        sistem_kaze = bool(pogodak["pokriveno"].any()) if izvuceno else False
        redovi.append({"oglas_id": t["oglas_id"], "vestina": t["vestina"], "izvuceno": izvuceno,
                       "covek": t["pokriveno"], "sistem": sistem_kaze})
    detalji = pd.DataFrame(redovi)

    tp = int((detalji["covek"] & detalji["sistem"]).sum())      # oba kažu „pokriveno“
    fp = int((~detalji["covek"] & detalji["sistem"]).sum())     # sistem kaže „pokriveno“, a nije
    fn = int((detalji["covek"] & ~detalji["sistem"]).sum())     # pokriveno je, a sistem nije video
    preciznost = tp / (tp + fp) if tp + fp else 0.0
    odziv = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * preciznost * odziv / (preciznost + odziv) if preciznost + odziv else 0.0
    mere = {
        "izvuceno": round(detalji["izvuceno"].mean(), 3) if len(detalji) else 0.0,
        "preciznost": round(preciznost, 3),
        "odziv": round(odziv, 3),
        "f1": round(f1, 3),
        "tp": tp, "fp": fp, "fn": fn,
    }
    return {"mere": mere, "detalji": detalji}
