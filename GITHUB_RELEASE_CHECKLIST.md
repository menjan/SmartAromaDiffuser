# Checklist: eerste GitHub-release v1.0.0

**GitHub-repository:** https://github.com/menjan/SmartAromaDiffuser — eigenaar en projectlinks zijn al ingevuld. Controleer vóór publiceren de bestandsstructuur en de daadwerkelijke werking in Home Assistant.

- [x] GitHub-gebruikersnaam `menjan` is ingevuld in manifest en installatie-URL’s.
- [x] Publieke repository met exact de naam `SmartAromaDiffuser` is aangemaakt. Controleer in GitHub of Issues aanstaan.
- [ ] Bestanden staan in de **root** van de repository, met `custom_components/smartaromadiffuser/manifest.json` in die exacte structuur (geen extra maplaag).
- [ ] Overbodige `.DS_Store`, `__MACOSX`, privélogs, persoonlijke BLE-adressen en secrets zijn niet geüpload.
- [ ] Home Assistant herkent de integratie na installatie en herstart. Hoofdschakelaar en lamp zijn op het echte apparaat getest; intensiteit en bewaarde programma's zijn gecontroleerd.
- [ ] Bij eerdere installaties is de brekende domeinnaamswijziging uitgelegd en een backup gemaakt.
- [ ] Repository-description en topics toegevoegd (bijv. `home-assistant`, `bluetooth`, `esphome`, `aroma-diffuser`, `hacs`).
- [ ] GitHub **Release** `v1.0.0` gemaakt (niet alleen een tag). Titel `SmartAromaDiffuser v1.0.0`. Gebruik `RELEASE_NOTES_v1.0.0.md` voor de tekst.
- [ ] In een test-Home Assistant: toevoegen via HACS (HA 2026.10 of ouder) of Marketplace (HA 2026.11+), installeren vanaf v1.0.0, Home Assistant herstarten, integratie configureren.

In de publieke HACS-catalogus komen is een **aparte, optionele stap**; custom-repository-installatie vereist geen acceptatie in de catalogus. Voor opname in de catalogus zijn aanvullende controles/acties (waaronder HACS- en hassfest-validatie) nodig.
