# SBB Dashboard Cards fuer Home Assistant

Dieses Repo enthaelt ein Dashboard-Mockup fuer Home Assistant mit:

- Licht-Tile mit Helligkeit und temporaerem Farbmodus (Double-Tap + Timeout)
- Kamera-Ansicht mit Umschaltung zwischen Normal- und Vollbildmodus
- Auto-Vollbild bei Event-Triggern (Bewegung, Klingel, Alarm) inklusive Timeout
- Test-Triggern, damit alles ohne echte Sensoren pruefbar ist

## Inhalt

- `dashboard_mockup.yaml`: Lovelace Dashboard/View (Raw YAML)
- `packages/dashboard_cards_mockup.yaml`: Helper, Timer, Scripts und Automationen

## Voraussetzungen

- Laufende Home-Assistant-Instanz
- Zugriff auf den Konfigurationsordner `/config`
- Dashboard im YAML-Modus oder Nutzung des Raw Configuration Editors

## Installation in Home Assistant

1. **Packages aktivieren**
   In `/config/configuration.yaml` sicherstellen, dass Packages eingebunden sind:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

2. **Package-Datei kopieren**
   Datei aus diesem Repo nach Home Assistant kopieren:

- Von: `packages/dashboard_cards_mockup.yaml`
- Nach: `/config/packages/dashboard_cards_mockup.yaml`

3. **Dashboard YAML importieren**
   Inhalt von `dashboard_mockup.yaml` in ein Lovelace Dashboard uebernehmen:

- Entweder neues YAML-Dashboard anlegen
- Oder im bestehenden Dashboard den Raw YAML Editor verwenden

4. **Entitaeten anpassen**
   Beispiel-Entitaeten auf deine Installation mappen, z. B.:

- `light.wohnzimmer`
- `camera.haustuer`
- `light.flur`
- `switch.gartenpumpe`
- `lock.haustuer`

5. **Konfiguration pruefen und neu laden**

- `Einstellungen > System > Reparaturen` (Config-Check)
- Danach Home Assistant neu starten

## Funktionsweise

### Light Card

- `Tap`: Licht ein/aus
- `Slider`: Helligkeit (Normalmodus)
- `Double-Tap`: Farbmodus fuer 12 Sekunden
- Bei Ablauf des Timers wird der Farbmodus automatisch deaktiviert

### Kamera Card

- Normalansicht mit Live-Bild + Schnellaktionen
- `Tap` oeffnet Vollbildansicht
- Vollbildansicht zeigt Kamera + Steuerkacheln
- Auto-Vollbild bei aktiver Event-Bedingung (wenn Auto-Modus aktiv)
- Timeout schliesst Vollbild, sobald kein Event mehr aktiv ist

## Testmodus (ohne echte Sensoren)

Diese Test-Helper sind enthalten:

- `input_boolean.camera_event_motion`
- `input_boolean.camera_event_doorbell`
- `input_boolean.camera_event_alarm`

Sie simulieren die Event-Trigger fuer die Auto-Vollbild-Logik.

## Auf produktive Sensoren umstellen

In `packages/dashboard_cards_mockup.yaml` die Template-Logik von
`binary_sensor.kamera_auto_vollbild_bedingung` auf echte Sensoren anpassen.
