"""Ceo tok, od podataka do rezultata (koraci 1–5 iz dnevnika).

    1. učitavanje   → predmeti i oglasi
    2. ekstrakcija  → lista veština za svaki predmet i oglas
    3. ESCO         → svaka veština dobija ESCO naziv i ID
    4. poređenje    → za svaki oglas: šta je pokriveno, mera poklapanja u oba smera
    5. rezultat     → jaz, zastareo sadržaj, dataset
"""

import pandas as pd

from . import ucitavanje
from .dataset import snimi
from .ekstrakcija import napravi_ekstraktor
from .embedding import Embedder
from .esco import EscoMaper, tekst_za_embedding, ucitaj_esco
from .llm import LLM
from .poredjenje import jaz, oznaci_pokrivenost, poklapanja, zastareo_sadrzaj


def pokreni(cfg: dict, snimi_rezultate: bool = True, ispis: bool = True) -> dict:
    def log(poruka):
        if ispis:
            print(poruka)

    # --- Korak 1: učitavanje ---
    predmeti = ucitavanje.ucitaj_predmete(cfg["podaci"]["predmeti"])
    oglasi = ucitavanje.ucitaj_oglase(cfg["podaci"]["oglasi"])
    esco = ucitaj_esco(cfg["podaci"]["esco"])
    log(f"[1] {len(predmeti)} predmeta, {len(oglasi)} oglasa, {len(esco)} ESCO veština (nivo {cfg['nivo_predmeta']})")

    llm = LLM(cfg["llm"]["provider"], cfg["llm"]["model"], cfg["llm"]["temperatura"])
    embedder = Embedder(cfg["embedding_model"],
                        tekstovi_za_ucenje=[tekst_za_embedding(r) for _, r in esco.iterrows()])

    # --- Korak 2: izvlačenje veština ---
    ekstraktor = napravi_ekstraktor(cfg["ekstrakcija"], esco, llm)
    redovi_p, tekstovi_p = [], []
    for p in predmeti:
        tekst = ucitavanje.tekst_predmeta(p, cfg["nivo_predmeta"])
        tekstovi_p.append({"predmet_id": p["id"], "naziv": p["naziv"], "nivo": cfg["nivo_predmeta"], "tekst": tekst})
        for v in ekstraktor.izvuci(tekst):
            redovi_p.append({"predmet_id": p["id"], "predmet_naziv": p["naziv"], **v})
    redovi_o = []
    for _, o in oglasi.iterrows():
        tekst = ucitavanje.tekst_oglasa(o, cfg["oglas_sa_opisom_firme"])
        for v in ekstraktor.izvuci(tekst):
            redovi_o.append({"oglas_id": o["id"], **v})
    vestine_predmeta = pd.DataFrame(redovi_p, columns=["predmet_id", "predmet_naziv", "vestina", "citat"])
    vestine_oglasa = pd.DataFrame(redovi_o, columns=["oglas_id", "vestina", "citat"])
    log(f"[2] tehnika '{cfg['ekstrakcija']}': {len(vestine_predmeta)} veština iz predmeta, "
        f"{len(vestine_oglasa)} iz oglasa")

    # --- Korak 3: prevođenje na ESCO ---
    maper = EscoMaper(esco, embedder, llm, cfg["top_k"], cfg["prag_esco"])
    kes = {}                                   # ista veština se mapira samo jednom

    def dodaj_esco(df):
        mapirano = [kes.setdefault(v, maper.mapiraj(v)) for v in df["vestina"]]
        return pd.concat([df.reset_index(drop=True), pd.DataFrame(mapirano, columns=["esco_uri", "esco_naziv", "slicnost"])
                          .rename(columns={"slicnost": "esco_slicnost"})], axis=1)

    vestine_predmeta = dodaj_esco(vestine_predmeta)
    vestine_oglasa = dodaj_esco(vestine_oglasa)
    bez_para = (vestine_oglasa["esco_uri"] == "").sum()
    log(f"[3] ESCO: {len(kes)} različitih veština mapirano; {bez_para} veština iz oglasa nema par u ESCO-u")

    # --- Korak 4: poređenje ---
    oznacene = oznaci_pokrivenost(vestine_oglasa, vestine_predmeta, cfg["put"], embedder, cfg["prag_b"])
    tabela_poklapanja = poklapanja(oznacene, vestine_predmeta, cfg["put"], embedder, cfg["prag_b"])
    tabela_poklapanja = oglasi[["id", "naziv", "firma"]].rename(columns={"id": "oglas_id"}).merge(
        tabela_poklapanja, on="oglas_id", how="left").fillna({"oglas_smer": 0.0, "smer_oglas": 0.0})
    tabela_poklapanja = tabela_poklapanja.sort_values("oglas_smer", ascending=False)
    log(f"[4] Put {cfg['put']}: prosečno poklapanje oglas→smer {tabela_poklapanja['oglas_smer'].mean():.0%}")

    # --- Korak 5: jaz i zastareo sadržaj ---
    tabela_jaz = jaz(oznacene, len(oglasi))
    tabela_zastareo = zastareo_sadrzaj(oznacene, vestine_predmeta, cfg["put"], len(oglasi),
                                       cfg["zastareo_max_udeo"], embedder, cfg["prag_b"])
    log(f"[5] jaz: {len(tabela_jaz)} veština; kandidati za zastareo sadržaj: {len(tabela_zastareo)}")

    tabele = {
        "oglasi": oglasi,
        "predmeti": pd.DataFrame(tekstovi_p),
        "vestine_oglasa": oznacene.drop(columns=["kljuc"]),
        "vestine_predmeta": vestine_predmeta,
        "poklapanja": tabela_poklapanja,
        "jaz": tabela_jaz.drop(columns=["kljuc"]),
        "zastareo": tabela_zastareo,
    }
    if snimi_rezultate:
        folder = snimi(f"rezultati/{cfg['naziv_pokretanja']}", tabele, cfg)
        log(f"Rezultati snimljeni u {folder}/")
    return tabele
