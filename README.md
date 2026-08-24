# Dokumentácia: Python Knižnica pre Obsidian Local REST API (v4)

Táto knižnica poskytuje objektovo-orientované rozhranie (wrapper) pre komunikáciu s vaším **Obsidian trezorom (vault)** pomocou komunitného pluginu **Local REST API**. Umožňuje automatizovať správu vašej osobnej databázy znalostí priamo z Pythonu.

Verzia **v4** opravuje dva kritické problémy pri práci s priečinkami, ktoré sa prejavujú v reálnom prostredí aplikácie Obsidian:
1. **Oprava 500 Server Error pri vytváraní priečinkov:** Obsidian blokuje vytváranie a prácu so skrytými systémovými súbormi (súbory začínajúce bodkou, ako napr. `.keep`), čo spôsobovalo chybu `500 Internal Server Error`. Knižnica bola upravená tak, aby na inicializáciu priečinkov používala regulárny pomocný súbor `keep.md`.
2. **Oprava nefunkčného mazania priečinkov (Rekurzívne čítanie):** Predvolený koncový bod `/vault/` v pluginu Local REST API vracia iba súbory a priečinky z **koreňového adresára** (nie je rekurzívny). Z tohto dôvodu metóda `vymaz_priecinok` predtým nevedela zmazať súbory v podadresároch a priečinok ostal v trezore. Verzia **v4** prináša robustnú rekurzívnu metódu `zoznam_suborov_v_priecinku`, ktorá automaticky prehľadáva celú adresárovú štruktúru trezoru.

---

## ⚙️ Závislosti (Requirements)

Na používanie tejto knižnice potrebujete mať v systéme nainštalované nasledujúce balíky:

1. **Python 3.7+**
2. Knižnicu **`requests`** pre HTTP komunikáciu.
3. Knižnicu **`urllib3`** (býva súčasťou `requests`) na správu pripojení a SSL varovaní.

### Inštalácia závislostí:
```bash
pip install requests
```

### Príprava na strane Obsidianu:
1. V Obsidiane otvorte **Nastavenia -> Komunitné pluginy (Community Plugins)**.
2. Vyhľadajte, nainštalujte a povoľte plugin **Local REST API** od autora *coddingtonbear*.
3. V nastaveniach pluginu skopírujte vygenerovaný **API Key** a uistite sa, že beží HTTPS server (štandardný port je `27124`).

---\n
## 🚀 Inicializácia a Rýchly štart

Knižnicu importujete a inicializujete vytvorením inštancie triedy `ObsidianClient`. Môžete použiť predvolené hodnoty (ktoré sú nakonfigurované na váš lokálny trezor), alebo zadať vlastné parametre.

```python
from obsidian_client import ObsidianClient

# Inicializácia s prednastaveným API kľúčom a portom 27124
client = ObsidianClient()

# Inicializácia s vlastnými parametrami (napríklad pre iný počítač či port)
client_vlastny = ObsidianClient(
    api_key="VAS_API_KLUC_Z_NASTAVENI",
    base_url="https://127.0.0.1:27124"
)
```

---

## 🛠️ Prehľad Metód (API Reference)

### 1. Práca s Poznámkami (CRUD)

*   `vytvor_alebo_uprav_poznamku(cesta_k_suboru: str, obsah: str) -> requests.Response`
    *   **Popis:** Vytvorí nový `.md` súbor (alebo akýkoľvek iný súbor) v trezore s určeným obsahom. Ak súbor na danej ceste už existuje, prepíše sa. Chýbajúce priečinky v ceste sa automaticky vytvoria.
*   `pridaj_na_konec_poznamky(cesta_k_suboru: str, pridany_text: str) -> requests.Response`
    *   **Popis:** Otvorí existujúcu poznámku a pridá text na jej koniec.
*   `citaj_poznamku(cesta_k_suboru: str) -> str`
    *   **Popis:** Stiahne obsah zadanej poznámky z trezoru a vráti ho ako textový reťazec.
*   `vymaz_poznamku(cesta_k_suboru: str) -> requests.Response`
    *   **Popis:** Natrvalo vymaže špecifikovaný súbor alebo poznámku z vášho trezoru.
*   `zoznam_vsetkych_suborov() -> List[str]`
    *   **Popis:** Získa zoznam ciest ku **všetkým** súborom nachádzajúcim sa vo vašom trezore rekurzívnym prehľadávaním.

### 2. Správa Priečinkov (Folders) - *ROBUSTNÁ IMPLEMENTÁCIA*

Štandardný plugin Local REST API nepodporuje priamu správu priečinkov cez `/folders/` (vracia chybu `404 Not Found`). Naša knižnica preto používa natívne obchádzky:

*   `vytvor_priecinok(cesta_k_priecinku: str) -> None`
    *   **Popis:** Vytvorí priečinok na zadanej relatívnej ceste v trezore. Na pozadí zapíše dočasný prázdny súbor `keep.md` (čo prinúti Obsidian automaticky vytvoriť celú adresárovú štruktúru) a následne ho vymaže. Priečinok v trezore ostane.
    *   **Parametre:** `cesta_k_priecinku` (napr. `"Archív/2026"`).
*   `vymaz_priecinok(cesta_k_priecinku: str) -> None`
    *   **Popis:** Vymaže špecifikovaný priečinok v trezore tak, že rekurzívne vyhľadá a odstráni **všetky** súbory, ktoré sa nachádzajú pod touto cestou.
*   `presun_priecinok(stara_cesta: str, nova_cesta: str) -> None`
    *   **Popis:** Premenuje alebo presunie celý priečinok. Metóda rekurzívne presunie všetky vnútorné súbory na novú cestu, čím zabezpečí čistú reorganizáciu bez straty dát.

### 3. Správa Záznamov v Priečinkoch

*   `vytvor_zaznam_v_priecinku(priecinok: str, nazov_suboru: str, obsah: str) -> requests.Response`
    *   **Popis:** Pohodlné uloženie súboru priamo do zadaného priečinka.
*   `vymaz_zaznam_v_priecinku(priecinok: str, nazov_suboru: str) -> requests.Response`
    *   **Popis:** Vymaže konkrétny súbor v zadanom priečinku.
*   `presun_subor(stara_cesta: str, nova_cesta: str) -> None`
    *   **Popis:** Presunie alebo premenuje súbor (poznámku alebo binárny súbor) v rámci trezoru. Pracuje na úrovni bajtov, takže bezpečne zachováva aj binárne súbory (obrázky, PDF) a ich pôvodný `Content-Type`.

### 4. Vyhľadávanie v Trezore (Search)

*   `vyhladaj_jednoducho(dopyt: str, dlzka_kontextu: int = 100) -> List[dict]`
    *   **Popis:** Fuzzy fulltextové vyhľadávanie v celom trezore.
*   `vyhladaj_dataview(dql_dopyt: str) -> List[dict]`
    *   **Popis:** Spustí dotaz v jazyku Dataview Query Language (DQL). Vyžaduje plugin *Dataview*.
*   `vyhladaj_jsonlogic(json_logic_dopyt: dict) -> List[dict]`
    *   **Popis:** Filtrovanie poznámok na základe metadát a tagov pomocou logických výrazov [JsonLogic](https://jsonlogic.com/).

---

## 💡 Príklady Použitia (Examples)

Nasledujúci ucelený príklad predvádza prácu so správou priečinkov a súborov v nich:

```python
from obsidian_client import ObsidianClient

# Inicializácia klienta
client = ObsidianClient()

# 1. VYTVORENIE PRIEČINKA
print("Vytváram priečinok...")
client.vytvor_priecinok("Projekty/Automatizacia")

# 2. VYTVORENIE ZÁZNAMU V PRIEČINKU
print("Vytváram záznam v novom priečinku...")
obsah_zaznamu = """---
tags: [automatizacia, test]
stav: vytvorene
---
# Moja nová úloha v priečinku
Tento záznam bol vytvorený automatizovane v priečinku.
"""
client.vytvor_zaznam_v_priecinku("Projekty/Automatizacia", "NovaUloha.md", obsah_zaznamu)

# 3. PRESUNUTIE / PREMENOVANIE SÚBORU V PRIEČINKU
print("Presúvam súbor na novú cestu...")
client.presun_subor(
    stara_cesta="Projekty/Automatizacia/NovaUloha.md",
    nova_cesta="Projekty/Automatizacia/HotovaUloha.md"
)

# 4. PREMENOVANIE / PRESUN CELÉHO PRIEČINKA
# Presunie priečinok "Automatizacia" so všetkými jeho súbormi do priečinka "Archiv_2026"
print("Premenovávam celý priečinok...")
client.presun_priecinok(
    stara_cesta="Projekty/Automatizacia",
    nova_cesta="Projekty/Archiv_2026"
)

# 5. KONTROLA ZOZNAMU SÚBOROV (Teraz naozaj rekurzívne!)
subory = client.zoznam_vsetkych_suborov()
print("Súbory v archíve:")
for s in subory:
    if "Archiv_2026" in s:
        print(f"  - {s}")

# 6. MAZANIE PRIEČINKA (Upratovanie)
# Vymaže priečinok Archiv_2026 vrátane všetkých súborov v ňom
print("Vymazávam celý priečinok (upratovanie)...")
client.vymaz_priecinok("Projekty/Archiv_2026")
print("Hotovo!")
```

---

## ⚠️ Riešenie problémov (Troubleshooting)

1. **Prečo mi `vytvor_priecinok` predtým vyhadzoval chybu 500 (Internal Server Error)?**
   * Obsidian Local REST API na pozadí neumožňuje vytvárať súbory začínajúce bodkou (ako `.keep`), pretože sú vnímané ako skryté/systémové. Vo verzii **v4** bola obchádzka zmenená na normálny súbor `keep.md`, ktorý Obsidian bez problémov povolí zapísať a vymazať.
2. **Prečo mi predtým mazanie prebehlo "úspešne", ale priečinky v trezore ostali?**
   * Endpoint `/vault/` vracia iba súbory v koreňovom priečinku trezoru. Ak ste teda premenovali priečinok na `Projekty/PresunutyPriečinok` a volali `zoznam_vsetkych_suborov`, knižnica tento priečinok nenašla (lebo nebol v roote) a nenašla v ňom ani žiadne súbory na zmazanie. Preto vyhlásila mazanie za úspešné (zmazala 0 súborov), no vaše reálne súbory ostali v trezore. S novou rekurzívnou metódou vo verzii **v4** sa tento problém nadobro vyriešil.
