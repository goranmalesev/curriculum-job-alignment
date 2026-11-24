"""Jedan ulaz za LLM, da bi engine radio sa bilo kojim modelom.

Ključ se čita iz promenljive okruženja (OPENAI_API_KEY ili ANTHROPIC_API_KEY),
nikad se ne piše u kod ni u repozitorijum.
Temperatura 0 znači da isti ulaz daje isti izlaz (ponovljivost).
"""

import json
import re


class LLM:
    def __init__(self, provider: str, model: str, temperatura: float = 0):
        self.provider = provider
        self.model = model
        self.temperatura = temperatura

    @property
    def ukljucen(self) -> bool:
        return self.provider not in ("", "none", None)

    def pitaj(self, prompt: str) -> str:
        """Šalje prompt modelu i vraća tekst odgovora."""
        if self.provider == "openai":
            from openai import OpenAI

            odgovor = OpenAI().chat.completions.create(
                model=self.model,
                temperature=self.temperatura,
                messages=[{"role": "user", "content": prompt}],
            )
            return odgovor.choices[0].message.content
        if self.provider == "anthropic":
            import anthropic

            odgovor = anthropic.Anthropic().messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=self.temperatura,
                messages=[{"role": "user", "content": prompt}],
            )
            return odgovor.content[0].text
        raise ValueError(f"LLM nije podešen (provider = {self.provider}).")

    def pitaj_json(self, prompt: str):
        """Kao `pitaj`, ali očekuje JSON u odgovoru i pretvara ga u Python objekat."""
        tekst = self.pitaj(prompt)
        poklapanje = re.search(r"(\[.*\]|\{.*\})", tekst, re.S)
        if not poklapanje:
            raise ValueError(f"LLM nije vratio JSON: {tekst[:200]}")
        return json.loads(poklapanje.group(1))
