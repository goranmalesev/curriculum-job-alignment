"""Embedding: tekst → niz decimalnih brojeva (vektor).

Dve mogućnosti:
- pravi višejezički model (sentence-transformers), npr. BAAI/bge-m3 — za prave rezultate;
- 'tfidf' — jednostavan model zasnovan na delovima reči, radi bez interneta.
  Služi SAMO da se pipeline proba; ne razume značenje ni prevod (srpski ↔ engleski).
"""

import numpy as np


class Embedder:
    def __init__(self, model: str, tekstovi_za_ucenje: list[str] | None = None):
        self.model_ime = model
        if model == "tfidf":
            from sklearn.feature_extraction.text import TfidfVectorizer

            self._tfidf = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), lowercase=True)
            self._tfidf.fit(tekstovi_za_ucenje or ["prazno"])
        else:
            from sentence_transformers import SentenceTransformer

            self._st = SentenceTransformer(model)

    @property
    def dimenzija(self) -> int:
        if self.model_ime == "tfidf":
            return len(self._tfidf.vocabulary_)
        return self._st.get_sentence_embedding_dimension()

    def vektori(self, tekstovi: list[str]) -> np.ndarray:
        """Vraća matricu: jedan red = jedan tekst, dužine 1 (pa je skalarni proizvod = kosinusna sličnost)."""
        if not tekstovi:
            return np.zeros((0, self.dimenzija))
        if self.model_ime == "tfidf":
            # TF-IDF vektori su već dužine 1; ostaju „retki“ (sparse) jer bi pun oblik
            # za ceo ESCO (~14.000 veština) zauzeo previše memorije.
            return self._tfidf.transform(tekstovi)
        else:
            m = self._st.encode(tekstovi, convert_to_numpy=True)
        norme = np.linalg.norm(m, axis=1, keepdims=True)
        norme[norme == 0] = 1
        return m / norme


def kosinusna_slicnost(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Sličnost svakog reda iz `a` sa svakim redom iz `b` (vektori su već normalizovani)."""
    rezultat = a @ b.T
    if hasattr(rezultat, "toarray"):          # retka matrica (tfidf) → obična
        rezultat = rezultat.toarray()
    return np.asarray(rezultat)
