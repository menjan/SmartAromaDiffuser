# Migrating to the new integration domain

**Important: this is a breaking migration, not a normal in-place update.** Home Assistant stores the integration domain in its config entries and entity/device registries. Renaming the directory alone does not update those records.

## Safe, supported procedure

1. Make a **full Home Assistant backup** and download it before proceeding. Also keep a copy of your old custom integration folder.
2. Take screenshots or notes of the current diffuser entity IDs, device name, dashboard cards, automations, scripts, and scenes. Export relevant YAML where possible.
3. Disable automations that operate the diffuser for the duration of the migration.
4. In **Settings → Devices & services**, open the currently installed legacy integration and **remove its configuration entry**. Only do this after the full backup; removal may also remove associated device/entity registry entries.
5. Stop or restart Home Assistant as appropriate, remove only the **old custom integration directory**, then copy `custom_components/smartaromadiffuser` from this release into `/config/custom_components/`.
6. Restart Home Assistant and add **SmartAromaDiffuser** under **Settings → Devices & services**. Enter the Bluetooth MAC address of your diffuser.
7. Compare new entity IDs with those saved in step 2. If desired, edit IDs to reuse the old ones, provided those IDs are unoccupied. Otherwise update automations, scripts, scenes and dashboard YAML to point to the new IDs.
8. Test the lamp, main switch, and intensity carefully; verify stored schedules in the official mobile app before relying on automation.
9. Re-enable your automations.

**Never edit `.storage/core.config_entries` or `.storage/core.entity_registry` by hand.** Do not install both legacy and new integrations to operate the same diffuser at the same time. For rollback, restore the full backup.

## New technical domain

`smartaromadiffuser`

The new version does not import existing Home Assistant configuration entries automatically. This avoids direct modifications to private HA registries and keeps the migration explicit.
