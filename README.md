# Home Assistant Viessmann Gridbox Integration works with EON
**Not an official Viessmann/ EON Integration**
<p><a href="https://my.home-assistant.io/redirect/config_flow_start?domain=gridx" class="my badge" target="_blank"><img src="https://my.home-assistant.io/badges/config_flow_start.svg"></a></p>


# Konkretes Anwendungsbeispiel
Im Haushalt ist ein Viessmann Wechselrichter, sowie eine Luftwaermepumpe installiert. Diese Geraete sind mit einer GridX-Box verbunden. 

# Viessmann GridX Integration: Was macht die Integration?
Diese Integration ruft die PV-Anlagendaten ueber die GridX-API ab. Die Anlagedaten werden dann in Home Assistant zur weiteren Ver-/Bearbeitung zur Verfuegung gestellt. 

## Authentifizierung

Die Integration verwendet den aktuellen E.ON-Home-/gridX-Auth0-Flow. Seit der
Umstellung des Webportals wird der Token fuer die Audience
`https://api.gridx.de` angefordert und der `access_token` als Bearer-Token
verwendet. Refresh-Tokens werden automatisch erneuert. Bestehende Eintraege
mit der frueheren Audience `my.gridx` werden beim Update automatisch migriert.
Der Password-Realm-Grant, die E.ON-Client-ID und der Realm selbst sind
unveraendert. Stand der Pruefung: 30. August 2026, anhand der oeffentlichen
Konfiguration unter <https://homeone.gridx.de/>.

## Energiezaehler

gridX liefert die kumulativen `*MeterReading*`-Felder in Wattsekunden (`Ws`).
Die Integration rechnet diese Werte durch Division durch 3.600 in Wattstunden
(`Wh`) um und stellt sie Home Assistant als fortlaufende Gesamtzaehler bereit.

## Energiewende im Eigenheim
### Photovoltaik und Wärmepumpen als Dream-Team
Die Energiewende findet längst nicht mehr nur in der Politik statt, sondern in Millionen von
Haushalten. Photovoltaikanlagen liefern sauberen Strom, Luftwärmepumpen sorgen effizient für
Wärme. Doch die entscheidende Frage lautet: Wie kann der Solarstrom im eigenen Haus
optimal genutzt werden, anstatt ihn ins Netz einzuspeisen?
Proprietäre Systeme: GridBox vs. Vaillant-Portal
Viessmann bietet mit seiner GridBox ein Energiemanagementsystem an, das Stromflüsse im
Haus überwacht und Viessmann-Geräte steuert. Doch die Einbindung fremder Systeme bleibt
eingeschränkt. Ähnlich verhält es sich bei Vaillant: Das Portal myVaillant Energy Management
erlaubt eine Prognose-basierte Steuerung, jedoch nur für hauseigene Wärmepumpen. Besitzer
beider Systeme können Daten zwar koppeln, aber die Wärmepumpe nicht direkt mit
PV-Überschuss betreiben.
# Open Source als Gamechanger
Hier kommt Open Source ins Spiel: Plattformen wie Home Assistant verknüpfen Geräte
herstellerübergreifend. Mit dem Kommunikationsstandard EEBUS können PV-Anlagen,
Wärmepumpen, Batteriespeicher und Wallboxen miteinander kommunizieren. So lässt sich der
Eigenverbrauch von Solarstrom erhöhen und der Überschuss gezielt nutzen – ohne teure
proprietäre Systeme.
# Die fehlende Interoperabilität bremst
Trotz EU-weitem Standardisierungsvorhaben durch EEBUS setzen viele Hersteller auf
geschlossene Systeme. Das zwingt Verbraucher in Abhängigkeiten und reduziert die Effizienz
erneuerbarer Energien. Die Technik ist vorhanden – doch sie wird durch Fragmentierung
künstlich eingeschränkt.
# Energiewende von unten
Hausbesitzer sind nicht machtlos: Mit Open-Source-Lösungen und günstiger Hardware lassen
sich smarte Steuerungen aufbauen, die den Eigenverbrauch erhöhen. Projekte wie Home
Assistant machen es möglich, den PV-Überschuss direkt zur Warmwasserbereitung
einzusetzen. Das reduziert Kosten und trägt aktiv zur Energiewende bei.
# Fazit
Die Zukunft liegt in offenen Schnittstellen und gemeinschaftlich entwickelten Lösungen. Wer
heute auf Open Source setzt, macht sich unabhängig von teuren Herstellerportalen und nutzt
seine Energie dort, wo sie am meisten bringt: im eigenen Zuhause.

## Beispiel der Darstellung in Home Assistant
<img width="1038" height="562" alt="image" src="https://github.com/user-attachments/assets/80a8c8c2-d232-4ee7-bfa9-1fb86f908f94" />

## Beispiel der Visualisierung in Grafana
<img width="2258" height="1146" alt="image" src="https://github.com/user-attachments/assets/007a8005-7844-4d54-9f2f-74a7f563475e" />
