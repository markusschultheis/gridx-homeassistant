# Multi-Brand Energy Manager (gridX) für Home Assistant

Inoffizielle Home-Assistant-Integration für Energiemanagementsysteme auf Basis
der gridX-Plattform – darunter E.ON Home Manager, migrierte Viessmann-GridBox-
Konten und weitere White-Label-Portale.

<p>
  <a href="https://my.home-assistant.io/redirect/config_flow_start?domain=gridx">
    <img src="https://my.home-assistant.io/badges/config_flow_start.svg" alt="gridX zu Home Assistant hinzufügen">
  </a>
</p>

> [!IMPORTANT]
> Dieses Community-Projekt ist keine offizielle Integration von gridX, E.ON,
> Viessmann oder einem der genannten Anbieter.

## Funktionen

- Abruf der aktuellen Anlagendaten aus der gridX-Cloud im 60-Sekunden-Takt
- Automatische Sensoren für die numerischen Werte der gridX-Live-API
- Leistung, Energie, Ladezustand und weitere Messwerte mit passenden
  Home-Assistant-Einheiten
- Korrekte Umrechnung kumulativer `*MeterReading*`-Werte von Wattsekunden
  (`Ws`) in Wattstunden (`Wh`)
- Fortlaufende Energiezähler mit `state_class: total_increasing`
- Auth0-Anmeldung mit aktuellem API-`access_token` und automatischer
  Erneuerung über Refresh-Tokens
- Provider-Auswahl mit automatischer Zuordnung von `client_id` und `realm`
- Automatische Migration älterer E.ON-Konfigurationen

## Unterstützte Portale

Die folgenden Zuordnungen stammen aus der öffentlich ausgelieferten
Konfiguration der gridX-Webanwendung und wurden zuletzt am 30. August 2026
überprüft:

| Portal | Portal | Portal |
| --- | --- | --- |
| 1KOMMA5° | Bdl Next | EFA-Home |
| EGS | empavo | enviaM |
| E.ON FEH (Niederlande) | E.ON Home Manager | EVM |
| EWV | Giedorf | Greenblocks |
| Heimwatt | hemos | IBC HomeOne Hub |
| KlarSolar | LEW | Octopus Energy |
| PV Green | sonnen | Stadtwerke Norderstedt |
| upVolt | Zero 1 | Viessmann GridBox (Legacy) |

Migrierte Viessmann-GridBox-Konten verwenden in der Regel **E.ON Home
Manager**. Der frühere Viessmann-Realm ist als Legacy-Zugang auswählbar, wurde
vom Anbieter jedoch eingestellt.

Die technische Zuordnung eines Portals bedeutet nicht, dass es mit einem
echten Kundenkonto durch dieses Projekt zertifiziert wurde. Anbieter können
Zugänge, Client-IDs oder API-Verhalten jederzeit ändern.

## Voraussetzungen

- Home Assistant 2026.4.4 oder neuer
- Ein gültiges Konto bei einem unterstützten gridX-Portal
- Zugriff von Home Assistant auf `gridx.eu.auth0.com` und `api.gridx.de`

## Installation mit HACS

1. In HACS **Integrationen** öffnen.
2. Über das Menü **Benutzerdefinierte Repositories** auswählen.
3. `https://github.com/markusschultheis/gridx-homeassistant` als Repository
   mit der Kategorie **Integration** hinzufügen.
4. Die Integration herunterladen und Home Assistant neu starten.
5. Unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** nach
   `gridX` suchen.
6. Das eigene Anbieterportal auswählen und E-Mail-Adresse sowie Passwort
   eingeben.

## Manuelle Installation

Den Ordner `custom_components/gridx` in das Verzeichnis `custom_components`
der Home-Assistant-Installation kopieren und Home Assistant anschließend neu
starten.

## Authentifizierung

Alle aufgeführten Portale verwenden denselben Auth0-Tenant und die gemeinsame
gridX-API. Je nach Portal unterscheiden sich nur `client_id` und `realm`; die
Integration setzt beide Werte anhand der Auswahl automatisch.

Tokens werden für die Audience `https://api.gridx.de` angefordert. Als
Bearer-Token wird vorrangig der `access_token` verwendet. Ältere Einträge mit
der früheren Audience `my.gridx` werden beim Laden automatisch migriert.

Benutzername und Passwort werden im Home-Assistant-Konfigurationseintrag
gespeichert und ausschließlich für die Anmeldung am gridX-Auth0-Endpunkt
verwendet.

## Energieeinheiten

Die gridX-API liefert kumulative Felder mit `MeterReading` im Namen in
Wattsekunden. Die Integration teilt diese Rohwerte durch 3.600 und stellt sie
in Home Assistant als Wattstunden dar. Dadurch lassen sich die Zähler korrekt
im Energie-Dashboard und in Langzeitstatistiken verwenden.

## Bekannte Einschränkungen

- Es wird derzeit nur das erste Gateway eines Kontos verwendet.
- Die Integration liest ausschließlich Live-Daten; historische gridX-Daten
  werden nicht separat importiert.
- Die verwendeten Schnittstellen sind nicht als stabile öffentliche
  Endkunden-API garantiert.
- Änderungen an Authentifizierung oder Datenformaten der Anbieter können ein
  Update der Integration erforderlich machen.

## Beispiele

### Darstellung in Home Assistant

![Darstellung der gridX-Sensoren in Home Assistant](https://github.com/user-attachments/assets/80a8c8c2-d232-4ee7-bfa9-1fb86f908f94)

### Visualisierung in Grafana

![Visualisierung der gridX-Daten in Grafana](https://github.com/user-attachments/assets/007a8005-7844-4d54-9f2f-74a7f563475e)

## Fehler melden

Fehlerberichte und Verbesserungsvorschläge können über die
[GitHub-Issues](https://github.com/markusschultheis/gridx-homeassistant/issues)
eingereicht werden. Bitte keine Passwörter, Tokens oder vollständigen
Diagnosedaten mit personenbezogenen Informationen veröffentlichen.

## Lizenz und Danksagung

Die eigenständigen Bestandteile dieses Projekts stehen unter der
[MIT-Lizenz](LICENSE), Copyright © 2025–2026 Markus Schultheis.

Teile des Providerkatalogs und der Provider-Auswahl wurden aus dem Projekt
[ha-gridx](https://github.com/lackas/ha-gridx) von Christian Lackas abgeleitet
und für diese Integration verändert. Diese Teile bleiben unter der
[Apache License 2.0](LICENSES/Apache-2.0.txt). Einzelheiten stehen in der Datei
[NOTICE](NOTICE).

Danke an `alexmsenger` für den Hinweis auf die geänderte gridX-
Authentifizierung. Die Providerwerte wurden zusätzlich anhand der öffentlich
ausgelieferten gridX-Webanwendung überprüft.

## Markenhinweis

gridX, E.ON, Viessmann, Home Assistant sowie die Namen und Marken der
aufgeführten Portale gehören ihren jeweiligen Rechteinhabern. Ihre Nennung
dient ausschließlich dazu, die technische Kompatibilität zu beschreiben. Es
besteht keine Verbindung, Partnerschaft, Unterstützung oder Freigabe durch
diese Unternehmen oder Projekte.
