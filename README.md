# Home Assistant gridX Multi-Provider Integration

**Inoffizielle Community-Integration.** Dieses Projekt steht in keiner Verbindung zu gridX oder den aufgeführten OEM-/Energieanbietern.

<p><a href="https://my.home-assistant.io/redirect/config_flow_start?domain=gridx" class="my badge" target="_blank"><img src="https://my.home-assistant.io/badges/config_flow_start.svg"></a></p>

## Zweck

Die Integration liest Live-Daten von Energiesystemen aus, deren OEM-Portal auf der gridX-HomeOne-Plattform basiert, und stellt die Werte Home Assistant zur weiteren Auswertung bereit.

Die ursprüngliche Referenzinstallation verwendet eine Viessmann VitoCharge VX3 mit Batteriespeicher und GridX-Box über das E.ON-Home-Portal. Seit Version 1.3.0 ist die Authentifizierung nicht mehr fest an E.ON gebunden, sondern verwendet auswählbare gridX-OEM-Providerprofile.

## Provider-Auswahl

Bekannte gridX-OEMs teilen sich den Auth0-Tenant und das Backend `api.gridx.de`. Provider-spezifisch sind mindestens `client_id` und `realm`; zusätzlich verwaltet die Integration die aktuell belegte Audience-/Bearer-Variante je Provider. Bei der Einrichtung wird deshalb zuerst der Provider ausgewählt und der technische Authentifizierungsvertrag automatisch gesetzt.

Unterstützte Profile umfassen unter anderem:

- E.ON Home Manager
- 1KOMMA5°
- EFA-Home
- enviaM
- EVM / EWV
- IBC HomeOne Hub
- LEW (Lechwerke)
- Octopus Energy
- sonnen
- Stadtwerke Norderstedt
- upVolt
- weitere in der öffentlichen gridX-HomeOne-Konfiguration geführte OEMs

Für noch nicht gelistete oder private OEM-Tenants gibt es weiterhin **Benutzerdefiniertes gridX-Profil** mit expliziter Client-ID, Realm und Audience.

### Reifegrad

Die gemeinsame Backend-/Auth0-Architektur macht die gelisteten Profile technisch kompatibel. Die Referenz- und Regressionserfahrung dieses Repositories liegt weiterhin vor allem auf E.ON Home. Andere OEMs sollten daher bis zu einem realen Feldtest als **technisch unterstützt, aber nicht feldvalidiert** betrachtet werden.

Das historische Viessmann-Auth0-Profil wird nur zur Migration bestehender Konfigurationen beibehalten. Es wird nicht für neue Einrichtungen angeboten, da der entsprechende Legacy-Realm laut aktueller öffentlicher gridX-Providerkonfiguration außer Betrieb ist.

## Authentifizierung

Gemeinsam für die bekannten Provider sind:

- Token-Endpunkt: `https://gridx.eu.auth0.com/oauth/token`
- API: `https://api.gridx.de`
- Scope: `email openid offline_access`
- Grant: Password Realm

Die Tokenverwendung ist derzeit nicht für alle OEMs identisch belegt:

- **E.ON Home Manager:** Audience `https://api.gridx.de`, bevorzugt `access_token`. Dieser Pfad ist im Referenzprojekt praktisch geprüft.
- **Weitere öffentliche HomeOne-OEM-Profile:** Audience `my.gridx`, bevorzugt `id_token`. Diese Variante entspricht der aktuellen öffentlichen Multi-Provider-Implementierung von `lackas/ha-gridx`.

Die Integration speichert beide Tokenarten, verwendet aber jeweils den zum Provider-/Audience-Vertrag passenden Bearer und besitzt einen Kompatibilitätsfallback, falls Auth0 nur die jeweils andere Tokenart liefert. Refresh-Tokens werden automatisch erneuert; ein abgewiesener Token löst genau einen kontrollierten Authentifizierungs-Neuversuch aus.

Bestehende Version-1/2-Konfigurationen werden beim Update auf Config-Version 3 migriert. E.ON-Home-Standardwerte werden automatisch dem Provider `eon_home` zugeordnet und auf den aktuellen API-Audience-Pfad geführt. Bekannte andere OEM-Client-ID/Realm-Kombinationen erhalten ihr Providerprofil. Nicht bekannte Kombinationen bleiben als benutzerdefiniertes Profil erhalten; eine explizit gespeicherte Audience wird dabei nicht stillschweigend auf E.ON umgestellt.

## Installation mit HACS

1. In HACS **Integrationen** öffnen.
2. Unter **Benutzerdefinierte Repositories** dieses Repository als Typ **Integration** hinzufügen.
3. Die Integration installieren.
4. Home Assistant neu starten.
5. Unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** nach `gridX` suchen.

## Manuelle Installation

Den Ordner `custom_components/gridx` vollständig nach folgendem Ziel kopieren:

```text
/config/custom_components/gridx
```

Danach Home Assistant neu starten und die Integration über **Einstellungen → Geräte & Dienste** hinzufügen.

## Einrichtung

Für ein bekanntes Providerprofil werden benötigt:

| Feld | Beschreibung |
|---|---|
| Provider | gridX-basierter OEM / Portalbetreiber |
| Benutzername | Konto des ausgewählten OEM-Portals |
| Passwort | Passwort dieses Kontos |

Für **Benutzerdefiniertes gridX-Profil** werden zusätzlich Client-ID, Realm und Audience abgefragt.

Vor dem Speichern werden Anmeldung und Gateway-/System-ID read-only geprüft. Die System-ID wird als eindeutige Home-Assistant-Konfigurations-ID verwendet, damit dasselbe gridX-System nicht versehentlich doppelt eingerichtet wird.

## Sensoren und Einheiten

Die Integration stellt numerische API-Felder als Home-Assistant-Sensoren bereit. Vorhandene Sensor-Unique-IDs bleiben gegenüber älteren Versionen erhalten, damit bestehende Dashboards und Automationen nicht unnötig brechen.

### Kumulative Energiezähler

gridX liefert kumulative `*MeterReading*`-Felder in Wattsekunden (`Ws`). Die Integration rechnet diese Werte durch Division durch 3.600 in Wattstunden (`Wh`) um und stellt sie als fortlaufende Gesamtzähler bereit.

## Sicherheits- und Funktionsgrenze

Die Integration ist ein Cloud-Telemetrieadapter. Die Provider-Auswahl erweitert ausschließlich die Authentifizierungskompatibilität. Sie verleiht keine Schreib- oder Steuerberechtigung für Wechselrichter, Batterie, Wärmepumpe oder Wallbox.

## Referenzanwendung

Im Referenzhaushalt sind ein Viessmann-Wechselrichter, Batteriespeicher und eine Luftwärmepumpe mit einer GridX-Box verbunden. Home Assistant dient dort der herstellerübergreifenden Visualisierung und Weiterverarbeitung der Energiedaten.

## Beispiel der Darstellung in Home Assistant

<img width="1038" height="562" alt="image" src="https://github.com/user-attachments/assets/80a8c8c2-d232-4ee7-bfa9-1fb86f908f94" />

## Beispiel der Visualisierung in Grafana

<img width="2258" height="1146" alt="image" src="https://github.com/user-attachments/assets/007a8005-7844-4d54-9f2f-74a7f563475e" />
