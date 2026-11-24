"""Dataset kao rezultat projekta (smernica profesora, 23.11.).

Sve što pipeline prikupi i izračuna snima se u folder rezultati/<naziv_pokretanja>/:

  oglasi.csv           ceo tekst oglasa + izvor, link, datum
  predmeti.csv         tekst predmeta na izabranom nivou (V0–V3)
  vestine_oglasa.csv   veština, citat, ESCO naziv i ID, da li je pokrivena i kojim predmetom
  vestine_predmeta.csv veština, citat, ESCO naziv i ID, predmet
  poklapanja.csv       mera poklapanja za svaki oglas, u oba smera
  jaz.csv              tražene veštine koje smer ne pokriva
  zastareo.csv         veštine koje se uče, a (skoro) ne traže
  config.yaml          podešavanja sa kojima je pokretanje urađeno (da bi se moglo ponoviti)
"""

from pathlib import Path

import yaml


def snimi(folder: str, tabele: dict, config: dict) -> Path:
    putanja = Path(folder)
    putanja.mkdir(parents=True, exist_ok=True)
    for ime, tabela in tabele.items():
        tabela.to_csv(putanja / f"{ime}.csv", index=False, encoding="utf-8")
    with open(putanja / "config.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, allow_unicode=True, sort_keys=False)
    return putanja
