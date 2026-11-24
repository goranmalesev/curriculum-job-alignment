"""ESCO: učitavanje i Korak 3 — prevođenje veštine na ESCO naziv.

Pravi ESCO fajl (skills_en.csv sa ESCO portala) ima, između ostalog, kolone:
conceptUri, preferredLabel, altLabels (sinonimi, svaki u svom redu), description.
"""

import pandas as pd

from .embedding import Embedder, kosinusna_slicnost
from .llm import LLM
from .tekst import normalizuj


def ucitaj_esco(putanja: str) -> pd.DataFrame:
    esco = pd.read_csv(putanja, dtype=str).fillna("")
    return esco[["conceptUri", "preferredLabel", "altLabels", "description"]].reset_index(drop=True)


def tekst_za_embedding(red: pd.Series) -> str:
    """Tekst ESCO veštine koji se pretvara u embedding: naziv + sinonimi."""
    sinonimi = red["altLabels"].replace("\n", ", ")
    return f"{red['preferredLabel']}. {sinonimi}".strip(". ")


class EscoMaper:
    """Za veštinu iz teksta nalazi ESCO veštinu (korak 3)."""

    def __init__(self, esco: pd.DataFrame, embedder: Embedder, llm: LLM, top_k: int, prag: float):
        self.esco = esco
        self.embedder = embedder
        self.llm = llm
        self.top_k = top_k
        self.prag = prag
        # Svaku ESCO veštinu JEDNOM pretvorim u embedding (korak 3, tačka 1).
        self.esco_vektori = embedder.vektori([tekst_za_embedding(r) for _, r in esco.iterrows()])
        # Rečnik tačnih naziva: ako je veština napisana isto kao ESCO naziv ili sinonim,
        # embedding nije potreban (brže i sigurnije, npr. „Git“ → ESCO „Git“).
        self.tacni_nazivi = {}
        for i, red in esco.iterrows():
            for naziv in [red["preferredLabel"], *red["altLabels"].split("\n")]:
                if naziv.strip():
                    self.tacni_nazivi.setdefault(normalizuj(naziv), i)

    def kandidati(self, vestina: str) -> list[tuple[int, float]]:
        """Korak 3, tačka 2: top-k najsličnijih ESCO veština (indeks, sličnost)."""
        v = self.embedder.vektori([vestina])
        slicnosti = kosinusna_slicnost(v, self.esco_vektori)[0]
        najbolji = slicnosti.argsort()[::-1][: self.top_k]
        return [(int(i), float(slicnosti[i])) for i in najbolji]

    def mapiraj(self, vestina: str) -> dict:
        """Korak 3: prvo tačan naziv; ako ga nema, embedding nađe kandidate, pa se bira tačan
        (LLM, ili najbolji kandidat iznad praga ako LLM nije uključen)."""
        tacan = self.tacni_nazivi.get(normalizuj(vestina))
        if tacan is not None:
            red = self.esco.iloc[tacan]
            return {"esco_uri": red["conceptUri"], "esco_naziv": red["preferredLabel"], "slicnost": 1.0}

        kandidati = self.kandidati(vestina)
        izbor = None
        if self.llm.ukljucen:
            izbor = self._llm_bira(vestina, kandidati)
        elif kandidati and kandidati[0][1] >= self.prag:
            izbor = kandidati[0][0]

        if izbor is None:
            return {"esco_uri": "", "esco_naziv": "", "slicnost": kandidati[0][1] if kandidati else 0.0}
        red = self.esco.iloc[izbor]
        slicnost = dict(kandidati).get(izbor, 0.0)
        return {"esco_uri": red["conceptUri"], "esco_naziv": red["preferredLabel"], "slicnost": slicnost}

    def _llm_bira(self, vestina: str, kandidati: list[tuple[int, float]]) -> int | None:
        spisak = "\n".join(
            f"{n}. {self.esco.iloc[i]['preferredLabel']} — {self.esco.iloc[i]['description'][:200]}"
            for n, (i, _) in enumerate(kandidati, start=1)
        )
        prompt = (
            f"Veština iz teksta: \"{vestina}\"\n\n"
            f"Kandidati iz ESCO taksonomije:\n{spisak}\n\n"
            "Koji kandidat ima ISTO značenje kao veština iz teksta? "
            "Odgovori samo JSON-om: {\"izbor\": <redni broj>} ili {\"izbor\": 0} ako nijedan ne odgovara."
        )
        broj = int(self.llm.pitaj_json(prompt).get("izbor", 0))
        if 1 <= broj <= len(kandidati):
            return kandidati[broj - 1][0]
        return None
