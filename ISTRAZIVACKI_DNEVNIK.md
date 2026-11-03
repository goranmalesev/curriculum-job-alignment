# Istraživački dnevnik

**Projekat 11 — Procena relevantnosti kurikuluma analizom oglasa za posao**
(*Curriculum Relevance Assessment by Analyzing Job Ads*)

Autor: Goran Malešev (E2 162) · Mentor: Goran Savić

---

## 1. Osnovni pojmovi

| Pojam | Značenje u ovom projektu |
|---|---|
| **Kurikulum** | Nastavni plan i program: predmeti, ciljevi, sadržaj, ishodi učenja. Izvor informacija o tome šta student uči. |
| **Oglas za posao** | Tekstualni opis radnog mesta sa zadacima i veštinama koje poslodavac traži. Izvor informacija o potražnji. |
| **Veština / kompetencija** | Znanje ili sposobnost potrebna za obavljanje zadatka (npr. SQL, REST API, timski rad). |
| **Ekstrakcija veština** | Izdvajanje veština iz teksta (oglasa ili opisa predmeta), ručno ili pomoću NLP/LLM-a. |
| **ESCO** | Evropska taksonomija veština i zanimanja sa standardnim nazivima i ID-evima. Služi kao zajednički „jezik“ za obe strane. |
| **Taksonomija / baza veština** | Strukturisan skup veština sa standardnim nazivima (ESCO, O*NET). |
| **Embedding** | Tekst pretvoren u vektor brojeva tako da su značenjski slični tekstovi blizu. |
| **Kosinusna sličnost** | Mera sličnosti dva vektora (−1 do 1). Koristi se za poređenje veština i opisa. |
| **Višejezički model** | Model koji tekstove na različitim jezicima (ovde srpski i engleski) smešta u isti vektorski prostor. |
| **LLM** | Veliki jezički model; ovde za izdvajanje veština u strukturisanom obliku i za proveru uparivanja. |
| **Skills gap (jaz)** | Razlika između veština koje se traže u oglasima i veština koje kurikulum pokriva. |
| **Obogaćivanje** | Dodavanje izvora (ishodi, silabus, materijali, info o firmi, ESCO opisi) radi pouzdanijeg uparivanja. |
| **Ablacija** | Eksperiment u kome se izvori dodaju/uklanjaju jedan po jedan da bi se izmerio doprinos svakog. |
| **Referentni skup (gold standard)** | Ručno označeni parovi na kojima se meri tačnost sistema. |
| **Cohenov κ** | Mera slaganja dva označavača korigovana za slučajno slaganje. |
| **Krouler (crawler/scraper)** | Program koji automatski prikuplja tekstove sa veb stranica. |

---

## 2. Dnevnik

### Unos 1 — pregled literature (do 28.10.2026)

- Pregledano 12 izvora; **u celini pročitano 5** (Andonovikj i Boškoski 2024; Senger i sar. 2024; Patterson 2026; Pelucchi i sar. 2026; Turaev i sar. 2026), ostali na nivou apstrakta.
- Najbliži rad: **Turaev i sar. (2026), arXiv:2606.01982**. Koriste dva LLM-a za ekstrakciju, ESCO za standardizaciju i SBERT za poređenje; ponuda su gotovo samo ishodi učenja (CLO); pilot sa 30 oglasa; jedan program.
- Zapažanje: u pregledanim radovima nisam našao sistematsko poređenje koliko svaki izvor obogaćivanja popravlja uparivanje. (Hipoteza, treba je proveriti dalje.)
- Dokument sa pregledom: `Projekat11_final.docx`.

### Unos 2 — konsultacije sa profesorom (28.10.2026)

Beleške sa konsultacija (kako sam ih razumeo):

1. **Oslanjam se na Turaeva i sar.**, ali sa više informacija: više izvora i više strana (kurikulum i oglasi, svaki obogaćen dodatnim izvorima).
2. **Treba definisati metodologiju:** kako praktično tražim odnos između kompetencija i kurikuluma, kojim vrstama izvora i kojim postupkom prikupljanja (krouleri).
3. **Izbor embedding modela**, i to **višejezičkog (srpski + engleski)**.
4. **Dva koloseka:** (a) softverski engine (ponovljiv pipeline) i (b) naučno istraživanje (pitanja, eksperimenti, evaluacija). Treba ih razdvojiti u razmišljanju i u repozitorijumu.
5. **Pogledati i mimo rada** Turaeva i sar.: druge metode i izvore.
6. **GitHub repozitorijum** deljen sa profesorom (nalog: `savic071`); u njemu istraživački dnevnik, osnovni pojmovi i sledeći koraci.

Otvorena pitanja za potvrdu: domen/program, dostupnost silabusa, obim oglasa, jezik teksta rada, format isporuke.

---

## 3. Metodologija (prvi predlog)

### 3.1 Kako praktično tražim odnos kompetencija ↔ kurikulum

1. **Podela na jedinice:** kurikulum se deli na jedinice analize (predmet, ishod učenja, tema); oglas na zahteve.
2. **Ekstrakcija:** LLM iz svake jedinice izdvaja kompetencije u JSON šemi (po uzoru na Turaev i sar.: oznaka, domen, znanje, veština, nivo, kontekst, dokaz).
3. **Standardizacija:** kompetencije se mapiraju na ESCO (embeddings → top-K kandidata → LLM potvrđuje/odbacuje, kao kod Pelucchi i sar.).
4. **Matrica sličnosti:** za svaki par (kompetencija iz oglasa, kompetencija iz kurikuluma) računa se kosinusna sličnost.
5. **Mere usklađenosti:**
   - udeo veštine u oglasima i udeo u kurikulumu → **jaz = udeo u oglasima − udeo u kurikulumu**;
   - **pokrivenost** (koliko traženih veština se uči) i **dubina** (koliko je najbliža veština koja se uči slična traženoj), po uzoru na indeks VAI (Pelucchi i sar.).
6. **Vizuelizacija:** heatmap predmeti × kompetencije, rang-lista najvećih jazova, graf kompetencija.

### 3.2 Više izvora (po čemu se razlikujemo od Turaeva i sar.)

| Nivo | Izvor | Strana |
|---|---|---|
| C0 | naziv + kratak opis predmeta / tekst oglasa | obe (baseline) |
| C1 | + ishodi učenja (CLO) | kurikulum |
| C2 | + detaljan sadržaj / silabus | kurikulum |
| C3 | + nastavni materijali | kurikulum |
| C4 | + informacije o firmi i industriji | oglasi |
| C5 | + ESCO opisi i srodne veštine | obe |

Ablacija: isti pipeline se pokreće za različite kombinacije nivoa, a kvalitet se poredi sa referentnim skupom.

### 3.3 Prikupljanje podataka (krouleri)

- **Oglasi:** domaći i međunarodni portali ili gotovi skupovi podataka. Pre prikupljanja proveriti uslove korišćenja i `robots.txt`; prikupljati samo javne podatke, bez ličnih podataka, ograničiti brzinu upita (npr. 2 s), čuvati datum prikupljanja i objavljivati samo agregatne rezultate (praksa iz Patterson 2026).
- **Kurikulum:** knjiga predmeta / studijski program sa sajta fakulteta (PDF → tekst), po predmetu: naziv, cilj, ishodi, sadržaj, literatura.
- **Informacije o firmama:** javno dostupni opisi firmi (sajt firme, javni registri). Proveriti pravila korišćenja.
- **ESCO:** preuzeti skupove podataka sa zvaničnog portala; proveriti da li postoji srpska verzija.
- **Čuvanje:** sirovi tekst + obrađeni JSON, sa izvorom i datumom. **Sirove podatke ne dodavati u javni repozitorijum.**

### 3.4 Embedding model (višejezički, srpski + engleski)

Kandidati za poređenje:

| Model | Napomena |
|---|---|
| `BAAI/bge-m3` | 100+ jezika, vektori od 1024 dimenzije, kontekst do 8192 tokena |
| `intfloat/multilingual-e5-large` | oko 100 jezika, 1024 dimenzije |
| `paraphrase-multilingual-mpnet-base-v2` | koristili su ga Pelucchi i sar. (2026) |
| `LaBSE` (kontrola) | 109 jezika, namenjen pronalaženju prevoda; u jednom benchmarku slab za pretragu |

**Ne pretpostavljam da je kvalitet za srpski isti kao za engleski.** Plan: mali test (npr. 30–50 parova srpska–engleska veština ili srpski opis–ESCO veština, ručno označenih) i izbor modela po rezultatu. Normalizovati pismo (ćirilica → latinica) pre obrade.

### 3.5 Evaluacija

- Referentni skup od 100–200 parova (obim dogovoriti), dva označavača, Cohenov κ.
- Preciznost, odziv, F1 za uparivanje; MRR i RP@k za mapiranje na ESCO.
- Poređenje strategija: samo embeddings / samo LLM / dvostepeno.
- Stabilnost rezultata: koliko se rang-lista jazova menja kad se promeni nivo obogaćivanja ili model.

### 3.6 Dva koloseka

| Softverski engine | Naučno istraživanje |
|---|---|
| ponovljiv pipeline (krouleri → ekstrakcija → mapiranje → poređenje) | istraživačka pitanja i hipoteze |
| konfigurabilni izvori i modeli | eksperimenti (ablacija, poređenje modela) |
| dashboard / vizuelizacija | evaluacija i tumačenje rezultata |

Istraživačka pitanja (nacrt): **RQ1** koji izvori obogaćivanja najviše popravljaju uparivanje; **RQ2** da li se doprinos sabira; **RQ3** embeddings vs LLM vs dvostepeno; **RQ4** najveći jazovi u izabranom programu.

---

## 4. Sledeći koraci

Format: **šta radim — kako — rezultat**.

| # | Šta radim | Kako | Rezultat |
|---|---|---|---|
| 1 | Pravim repozitorijum i dnevnik | GitHub, dodajem `savic071` kao saradnika | repo sa README i ovim dnevnikom |
| 2 | Potvrđujem domen i podatke | pitanja profesoru; provera dostupnosti silabusa | odluka: program, obim, jezik |
| 3 | Biram ESCO podatke | preuzimam ESCO, proveravam jezike | lokalna kopija ESCO |
| 4 | Pilot prikupljanje | 10 predmeta + ~50 oglasa, jednostavan krouler | mali skup podataka u `data/` (van repozitorijuma) |
| 5 | Biram embedding model | test na 30–50 označenih parova, 3–4 modela | izabran model + tabela rezultata |
| 6 | Ekstrakcija kompetencija | LLM + JSON šema, fiksiran model i parametri | JSON kompetencija za pilot |
| 7 | Mapiranje i poređenje | embeddings top-K + LLM provera, matrica sličnosti | prva gap analiza na pilotu |
| 8 | Referentni skup | ručno označavanje, dva označavača | gold skup + κ |
| 9 | Ablacija izvora | pokretanje pipeline-a za C0–C5 | tabela: kvalitet po nivou obogaćivanja |
| 10 | Aplikacija i vizuelizacija | dashboard (heatmap, rang-lista jazova) | prototip |
| 11 | Pisanje rada (~10 strana) | motivacija, srodni radovi, rešenje, rezultati | tekst |

Nedeljni zapisi se dodaju ispod kao novi unosi (**Unos 3, Unos 4, ...**).

---

## 5. Literatura (glavna)

- Turaev, S., John, M., Awad, M., Zaki, N., & Shuaib, K. (2026). *An NLP-driven framework for curriculum-labor market alignment.* arXiv:2606.01982 (preprint).
- Pelucchi, M. i sar. (2026). *Bridging skills demand and vocational qualifications* (konferencijska prezentacija, Lightcast).
- Patterson, A. (2026). *UpSkill-Scanner.* Issues in Information Systems, 27(2), 79–94.
- Senger, E. i sar. (2024). *Deep learning-based computational job market analysis.* NLP4HR 2024.
- Andonovikj, V., & Boškoski, P. (2024). *Extracting competencies from job adverts and academic syllabi.* ERK 2024.

Pun spisak: `Projekat11_final.docx`, odeljak 6.
