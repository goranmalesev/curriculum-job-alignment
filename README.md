# Procena relevantnosti kurikuluma analizom oglasa za posao

Projekat 11 — *Curriculum Relevance Assessment by Analyzing Job Ads*.
Autor: Goran Malešev (E2 162) · Mentor: Goran Savić

Cilj: istražiti kako se relevantnost nastavnog programa može proceniti poređenjem kompetencija iz kurikuluma sa kompetencijama traženim u oglasima za posao, i koji izvori obogaćivanja (ishodi učenja, silabus, materijali, informacije o firmama, ESCO) najviše doprinose kvalitetu uparivanja.

Projekat se oslanja na Turaev i sar. (2026), arXiv:2606.01982, uz više izvora i višejezički (srpski + engleski) model.

## Sadržaj repozitorijuma

```
.
├── README.md
├── ISTRAZIVACKI_DNEVNIK.md   # pojmovi, metodologija, plan i sledeći koraci
├── DNEVNIK_EVIDENCIJE.md     # evidencija rada: šta sam radio pri svakom radu
├── docs/                     # pregled literature (Projekat11_final.docx)
├── src/                      # engine: krouleri, ekstrakcija, mapiranje, poređenje
├── experiments/              # naučni deo: ablacija, poređenje modela, evaluacija
├── notebooks/                # eksperimentalni notebook-ovi
└── data/                     # lokalno, NIJE u repozitorijumu (vidi .gitignore)
```

## Dva koloseka

- **Softverski engine** (`src/`): ponovljiv pipeline od prikupljanja do vizuelizacije.
- **Naučno istraživanje** (`experiments/`): istraživačka pitanja, eksperimenti i evaluacija.

## Podaci

Sirovi oglasi i dokumenti kurikuluma se ne objavljuju u repozitorijumu (uslovi korišćenja izvora). U repozitorijum ulaze samo kod, agregatni rezultati i kratki primeri.

## Status

Prva faza: pregled literature i određivanje doprinosa (oktobar 2026). Detalji u `ISTRAZIVACKI_DNEVNIK.md`.
