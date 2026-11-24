# Procena relevantnosti kurikuluma analizom oglasa za posao

Projekat 11 — *Curriculum Relevance Assessment by Analyzing Job Ads*
Predmet: Savremene obrazovne tehnologije i standardi (SOTIS)
Autor: Goran Malešev (E2 162) · Mentor: Goran Savić

## O čemu je projekat

1. Iz 2–3 predmeta smera Računarstvo i automatika na FTN-u (uz nastavne materijale) i iz oglasa za posao izvlačim **listu veština**.
2. Obe liste prevodim na **iste standardne nazive** (ESCO), da bih mogao da ih uporedim.
3. Za svaki oglas računam **meru poklapanja u oba smera**: koliko traženih veština smer pokriva (oglas → smer) i koliko od onoga što smer uči oglas traži (smer → oglas). Student dobija listu poslova koji odgovaraju njegovom smeru, a fakultet vidi šta mu nedostaje (jaz).
4. Jedan od rezultata je i **dataset**: celi oglasi, predmeti i izvučene veštine.

**Istraživačko pitanje:** da li uparivanje postaje tačnije kada predmetu dodam još izvora (ishode učenja, sadržaj, nastavne materijale), i koji izvor najviše pomaže. Tačnost merim na test skupu (Ivanin dataset) i ručno proverenim primerima.

Projekat se oslanja na Turaev i sar. (2026), arXiv:2606.01982. Oni koriste samo ishode učenja i 30 oglasa; ja poredim više izvora, koristim oko 200 oglasa i višejezički (srpski + engleski) embedding model.

## Sadržaj repozitorijuma

| Šta | Gde |
|---|---|
| Istraživački dnevnik (pojmovi, metodologija, arhitektura, dnevnik rada) | `Istrazivacki_dnevnik.md` |
| Pregled literature (prva faza) | `Projekat11.docx` |
| Kod: softverski deo (koraci 1–5) | `engine/` |
| Kod: istraživački deo (koraci 6–8) | `istrazivanje/` |
| Kako se pokreće kod | `PIPELINE.md` |
| Mali izmišljeni primer podataka | `primer_podaci/` |

Detaljna struktura je u dnevniku, odeljak 3.5.

## Brzo pokretanje

```bash
pip install pandas numpy scikit-learn pyyaml streamlit
python pokreni.py                  # pipeline na primeru
python -m istrazivanje.eksperimenti
streamlit run aplikacija.py        # aplikacija
```

## Dva dela projekta

- **Softverski deo (engine):** program koji od tekstova predmeta i oglasa pravi rezultat: pokrivenost i jaz (koraci 1–5 u dnevniku).
- **Istraživački deo:** eksperimenti koji proveravaju koliko je rezultat tačan i šta ga popravlja (koraci 6–8 u dnevniku).

## Podaci

Sirovi oglasi i dokumenti kurikuluma se ne objavljuju u repozitorijumu (uslovi korišćenja izvora). U repozitorijum ulaze samo kod, agregatni rezultati i kratki primeri.

## Status

- Oktobar 2026: pregled literature i određivanje doprinosa (`Projekat11.docx`).
- Novembar 2026: definisani metodologija i arhitektura (`Istrazivacki_dnevnik.md`).
- Novembar 2026: prva verzija pipeline-a, isprobana na izmišljenom primeru i sa pravim ESCO-om (v1.2.1).
- Sledeće: pravi podaci (2–3 predmeta sa materijalima, oglasi), Ivanin dataset kao test skup, preispitivanje tehnike izvlačenja veština (LLM), izbor višejezičkog embedding modela.
