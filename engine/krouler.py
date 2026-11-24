"""Korak 1 — pristojno preuzimanje stranica (osnova za krouler).

Ovo NIJE gotov krouler za neki portal: svaki portal ima drugačiju strukturu stranice,
pa funkciju `izvuci_oglas` treba napisati za izabrani portal.

Pravila (iz dnevnika):
- pre preuzimanja proveri robots.txt i uslove korišćenja sajta;
- pauza između zahteva;
- ne čuvaj lične podatke.

LinkedIn u uslovima korišćenja zabranjuje automatsko prikupljanje,
pa se za njega ovaj modul ne koristi bez dogovora sa profesorom.
"""

import time
import urllib.robotparser
from urllib.parse import urlparse

PAUZA_SEKUNDE = 2
KORISNIK = "curriculum-job-alignment (studentski istrazivacki projekat)"


def dozvoljeno(url: str) -> bool:
    """Proverava robots.txt sajta: da li je dozvoljeno preuzeti ovu stranicu."""
    osnova = "{0.scheme}://{0.netloc}".format(urlparse(url))
    rp = urllib.robotparser.RobotFileParser(osnova + "/robots.txt")
    rp.read()
    return rp.can_fetch(KORISNIK, url)


def preuzmi(url: str) -> str | None:
    """Preuzima HTML stranice ako robots.txt dozvoljava, uz pauzu."""
    import requests

    if not dozvoljeno(url):
        print(f"robots.txt ne dozvoljava: {url}")
        return None
    time.sleep(PAUZA_SEKUNDE)
    odgovor = requests.get(url, headers={"User-Agent": KORISNIK}, timeout=30)
    odgovor.raise_for_status()
    return odgovor.text


def izvuci_oglas(html: str) -> dict:
    """Iz HTML-a oglasa vadi polja: naziv, firma, tekst.

    TODO: napisati za izabrani portal (npr. pomoću BeautifulSoup, prema strukturi stranice).
    """
    raise NotImplementedError("Napisati za izabrani portal.")
