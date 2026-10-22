# SmartAromaDiffuser installeren in Home Assistant

Deze handleiding is voor gebruikers van een compatibele A326-geurverspreider. Je hebt Home Assistant nodig met een Bluetooth-adapter die **actief verbinding kan maken** met BLE-apparaten. Een ESPHome Bluetooth-proxy is een alternatief.

## 1. Controleer Bluetooth in Home Assistant

1. Open **Instellingen → Apparaten en diensten** in Home Assistant.
2. Controleer of de integratie **Bluetooth** aanwezig is. Zorg dat Home Assistant een geschikte Bluetooth-adapter heeft.
3. Heb je een ESPHome Bluetooth-proxy, controleer of die online en toegevoegd is via ESPHome. Let op: de proxy moet **actieve Bluetooth-verbindingen** ondersteunen.
4. Zorg dat de diffuser stroom heeft en zich binnen Bluetooth-bereik bevindt.

## 2. Installatie via HACS of Marketplace

**Home Assistant 2026.10 of ouder:** gebruik HACS zoals hieronder. **Vanaf Home Assistant 2026.11:** gebruik **Instellingen → Marketplace**, voeg de GitHub-repository toe als *aangepaste repository* (mogelijk moet je GitHub verbinden) en installeer SmartAromaDiffuser. De repository is geschikt voor beide systemen.

**HACS (2026.10 of ouder)**

1. Installeer HACS als je dit nog niet hebt, volgens de [officiële HACS-instructies](https://hacs.xyz/).
2. Open **HACS → het menu (⋮) → Aangepaste repositories / Custom repositories**.
3. Vul de openbare GitHub-repository in: `https://github.com/menjan/SmartAromaDiffuser`.
4. Kies als type **Integratie / Integration** en bevestig.
5. Zoek **SmartAromaDiffuser**, installeer de gewenste release en **herstart Home Assistant**.

**Handmatig zonder HACS:** download de broncode (Code → Download ZIP), pak die uit, en kopieer uitsluitend de map `custom_components/smartaromadiffuser` naar `/config/custom_components/smartaromadiffuser` op je Home Assistant-systeem. Herstart HA.

## 3. Bluetooth-adres van de diffuser opzoeken

Voor het instellen vraagt de integratie om het **BLE-MAC-adres van de diffuser**, bijvoorbeeld `AA:BB:CC:DD:EE:FF`. Er staat bewust geen vast adres in de code: ieder apparaat heeft zijn eigen adres.

- Kijk of het apparaat en adres zichtbaar zijn in de Bluetooth-apparaatinformatie of de Bluetooth-diagnostiek van Home Assistant. De interface kan per Home Assistant-versie verschillen.
- Lukt dat niet, scan vlak bij de ingeschakelde diffuser met een BLE-scanner op je telefoon (bijvoorbeeld nRF Connect). Identificeer de diffuser zorgvuldig; ga niet uit van een willekeurig apparaat dat je ziet.
- Als de fabrikantenapp verbonden is, verbreek die verbinding eerst; sommige diffusers laten slechts één actieve verbinding tegelijk toe.
- Een wisselend of niet zichtbaar adres kan op BLE-adresrandomisatie of bereikproblemen wijzen; de integratie werkt met het ingevoerde adres.

Publiceer je eigen MAC-adres niet in screenshots, logs of openbare GitHub-issues.

## 4. De integratie toevoegen

1. Ga naar **Instellingen → Apparaten en diensten → Integratie toevoegen**.
2. Zoek **SmartAromaDiffuser**.
3. Vul het correcte Bluetooth-adres in en bevestig.
4. Er verschijnen een hoofdschakelaar, een lamp, een intensiteitsregelaar en diagnostische entiteiten.
5. Test eerst **Hoofdschakelaar AAN/UIT** en **Ingebouwde lamp AAN/UIT** en controleer het apparaat zelf.
6. Noteer of fotografeer je bestaande tijdschema's in de originele app voordat je de intensiteit (1–5) gaat testen. Controleer daarna of de tijdschema's gelijk zijn gebleven.

De vier tijdschema's stel je **niet** in Home Assistant in. Deze versie is bewust eenvoudig gehouden.

## 5. Verbindingsproblemen oplossen

**Symptoom: `Connection lost`, opdrachten werken soms wel en soms niet of de diffuser is onbereikbaar.**

1. Controleer stroomvoorziening, bereik en of de BLE-verbinding van de originele telefoonapp is verbroken.
2. Probeer **Status vernieuwen**; kijk in **Instellingen → Systeem → Logboeken** als de opdracht mislukt.
3. Controleer of de Bluetooth-adapter of ESPHome-proxy online is. Een RSSI-waarde van `0` of een ontbrekende RSSI-waarde is **geen betrouwbaar bewijs** voor een actieve verbinding; RSSI komt uit BLE-advertenties.
4. Plaats bij aanhoudende bereikproblemen een geschikte **ESPHome Bluetooth-proxy** dichtbij de diffuser, bij voorkeur met zo weinig mogelijk obstakels. Een ondersteunde ESP32-C3-smartplug met ESPHome kan daarvoor dienen.
5. Belangrijk: de proxy moet **`bluetooth_proxy: active: true`** ondersteunen. Alleen advertenties doorsturen is onvoldoende voor deze integratie.
6. Controleer in Home Assistant of de proxy via ESPHome is toegevoegd en of Bluetooth de proxy ziet. Test opnieuw. Een proxy vergroot het Bluetooth-bereik, maar garandeert niet dat elke BLE-verbreking verdwijnt.

**Voorbeeld van de relevante regels in een bestaande, compatibele ESPHome-configuratie:**

```yaml
esp32_ble_tracker:

bluetooth_proxy:
  active: true
```

Dit is **geen complete firmwareconfiguratie** voor iedere smartplug: behoud de bestaande apparaatspecifieke configuratie (zeker de veilige relais-/uitgangsinstellingen) en voeg alleen de ontbrekende Bluetooth-componenten toe. Flash niet zomaar generieke firmware op een netspanningsstekker. Bekijk de [ESPHome-documentatie](https://esphome.io/components/bluetooth_proxy/).

**Telefoonapp kan niet verbinden:** klik op **Verbinding verbreken** of wacht tot de verbinding automatisch wordt losgelaten. De standaard bewaartijd is **35 seconden**; `0` betekent dat de verbinding onbeperkt kan blijven bestaan. Open op dezelfde Home Assistant-integratie via **Configureren** de opties voor bewaartijd en automatisch vernieuwen.

## 6. Voor bestaande installaties

Ga bij een andere eerdere technische integratienaam niet rechtstreeks bestanden hernoemen. Maak eerst een volledige Home Assistant-back-up en volg de [migratiehandleiding](../MIGRATION.md).

## Bug melden

Meld een probleem in GitHub Issues met je HA-versie, versie van de integratie, type Bluetooth-adapter/proxy en een foutmelding. Verwijder persoonlijke adressen, MAC-adressen, tokens en privésleutels uit logbestanden.
