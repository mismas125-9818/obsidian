# 📚 Dokumentácia: Python Knižnica pre Obsidian Local REST API (v4)

Táto knižnica poskytuje robustné, objektovo-orientované rozhranie (wrapper) pre komunikáciu s vaším **Obsidian trezorom (vault)** pomocou komunitného pluginu **Local REST API**. Umožňuje plnú automatizáciu a správu vašich poznámok, priečinkov a vyhľadávania priamo z Python skriptov.

Verzia **v4** dokumentácie reflektuje najnovšiu stabilnú verziu knižnice (`obsidian_client-v9.py`), ktorá úspešne rieši zložité chovania aplikácie Obsidian, akými sú blokovanie skrytých systémových súborov (chyba 500 pri `.keep`) a potreba fyzického odmazávania prázdnych adresárov z disku pomocou API.

---

## ⚙️ Požiadavky a Inštalácia

### 1. Systémové závislosti
Pre beh knižnice potrebujete mať nainštalovaný:
* **Python 3.7+**
* Knižnicu **`requests`** pre sieťovú komunikáciu.
* Knižnicu **`urllib3`** (štandardne dodávanú s requests) pre správu SSL certifikátov.

Inštalácia balíkov cez terminál:
```bash
pip install requests
```

### 2. Príprava na strane Obsidianu
1. V aplikácii Obsidian otvorte **Settings** (Nastavenia) -> **Community Plugins** (Komunitné pluginy).
2. Kliknite na **Browse** (Prehliadať), vyhľadajte plugin **Local REST API** (od autora *coddingtonbear*) a nainštalujte ho.
3. Po inštalácii plugin **povoľte**.
4. Otvorte nastavenia pluginu Local REST API:
   * Vygenerujte a skopírujte si **API Key** (API kľúč).
   * Overte port pre pripojenie (štandardne **`27124`** pre bezpečné HTTPS, alebo **`27123`** pre nešifrované HTTP).

---

## 🚀 Inicializácia a Pripojenie

Knižnicu importujete do svojho projektu a inicializujete vytvorením inštancie triedy `ObsidianClient`. Knižnica automaticky potláča varovania o neoverených SSL certifikátoch (keďže Obsidian generuje lokálny self-signed certifikát).

```python
from obsidian_client import ObsidianClient

# Inicializácia s vaším vopred nakonfigurovaným API kľúčom a adresou
client = ObsidianClient()

# Inicializácia s vlastnými parametrami (napr. pre iný port alebo stroj)
client_vlastny = ObsidianClient(
    api_key="VAS_API_KLUC_Z_NASTAVENI",
    base_url="https://127.0.0.1:27124"
)
```

---

## 🛠️ Kompletný Prehľad Metód (API Reference)

### 1. Základná práca s poznámkami (CRUD)

#### `vytvor_alebo_uprav_poznamku(cesta_k_suboru: str, obsah: str) -> requests.Response`
Vytvorí novú poznámku (`.md`) alebo kompletne prepíše obsah už existujúcej poznámky na zadanej ceste. Ak adresáre v ceste neexistujú, Obsidian ich na pozadí automaticky vytvorí.
* **`cesta_k_suboru`**: Relatívna cesta od koreňa trezoru (napr. `"Projekty/Ciele2026.md"`).
* **`obsah`**: Textový obsah uležený s kódovaním UTF-8.

#### `pridaj_na_konec_poznamky(cesta_k_suboru: str, pridany_text: str) -> requests.Response`
Otvorí existujúcu poznámku a bezpečne pridá nový text na jej koniec. Ak súbor neexistuje, vytvorí sa prázdny a text sa zapíše.
* **`pridany_text`**: Text na pridanie (napr. `"\n- [ ] Nová úloha z Pythonu"`).

#### `citaj_poznamku(cesta_k_suboru: str) -> str`
Načíta kompletný obsah poznámky z trezoru.
* **Návratová hodnota**: Textový obsah vrátane YAML front matter dekódovaný v UTF-8.

#### `vymaz_poznamku(cesta_k_suboru: str) -> requests.Response`
Natrvalo vymaže špecifikovaný súbor alebo poznámku z vášho trezoru.

#### `zoznam_vsetkych_suborov() -> List[str]`
Načíta zoznam **všetkých** súborov a priečinkov v celom trezore. Knižnica na pozadí vykonáva robustné rekurzívne prehľadávanie, keďže štandardný `/vault/` endpoint vracia len položky z koreňového adresára.

---

### 2. Správa Priečinkov (Folders)

Keďže Obsidian REST API nemá priamy endpoint na čisté zakladanie prázdnych zložiek, knižnica využíva overené systémové obchádzky.

#### `vytvor_priecinok(cesta_k_priecinku: str) -> None`
Vytvorí nový priečinok na zadanej relatívnej ceste. 
* *Technické pozadie:* Na pozadí zapíše dočasný súbor `keep.md`. Obsidian je tým donútený vytvoriť celú zložku na disku, na čo knižnica súbor `keep.md` ihneď odstráni. Priečinok v Obsidiane zostane pripravený a čistý.

#### `vymaz_priecinok(cesta_k_priecinku: str) -> None`
Vymaže priečinok vrátane všetkých súborov a podadresárov v ňom.
* *Technické pozadie:* Metóda najprv rekurzívne vyhľadá a vymaže všetky vnútorné súbory, aby nezostali visieť na disku. Následne odošle požiadavku `DELETE` priamo na cestu prázdneho priečinka, čím ho **fyzicky odstráni z disku** a zmizne aj z bočného panela Obsidianu.

#### `presun_priecinok(stara_cesta: str, nova_cesta: str) -> None`
Kompletne presunie alebo premenuje priečinok vrátane rekurzívneho presunu všetkých vnútorných súborov na novú cestu. Po úspešnom presune súborov starý prázdny priečinok automaticky a čisto vymaže.

---

### 3. Práca so súbormi vo vnútri priečinkov

#### `vytvor_zaznam_v_priecinku(priecinok: str, nazov_suboru: str, obsah: str) -> requests.Response`
Pohodlná skratka na uloženie nového súboru (poznámky) priamo do určeného priečinka.
* **`priecinok`**: Názov alebo cesta priečinka (napr. `"Práca/Projekty"`).
* **`nazov_suboru`**: Názov súboru s príponou (napr. `"report.md"`).

#### `vymaz_zaznam_v_priecinku(priecinok: str, nazov_suboru: str) -> requests.Response`
Vymaže konkrétny súbor v zadanom priečinku.

#### `presun_subor(stara_cesta: str, nova_cesta: str) -> None`
Presunie alebo premenuje súbor v rámci trezoru. Táto metóda pracuje na úrovni raw bajtov, čo znamená, že **bezpečne prenáša nielen poznámky, ale aj binárne prílohy (obrázky, PDF)** a plne zachováva ich pôvodný `Content-Type`.

---

### 4. Vyhľadávanie v Trezore (Search)

Knižnica plne integruje tri pokročilé formáty vyhľadávania podporované Local REST API:

#### `vyhladaj_jednoducho(dopyt: str, dlzka_kontextu: Optional[int] = 100) -> List[dict]`
Fuzzy fulltextové vyhľadávanie v celom trezore. Vracia zoznam zodpovedajúcich súborov, ich skóre relevantnosti a textové úryvky (kontext) okolo nájdenej zhody.

#### `vyhladaj_dataview(dql_dopyt: str) -> List[dict]`
Spustí dopyt v jazyku **Dataview Query Language (DQL)**. Vyžaduje, aby ste mali v Obsidiane nainštalovaný a aktívny plugin *Dataview*.
* **Príklad dopytu**: `"TABLE file.folder, tags FROM #projekty"`

#### `vyhladaj_jsonlogic(json_logic_dopyt: Union[dict, str]) -> List[dict]`
Vyhľadávanie v metadátach a vlastnostiach poznámok pomocou štruktúrovanej logiky [JsonLogic](https://jsonlogic.com/). Vhodné pre filtrovanie podľa tagov, front matter premenných, veľkosti či dátumov.

---

## 💡 Kompletný Ukážkový Scenár (Quickstart)

Tento príklad predvádza kompletný životný cyklus: vytvorenie priečinka, zápis poznámky, jej modifikáciu, presun, fulltextové vyhľadávanie a na záver kompletné čisté vymazanie testovacieho prostredia (vrátane prázdnych zložiek z disku).

```python
import time
from obsidian_client import ObsidianClient

# 1. Inicializácia
client = ObsidianClient()

test_priecinok = "Projekty/PythonTestPriecinok"
test_subor = "Uloha.md"

# 2. Vytvorenie priečinka (čistá keep.md obchádzka)
print("Vytváram prázdny priečinok...")
client.vytvor_priecinok(test_priecinok)

# 3. Zápis súboru do priečinka
print("Zapisujem testovaciu poznámku...")
obsah_poznamky = """---
tags: [it/automatizacia, test/python]
priorita: vysoka
---
# Automatizačný test
Heslo dňa pre overenie vyhľadávania je: **Kryptonit2026**.
"""
client.vytvor_zaznam_v_priecinku(test_priecinok, test_subor, obsah_poznamky)

# 4. Pridanie riadku na koniec
print("Dopĺňam poznámku...")
client.pridaj_na_konec_poznamky(f"{test_priecinok}/{test_subor}", "\n- [ ] Pridané neskôr z Pythonu.")

# 5. Vyhľadávanie v trezore
print("\nTestujem fulltextové vyhľadávanie...")
time.sleep(1)  # Malá pauza na indexáciu Obsidianom
vysledky = client.vyhladaj_jednoducho("Kryptonit2026")
for v in vysledky:
    print(f" -> Nájdená zhoda v súbore: {v['filename']} (Skóre: {v['score']})")

# 6. Premenovanie priečinka (presunie aj všetky súbory v ňom a starý zmaže)
novy_priecinok = "Projekty/PythonArchiv"
print(f"\nPresúvam celý priečinok do '{novy_priecinok}'...")
client.presun_priecinok(test_priecinok, novy_priecinok)

# 7. Čistenie (Upratanie) - Vymaže nový priečinok so všetkými súbormi a zmaže ho z disku
print("Čistím testovacie prostredie (vymazávam priečinok z disku)...")
client.vymaz_priecinok(novy_priecinok)
print("Hotovo! Priečinok bol úspešne vymazaný z vášho trezoru.")
```

---

## ⚠️ Riešenie problémov (Troubleshooting)

### 1. Prečo metóda `vytvor_priecinok` predtým zlyhávala s chybou `500 Internal Server Error`?
* **Dôvod:** Obsidian nepovoľuje cez API vytvárať skryté súbory alebo súbory, ktoré začínajú bodkou (ako `.keep`). Ak sa o to pokúsite, interný engine Obsidianu vyhodí chybu.
* **Riešenie:** Knižnica bola upravená tak, aby namiesto `.keep` zapisovala štandardný Markdown súbor `keep.md`, ktorý Obsidian bez problémov povolí vytvoriť aj vymazať.

### 2. Prečo sa priečinky v Obsidiane predtým nemazali a zostávali prázdne v bočnom paneli?
* **Dôvod:** Pôvodné verzie sa spoliehali na to, že po zmazaní súborov priečinok zmizne sám, alebo sa pokúšali mazať priečinok rekurzívne bez dôkladného zoznamu. Štandardné API pre zoznam súborov navyše neprehľadáva podadresáre rekurzívne.
* **Riešenie:** V najnovšej verzii knižnica najprv prejde kompletný zoznam súborov rekurzívnou metódou `zoznam_suborov_v_priecinku`, vymaže všetky vnútorné položky, a na záver odošle požiadavku `DELETE` priamo na cestu samotného prázdneho priečinka. Tým ho Obsidian fyzicky odstráni z disku počítača.

### 3. Chyba `ConnectionRefusedError` alebo `MaxRetryError`
* Uistite sa, že aplikácia Obsidian je v pozadí **spustená** (REST API beží lokálne priamo v procese aplikácie).
* Skontrolujte, či port v inicializácii klienta (`27124`) zodpovedá portu zobrazenému v nastaveniach pluginu Local REST API.

### 4. Chyba `401 Unauthorized`
* Overte, či sa API kľúč, ktorý odovzdávate pri vytváraní inštancie `ObsidianClient()`, zhoduje s kľúčom, ktorý vidíte v nastaveniach pluginu Local REST API priamo v Obsidiane.
