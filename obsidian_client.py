import requests
import urllib3
from typing import List, Optional, Union
import re

# Potlačenie varovaní pre lokálny SSL certifikát Obsidianu
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ObsidianClient:
    """
    Robustná knižnica pre prácu s Obsidian REST API v Pythone.
    Umožňuje kompletnú správu poznámok, priečinkov, vyhľadávanie a automatizáciu.
    Kompatibilná so štandardnou špecifikáciou pluginu Local REST API.
    """
    
    def __init__(self, api_key: str = "89231b04eaf3dcdce34dcdbbd077559f58165991aef62a72d68a43438d27d78c", base_url: str = "https://127.0.0.1:27124"):
        """
        Inicializuje klienta pre Obsidian API.
        
        :param api_key: Váš API token z pluginu Local REST API v Obsidiane.
        :param base_url: Základná URL adresa API (štandardne https://127.0.0.1:27124).
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "text/markdown"
        }

    # ==========================================
    # 1. ZÁKLADNÁ PRÁCA S POZNÁMKAMI (CRUD)
    # ==========================================

    def vytvor_alebo_uprav_poznamku(self, cesta_k_suboru: str, obsah: str) -> requests.Response:
        """
        Vytvorí novú poznámku alebo prepíše existujúcu poznámku v trezore (vault).
        Ak nadradené priečinky neexistujú, Obsidian ich automaticky vytvorí.
        
        :param cesta_k_suboru: Relatívna cesta k poznámke v trezore (napr. 'Projekty/PythonTest.md')
        :param obsah: Textový obsah, ktorý sa zapíše do súboru
        :return: requests.Response objekt
        """
        url = f"{self.base_url}/vault/{cesta_k_suboru.lstrip('/')}"
        response = requests.put(url, data=obsah.encode('utf-8'), headers=self.headers, verify=False)
        response.raise_for_status()
        return response

    def pridaj_na_konec_poznamky(self, cesta_k_suboru: str, pridany_text: str) -> requests.Response:
        """
        Pridá nový text na koniec existujúcej poznámky.
        
        :param cesta_k_suboru: Relatívna cesta k poznámke v trezore (napr. 'Projekty/PythonTest.md')
        :param pridany_text: Text, ktorý sa pridá na koniec súboru
        :return: requests.Response objekt
        """
        url = f"{self.base_url}/vault/{cesta_k_suboru.lstrip('/')}"
        response = requests.post(url, data=pridany_text.encode('utf-8'), headers=self.headers, verify=False)
        response.raise_for_status()
        return response

    def citaj_poznamku(self, cesta_k_suboru: str) -> str:
        """
        Prečíta a vráti obsah existujúcej poznámky v trezore (vault).
        
        :param cesta_k_suboru: Relatívna cesta k poznámke v trezore (napr. 'Projekty/PythonTest.md')
        :return: Obsah poznámky ako reťazec (string) s kódovaním UTF-8
        """
        url = f"{self.base_url}/vault/{cesta_k_suboru.lstrip('/')}"
        response = requests.get(url, headers=self.headers, verify=False)
        response.raise_for_status()
        return response.content.decode('utf-8')

    def vymaz_poznamku(self, cesta_k_suboru: str) -> requests.Response:
        """
        Vymaže konkrétny súbor/poznámku z trezoru.
        
        :param cesta_k_suboru: Relatívna cesta k súboru v trezore (napr. 'Projekty/PythonTest.md')
        :return: requests.Response objekt
        """
        url = f"{self.base_url}/vault/{cesta_k_suboru.lstrip('/')}"
        response = requests.delete(url, headers=self.headers, verify=False)
        response.raise_for_status()
        return response

    def zoznam_suborov_v_priecinku(self, priecinok: str = "", rekurzivne: bool = True) -> List[str]:
        """
        Robustne získa zoznam všetkých súborov v konkrétnom priečinku.
        Ak je rekurzivne=True, prechádza podadresáre.
        Automaticky sa vyrovnáva s rozdielmi v API, či vracia cesty absolútne voči trezoru, alebo relatívne voči priečinku.
        
        :param priecinok: Relatívna cesta k priečinku v trezore (napr. 'Projekty')
        :param rekurzivne: Či sa majú prechádzať aj podadresáre
        :return: Zoznam relatívnych ciest k súborom od koreňa trezoru
        """
        priecinok_clean = priecinok.strip("/")
        url = f"{self.base_url}/vault/{priecinok_clean}/" if priecinok_clean else f"{self.base_url}/vault/"
        headers = {**self.headers, "Accept": "application/json"}
        
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        
        polozky = response.json().get("files", [])
        vysledok = []
        
        for p in polozky:
            # Určenie plnej cesty od koreňa trezoru
            # Niektoré verzie API vracajú plnú cestu, iné len názov súboru/priečinka
            je_plna_cesta = p.startswith(priecinok_clean + "/") if priecinok_clean else True
            plna_cesta = p if je_plna_cesta else f"{priecinok_clean}/{p}"
            
            if p.endswith("/"):
                # Je to priečinok
                if rekurzivne:
                    podpriecinok = plna_cesta.rstrip("/")
                    vysledok.extend(self.zoznam_suborov_v_priecinku(podpriecinok, rekurzivne=True))
            else:
                vysledok.append(plna_cesta)
                
        return vysledok

    def zoznam_vsetkych_suborov(self) -> List[str]:
        """
        Načíta zoznam všetkých súborov nachádzajúcich sa vo vašom trezore (vault) rekurzívne.
        (Štandardné GET /vault/ vracia iba koreňové súbory, táto metóda vykonáva robustnú rekurzívnu obchádzku).
        
        :return: Zoznam relatívnych ciest k všetkým súborom (napr. ['Projekty/PythonTest.md', 'index.md'])
        """
        return self.zoznam_suborov_v_priecinku("", rekurzivne=True)

    # ==========================================\n    # 2. SPRÁVA PRIEČINKOV (FOLDERS)\n    # ==========================================

    def vytvor_priecinok(self, cesta_k_priecinku: str) -> None:
        """
        Vytvorí priečinok v trezore.
        Keďže Local REST API nepodporuje priamy koncový bod na vytváranie priečinkov,
        metóda vytvorí dočasný legitímny súbor 'keep.md' na danej ceste (čím donúti Obsidian
        vytvoriť priečinky) a následne ho vymaže. Súbory s bodkou na začiatku (napr. .keep)
        spôsobujú na strane Obsidianu 500 Internal Server Error, preto sa používa normálna markdown prípona.
        
        :param cesta_k_priecinku: Relatívna cesta k priečinku v trezore (napr. 'Archív/2026')
        """
        cesta_k_priecinku = cesta_k_priecinku.strip("/")
        placeholder = f"{cesta_k_priecinku}/keep.md"
        self.vytvor_alebo_uprav_poznamku(placeholder, "")
        self.vymaz_poznamku(placeholder)

    def vymaz_priecinok(self, cesta_k_priecinku: str) -> None:
        """
        Vymaže priečinok v trezore tak, že najprv rekurzívne odstráni všetky súbory,
        ktoré sa v ňom nachádzajú, a na záver pošle požiadavku DELETE na vymazanie samotného priečinka z disku.
        
        :param cesta_k_priecinku: Relatívna cesta k priečinku (napr. 'Archív/2026')
        """
        cesta_clean = cesta_k_priecinku.strip("/")
        prefix = cesta_clean + "/"
        vsetky_subory = self.zoznam_vsetkych_suborov()
        subory_na_zmazanie = [s for s in vsetky_subory if s.startswith(prefix)]
        
        # 1. Najprv vymažeme všetky súbory vo vnútri priečinka
        for subor in subory_na_zmazanie:
            try:
                self.vymaz_poznamku(subor)
            except Exception:
                pass
                
        # 2. Na záver vymažeme samotný prázdny priečinok
        try:
            self.vymaz_poznamku(cesta_clean)
        except Exception:
            try:
                self.vymaz_poznamku(cesta_clean + "/")
            except Exception:
                pass

    def presun_priecinok(self, stara_cesta: str, nova_cesta: str) -> None:
        """
        Presunie alebo premenuje priečinok vrátane všetkých súborov, ktoré sa v ňom nachádzajú.
        Vykonáva sa rekurzívnym presunom jednotlivých súborov na novú cestu a čistým vymazaním starého priečinka.
        
        :param stara_cesta: Pôvodná relatívna cesta k priečinku
        :param nova_cesta: Nová relatívna cesta k priečinku
        """
        stara_cesta = stara_cesta.strip("/")
        nova_cesta = nova_cesta.strip("/")
        
        vsetky_subory = self.zoznam_vsetkych_suborov()
        prefix = stara_cesta + "/"
        subory_na_presun = [s for s in vsetky_subory if s.startswith(prefix)]
        
        if not subory_na_presun:
            self.vytvor_priecinok(nova_cesta)
            try:
                self.vymaz_priecinok(stara_cesta)
            except Exception:
                pass
            return

        # Presun každého súboru rekurzívne do novej štruktúry
        for stary_subor in subory_na_presun:
            relativna_cesta = stary_subor[len(prefix):]
            novy_subor = f"{nova_cesta}/{relativna_cesta}"
            self.presun_subor(stary_subor, novy_subor)
            
        # Zmazanie starého prázdneho priečinka
        try:
            self.vymaz_priecinok(stara_cesta)
        except Exception:
            pass

    # ==========================================\n    # 3. SPRÁVA ZÁZNAMOV V PRIEČINKOCH\n    # ==========================================

    def vytvor_zaznam_v_priecinku(self, priecinok: str, nazov_suboru: str, obsah: str) -> requests.Response:
        """
        Pohodlná metóda na vytvorenie súboru (napr. poznámky) vo vnútri konkrétneho priečinka.
        
        :param priecinok: Názov/cesta k priečinku v trezore (napr. 'Práca/Úlohy')
        :param nazov_suboru: Názov súboru vrátane prípony (napr. 'Zoznam.md')
        :param obsah: Textový obsah súboru
        :return: requests.Response objekt
        """
        cesta_k_suboru = f"{priecinok.strip('/')}/{nazov_suboru.lstrip('/')}"
        return self.vytvor_alebo_uprav_poznamku(cesta_k_suboru, obsah)

    def vymaz_zaznam_v_priecinku(self, priecinok: str, nazov_suboru: str) -> requests.Response:
        """
        Vymaže konkrétny súbor v zadanom priečinku.
        
        :param priecinok: Relatívna cesta k priečinku
        :param nazov_suboru: Názov súboru na vymazanie
        :return: requests.Response objekt
        """
        cesta_k_suboru = f"{priecinok.strip('/')}/{nazov_suboru.lstrip('/')}"
        return self.vymaz_poznamku(cesta_k_suboru)

    def presun_subor(self, stara_cesta: str, nova_cesta: str) -> None:
        """
        Presunie alebo premenuje súbor (poznámku alebo binárny súbor) v rámci trezoru.
        Metóda načíta pôvodný raw obsah súboru, zapíše ho na novú cieľovú cestu s rovnakým Content-Type a zmaže pôvodný.
        
        :param stara_cesta: Pôvodná relatívna cesta k súboru (napr. 'Denník/stary.md')
        :param nova_cesta: Nová relatívna cesta k súboru (napr. 'Archív/novy.md')
        """
        url_stara = f"{self.base_url}/vault/{stara_cesta.lstrip('/')}"
        
        # 1. Získanie pôvodného súboru
        response_get = requests.get(url_stara, headers=self.headers, verify=False)
        response_get.raise_for_status()
        
        raw_obsah = response_get.content
        content_type = response_get.headers.get("Content-Type", "text/markdown")
        
        # 2. Uloženie na novú cestu (s rovnakým typom obsahu)
        url_nova = f"{self.base_url}/vault/{nova_cesta.lstrip('/')}"
        headers_nova = {**self.headers, "Content-Type": content_type}
        
        response_put = requests.put(url_nova, data=raw_obsah, headers=headers_nova, verify=False)
        response_put.raise_for_status()
        
        # 3. Vymazanie pôvodného súboru
        response_delete = requests.delete(url_stara, headers=self.headers, verify=False)
        response_delete.raise_for_status()

    # ==========================================\n    # 4. POKROČILÉ VYHĽADÁVANIE (SEARCH)\n    # ==========================================

    def vyhladaj_jednoducho(self, dopyt: str, dlzka_kontextu: Optional[int] = 100) -> List[dict]:
        """
        Vykoná jednoduché fulltextové vyhľadávanie v celom trezore.
        
        :param dopyt: Text, ktorý chcete vyhľadať
        :param dlzka_kontextu: Dĺžka kontextového úryvku vráteného okolo zhody (predvolená 100 znakov)
        :return: Zoznam slovníkov s výsledkami (obsahuje filename, score, matches s kontextom)
        """
        url = f"{self.base_url}/search/simple/"
        params = {"query": dopyt}
        if dlzka_kontextu is not None:
            params["contextLength"] = dlzka_kontextu
            
        response = requests.post(url, params=params, headers=self.headers, verify=False)
        response.raise_for_status()
        return response.json()

    def vyhladaj_dataview(self, dql_dopyt: str) -> List[dict]:
        """
        Vykoná vyhľadávanie pomocou Dataview Query Language (DQL).
        Vyžaduje nainštalovaný a povolený plugin Dataview v Obsidiane.
        
        :param dql_dopyt: DQL dotaz, napríklad 'TABLE rating FROM #game SORT rating DESC'
        :return: Zoznam výsledkov vyhľadávania
        """
        url = f"{self.base_url}/search/"
        headers = {**self.headers, "Content-Type": "application/vnd.olrapi.dataview.dql+txt"}
        response = requests.post(url, data=dql_dopyt.encode('utf-8'), headers=headers, verify=False)
        response.raise_for_status()
        return response.json()

    def vyhladaj_jsonlogic(self, json_logic_dopyt: Union[dict, str]) -> List[dict]:
        """
        Vykoná vyhľadávanie v metadátach pomocou komplexných dotazov JsonLogic.
        
        :param json_logic_dopyt: Slovník alebo JSON reťazec reprezentujúci JsonLogic logiku
        :return: Zoznam zodpovedajúcich súborov s vyhodnoteným výsledkom
        """
        import json
        url = f"{self.base_url}/search/"
        headers = {**self.headers, "Content-Type": "application/vnd.olrapi.jsonlogic+json"}
        
        if isinstance(json_logic_dopyt, dict):
            telo = json.dumps(json_logic_dopyt)
        else:
            telo = json_logic_dopyt
            
        response = requests.post(url, data=telo.encode('utf-8'), headers=headers, verify=False)
        response.raise_for_status()
        return response.json()

        # ==========================================
    # 5. PRÁCA S TAGMI A ODKAZMI (LINKS & TAGS)
    # ==========================================
    
    def ziskaj_tagy_z_poznamky(self, cesta_k_suboru: str) -> List[str]:
        """Extrahuje všetky tagy (inline aj z YAML front matter) z poznámky."""
        obsah = self.citaj_poznamku(cesta_k_suboru)
        tagy = set()
        
        # 1. Extrahovať tagy z YAML front matter
        yaml_match = re.search(r'^---\s*\n(.*?)\n---', obsah, re.DOTALL | re.MULTILINE)
        if yaml_match:
            yaml_block = yaml_match.group(1)
            tags_line_match = re.search(r'^tags:\s*\[?(.*?)\]?$', yaml_block, re.MULTILINE)
            if tags_line_match:
                raw_tags = tags_line_match.group(1)
                for t in re.split(r'[,\s]+', raw_tags):
                    if t.strip():
                        tagy.add(t.strip().strip('#'))
            for match in re.finditer(r'^\s*-\s*#?([a-zA-Z0-9_\-/]+)', yaml_block, re.MULTILINE):
                tagy.add(match.group(1))

        # 2. Extrahovať inline tagy z tela poznámky
        inline_tagy = re.findall(r'(?:^|\s)(#[a-zA-Z0-9_\-/]+)(?=\s|$)', obsah, re.MULTILINE)
        for t in inline_tagy:
            tagy.add(t.lstrip('#'))
            
        return sorted(list(tagy))

    def ziskaj_odkazy_z_poznamky(self, cesta_k_suboru: str) -> List[dict]:
        """Extrahuje všetky odkazy (Wikilinky aj Markdown linky) z poznámky."""
        obsah = self.citaj_poznamku(cesta_k_suboru)
        odkazy = []
        
        for match in re.finditer(r'\[\[(.*?)\]\]', obsah):
            target = match.group(1).split('|')[0].strip()
            odkazy.append({'type': 'wikilink', 'target': target})
            
        for match in re.finditer(r'\[.*?\]\((.*?)\)', obsah):
            target = match.group(1).strip()
            if not target.startswith('http'):
                target = target.replace('.md', '')
                odkazy.append({'type': 'markdown', 'target': target})
                
        return odkazy

    def najdi_spatne_odkazy(self, cielova_poznamka: str) -> List[str]:
        """Nájde všetky poznámky, ktoré obsahujú odkaz na zadanú poznámku."""
        dopyt = f"[[{cielova_poznamka}]]"
        vysledky = self.vyhladaj_jednoducho(dopyt)
        
        backlinky = []
        pattern = re.compile(r'\[\[' + re.escape(cielova_poznamka) + r'(?:\|.*?)?\]\]')
        
        for v in vysledky:
            try:
                obsah = self.citaj_poznamku(v['filename'])
                if pattern.search(obsah):
                    backlinky.append(v['filename'])
            except Exception:
                pass
        return backlinky

    def pridaj_tag_do_poznamky(self, cesta_k_suboru: str, tag: str) -> requests.Response:
        """Pridá tag do poznámky. Ak existuje YAML 'tags:', pridá ho tam, inak ako inline."""
        tag = tag.strip().lstrip('#')
        obsah = self.citaj_poznamku(cesta_k_suboru)
        
        # Robustná kontrola, či tag už existuje ako samostatné slovo
        if re.search(r'(?:^|\s)#' + re.escape(tag) + r'(?=\s|$)', obsah, re.MULTILINE):
            return None # Tag už existuje
            
        yaml_match = re.search(r'^(---\s*\n.*?tags:\s*\[?)(.*?)(\]?.*?\n---)', obsah, re.DOTALL | re.MULTILINE)
        if yaml_match:
            pred = yaml_match.group(1)
            stare_tagy = yaml_match.group(2).strip()
            kon = yaml_match.group(3)
            
            if not stare_tagy:
                novy_zoznam = tag
            elif stare_tagy.endswith(']'):
                novy_zoznam = f"{stare_tagy[:-1]}, {tag}]"
            else:
                novy_zoznam = f"{stare_tagy}, {tag}"
                
            novy_obsah = obsah[:yaml_match.start()] + pred + novy_zoznam + kon + obsah[yaml_match.end():]
        else:
            novy_obsah = obsah.rstrip() + f"\n\n#{tag}\n"
            
        return self.vytvor_alebo_uprav_poznamku(cesta_k_suboru, novy_obsah)

    def odstran_tag_z_poznamky(self, cesta_k_suboru: str, tag: str) -> requests.Response:
        """Odstráni konkrétny tag z poznámky (z YAML aj z inline textu)."""
        tag = tag.strip().lstrip('#')
        obsah = self.citaj_poznamku(cesta_k_suboru)
        
        # 1. Odstránenie inline tagu (OPRAVA: Použitie skupiny \1 namiesto lookbehindu)
        # Zachováva medzeru alebo začiatok riadku, aby sa nezlepili slová
        novy_obsah = re.sub(r'(^|\s)#' + re.escape(tag) + r'(?=\s|$)', r'\1', obsah, flags=re.MULTILINE)
        
        # 2. Upratanie YAML (odstránenie tagu z riadku tags:)
        def remove_from_yaml(match):
            line = match.group(0)
            line = re.sub(r'[,\s]*' + re.escape(tag) + r'[,\s]*', ' ', line)
            line = re.sub(r',\s*,', ',', line)
            line = re.sub(r'\[\s*,', '[', line)
            line = re.sub(r',\s*\]', ']', line)
            line = re.sub(r'\[\s*\]', '', line) # Ak nezostal žiadny tag, vymažeme prázdne zátvorky
            return line.strip()

        novy_obsah = re.sub(r'^tags:.*$', remove_from_yaml, novy_obsah, flags=re.MULTILINE)
        
        return self.vytvor_alebo_uprav_poznamku(cesta_k_suboru, novy_obsah.strip() + "\n")

    def zoznam_vsetkych_tagov_v_trezore(self) -> List[str]:
        """Prejde všetky súbory a vráti unikátny zoznam všetkých tagov."""
        vsetky_tagy = set()
        for subor in self.zoznam_vsetkych_suborov():
            if subor.endswith('.md'):
                try:
                    tagy = self.ziskaj_tagy_z_poznamky(subor)
                    vsetky_tagy.update(tagy)
                except Exception:
                    pass
        return sorted(list(vsetky_tagy))

# ==========================================
# HLAVNÝ BLOK (Mimo triedy!)
# ==========================================
if __name__ == "__main__":
    print("--- Ukážka robustného použitia knižnice ObsidianClient ---")
    
    client = ObsidianClient()
    test_priecinok = "Projekty/TestPriečinok"
    test_subor = "TestPoznamka.md"
    novy_obsah = "# Testovací súbor v priečinku\nTento súbor bude automaticky presunutý."
    
    # 1. Tvorenie priečinka
    print("\n[1] Vytváranie prázdneho priečinka...")
    try:
        client.vytvor_priecinok(test_priecinok)
        print(f"Priečinok '{test_priecinok}' bol pripravený.")
    except Exception as e:
        print(f"Nepodarilo sa vytvoriť priečinok: {e}")
        
    # 2. Vytvorenie súboru v priečinku
    print("\n[2] Vytváranie súboru v priečinku...")
    try:
        client.vytvor_zaznam_v_priecinku(test_priecinok, test_subor, novy_obsah)
        print(f"Súbor '{test_subor}' bol vytvorený v '{test_priecinok}'.")
    except Exception as e:
        print(f"Nepodarilo sa vytvoriť súbor v priečinku: {e}")
        
    # 3. Presunutie súboru
    stary_subor_cesta = f"{test_priecinok}/{test_subor}"
    novy_subor_cesta = f"{test_priecinok}/Presunuty_{test_subor}"
    print(f"\n[3] Presúvanie súboru z '{stary_subor_cesta}' do '{novy_subor_cesta}'...")
    try:
        client.presun_subor(stary_subor_cesta, novy_subor_cesta)
        print("Súbor úspešne presunutý.")
    except Exception as e:
        print(f"Chyba pri presúvaní súboru: {e}")

    # 4. Modifikácia / premenovanie celého priečinka
    novy_priecinok = "Projekty/PresunutyPriečinok"
    print(f"\n[4] Premenovanie celého priečinka '{test_priecinok}' na '{novy_priecinok}'...")
    try:
        client.presun_priecinok(test_priecinok, novy_priecinok)
        print("Celý priečinok vrátane súborov bol presunutý, starý priečinok bol vyčistený.")
    except Exception as e:
        print(f"Chyba pri presúvaní priečinka: {e}")

    # 5. Výpis všetkých súborov v novom priečinku
    print("\n[5] Kontrola existujúcich súborov v trezore:")
    try:
        vsetky_subory = client.zoznam_vsetkych_suborov()
        print(f"Celkový rekurzívny počet súborov: {len(vsetky_subory)}")
        for s in vsetky_subory:
            if novy_priecinok in s:
                print(f"  - {s}")
    except Exception as e:
        print(f"Chyba pri načítaní zoznamu: {e}")

    # 6. Upratanie - Vymazanie priečinka a všetkých súborov v ňom
    print(f"\n[6] Upratovanie - Mazanie priečinka '{novy_priecinok}'...")
    try:
        client.vymaz_priecinok(novy_priecinok)
        print("Priečinok aj so všetkým obsahom bol úspešne vymazaný z disku.")
    except Exception as e:
        print(f"Chyba pri mazaní priečinka: {e}")
if __name__ == "__main__":
    print("--- Ukážka robustného použitia knižnice ObsidianClient (v9 - Kompletné Upratovanie) ---")
    
    client = ObsidianClient()
    
    test_priecinok = "Projekty/TestPriečinok"
    test_subor = "TestPoznamka.md"
    novy_obsah = "# Testovací súbor v priečinku\nTento súbor bude automaticky presunutý."
    
    # 1. Tvorenie priečinka (pomocou robustnej keep.md obchádzky)
    print("\n[1] Vytváranie prázdneho priečinka...")
    try:
        client.vytvor_priecinok(test_priecinok)
        print(f"Priečinok '{test_priecinok}' bol pripravený.")
    except Exception as e:
        print(f"Nepodarilo sa vytvoriť priečinok: {e}")
        
    # 2. Vytvorenie súboru v priečinku
    print("\n[2] Vytváranie súboru v priečinku...")
    try:
        client.vytvor_zaznam_v_priecinku(test_priecinok, test_subor, novy_obsah)
        print(f"Súbor '{test_subor}' bol vytvorený v '{test_priecinok}'.")
    except Exception as e:
        print(f"Nepodarilo sa vytvoriť súbor v priečinku: {e}")
        
    # 3. Presunutie súboru
    stary_subor_cesta = f"{test_priecinok}/{test_subor}"
    novy_subor_cesta = f"{test_priecinok}/Presunuty_{test_subor}"
    print(f"\n[3] Presúvanie súboru z '{stary_subor_cesta}' do '{novy_subor_cesta}'...")
    try:
        client.presun_subor(stary_subor_cesta, novy_subor_cesta)
        print("Súbor úspešne presunutý.")
    except Exception as e:
        print(f"Chyba pri presúvaní súboru: {e}")

    # 4. Modifikácia / premenovanie celého priečinka
    novy_priecinok = "Projekty/PresunutyPriečinok"
    print(f"\n[4] Premenovanie celého priečinka '{test_priecinok}' na '{novy_priecinok}'...")
    try:
        client.presun_priecinok(test_priecinok, novy_priecinok)
        print("Celý priečinok vrátane súborov bol presunutý, starý priečinok bol vyčistený.")
    except Exception as e:
        print(f"Chyba pri presúvaní priečinka: {e}")

    # 5. Výpis všetkých súborov v novom priečinku
    print("\n[5] Kontrola existujúcich súborov v trezore:")
    try:
        vsetky_subory = client.zoznam_vsetkych_suborov()
        print(f"Celkový rekurzívny počet súborov: {len(vsetky_subory)}")
        for s in vsetky_subory:
            if novy_priecinok in s:
                print(f"  - {s}")
    except Exception as e:
        print(f"Chyba pri načítaní zoznamu: {e}")

    # 6. Upratanie - Vymazanie priečinka a všetkých súborov v ňom
    print(f"\n[6] Upratovanie - Mazanie priečinka '{novy_priecinok}'...")
    try:
        client.vymaz_priecinok(novy_priecinok)
        print("Priečinok aj so všetkým obsahom bol úspešne vymazaný z disku.")
    except Exception as e:
        print(f"Chyba pri mazaní priečinka: {e}")
