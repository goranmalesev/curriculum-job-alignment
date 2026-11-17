# Istraživački dnevnik

**Projekat 11 — Procena relevantnosti kurikuluma analizom oglasa za posao**
(*Curriculum Relevance Assessment by Analyzing Job Ads*)

Autor: Goran Malešev (E2 162) · Mentor: Goran Savić

---

## 0. Projekat u tri rečenice

1. Iz kurikuluma jednog smera na FTN-u i iz oglasa za posao izvlačim **listu veština**.
2. Obe liste prevodim na **iste standardne nazive** (ESCO), da bih mogao da ih uporedim.
3. Za svaki oglas računam **koliko traženih veština smer pokriva**. Tako student dobija listu poslova koji odgovaraju njegovom smeru, a fakultet vidi šta mu nedostaje.

**Šta je novo u odnosu na najbliži rad (Turaev i sar., 2026):** oni koriste samo ishode učenja i 30 oglasa. Ja proveravam da li uparivanje postaje tačnije kada predmetu dodam još izvora (ishode, sadržaj, materijale), i to merim na ručno proverenim primerima.

Kako su delovi sistema povezani: odeljak 3 (Arhitektura sistema).

---

## 0.1 Kako metodologija pokriva zadatak projekta

| Zahtev iz zadatka | Gde se rešava |
|---|---|
| Izdvojiti kompetencije iz kurikuluma i oglasa | Korak 2 |
| Uporediti ih | Koraci 3 i 4 |
| Pokazati šta kurikulum dobro pokriva | Korak 4 (pokrivenost oglasa) |
| Pokazati nedostatke | Korak 5 (jaz) |
| Pokazati zastarele sadržaje | Korak 5 (uči se, a ne traži se) |
| Obogatiti kratke tekstove dodatnim izvorima | Korak 7 (V0–V3, opis firme) |
| Istražiti koji izvori najviše doprinose | Korak 7 + ručna provera iz koraka 6 |
| Prototip za jedan domen | Korak 5 (aplikacija), domen: FTN, smer Računarstvo i automatika |

## 0.2 Šta preuzimam od Turaeva i sar. (2026), a šta radim drugačije

| | Turaev i sar. | Moj projekat |
|---|---|---|
| Program | Računarstvo, UAE University, 85 predmeta | FTN, Računarstvo i automatika |
| Šta čitaju iz predmeta | samo ishode učenja | opis, ishode, sadržaj, materijale (poredim šta pomaže) |
| Oglasi | 30, isečeni na rečenice-zahteve (483) | ~200, iz njih LLM izvlači veštine |
| Izvlačenje veština | dva LLM-a, neslaganja se rešavaju u dva koraka | jedan LLM (fiksiran model), uz citat iz teksta |
| Standardizacija | ESCO, SBERT, prag sličnosti 0,50 | ESCO preko višejezičkog embeddinga + LLM bira tačnu veštinu; poredim i put bez ESCO-a |
| Provera | uzorak od 50 zapisa, Cohenov κ = 0,79 za polje veštine | ručno označenih 50 oglasa, preciznost i odziv |
| Jezik | engleski | srpski + engleski |
| Rezultat | jaz po oblastima računarstva | jaz + lista poslova za studenta |

Pored Turaeva, koristim ideje iz još dva rada:
- **Andonovikj i Boškoski (2024)** uparuju tekst sa ESCO veštinama samo pomoću embeddinga i kosinusne sličnosti, bez dodatne provere. Tu ideju koristim u **Putu B** (korak 8), s tim što veštinu iz oglasa ne poredim sa ESCO-om, nego direktno sa veštinama iz predmeta.
- **Pelucchi i sar. (2026)** uparuju u dva koraka. Prvo embedding brzo pronađe nekoliko najsličnijih veština (kandidata). Među njima je obično i tačna, ali ima i pogrešnih. Zatim LLM pregleda kandidate i odluči koji je tačan. Isto radim u **koraku 3**: za veštinu „SQL upiti“ embedding vrati 5 kandidata (npr. SQL, PL/SQL, MySQL, NoSQL, upravljanje bazama podataka), a LLM izabere **SQL**. Sam embedding bi lako izabrao pogrešnu veštinu, npr. MySQL, jer je i ona značenjem blizu.

## 1. Osnovni pojmovi (onako kako ih ja koristim)

| Pojam | Šta znači u ovom projektu |
|---|---|
| **Kurikulum** | Spisak predmeta smera sa opisom, ciljem, ishodima i sadržajem svakog predmeta. |
| **Oglas** | Tekst oglasa za posao: šta se radi i šta se traži od kandidata. |
| **Veština** | Jedna konkretna stvar koju neko zna ili ume: „SQL“, „Java“, „rad u timu“. |
| **Ekstrakcija veština** | Iz teksta izvučem listu veština. Npr. iz „Iskustvo sa Javom i Spring Bootom“ dobijem `[Java, Spring Boot]`. |
| **ESCO** | Evropski spisak veština. Svaka veština ima jedan standardni naziv i ID. Koristim ga kao rečnik da „JS“, „JavaScript“ i „Javascript programiranje“ postanu ista stavka. |
| **Mapiranje na ESCO** | Za veštinu iz teksta nađem kojoj ESCO veštini odgovara. |
| **Embedding** | Tekst pretvoren u niz brojeva. Tekstovi sličnog značenja dobijaju slične nizove, pa mogu da merim koliko su dva teksta slična. |
| **Kosinusna sličnost** | Broj koji kaže koliko su dva embeddinga slična: blizu 1 znači „isto značenje“, blizu 0 znači „nema veze“. |
| **Višejezički model** | Embedding model koji „baze podataka“ i „databases“ smešta blizu, pa mogu da poredim srpski i engleski tekst. |
| **LLM** | Veliki jezički model (npr. GPT, Claude). Koristim ga za izvlačenje veština iz teksta i za proveru da li je neko uparivanje tačno. |
| **Pokrivenost oglasa** | Koliki deo veština iz oglasa smer pokriva. Oglas traži 8 veština, smer pokriva 4: pokrivenost je 4/8 = 50%. |
| **Jaz (skills gap)** | Veštine koje se često traže u oglasima, a nijedan predmet ih ne pokriva. |
| **Obogaćivanje** | Kratkom opisu predmeta dodam još teksta (ishode, sadržaj, materijale) da bi se lakše videlo šta se na predmetu uči. |
| **Referentni skup** | Mali skup primera koje sam **ručno** proverio. Služi da izmerim koliko sistem greši. |
| **Krouler** | Program koji automatski skida tekstove sa sajta (npr. oglase). |

---

## 2. Metodologija: šta konkretno radim

Postupak objašnjavam na jednom primeru. **Nazivi predmeta, tekst oglasa i brojevi u primeru su izmišljeni i služe samo za ilustraciju.** Prave vrednosti će biti u pilotu.

### Korak 1 — Prikupljam podatke

**Kurikulum.** Sa sajta FTN-a preuzimam knjigu predmeta za smer *Računarstvo i automatika*. Za svaki predmet čuvam: naziv, cilj, ishode učenja, sadržaj i literaturu.

**Oglasi.** Sa jednog portala (npr. Infostud ili HelloWorld) prikupljam oglase za poslove koji odgovaraju smeru („Java developer“, „Software engineer“, „QA engineer“...). Za početak je dovoljno oko 200 oglasa. Pre prikupljanja proveravam uslove korišćenja sajta i `robots.txt`. Ne čuvam lične podatke, a sirove oglase ne stavljam u javni repozitorijum.

*Primer:*
> **Predmet „Baze podataka“** — Ishodi: student ume da projektuje relacionu bazu i piše SQL upite. Sadržaj: ER model, normalizacija, SQL, transakcije, PostgreSQL.
>
> **Oglas „Junior Backend Developer“** — Tražimo: Java, Spring Boot, SQL (PostgreSQL), REST API, Git, Docker, dobra komunikacija.

### Korak 2 — Iz svakog teksta izvlačim listu veština

LLM-u dam tekst i tražim da vrati listu veština. Uz svaku veštinu mora da navede i deo teksta iz kog ju je izvukao, da bih mogao da proverim da nije izmislio.

*Primer:*
- Predmet „Baze podataka“ → `[projektovanje relacionih baza, SQL, normalizacija, transakcije, PostgreSQL]`
- Oglas → `[Java, Spring Boot, SQL, PostgreSQL, REST API, Git, Docker, komunikacija]`

### Korak 3 — Prevodim veštine na ESCO nazive

Problem: ista veština se piše na različite načine („SQL upiti“, „SQL“, „rad sa bazama“). Zato svaku veštinu prevodim na ESCO naziv:

1. Svaku ESCO veštinu jednom pretvorim u embedding.
2. Veštinu iz teksta pretvorim u embedding i nađem 5 najsličnijih ESCO veština.
3. LLM bira koja od tih 5 je tačna, ili kaže „nijedna“.

*Primer:* „SQL upiti“ → kandidati iz ESCO-a → LLM bira **SQL**.

Posle ovog koraka i predmeti i oglasi su **liste ESCO veština**, pa ih mogu direktno porediti.

**Napomena o jeziku:** ESCO postoji na 28 jezika, ali **srpski nije među njima** (hrvatski jeste). Zato veštine sa srpskog ne tražim po nazivu, već preko višejezičkog embedding modela, koji srpsku veštinu poredi sa engleskim ESCO nazivima. Kao proveru mogu da probam i hrvatske ESCO nazive.

### Korak 4 — Poredim oglas sa smerom

Spojim veštine svih predmeta smera u jednu listu. Za svaki oglas gledam koje njegove veštine se nalaze u toj listi.

*Primer:*

| Veština iz oglasa | Da li je smer pokriva? | Kojim predmetom? |
|---|---|---|
| Java | da | Objektno programiranje (primer) |
| Spring Boot | ne | — |
| SQL | da | Baze podataka |
| PostgreSQL | da | Baze podataka |
| REST API | da | Veb programiranje (primer) |
| Git | ne | — |
| Docker | ne | — |
| komunikacija | ne | — |

**Pokrivenost oglasa = 4/8 = 50%.** Nedostaju Spring Boot, Git, Docker i komunikacija.

### Korak 5 — Rezultat za studenta i za fakultet

- **Student** bira smer i vidi oglase poređane po pokrivenosti, a za svaki oglas i šta mu nedostaje. To je aplikacija koju je profesor opisao.
- **Fakultet** vidi veštine koje se često traže u oglasima, a nijedan predmet ih ne pokriva (npr. „Docker se traži u 40% oglasa, nijedan predmet ga ne pokriva“). To je jaz.
- **Fakultet** vidi i obrnuto: veštine koje predmeti uče, a skoro nijedan oglas ih ne traži (npr. „alat X se uči na dva predmeta, a traži se u 1% oglasa“). To su kandidati za **zastareo sadržaj**. Ovo ne znači automatski da je sadržaj loš (teorija i osnove se retko pišu u oglasima), već da ga treba pogledati.

Oba prikaza dolaze iz **iste tabele** (oglasi × veštine × predmeti), samo je drugačije čitamo: student čita po redovima (oglas po oglas), fakultet po kolonama (veština po veština).

### Korak 6 — Proveravam koliko sistem greši

1. Ručno pregledam 50 oglasa i za svaku veštinu zapišem da li je smer pokriva (ja odlučujem, gledajući opise predmeta).
2. Sistem uradi isto automatski.
3. Poredim:
   - **Preciznost:** kada sistem kaže „pokriveno“, koliko često je u pravu?
   - **Odziv:** od svih veština koje su stvarno pokrivene, koliko ih je sistem našao?

Ako stignem, neko drugi nezavisno označi isti skup, pa proverim koliko se slažemo.

### Korak 7 — Glavni eksperiment: da li više izvora pomaže?

Isti postupak (koraci 2–6) pokrećem više puta, svaki put sa više teksta o predmetu:

| Verzija | Šta sistem zna o predmetu |
|---|---|
| V0 | samo naziv i kratak opis |
| V1 | + ishodi učenja |
| V2 | + detaljan sadržaj |
| V3 | + nastavni materijali (ako su dostupni) |

Za svaku verziju zapišem preciznost i odziv iz koraka 6. **Pitanje: da li rezultat raste kada dodam izvor, i koji izvor najviše pomaže?**

Isto mogu da uradim i na strani oglasa (oglas sam / oglas + opis firme).

### Korak 8 — Drugi eksperiment: sa ESCO-om ili bez njega

- **Put A (preko ESCO-a):** kako je opisano gore.
- **Put B (bez ESCO-a):** veštinu iz oglasa direktno poredim embeddingom sa veštinama iz predmeta. Ako je sličnost iznad praga, računam da je pokrivena. **Prag ne biram unapred:** probam nekoliko vrednosti (npr. 0,5; 0,6; 0,7; 0,8) na ručno označenom skupu i uzmem onu koja daje najbolji rezultat.

Na istom ručnom skupu poredim koji put češće pogađa. Put B je jednostavniji, ali može da pogreši kod sličnih veština (npr. „MySQL“ i „PostgreSQL“). Put A je strožiji, ali ESCO možda ne sadrži sve nove alate.

### Izbor embedding modela

Pošto su predmeti na srpskom, a mnogi oglasi na engleskom, treba mi višejezički model. Kandidati: `BAAI/bge-m3`, `intfloat/multilingual-e5-large`, `paraphrase-multilingual-mpnet-base-v2`. Biram tako što ručno napravim 30–50 parova (npr. „baze podataka“ – „databases“, „rad u timu“ – „teamwork“) i proverim koji model ih najbolje prepoznaje kao slične. Ćirilicu pre obrade prebacujem u latinicu.

---

## 3. Arhitektura sistema

Ovaj odeljak pokazuje **od kojih delova se sistem sastoji i kako podaci prolaze kroz njih**. Delovi se poklapaju sa koracima metodologije iz odeljka 2.

### 3.1 Dva dela projekta

Kao što je dogovoreno na konsultacijama, projekat ima dva odvojena dela:

| Softverski deo (engine) | Istraživački deo |
|---|---|
| Program koji od tekstova predmeta i oglasa pravi rezultat: pokrivenost i jaz. | Eksperimenti koji proveravaju koliko je taj rezultat tačan i šta ga popravlja. |
| Koraci 1–5 iz odeljka 2 | Koraci 6–8 iz odeljka 2 |
| Rezultat: aplikacija za studenta i pregled za fakultet | Rezultat: tabele preciznosti i odziva, odgovor na istraživačko pitanje |

Istraživački deo **ne pravi novi sistem**, nego isti engine pokreće više puta sa različitim podešavanjima (V0–V3, Put A / Put B, različiti embedding modeli) i meri rezultat.

---

### 3.2 Dijagram

```mermaid
flowchart TB
    subgraph IZVORI["Izvori podataka"]
        K["Knjiga predmeta FTN<br/>(PDF)"]
        O["Portal sa oglasima"]
        E["ESCO<br/>(CSV, engleski + hrvatski)"]
    end

    subgraph ENGINE["Softverski deo (engine)"]
        S1["1. Prikupljanje<br/>krouler + čitanje PDF-a"]
        S2["2. Izvlačenje veština<br/>LLM + citat iz teksta"]
        S3["3. Prevođenje na ESCO<br/>embedding → 5 kandidata → LLM bira"]
        S4["4. Poređenje<br/>tabela oglasi × veštine × predmeti"]
    end

    subgraph IZLAZ["5. Rezultat"]
        A1["Za studenta:<br/>oglasi po pokrivenosti + šta fali"]
        A2["Za fakultet:<br/>jaz i moguće zastareo sadržaj"]
    end

    subgraph ISTR["Istraživački deo"]
        R1["6. Ručno označenih 50 oglasa"]
        R2["Merenje: preciznost i odziv"]
        R3["7–8. Eksperimenti:<br/>V0–V3, Put A / Put B, modeli"]
    end

    K --> S1
    O --> S1
    S1 --> S2 --> S3 --> S4
    E --> S3
    S4 --> A1
    S4 --> A2
    S4 --> R2
    R1 --> R2
    R3 -. "pokreće engine sa drugim podešavanjima" .-> S2
    R2 --> R3
```

---

### 3.3 Put jednog oglasa kroz sistem

Najlakše se razume ako se prati jedan oglas (primer je izmišljen, isti kao u odeljku 2):

| Deo | Šta ulazi | Šta izlazi |
|---|---|---|
| **1. Prikupljanje** | stranica oglasa „Junior Backend Developer“ | čist tekst oglasa + datum i izvor |
| **2. Izvlačenje veština** | tekst oglasa | `[Java, Spring Boot, SQL, PostgreSQL, REST API, Git, Docker, komunikacija]`, uz citat za svaku |
| **3. Prevođenje na ESCO** | „SQL“, „Git“, ... | ESCO naziv i ID za svaku veštinu (ili „nema u ESCO-u“) |
| **4. Poređenje** | ESCO veštine oglasa + ESCO veštine svih predmeta RA | Java (da), SQL (da) PostgreSQL (da) REST API (da) Spring Boot (n e) Git (ne) Docker (ne) komunikacija (ne) |
| **5. Rezultat** | tabela iz koraka 4 | pokrivenost 50%; nedostaju Spring Boot, Git, Docker i komunikacija |

Predmet prolazi **isti put** (koraci 1–3), samo što je ulaz tekst iz knjige predmeta umesto oglasa.

---

### 3.4 Delovi sistema (moduli)

| Modul | Šta radi | Ulaz | Izlaz |
|---|---|---|---|
| `prikupljanje` | Skida oglase sa portala i vadi tekst predmeta iz PDF-a. Poštuje `robots.txt`, pravi pauzu između zahteva, ne čuva lične podatke. | URL-ovi, PDF | tekst + datum + izvor |
| `ekstrakcija` | Šalje tekst LLM-u i dobija listu veština sa citatima. Model i podešavanja su fiksirani da bi rezultat bio ponovljiv. | tekst | lista veština (JSON) |
| `esco` | Pretvara ESCO veštine u embeddinge (jednom) i za svaku veštinu iz teksta nalazi ESCO naziv. | lista veština | lista ESCO ID-eva |
| `poredjenje` | Pravi tabelu oglasi × veštine × predmeti i računa pokrivenost i jaz. | ESCO veštine oglasa i predmeta | pokrivenost po oglasu, lista jazova |
| `aplikacija` | Student bira smer i vidi oglase; fakultet vidi jaz. | rezultati poređenja | prikaz u pregledaču |
| `evaluacija` | Poredi sistem sa ručno označenim oglasima. | rezultat sistema + ručne oznake | preciznost, odziv |
| `eksperimenti` | Pokreće engine za V0–V3, Put A / Put B i različite modele i zapisuje rezultate. | podešavanja | tabela rezultata |

---

### 3.5 Planirana struktura repozitorijuma

Ovo je plan, ne trenutno stanje. Za sada repozitorijum ima samo `README.md`, `Istrazivacki_dnevnik.md` i `.gitignore`; foldere dodajem kada počnem da pišem kod za taj deo, a strukturu menjam posle dogovora sa profesorom.

```
projekat11/
├── README.md               kratak opis projekta
├── DNEVNIK.md              istraživački dnevnik sa arhitekturom (ovaj dokument)
├── docs/                   pregled literature, beleške, slike
```

---

### 3.6 Tehnologije (plan, može da se promeni)

| Za šta | Plan | Zašto |
|---|---|---|
| Jezik | Python | najviše biblioteka za obradu teksta |
| Čitanje PDF-a | `pdfplumber` | knjiga predmeta je u PDF-u |
| Krouler | `requests` + `BeautifulSoup` | dovoljno za jednostavne stranice sa oglasima |
| Embeddings | `sentence-transformers` | lako se menja model (bge-m3, multilingual-e5, mpnet) |
| LLM | jedan model preko API-ja, odluka posle dogovora o budžetu | izvlačenje veština i izbor ESCO kandidata |
| Čuvanje podataka | CSV / JSON fajlovi | za ~200 oglasa baza nije potrebna |
| Aplikacija | Streamlit | brz prototip bez posebnog frontenda |

---

## 4. Šta još ne znam (proveriti)

- Da li su ishodi učenja i sadržaj dostupni za sve predmete RA, i da li mogu da dobijem nastavne materijale.
- Da li ESCO dovoljno dobro pokriva konkretne alate (Docker, React, Kubernetes...).
- Koji portal za oglase dozvoljava prikupljanje.
- Koji LLM koristim i koliki je budžet.
- Koliko dobro višejezički modeli rade za srpski (proveravam testom iz odeljka „Izbor embedding modela“).

**Rešeno:** ESCO ne postoji na srpskom (postoji na 28 jezika, među njima hrvatski). Izvor: [ESCO languages](https://esco.ec.europa.eu/en/escopedia/ESCO-languages).

---

## 5. Dnevnik

### Unos 1 — pregled literature (do 28.10.2026)

- Pregledano 12 izvora, u celini pročitano 5 (Andonovikj i Boškoski 2024; Senger i sar. 2024; Patterson 2026; Pelucchi i sar. 2026; Turaev i sar. 2026), ostali na nivou apstrakta.
- Najbliži rad: Turaev i sar. (2026). Izvlače veštine iz ishoda učenja pomoću LLM-a, mapiraju ih na ESCO i porede sa 30 oglasa za jedan program.
- Zapažanje: nisam našao rad koji meri koliko svaki dodatni izvor o predmetu poboljšava uparivanje. To je moja hipoteza za doprinos; proveriću je čitanjem punih tekstova.
- Dokument: `Projekat11_final.docx`.

### Unos 2 — konsultacije sa profesorom (28.10.2026)

- Oslanjam se na Turaeva i sar., ali sa više izvora na obe strane.
- Metodologiju opisati konkretno: šta tačno radim, kojim redom, sa kojim podacima.
- Mapiranje kurikuluma na nešto konkretno: preko ESCO-a i preko embeddinga.
- Embedding model mora biti višejezički (srpski + engleski).
- Razdvojiti softverski deo (pipeline, aplikacija) od istraživačkog dela (eksperimenti, evaluacija).
- Pogledati i druge metode i izvore, ne samo Turaeva i sar.
- Domen: FTN Novi Sad. Student bira smer i dobija oglase povezane sa smerom.
- GitHub repozitorijum deljen sa profesorom (`savic071`).

### Unos 3 — prepravka metodologije (08.11.2026)

- Metodologiju sam prepisao kao niz koraka sa primerom (odeljak 2), da bude jasno šta ulazi i šta izlazi iz svakog koraka.
- Izbacio sam stvari koje za sada ne koristim (složen indeks usklađenosti, mere za rangiranje), da se fokusiram na osnovno: pokrivenost oglasa, preciznost i odziv.
- Sledeće: početi od smera Računarstvo i automatika i proveriti dostupnost kurikuluma.
---

## 6. Glavna literatura

- Turaev, S., John, M., Awad, M., Zaki, N., & Shuaib, K. (2026). *An NLP-driven framework for curriculum-labor market alignment.* arXiv:2606.01982 (preprint).
- Pelucchi, M. i sar. (2026). *Bridging skills demand and vocational qualifications* (konferencijska prezentacija, Lightcast).
- Patterson, A. (2026). *UpSkill-Scanner.* Issues in Information Systems, 27(2), 79–94.
- Senger, E. i sar. (2024). *Deep learning-based computational job market analysis.* NLP4HR 2024.
- Andonovikj, V., & Boškoski, P. (2024). *Extracting competencies from job adverts and academic syllabi.* ERK 2024.

Pun spisak: `Projekat11.docx`, odeljak 6.
