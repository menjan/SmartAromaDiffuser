# Stap voor stap publiceren op GitHub

## Repository aangemaakt

De openbare repository bestaat al: **[menjan/SmartAromaDiffuser](https://github.com/menjan/SmartAromaDiffuser)**. Alle documentatie- en codeowner-verwijzingen zijn ingevuld. Voeg bij de eerste upload geen extra bovenliggende map toe.

## 1. Controleer GitHub-instellingen

1. Open de [repository](https://github.com/menjan/SmartAromaDiffuser).
2. Controleer onder **Settings → General → Features** of **Issues** aanstaat.
3. Als er nog geen code in de repository staat, ga direct door met stap 2.

## 2. Upload de bestanden

1. Pak het definitieve ZIP-bestand uit op je computer. Op macOS: selecteer de bestanden en de twee mappen **binnen** `SmartAromaDiffuser` (gebruik `Cmd+Shift+.` om ook `.gitignore` te tonen).
2. Open op GitHub bij de lege repository **uploading an existing file**, of **Add file → Upload files**.
3. Selecteer de **inhoud van de uitgepakte map** (dus README.md, LICENSE, `custom_components`, `docs` enz.), niet het ZIP-bestand zelf of een extra overkoepelende map. Sleep bestanden **én de twee mappen** naar het uploadscherm. De GitHub-webinterface kan mappen met inhoud uploaden; als dat in jouw browser niet lukt, gebruik GitHub Desktop.
4. Controleer vóór de commit of je pad `custom_components/smartaromadiffuser/manifest.json` ziet, zonder extra bovenliggende map.
5. Vul als committekst bijvoorbeeld **Initial release: SmartAromaDiffuser 1.0.0** in, en commit naar `main`.
6. Controleer of GitHub de README op de homepage weergeeft en de installatiehandleiding werkt.

## 3. Publiceer de GitHub Release

1. Klik in de repository op **Releases → Draft a new release**.
2. Maak een nieuwe tag aan: **v1.0.0**, vanaf branch `main`.
3. Titel: **SmartAromaDiffuser v1.0.0**.
4. Plak de tekst uit `RELEASE_NOTES_v1.0.0.md`.
5. Klik **Publish release**. Voor deze HACS-repository is geen extra ZIP-asset noodzakelijk: HACS kan de bronbestanden van de release gebruiken.

## 4. Test de publieke installatie

1. In HA 2026.10 of ouder: HACS → Custom repositories → plak de URL `https://github.com/menjan/SmartAromaDiffuser` en kies **Integration**.
2. Vanaf HA 2026.11: gebruik Instellingen → Marketplace → aangepaste repository (GitHub-verbinding kan nodig zijn). Installeer v1.0.0, herstart indien gevraagd en voeg SmartAromaDiffuser toe via Apparaten en diensten.
3. Test lamp, hoofdschakelaar en pas na het vastleggen van oude schema's de intensiteit.
4. Gebruik bij bestaande installaties eerst de aparte [migratiehandleiding](../MIGRATION.md).

## 5. Latere updates

Pas de benodigde bestanden aan, verhoog `version` in `custom_components/smartaromadiffuser/manifest.json`, werk CHANGELOG en release notes bij, commit en publiceer een **nieuwe GitHub Release met overeenkomstige tag** (bijvoorbeeld `v1.0.1`). Niet dezelfde v1.0.0-tag hergebruiken.

## Optioneel: officiële catalogus

Een custom HACS-repository hoeft **niet** op de openbare HACS-lijst te staan. Voor officiële catalogusopname moet je voldoen aan de dan geldende HACS/Marketplace-controles, waaronder repositorymetadata en de vereiste GitHub Actions.
