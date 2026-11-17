Procena relevantnosti kurikuluma analizom oglasa za posao

Projekat 11 — Curriculum Relevance Assessment by Analyzing Job Ads Predmet: Savremene obrazovne tehnologije i standardi (SOTIS) Autor: Goran Malešev (E2 162) · Mentor: Goran Savić

O čemu je projekat
Iz kurikuluma jednog smera na FTN-u (Računarstvo i automatika) i iz oglasa za posao izvlačim listu veština.
Obe liste prevodim na iste standardne nazive (ESCO), da bih mogao da ih uporedim.
Za svaki oglas računam koliko traženih veština smer pokriva. Student dobija listu poslova koji odgovaraju njegovom smeru, a fakultet vidi šta mu nedostaje (jaz).

Istraživačko pitanje: da li uparivanje postaje tačnije kada predmetu dodam još izvora (ishode učenja, sadržaj, nastavne materijale), i koji izvor najviše pomaže. Tačnost merim na ručno proverenim primerima.

Projekat se oslanja na Turaev i sar. (2026), arXiv:2606.01982. Oni koriste samo ishode učenja i 30 oglasa; ja poredim više izvora, koristim oko 200 oglasa i višejezički (srpski + engleski) embedding model.

Sadržaj repozitorijuma
.
├── README.md                 ovaj fajl
├── ISTRAZIVACKI_DNEVNIK.md   pojmovi, metodologija, arhitektura, dnevnik rada, sledeći koraci
├── Projekat11.docx           pregled literature (prva faza)
└── .gitignore                data/ ne ide na repozitorijum

Foldere za kod dodajem kada počnem implementaciju. Planirana struktura je u dnevniku, odeljak 3.5.

Dva dela projekta
Softverski deo (engine): program koji od tekstova predmeta i oglasa pravi rezultat: pokrivenost i jaz (koraci 1–5 u dnevniku).
Istraživački deo: eksperimenti koji proveravaju koliko je rezultat tačan i šta ga popravlja (koraci 6–8 u dnevniku).
Podaci

Sirovi oglasi i dokumenti kurikuluma se ne objavljuju u repozitorijumu (uslovi korišćenja izvora). U repozitorijum ulaze samo kod, agregatni rezultati i kratki primeri.

Status
Oktobar 2026: pregled literature i određivanje doprinosa (Projekat11.docx).
Novembar 2026: definisani metodologija i arhitektura (ISTRAZIVACKI_DNEVNIK.md).
Sledeće: prikupljanje kurikuluma smera RA i prvih oglasa, izbor embedding modela.
