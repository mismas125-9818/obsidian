# ObsidianClient - Dokumentácia knižnice

`ObsidianClient` je robustná Python knižnica určená na prácu s **Obsidian Local REST API**. Umožňuje kompletnú správu poznámok, priečinkov, vyhľadávanie pomocou Dataview a JsonLogic, ako aj automatizovanú prácu s tagmi a odkazmi (backlinkami).

---

## Obsah
1. [Inštalácia a požiadavky](#1-inštalácia-a-požiadavky)
2. [Inicializácia klienta](#2-inicializácia-klienta)
3. [Základná práca s poznámkami (CRUD)](#3-základná-práca-s-poznámkami-crud)
4. [Správa priečinkov (Folders)](#4-správa-priečinkov-folders)
5. [Správa záznamov v priečinkoch](#5-správa-záznamov-v-priečinkoch)
6. [Pokročilé vyhľadávanie (Search)](#6-pokročilé-vyhľadávanie-search)
7. [Práca s tagmi a odkazmi](#7-práca-s-tagmi-a-odkazmi)
8. [Kompletný príklad použitia](#8-kompletný-príklad-použitia)
9. [Riešenie známych špecifík API](#9-riešenie-známych-špecifík-api)

---

## 1. Inštalácia a požiadavky

Knižnica vyžaduje Python 3.7+ a nasledujúce závislosti:

```bash
pip install requests urllib3
```

V aplikácii Obsidian je potrebné mať nainštalovaný a aktivovaný komunizný plugin **Local REST API**. V nastaveniach pluginu získate váš API token.

---

## 2. Inicializácia klienta

Trida `ObsidianClient` prijíma API kľúč a URL adresu lokálneho servera Obsidianu.

```python
from obsidian_client import ObsidianClient

# Inicializácia s vlastným API kľúčom
client = ObsidianClient(
    api_key="VÁS_API_TOKEN_Z_OBSIDIANU",
    base_url="https://127.0.0.1:27124"  # Štandardný port Local REST API
)
```

---

## 3. Základná práca s poznámkami (CRUD)

### `vytvor_alebo_uprav_poznamku(cesta_k_suboru, obsah)`
Vytvorí novú poznámku alebo prepíše existujúcu poznámku v trezore (vault). Nadradené priečinky sa vytvoria automaticky.

- **`cesta_k_suboru`** (*str*): Relatívna cesta k poznámke (napr. `'Projekty/PythonTest.md'`).
- **`obsah`** (*str*): Textový alebo Markdown obsah.
- **Návratová hodnota**: `requests.Response`

```python
client.vytvor_alebo_uprav_poznamku("Poznamky/Napad.md", "# Nový nápad\nTento text bol vytvorený cez API.")
```

### `citaj_poznamku(cesta_k_suboru)`
Prečíta a vráti obsah existujúcej poznámky v trezore ako UTF-8 reťazec.

- **`cesta_k_suboru`** (*str*): Cesta k súboru.
- **Návratová hodnota**: `str`

```python
text = client.citaj_poznamku("Poznamky/Napad.md")
print(text)
```

### `pridaj_na_konec_poznamky(cesta_k_suboru, pridany_text)`
Pridá text na koniec existujúcej poznámky (append).

- **`cesta_k_suboru`** (*str*): Cesta k súboru.
- **`pridany_text`** (*str*): Text na pridanie.
- **Návratová hodnota**: `requests.Response`

```python
client.pridaj_na_konec_poznamky("Poznamky/Napad.md", "\n\n- [ ] Pridať ďalší krok")
```

### `vymaz_poznamku(cesta_k_suboru)`
Vymaže konkrétnu poznámku alebo súbor z trezoru.

```python
client.vymaz_poznamku("Poznamky/Napad.md")
```

### `zoznam_suborov_v_priecinku(priecinok="", rekurzivne=True)`
Vráti zoznam relatívnych ciest k súborom v zadanom priečinku.

```python
subory = client.zoznam_suborov_v_priecinku("Projekty", rekurzivne=True)
print(subory)
```

### `zoznam_vsetkych_suborov()`
Rekurzívne prejde celý trezor a vráti zoznam všetkých súborov.

```python
vsetky = client.zoznam_vsetkych_suborov()
```

---

## 4. Správa priečinkov (Folders)

Local REST API nemá priamy koncový bod na vytváranie priečinkov. Knižnica toto správanie elegantne obchádza.

### `vytvor_priecinok(cesta_k_priecinku)`
Vytvorí nový priečinok v trezore pomocou dočasného súboru `keep.md`, ktorý po vytvorení adresára automaticky vymaže.

```python
client.vytvor_priecinok("Archív/2026/Projekt_A")
```

### `vymaz_priecinok(cesta_k_priecinku)`
Rekurzívne najprv odstráni všetky súbory vo vnútri priečinka a následne vymaže samotný priečinok z disku.

```python
client.vymaz_priecinok("Archív/2026/Projekt_A")
```

### `presun_priecinok(stara_cesta, nova_cesta)`
Presunie alebo premenuje celý priečinok vrátane všetkých jeho súborov a podadresárov. Starý prázdny priečinok vyčistí.

```python
client.presun_priecinok("Projekty/StaryNazov", "Projekty/NovyNazov")
```

---

## 5. Správa záznamov v priečinkoch

### `vytvor_zaznam_v_priecinku(priecinok, nazov_suboru, obsah)`
Pohodlná metóda na vytvorenie súboru vo vnútri špecifikovaného priečinka.

```python
client.vytvor_zaznam_v_priecinku("Úlohy", "Dnes.md", "# Dnešné úlohy")
```

### `vymaz_zaznam_v_priecinku(priecinok, nazov_suboru)`
Vymaže konkrétny súbor v danom priečinku.

```python
client.vymaz_zaznam_v_priecinku("Úlohy", "Dnes.md")
```

### `presun_subor(stara_cesta, nova_cesta)`
Presunie alebo premenuje súbor v rámci trezoru so zachovaním pôvodného typov obsahu (`Content-Type`).

```python
client.presun_subor("Denník/2026-01-01.md", "Archív/2026-01-01.md")
```

---

## 6. Pokročilé vyhľadávanie (Search)

### `vyhladaj_jednoducho(dopyt, dlzka_kontextu=100)`
Vykoná fulltextové vyhľadávanie v celom trezore s nastavením dĺžky úryvku kontextu.

```python
vysledky = client.vyhladaj_jednoducho("Python", dlzka_kontextu=50)
for res in vysledky:
    print(res["filename"], res["matches"])
```

### `vyhladaj_dataview(dql_dopyt)`
Vykoná vyhľadávanie pomocou Dataview Query Language (DQL). Vyžaduje nainštalovaný plugin **Dataview**.

```python
dql = "TABLE rating, status FROM #kniha SORT rating DESC"
vysledky = client.vyhladaj_dataview(dql)
```

### `vyhladaj_jsonlogic(json_logic_dopyt)`
Vykoná vyhľadávanie v metadátach pomocou komplexného dopytu JsonLogic (vhodné pre filtrovanie podľa YAML front matter).

```python
query = {
    "==": [{"var": "frontmatter.status"}, "dokončené"]
}
vysledky = client.vyhladaj_jsonlogic(query)
```

---

## 7. Práca s tagmi a odkazmi

### `ziskaj_tagy_z_poznamky(cesta_k_suboru)`
Extrahuje všetky tagy z poznámky – tak z YAML front matter, ako aj inline tagy (`#tag`).

```python
tagy = client.ziskaj_tagy_z_poznamky("Projekty/Python.md")
# Vráti: ['python', 'dev', 'projekty']
```

### `ziskaj_odkazy_z_poznamky(cesta_k_suboru)`
Extrahuje všetky interné odkazy (Wikilinky `[[odkaz]]` aj Markdown odkazové syntaxe).

```python
odkazy = client.ziskaj_odkazy_z_poznamky("Projekty/Python.md")
```

### `najdi_spatne_odkazy(cielova_poznamka)`
Nájde všetky poznámky, ktoré ukazujú (odkazujú) na zadanú cielovú poznámku.

```python
backlinks = client.najdi_spatne_odkazy("Python")
```

### `pridaj_tag_do_poznamky(cesta_k_suboru, tag)`
Pridá tag do poznámky. Ak v poznámke existuje YAML `tags:`, pridá ho tam, inak vloží inline tag na koniec súboru.

```python
client.pridaj_tag_do_poznamky("Projekty/Python.md", "dolezite")
```

### `odstran_tag_z_poznamky(cesta_k_suboru, tag)`
Odstráni konkrétny tag z poznámky (z YAML hlavičky aj inline textu).

```python
client.odstran_tag_z_poznamky("Projekty/Python.md", "dolezite")
```

### `zoznam_vsetkych_tagov_v_trezore()`
Prejde rekurzívne všetky `.md` súbory v trezore a vráti zjednotený unikátny zoznam všetkých tagov.

```python
vsetky_tagy = client.zoznam_vsetkych_tagov_v_trezore()
```

---

## 8. Kompletný príklad použitia

```python
from obsidian_client import ObsidianClient

client = ObsidianClient(api_key="tvoj_api_token")

# 1. Vytvorenie priečinka a poznámky
priecinok = "Projekty/Knižnica"
client.vytvor_priecinok(priecinok)

obsah = """---
tags: [python, api]
---
# Obsidian Client Python
Tento modul slúži na spájanie Pythonu s [[Obsidian]].
"""

client.vytvor_zaznam_v_priecinku(priecinok, "Prehlad.md", obsah)

# 2. Pridanie tagu a kontrola tagov
client.pridaj_tag_do_poznamky(f"{priecinok}/Prehlad.md", "dokumentacia")
tagy = client.ziskaj_tagy_z_poznamky(f"{priecinok}/Prehlad.md")
print("Tagy v poznámke:", tagy)

# 3. Vyhľadávanie
vysledky = client.vyhladaj_jednoducho("Obsidian")
print(f"Nájdené výsledky: {len(vysledky)}")

# 4. Upratanie
client.vymaz_priecinok(priecinok)
```

---

## 9. Riešenie známych špecifík API

1. **Vytváranie adresárov**: Local REST API nepodporuje natívny endpoint pre vytvorenie adresára. Používa sa vytvorenie legitímneho súboru `keep.md` a jeho okamžité zmazanie. (Súbory s bodkou ako `.keep` spúšťajú na strane Obsidianu serverovú chybu HTTP 500).
2. **Vymazávanie a presun priečinkov**: API neumaže priečinok s obsahom. Knižnica najprv rekurzívne vyčistí súbory v priečinku a až potom vymaže samotný adresár.
3. **SSL Varovania**: Nakoľko Obsidian používa lokálny samo-podpísaný SSL certifikát, knihovňa automaticky vypína varovania `InsecureRequestWarning` pomocou `urllib3.disable_warnings()`.
