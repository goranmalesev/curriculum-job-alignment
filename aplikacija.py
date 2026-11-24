"""Prototip aplikacije (korak 5): čita rezultate pipeline-a i prikazuje ih.

Pokretanje:
    streamlit run aplikacija.py

Tri prikaza:
- Smer → oglasi: oglasi poređani po tome koliko ih smer pokriva
- Oglas → smer:  za izabran oglas, šta smer pokriva, a šta nedostaje
- Za fakultet:   jaz i kandidati za zastareo sadržaj
"""

from pathlib import Path

import pandas as pd
import streamlit as st
import yaml

st.set_page_config(page_title="Kurikulum i oglasi", layout="wide")
st.title("Kurikulum ↔ oglasi za posao")

pokretanja = sorted(p.name for p in Path("rezultati").glob("*") if (p / "poklapanja.csv").exists())
if not pokretanja:
    st.warning("Nema rezultata. Prvo pokreni: python pokreni.py")
    st.stop()

# Podrazumevano se prikazuje pokretanje iz config.yaml (npr. "primer"), a ne prvo po abecedi.
try:
    with open("config.yaml", encoding="utf-8") as f:
        podrazumevano = yaml.safe_load(f)["naziv_pokretanja"]
except Exception:
    podrazumevano = None
indeks = pokretanja.index(podrazumevano) if podrazumevano in pokretanja else 0
izbor = st.sidebar.selectbox("Pokretanje (podešavanja)", pokretanja, index=indeks)
folder = Path("rezultati") / izbor

# Iznad tabova piše sa kojim podešavanjima su rezultati dobijeni.
with open(folder / "config.yaml", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)
st.info(f"Prikazujem: **{izbor}** — nivo predmeta {cfg['nivo_predmeta']}, put {cfg['put']}, "
        f"ekstrakcija '{cfg['ekstrakcija']}'. Drugo pokretanje biraš u meniju levo.")
poklapanja = pd.read_csv(folder / "poklapanja.csv")
vestine = pd.read_csv(folder / "vestine_oglasa.csv").fillna("")
oglasi = pd.read_csv(folder / "oglasi.csv", dtype=str).fillna("")
jaz = pd.read_csv(folder / "jaz.csv")
zastareo = pd.read_csv(folder / "zastareo.csv")

smer_oglasi, oglas_smer, fakultet = st.tabs(["Smer → oglasi", "Oglas → smer", "Za fakultet"])

with smer_oglasi:
    st.caption("oglas_smer = koliko veština iz oglasa smer pokriva; smer_oglas = koliko od onoga što smer uči oglas traži")
    st.dataframe(poklapanja[["naziv", "firma", "oglas_smer", "smer_oglas", "nedostaje"]],
                 hide_index=True, width="stretch")

with oglas_smer:
    nazivi = dict(zip(oglasi["naziv"] + " — " + oglasi["firma"], oglasi["id"]))
    izabran = st.selectbox("Oglas", list(nazivi))
    oglas_id = nazivi[izabran]
    red = poklapanja[poklapanja["oglas_id"].astype(str) == str(oglas_id)]
    if len(red):
        st.metric("Pokrivenost oglasa", f"{red.iloc[0]['oglas_smer']:.0%}")
    v = vestine[vestine["oglas_id"].astype(str) == str(oglas_id)]
    st.dataframe(v[["vestina", "esco_naziv", "pokriveno", "predmet", "citat"]],
                 hide_index=True, width="stretch")

with fakultet:
    st.subheader("Jaz: traži se, a smer ne pokriva")
    st.dataframe(jaz, hide_index=True, width="stretch")
    st.subheader("Kandidati za zastareo sadržaj: uči se, a (skoro) ne traži")
    st.caption("Ovo nije dokaz da je sadržaj loš: teorija i osnove se retko pišu u oglasima.")
    st.dataframe(zastareo, hide_index=True, width="stretch")
