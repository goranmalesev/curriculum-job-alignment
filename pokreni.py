"""Pokretanje pipeline-a iz komandne linije.

Primeri:
    python pokreni.py                              # sve kako piše u config.yaml
    python pokreni.py --nivo V1 --put B            # promena nivoa i puta bez menjanja config.yaml
    python pokreni.py --config moj_config.yaml
"""

import argparse

import yaml

from engine.pipeline import pokreni


def main():
    p = argparse.ArgumentParser(description="Pipeline: kurikulum ↔ oglasi za posao")
    p.add_argument("--config", default="config.yaml")
    p.add_argument("--nivo", choices=["V0", "V1", "V2", "V3"], help="nivo teksta o predmetu")
    p.add_argument("--put", choices=["A", "B"], help="A = preko ESCO-a, B = bez ESCO-a")
    p.add_argument("--ekstrakcija", choices=["recnik", "llm"])
    p.add_argument("--naziv", help="naziv pokretanja (folder u rezultati/)")
    a = p.parse_args()

    with open(a.config, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if a.nivo:
        cfg["nivo_predmeta"] = a.nivo
    if a.put:
        cfg["put"] = a.put
    if a.ekstrakcija:
        cfg["ekstrakcija"] = a.ekstrakcija
    if a.naziv:
        cfg["naziv_pokretanja"] = a.naziv

    pokreni(cfg)


if __name__ == "__main__":
    main()
