"""Koraci 7 i 8 — eksperimenti.

Isti engine se pokreće za svaku kombinaciju:
    nivo teksta o predmetu (V0–V3)  ×  put (A = preko ESCO-a, B = bez ESCO-a)
i za svaku se meri preciznost i odziv na test skupu.

Pokretanje:
    python -m istrazivanje.eksperimenti
    python -m istrazivanje.eksperimenti --nivoi V0 V1 --putevi A

Rezultat: rezultati/eksperimenti.csv (jedan red = jedno pokretanje).
"""

import argparse
import copy
from pathlib import Path

import pandas as pd
import yaml

from engine.pipeline import pokreni
from istrazivanje.evaluacija import proceni, ucitaj_test_skup


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", default="config.yaml")
    p.add_argument("--nivoi", nargs="+", default=["V0", "V1", "V2", "V3"])
    p.add_argument("--putevi", nargs="+", default=["A", "B"])
    a = p.parse_args()

    with open(a.config, encoding="utf-8") as f:
        osnovni = yaml.safe_load(f)
    test = ucitaj_test_skup(osnovni["test_skup"])

    redovi = []
    for put in a.putevi:
        for nivo in a.nivoi:
            cfg = copy.deepcopy(osnovni)
            cfg["nivo_predmeta"], cfg["put"] = nivo, put
            cfg["naziv_pokretanja"] = f"eksperiment_{nivo}_put{put}"
            tabele = pokreni(cfg, snimi_rezultate=True, ispis=False)
            rezultat = proceni(tabele["vestine_oglasa"], test)
            redovi.append({"nivo": nivo, "put": put, "ekstrakcija": cfg["ekstrakcija"],
                           "embedding": cfg["embedding_model"], **rezultat["mere"]})
            m = rezultat["mere"]
            print(f"{nivo}  put {put}:  preciznost {m['preciznost']:.2f}  odziv {m['odziv']:.2f}  F1 {m['f1']:.2f}")

    tabela = pd.DataFrame(redovi)
    Path("rezultati").mkdir(exist_ok=True)
    tabela.to_csv("rezultati/eksperimenti.csv", index=False)
    print("\nTabela snimljena u rezultati/eksperimenti.csv")


if __name__ == "__main__":
    main()
