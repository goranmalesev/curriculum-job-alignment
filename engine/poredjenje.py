"""Korak 4 i 5 — poređenje oglasa i smera, jaz i zastareo sadržaj.

Poklapanje se računa u DVA smera (smernica profesora, 23.11.):
- oglas → smer: koliko veština iz oglasa smer pokriva      = pokriveno / sve veštine oglasa
- smer → oglas: koliko od onoga što smer uči oglas traži   = tražene veštine smera / sve veštine smera

Dva puta (korak 8):
- Put A: veštine se porede preko ESCO ID-a (ista ESCO veština = poklapanje)
- Put B: veština iz oglasa se direktno poredi embeddingom sa veštinama predmeta (sličnost >= prag)
"""

import pandas as pd

from .embedding import Embedder, kosinusna_slicnost
from .tekst import normalizuj


def kljuc(red: pd.Series) -> str:
    """Put A: veštinu predstavlja ESCO ID; ako nema para u ESCO-u, njen normalizovan naziv."""
    return red["esco_uri"] if red["esco_uri"] else "tekst:" + normalizuj(red["vestina"])


def oznaci_pokrivenost(vestine_oglasa: pd.DataFrame, vestine_predmeta: pd.DataFrame,
                       put: str, embedder: Embedder | None, prag_b: float) -> pd.DataFrame:
    """Za svaku veštinu iz oglasa: da li je smer pokriva i kojim predmetom."""
    v = vestine_oglasa.copy()
    if put == "A":
        v["kljuc"] = v.apply(kljuc, axis=1)
        p = vestine_predmeta.assign(kljuc=vestine_predmeta.apply(kljuc, axis=1))
        predmeti_po_kljucu = p.groupby("kljuc")["predmet_naziv"].apply(lambda s: ", ".join(sorted(set(s))))
        v["pokriveno"] = v["kljuc"].isin(predmeti_po_kljucu.index)
        v["predmet"] = v["kljuc"].map(predmeti_po_kljucu).fillna("")
        v["slicnost"] = v["pokriveno"].astype(float)
    elif put == "B":
        v["kljuc"] = v["vestina"].map(normalizuj)
        if len(v) and len(vestine_predmeta):
            s = kosinusna_slicnost(embedder.vektori(v["vestina"].tolist()),
                                   embedder.vektori(vestine_predmeta["vestina"].tolist()))
            najbolji = s.argmax(axis=1)
            v["slicnost"] = s.max(axis=1)
            v["pokriveno"] = v["slicnost"] >= prag_b
            v["predmet"] = [vestine_predmeta.iloc[j]["predmet_naziv"] if ok else ""
                            for j, ok in zip(najbolji, v["pokriveno"])]
        else:
            v["slicnost"], v["pokriveno"], v["predmet"] = 0.0, False, ""
    else:
        raise ValueError(f"Nepoznat put: {put}")
    return v


def kljucevi_smera(vestine_predmeta: pd.DataFrame, put: str) -> pd.Series:
    if put == "A":
        return vestine_predmeta.apply(kljuc, axis=1)
    return vestine_predmeta["vestina"].map(normalizuj)


def poklapanja(oznacene: pd.DataFrame, vestine_predmeta: pd.DataFrame, put: str,
               embedder: Embedder | None, prag_b: float) -> pd.DataFrame:
    """Mera poklapanja za svaki oglas, u oba smera."""
    smer = vestine_predmeta.assign(kljuc=kljucevi_smera(vestine_predmeta, put)).drop_duplicates("kljuc")
    redovi = []
    for oglas_id, grupa in oznacene.groupby("oglas_id", sort=False):
        grupa = grupa.drop_duplicates("kljuc")
        broj = len(grupa)
        pokriveno = int(grupa["pokriveno"].sum())

        # smer → oglas: koliko veština smera ovaj oglas traži
        if len(smer) == 0:
            trazene_smer = 0
        elif put == "A":
            trazene_smer = smer["kljuc"].isin(set(grupa["kljuc"])).sum()
        else:
            s = kosinusna_slicnost(embedder.vektori(smer["vestina"].tolist()),
                                   embedder.vektori(grupa["vestina"].tolist()))
            trazene_smer = int((s.max(axis=1) >= prag_b).sum())

        redovi.append({
            "oglas_id": oglas_id,
            "broj_vestina_oglasa": broj,
            "pokriveno": pokriveno,
            "oglas_smer": round(pokriveno / broj, 3) if broj else 0.0,
            "smer_oglas": round(trazene_smer / len(smer), 3) if len(smer) else 0.0,
            "nedostaje": ", ".join(grupa.loc[~grupa["pokriveno"], "vestina"]),
        })
    return pd.DataFrame(redovi)


def jaz(oznacene: pd.DataFrame, broj_oglasa: int) -> pd.DataFrame:
    """Veštine iz oglasa koje smer ne pokriva, poređane po tome koliko se često traže."""
    po_vestini = (oznacene.drop_duplicates(["oglas_id", "kljuc"])
                  .groupby("kljuc")
                  .agg(vestina=("vestina", "first"),
                       esco_naziv=("esco_naziv", "first"),
                       broj_oglasa=("oglas_id", "nunique"),
                       pokriveno=("pokriveno", "max")))
    po_vestini["udeo_oglasa"] = (po_vestini["broj_oglasa"] / broj_oglasa).round(3)
    return (po_vestini[~po_vestini["pokriveno"]]
            .sort_values("broj_oglasa", ascending=False)
            .reset_index())


def zastareo_sadrzaj(oznacene: pd.DataFrame, vestine_predmeta: pd.DataFrame, put: str,
                     broj_oglasa: int, max_udeo: float, embedder: Embedder | None = None,
                     prag_b: float = 0.7) -> pd.DataFrame:
    """Veštine koje predmeti uče, a oglasi ih (skoro) ne traže. Kandidati za proveru, ne dokaz."""
    smer = vestine_predmeta.assign(kljuc=kljucevi_smera(vestine_predmeta, put)).reset_index(drop=True)
    if put == "A":
        trazi = oznacene.groupby("kljuc")["oglas_id"].nunique()
        smer["broj_oglasa"] = smer["kljuc"].map(trazi).fillna(0).astype(int)
    else:
        # Put B: veština smera se traži u oglasu ako joj je neka veština tog oglasa dovoljno slična.
        smer["broj_oglasa"] = 0
        if len(smer) and len(oznacene):
            s = kosinusna_slicnost(embedder.vektori(smer["vestina"].tolist()),
                                   embedder.vektori(oznacene["vestina"].tolist()))
            ids = oznacene["oglas_id"].to_numpy()
            smer["broj_oglasa"] = [len(set(ids[s[i] >= prag_b])) for i in range(len(smer))]
    smer["udeo_oglasa"] = (smer["broj_oglasa"] / broj_oglasa).round(3) if broj_oglasa else 0.0
    kolone = ["predmet_naziv", "vestina", "esco_naziv", "broj_oglasa", "udeo_oglasa"]
    return (smer[smer["udeo_oglasa"] <= max_udeo]
            .drop_duplicates(["predmet_naziv", "kljuc"])[kolone]
            .sort_values(["predmet_naziv", "vestina"])
            .reset_index(drop=True))
