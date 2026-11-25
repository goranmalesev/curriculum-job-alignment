## Arhitektura pipeline-a

Dijagram prikazuje kako podaci prolaze kroz kod: od ulaznih fajlova, kroz pet koraka engine-a, do rezultata (dataset) i aplikacije. Istraživački deo (desno dole) ne pravi poseban sistem, nego isti pipeline pokreće više puta sa drugim podešavanjima.

```mermaid
flowchart TB
    subgraph ULAZ["Ulazni podaci (data/ ili primer_podaci/)"]
        P["predmeti.json<br/>naziv, opis, ishodi,<br/>sadržaj, materijali"]
        O["oglasi.csv<br/>ceo tekst oglasa,<br/>firma, izvor, datum"]
        E["ESCO skills_en.csv<br/>13.960 veština"]
    end

    CFG["config.yaml<br/>nivo V0–V3, put A/B,<br/>tehnika, model, pragovi"]
    RUN["pokreni.py → engine/pipeline.py"]

    subgraph ENGINE["engine/ — softverski deo"]
        K1["1. ucitavanje.py<br/>tekst predmeta po nivou V0–V3<br/>tekst oglasa (± opis firme)"]
        K2["2. ekstrakcija.py<br/>rečnik ILI LLM (llm.py)<br/>→ veština + citat"]
        K3["3. esco.py + embedding.py<br/>tačan naziv → ako nema:<br/>top-k kandidata → izbor"]
        K4["4. poredjenje.py<br/>Put A: isti ESCO ID<br/>Put B: sličnost ≥ prag"]
        K5["5. poredjenje.py + dataset.py<br/>poklapanje u oba smera,<br/>jaz, zastareo sadržaj"]
    end

    subgraph IZLAZ["rezultati/naziv_pokretanja/ — dataset"]
        D["oglasi, predmeti,<br/>vestine_oglasa, vestine_predmeta,<br/>poklapanja, jaz, zastareo, config"]
    end

    APP["aplikacija.py (Streamlit)<br/>Smer → oglasi · Oglas → smer · Za fakultet"]

    subgraph ISTR["istrazivanje/ — istraživački deo"]
        T["test_skup.csv<br/>(Ivanin dataset)"]
        EV["evaluacija.py<br/>preciznost, odziv, F1"]
        EX["eksperimenti.py<br/>V0–V3 × Put A/B"]
        TAB["rezultati/eksperimenti.csv"]
    end

    P --> K1
    O --> K1
    CFG --> RUN --> K1
    K1 --> K2 --> K3 --> K4 --> K5
    E --> K2
    E --> K3
    K5 --> D --> APP
    EX -. "pokreće pipeline<br/>sa drugim podešavanjima" .-> RUN
    D --> EV
    T --> EV
    EV --> TAB
    EX --> TAB
```

### Šta ulazi i izlazi iz svakog koraka

| Korak | Ulaz | Izlaz |
|---|---|---|
| 1. `ucitavanje.py` | `predmeti.json`, `oglasi.csv`, nivo iz `config.yaml` | čist tekst svakog predmeta i oglasa |
| 2. `ekstrakcija.py` | tekst | lista veština, uz citat iz teksta za svaku |
| 3. `esco.py` | lista veština, ESCO | ESCO naziv i ID za svaku veštinu (ili „nema u ESCO-u“) |
| 4. `poredjenje.py` | ESCO veštine oglasa i predmeta | za svaku veštinu iz oglasa: pokrivena ili ne, kojim predmetom |
| 5. `poredjenje.py`, `dataset.py` | tabela iz koraka 4 | mera poklapanja po oglasu (oba smera), jaz, zastareo sadržaj, dataset u CSV-u |
| aplikacija | dataset iz `rezultati/` | prikaz za studenta i fakultet |
| evaluacija | dataset + test skup | preciznost, odziv, F1 |
| eksperimenti | `config.yaml` + lista nivoa i puteva | tabela rezultata za sve kombinacije |
