# Crowdbike - Mobile Erfassung von Klimadaten mit Low-Cost-Sensoren

### First established at University of Freiburg, Enviromental Meteorology by [Andreas Christen](https://github.com/achristen)

- The original documentation and code  can be found [here](https://github.com/achristen/Meteobike)

## Benötigtes Material
1. Raspberry Pi Zero W mit Raspbian (bereits vorinstalliert)
1. Temperatur- und Feuchte-Sensor (Adafruit DHT22)
1. GPS Modul - Adafruit Ultimate Breakout
1. Nova PM-Sensor (optional)
1. UART zu USB Adapter (5V) zum Anschluss des PM-Sensors (optional)
1. Adapter Micro-USB zu USB zum Anschluss des PM-Sensors (optional)
1. Kabel (bunte Steckbrücken) zum Anschluss aller Sensoren
1. Powerbank zur Stromversorgung des Rasperry Pi's
1. Gehäuse und Tasche zur Montage am Fahrrad

## Benötigte Software/Hardware zur Einrichtung
1. Laptop/Computer mit MobaXterm (Download [hier](https://mobaxterm.mobatek.net/download-home-edition.html) Installer Edition oder Portable Edition)
1. WLAN-Netzwerk mit Zugang zum Internet
1. Smartphone mit VNC-Viewer (Download über Smartphone [Android](https://play.google.com/store/apps/details?id=com.realvnc.viewer.android&hl=de) oder [iOS](https://apps.apple.com/de/app/vnc-viewer-remote-desktop/id352019548))
1. Adapter Mini-HDMI zu HDMI
1. USB-Hub mit Micro-USB-Anschluss
1. Tastatur
1. Maus

## Einrichtung des Raspberry Pi - Erstmalige Verwendung

### Anschluss der Peripherie
1. Anschließen an Monitor via HDMI und Adapter
1. Anschließen des USB-Hubs mit Maus und Tastatur an den Eingang des Raspberry Pi auf der Platine bezeichnet mit `USB`
1. Anschließen der Powerbank an den Raspberry Pi an den Eingang `PWR IN`
1. Monitor einschalten
1. Raspberry pi sollte nun booten
1. Falls nötig anmelden als Benutzer: `pi` mit Passwort: `siehe PPP`

### Herstellen einer Netzwerkverbindung
1. Falls nötig WLAN am Raspberry Pi aktivieren (oben rechts im Bild)
1. Verbinden mit lokalem WLAN Netzwerk (Hiwneis der Raspberry Pi zero unterstützt nur 2,4 Ghz)
1. Netzwerkverbindung zum Smartphone vorbereiten
    1. Hotspot am Smartphone aktivieren, SSID (Name des WLAN_Netzwerks) und Passwort nachschauen
    1. Netzwerk am Raspberry Pi hinzufügen (wie zuvor)
    1. Verbindung herstellen. Wenn erfolgreich, zunächst wieder trennen und mit erster Verbindung fortfahren
1. Raspberry Pi kann angeschaltet (mit der Powerbak verbunden) bleiben!
>Die Verbindung zu Monitor und Tastatur kann aber nun erstmal getrennt werden

## Herstellen einer Verbindung vom Laptop via SSH
1. Verbinden des Laptops mit gleichem WLAN-Netzwerk wie Raspberry Pi (Mobiler Hotspot oder anderes WLAN-Netzwerk)
1. Starten von MobaXterm am Laptop/Computer
1. Session &rarr; SSH &rarr; Basic SSH settings &rarr; Remote host: `<Hostname des Raspberry Pi's>` z.B. `crowdbike13` &rarr; Specify username: `pi` &rarr; port: `22` &rarr; OK
1. Passwort eingeben: `siehe PPP`

## Installieren der Software
### Kurztipp: Navigation im Linux-Terminal
- Automatisches Ergänzen des Ausdrucks oder Pfads im Terminal immer mit der `TAB-Taste`
- Bestätigen von Befehlen immer mit `Enter`. Wenn erfolgreich, keine Rückgabe, ansonsten erscheint eine Error-Mitteilung anhand derer festgestellt werden kann, was nicht funktioniert hat.
- Verzeichnis wechseln `cd Verzeichnis Name` (im Stammverzeichnis `'/'` mit `cd /Verzeichnis-Name`)
- Ordnerinhalt anzeigen `ls` oder `ls -l` (-l für Liste)
- Order in aktuellem Verzeichnis erstellen `mkdir <Ordnername>`
- In übergeordnetes Verzeichnis wechseln `cd ..`
- Letzte eingebenen Befehle wiederaufrufen mit &uarr; und &darr; (Pfeiltasten rauf/runter)
### Für die Sensoren benötigte Programme herunterladen und installieren
- Installationen unter Linux meist mit `sudo apt-get install Programm-Name`
- Installieren folgender Programme mit obiger Syntax
- Alle Rückfragen wie `"Es werden zusätzlich 10MB Plattenspeicher genutzt"` mit `J`+`Enter` bestätigen
    - `build-essential`
    - `python-dev`
    - `python-openssl`
    - `git`
    - `gpsd`
    - `gpsd-clients`
    - `python-gps`
    - `libgpiod2`
- Installieren der Python Library für den Temperatursensor
    - `sudo pip3 install adafruit-circuitpython-dht`
    - `pip3 install gps`
    - `pip3 install retry`

- Benötigte Dateien von Github herunterladen
    - Prüfen ob man sich im home-Verzeichnis befindet durch Eingaben von `cd ~` und Bestätigen mit `Enter`
    - Crowdbike Software: `git clone https://theendlessriver13/Meteobike --depth=1`
- Serielle Schnittstelle aktivieren
    - `sudo raspi-config`
    - mit Pfeiltasten zu "Interfacing Options" navigieren und mit `Enter` bestätigen
    - Zu "P6 Serial" navigieren &rarr; `Enter`
    "Would you like to a login shell to be accessible over serial?" hier `<No>` auswählen
    - "Would you like the serial port hardware to be enabled?" hier `<Yes>` auswählen
    - "The serial login shell is disabled"
    - "The serial interface is enabled"
    - Mit `<Ok>` bestätigen
    - Mit `<Finish>` beenden (Hinweis: Pfeiltasten &larr;/&rarr; oder `TAB` nutzen um zu `<Finish>` zu springen)
    - "Would you like to reboot now?" mit `<yes>` bestätigen

- Nach dem reboot Raspberry Pi erneut ausschalten, um Sensoren anzuschließen
    - `sudo shutdown -P now`
    - Warten bis grüne LED nicht mehr leuchtet, dann Stromversorgung (Powerbank) trennen

## Anschluss der Sensoren
### Temperatur- und Feuchte-Sensor
#### **Achtung! Ein falscher Anschluss kann zur Zerstörung des Sensors oder des Raspberry-Pi führen. Deshalb vor dem Start erneut prüfen!**
1. Kabel wie folgt verbinden

|Sensor|Pi|Kabelfarbe|
|:---:|:---:|:---:|
|+|PIN 1 (3,3 V+)|rot|
|-|PIN 9 (GND)|schwarz|
|out|PIN 7 (GPCLK0)| gelb|

![Anschluss dht22](/Documentation/pi_dht22.png)
### GPS
#### **Achtung! Ein Falscher Anschluss kann zur Zerstörung des Sensors oder des Raspberry-Pi führen. Deshalb vor dem Start erneut prüfen.**
1. Kabel wie folgt verbinden

|GPS|Pi|Kabelfarbe|
|:---:|:---:|:---:|
|VIN|PIN 4 (5V+)|schwarz|
GND|PIN 6 (GND)|weiß|
|TX|PIN 10 (RXD)| violett|
|RX|PIN 8 (TXD)| grau|

![Anschluss gps](/Documentation/pi_gps.png)
### PM-Sensor (optional)
#### **Achtung! Ein falscher Anschluss kann zur Zerstörung des Sensors oder des Raspberry-Pi führen. Deshalb vor dem Start erneut prüfen.**
1. Micro-USB auf USB Adapter an den Micro-USB-Port `USB`  anschließen
1. An die USB-A-Buchse den UART-USB-Adapter anschließen
1. Am UART-Adapter den mittleren Pin mit dem äußeren Pin (5V) brücken (sieh Abb.)
1. Kabel wie folgt mit PM-Sensor verbinden

|PM-Sensor|UART-Adapter|Kabelfarbe|
|:---:|:---:|:---:|
|VIN|VCCI0|rot|
GND|GND|schwarz|
|TX|RXD| violett|
|RX|TXD| grau|

![Anschluss pm](/Documentation/pi_pm.png)
## Sensoren in Betrieb nehmen
- Raspberry Pi wieder mit der Powerbank verbinden und warten bis dieser gebootet hat
- Wieder Verbindung über SSH mit MobaXterm herstellen (siehe oben)
### GPS einrichten
- Folgende Befehle müssen nacheinander ausgeführt werden
1. `sudo systemctl stop serial-getty@ttyS0.service`
1. `sudo systemctl disable serial-getty@ttyS0.service`
1. `sudo systemctl stop gpsd.socket`
1. `sudo systemctl disable gpsd.socket`
- Autostart Befehl für GPS hinzufügen
1. Eingabe von: `crontab -e`
1. Falls nach einem Texteditor gefragt wird `nano` auswählen (durch Eingabe von entsprechender Zahl und Bestätigen mit `Enter`)
    ```bash
    pi@crowdbike6:~ $ crontab -e
    no crontab for pi - using an empty one

    Select an editor.  To change later, run 'select-editor'.
    1. /bin/nano        <---- easiest
    2. /usr/bin/vim.tiny
    3. /bin/ed

    Choose 1-3 [1]:
    ```
1. Navigation im Texteditor ist nur mit &uarr; &darr; &larr; &rarr; (Pfeiltasten) möglich
1. Nun letzte Zeile mit folgendem Ausdruck exakt ergänzen
    - `@reboot sudo gpsd /dev/ttyS0 -F /var/run/gpsd.sock`
>Das File sollte nun so aussehen
```sh
[...]
# For example, you can run a backup of all your user accounts
# at 5 a.m every week with:
# 0 5 * * 1 tar -zcf /var/backups/home.tgz /home/
#
# For more information see the manual pages of crontab(5) and cron(8)
#
# m h  dom mon dow   command
@reboot sudo gpsd /dev/ttyS0 -F /var/run/gpsd.sock
```
- Speichern mit `Strg + s` oder `Strg + o` und `Enter`
- Schließen des Editors mit `Strg + x`
- Raspberry Pi neustarten mit `sudo reboot`

## Erste Tests der Sensoren (optional)
### GPS
- Testen des GPS durch Eingabe `cgps -s`
    - **Hinweis:** Um Werte zu erhalten, muss das GPS Empfang haben. Dies ist erkennbar, wenn die mit `FIX` gekennzeichnete LED auf dem GPS-Modul nur noch ca. alle 10-15 Sekunden blinkt. Blinkt sie in kürzeren Intervallen, ist noch kein Empfang vorhanden.
    - Hier ist es meist nötig, den Raspberry Pi bei geöffneten Fenster auf die Fensterbank zu legen
    - Abbruch der Anzeige der GPS-Daten durch Drücken von `Strg + c`

### Temperatur- und Feuchtesensor
1. In Verzeichnis crowdbike navigieren `cd /home/pi/crowdbike`
1. Anlegen eines Testscripts für Temperatur- und Feuchtesensor
1. Eingabe von `nano temp_hum_test.py`
1. Kopieren (Einfügen in den Editor erfolgt durch `Rechtsklick`) oder abtippen des unten stehenden Codes
1. Durch `Strg + s` speichern und mit `Strg + x` den Texteditor wieder verlassen
```python
import adafruit_dht
import board
import time

dht22_sensor = adafruit_dht.DHT22(board.D4)

for i in range(10):
    try:
        temp = dht22_sensor.temperature
        hum = dht22_sensor.humidity
        print(temp, hum)
        time.sleep(1)
    except Exception:
       pass
```
- **Hinweis:** Einrückungen durch `TAB` **oder** 4-Leerzeichen am Anfang der Zeile beachten! Keine Mischung beider! Es führt zwangsläufig zu einem Sytax-Error!
- Starten des Scripts durch Eingabe von `python3 temp_hum_test.py`
- Es ist Möglich, dass zunächst `None None` als Ausgabe erscheint. Sollte das der Fall sein, einfach erneut probieren und Verkabelung prüfen.

### PM-Sensor (optional)
1. Navigieren in Ordner durch `cd /home/pi/crowdbike`
1. Anlegen eines Testscripts für den PM-Sensor
1. Eingabe von `nano pm_test.py`
1. Kopieren oder abtippen des unten stehenden Codes
1. Durch `Strg + s` speichern und mit `Strg + x` den Texteditor wieder verlassen
```python
from FUN import pm_sensor

for i in range(10):
    nova_sensor = pm_sensor(dev='/dev/ttyUSB0')
    print(nova_sensor.read_pm())
```
- **Hinweis:** Einrückungen durch `TAB` **oder** 4-Leerzeichen am Anfang der Zeile beachten
- Starten des Scripts durch Eingabe von `python3 pm_test.py`
## Anpassen/Personalisieren der Logger-Software
Es müssen im Folgenden noch einige kleinere Anpassungen vorgenommen werden, um die Software zu personalisieren und einzurichten
- Navigieren zum config-file durch `cd /home/pi/crowdbike/Code`
- Öffnen des files durch Eingabe von `nano config.json` und Bestätigen durch `Enter`
```json
{
    "user": { TODO:
        "studentname": "insert_username",
        "bike_nr": "01",
        "logfile_path": "/home/pi/crowdbike/data/",
        "pm_sensor": false,
        "sampling_rate": 5
    },
    "cloud": {
        "folder_token": "abcde1234",
        "passwd": "my_password",
        "base_url": "https://example.nextcloud.de"
    }
}
```
- Bei `studentname = `euren Namen eingeben. Ohne Leerzeichen und Umlaute. Der Name muss in doppelten Anführungszeichen stehen z.B. `"vorname_nachname"`. Komma am Ende beachten!
- Anpassung bei `bike_nr =` eure Nummer zuweisen (Aufkleber auf SD-Karten-Slot)
- Bei `pm_sensor` angeben ob ihr einen angeschlossen habt oder nicht (es ist nur `true` oder `false` erlaubt!)
- Die `sampling_rate` steuert die Häufigkeit in der eine Messung durchgeführt wird in Sekunden.
- Bei `folder_token` den in der PPP mitgeteilten Token eintragen.
- Ebenfalls bei `passwd` und `base_url` die in der PPP mitgeteilten Daten eintragen.
## Erstes Starten der Logger-Software
1. Navigieren zum Skript durch `cd ~/crowdbike/Code`
1. Ausführen durch Eingabe von `python3 crowdbike.py` (Das Starten dauert einen Moment). Es sollte sich nun ein Fenster mit einer grafischen Benutzeroberfläche geöffnet haben.
>![GUI](/Documentation/crowdbike_GUI.jpg)
### Hinweise:
- Sollten aktuell keine Werte vorhanden sein, werden sie als `nan` angezeigt und der **'Counter'** ist rot hinterlegt.
    - Dies kann der Fall sein:
        - Wenn das GPS (noch) keinen Empfang hat,
        - Wenn der PM-Sensor nicht angeschlossen oder richtig verbunden ist
    -  Ist alles in Ordnung ist dieser grün hinterlegt.
- Sobald das Programm gestartet wurde, werden Daten aufgezeichnet
- Die Momentanwerte werden angezeigt und aktualisieren sich automatisch
- Der Switch **'PM-Sensor'** schaltet die Abfrage des Feinstaubsensors ein bzw. aus und versetzt ihn, falls angeschlossen in einen Schlafmodus.
    - Ist kein PM-Sensor angeschlossen, sollte der Schalter ausgeschaltet (rot) sein, sodass das Programm nicht bei jeder Abfrage vergeblich versucht, den Sensor abzufragen.
- Die Aufzeichnung der Daten kann durch drücken des **'Stop'** Buttons beendet werden
- Das Programm verlassen und die Aufzeichnung beenden kann man über den **'Exit'** Button.

## Am Smartphone nutzen
1. Hotspot einschalten, der Raspberry Pi sollte sich automatisch verbinden, wenn keine anderen bekannten, stärkeren WLAN-Netzwerke vorhanden sind.
1. VNC-Viewer am Smartphone starten (kein Registrierung notwendig!)
1. Per **+** eine Verbindung hinzufügen
1. Bei `Address` die IP-Adresse z.B. `192.168.2.143` oder den Hostname z.B. (`crowdbike6`) eingeben
1. Namen der Verbindung festlegen z.B. 'crowdbike_6'
1. Nun funktioniert der Touchscreen des Smartphones wie ein Mousepad am Laptop

## Variante ohne GUI nutzen
TODO:
1. Die Variante ohne GUI befindet sich in `~/crowdbike/Code/crowdbike_nonGUI.py`
1. Es sind keine neuen Einstellungen notwendig, da die Anwendung auf die gleichen config-files zugreift.

### Automatischer Start beim Einschalten des Raspberry Pi für die `nonGUI`-Variante einrichten
- Eingabe von `crontab -e`
- Unten folgendes ergänzen: `@reboot sleep 10 && python3 /home/pi/crowdbike/Code/crowdbike_nonGUI.py >> /home/pi/crowdbike_nonGUI.log 2>&1` (alles in eine Zeile!)
#### Erklärung:
- `sleep 10` stellt sicher, dass die Software nach `gps.sock` gestartet wird
- `python3` besagt dass das File danach mit Python 3 gestartet werden soll
- `/home/pi/crowdbike/Code/crowdbike_nonGUI.py` ist der absolute Pfad zum Skript
- TODO: bash wrapper schreiben
- `>> /home/pi/crowdbike.log 2>&1` schreibt evtl. auftretende Error-Meldungen in das angegeben log-File. Sollten Probleme auftreten, ist dies die erste Anlaufstelle!
```sh
[...]
# For example, you can run a backup of all your user accounts
# at 5 a.m every week with:
# 0 5 * * 1 tar -zcf /var/backups/home.tgz /home/
#
# For more information see the manual pages of crontab(5) and cron(8)
#
# m h  dom mon dow   command
@reboot sudo gpsd /dev/ttyS0 -F /var/run/gpsd.sock
@reboot sleep 10 && python3 /home/pi/crowdbike/Code/crowdbike_nonGUI.py >> /home/pi/crowdbike_nonGUI.log 2>&1
```
- Beim folgenden Neustart sollte das Skript nun automatisch starten
- Ob das Skript läuft kann durch Navigieren zu `~/crwodbike/logs` und aufrufen von `tail -f my_logfilename.csv` geprüft werden.
- Das Beobachten wieder mit `Strg + c` abbrechen
## Sensor-Kalibrierung
TODO:
- Die Kalibrierung der Sensoren kann im File `~/crowdbike/Code/calibration.json` eingetragen werden.
    ```json
    {
        "temp_cal_a1": 1.00100,
        "temp_cal_a0": 0.00000,
        "vappress_cal_a1": 1.00000,
        "vappress_cal_a0": 0.00000
    }
    ```
- Vorheriger Test
## Zusammenbau des Systems mit Gehäuse, Tasche und Strahlungsschutz
TODO:
## Analyse/Darstellung im GIS
TODO:
## Quellen:
**Andreas Christen (2018):** Meteobike - Mapping urban heat islands with bikes. [GitHub](https://github.com/achristen/Meteobike/blob/master/readme.md). [19.01.2020].
