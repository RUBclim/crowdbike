# Crowdbike - Mobile Erfassung von Klimadaten mit Low-Cost-Sensoren

### First established at University of Freiburg, Enviromental Meteorology by [Andreas Christen](https://github.com/achristen)

- The original documentation and code  can be found [here](https://github.com/achristen/Meteobike)

## Benötigtes Material
1. Raspberry Pi Zero W mit Raspbian (bereits vorinstalliert)
1. Temperatur- und Feuchte Sensor (Adafruit DHT22)
1. GPS Modul - Adafruit Ultimate Breakout
1. Nova PM-Sensor (optional)
1. UART zu USB Adapter (5V) zum Anschluss des PM-Sensors
1. Adapter Micro-USB zu USB zum Anschluss des PM-Sensors
1. Kabel (bunte Steckbrücken) zum Anschluss aller Sensoren
1. Powerbank zur Stromversorgung des Rasperry Pi's
1. Gehäuse und Tasche zur Montage am Fahrrad

## Benötigte Software/Hardware zur Einrichtung
1. Laptop mit MobaXterm (Download [hier](https://mobaxterm.mobatek.net/download.html)) oder VNC-Viewer (Download [hier](https://www.realvnc.com/de/connect/download/viewer/))
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
1. Falls nötig WLAN am Raspberry Pi aktivieren (oben rechts)
1. Verbinden mit Netzwerk SSID `siehe PPP` und Passwort `siehe PPP`
1. Netzwerkverbindung zum Smartphone vorbereiten
    1. Hotspot am Smartphone aktivieren, SSID und Passwort nachschauen
    1. Netzwerk am Raspberry Pi hinzufügen
    1. Verbindung herstellen. Wenn erfolgreich, zunächst wieder trennen und mit erster Verbindung fortfahren
>Die Verbindung zu Monitor und Tastatur kann nun getrennt werden

## Herstellen einer Verbindung vom Laptop via SSH
1. Verbinden des Laptops mit gleichem WLAN-Netzwerk wie Raspberry Pi (Mobiler Hotspot oder anderes WLNA-Netzwerk)
1. Starten von MobaXterm am Laptop
1. Session &rarr; SSH &rarr; Basic SSH settings &rarr; Remote host: `<IP-Adresse des Raspberry Pi's>` &rarr; Specify username: `pi` &rarr; port: `22` &rarr; OK
1. Passwort eingeben: `siehe PPP`

## Installieren der Software
### Kurztipp: Navigation im Linux-Terminal
- Automatisches Ergänzen des Ausdrucks oder Pfads im Terminal immer mit der `TAB-Taste`
- Bestätigen von Befehlen immer mit `Enter`. Wenn erfolgreich, keine Rückgabe, ansonsten erscheint ein Error
- Verzeichnis wechseln `cd <Verzeichnis Name>` (im Stammverzeichnis `'/'` mit `cd /<Verzeichnis-Name>`)
- Ordnerinhalt anzeigen `ls` oder `ls -l` (als Liste)
- Order in aktuellem Verzeichnis erstellen `mkdir <Ordnername>`
- In übergeordnetes Verzeichnis wechseln `cd ..`
### Für die Sensoren benötigte Programme herunterladen und installieren
- Installationen unter Linux meist mit `sudo apt-get install <Programm-Name>`
- Installieren folgender Programme mit obiger Syntax
    - `build-essentials`
    - `python-dev` 
    - `python-openssl`
    - `git`
    - `gpsd`
    - `gpsd-clients`
    - `python-gps`
    - `libgpiod2`
- Installieren der Python Library für den Temperatursensor
    - `pip3 install adafruit-circuitpython-dht`
    - `pip3 install board`

- Ordner für Crowdbike-Projekt erstellen
    - `cd Dokumente`
    - `mkdir crowdbike`
- Benötigte Dateien von Github herunterladen 
- Crowdbike GUI: `git clone https://git.io/Jvkhr`

- Raspberry Pi ausschalten mit
    - `sudo shutdown -P now`
    - Warten bis grüne LED nicht mehr leuchtet, dann Stromversorgung trennen

## Anschluss der Sensoren
### Temperatur- und Feuchte-Sensor
TODO:
### GPS
TODO:
### PM-Sensor
TODO:
## Sensoren in Betrieb nehmen
### GPS einrichten
- Folgende Befehle müssen nacheinander ausgeführt werden
1. `sudo systemctl stop serial-getty@ttyS0.service`
1. `sudo systemctl disable serial-getty@ttyS0.service`
1. `sudo systemctl stop gpsd.socket`
1. `sudo systemctl disable gpsd.socket`
- Autostart Befehl für GPS hinzufügen
1. Eingabe von: `crontab -e`
1. Falls nach einem Texteditor gefragt wird `nano` auswählen (durch Eingabe von entsprechender Zahl)
1. Navigation im Texteditor nur mit &uarr; &darr; &larr; &rarr; (Pfeiltasten) möglich
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
- Speichern mit `Strg + s`
- Schließen mit `Strg + x`
- Raspberry Pi neustarten mit `sudo reboot`

## Erste Tests der Sensoren (optional)
### GPS
- Testen des GPS durch Eingabe `cgps -s`
    - **Hinweis:** Um Werte zu erhalten muss das GPS Empfang haben. Dies ist erkennbar, wenn die mit `FIX` gekennzeichnet LED auf dem GPS-Modul nur noch ca. alle 10-15 Sekunden blinkt. Blinkt sie in kürzeren Intervallen, ist noch kein Empfang vorhanden

### Temperatur- und Feuchtesensor
1. Starten von Python 3 durch Eingabe von `python3`
1. Eingabe von folgenden Zeilen. Nach Jeder Zeile Bestätigung mit `Enter`
```python
import adafruit_dht
import board

dht22_sensor = adafruit_dht.DHT22(board.D4)

for i in range(10):
    temp = dht22_sensor.temperature
    hum = dht22_sensor.humidity
    print(temp, hum)
```
- **Hinweis:** Einrückungen durch `TAB` am Anfang der Zeile beachten und letzte Zeile durch nochmaliges Drücken von `Enter` bestätigen.
- Abbruch durch `Strg + c` und Eingabe von `exit()`

### PM-Sensor
1. Navigieren in Ordner durch `cd /home/pi/Dokumente/crowdbike/Crowdbike/Code`
1. Starten von Python 3 durch Eingabe von `python3`
1. Eingabe von folgenden Zeilen. Nach Jeder Zeile Bestätigung mit `Enter`
```python
from   FUN   import pm_sensor

for i in range(10):
    nova_sensor = pm_sensor(dev='/dev/ttyUSB0')
    print(nova_sensor.read_pm())
```
- **Hinweis:** Einrückungen durch `TAB` am Anfang der Zeile beachten und letzte Zeile durch nochmaliges Drücken von `Enter` bestätigen.
- Abbruch durch `Strg + c` und Eingabe von `exit()`

## Anpassen/Personalisieren der Logger-Software
Es müssen im Folgenden noch einige kleinere Anpassungen am Skript der Logger-Software vorgenommen werden
- Navigieren zum Skript durch `cd /home/pi/Dokumente/crowdbike/Crowdbike/Code`
- Bearbeiten durch `nano -c crowdbike.py` durch `-c` werden nun im unteren Bereich die aktuelle Zeilennummer angezeigt, in der sich der Cursor gerade befindet
- Anpassung in Zeile `finale_Zeile eintragen` hier `raspberryid =` eurer Nummer zuweisen (Aufkleber auf SD-Karten-Slot)
- In Zeile `finale_Zeile eintragen` bei `studentname = `euren Namen eingeben. Möglichst ohne Leerzeichen und Sonderzeichen (ß, ä, ö, ü)
```python
[...]
from   FUN     import get_ip, read_dht22, pm_sensor

# __user parameters__
raspberryid = "00" # number of your pi
studentname = "Unknown_User"

# __calibration params__
[...]
```
- In Zeile `finale_Zeile eintragen` muss nun der Dateipfad eingestellt werden, an dem die Logs gespeichert werden sollen. Z.B. so: `logfile_path = '/home/pi/Dokumente/crowdbike/'`. **Hinweis:** auf exakte Positionen von `/` und `''` achten!
[...]
```python
[...]
vappress_cal_a0    = 0.00000 # enter the calibration coefficient offset for vapour pressure

window_title = "Crowdbike" + raspberryid
logfile_path = "/home/pi/Dokumente/crowdbike/"
if not os.path.exists(logfile_path):
  os.makedirs(logfile_path)
[...]
```
- Bei Bedarf kann noch die Log-Rate geändert werden. In Zeile `finale_Zeile eintragen` muss dafür `sampling_rate = ` geändert werden.
```python
[...]
recording     = False
pm_status     = True
sampling_rate = 5 

class GpsPoller(threading.Thread):
  def __init__(self):
[...]
```
## Erstes Starten der Logger-Software
1. Navigieren zum Skript durch `cd /home/pi/Dokumente/crowdbike/Crowdbike/Code`
1. Ausführen durch `python3 crowdbike.py` (Das Starten dauert einen Moment). Es sollte sich nun ein Fenster mit einer grafischen Benutzeroberfläche geöffnet haben
>![GUI](/Documentation/crowdbike_GUI.jpg)
### Hinweise:
- Sollten aktuell keine Werte vorhanden sein, werden sie als `nan` angezeigt und der **'Counter'** ist rot hinterlegt. Ist alles in Ordnung ist dieser grün hinterlegt.
    - Dies kann der Fall sein:
        - Wenn das GPS (noch) keinen Empfang hat
        - Wenn der PM-Sensor nicht angeschlossen oder richtig verbunden ist
- Sobald das Programm gestartet wurde, werden Daten aufgezeichnet
- Die Momentanwerte werden angezeigt und aktualisieren sich automatisch
- Der Switch **'PM-Sensor'** schaltet die Abfrage des Feinstaubsensors Ein bzw. Aus und versetzt ihn, falls angeschlossen in einen Schlafmodus.
    - Ist kein PM-Sensor angeschlossen, sollte der Schalter ausgeschaltet (rot) sein, sodass das Programm nicht bei jeder Abfrage vergeblich versucht dem Sensor abzufragen
- Die Aufzeichnung der Daten kann durch Drücken des **'Stop'** Buttons beendet werden
- Das Programm verlassen und die Aufzeichnung beenden kann man über den **'Exit'** Button

## Am Smartphone nutzen
1. Hotspot einschalten, Raspberry Pi sollte sich automatisch verbinden, wenn keine anderen bekannten, stärken WLAN-Netzwerke vorhanden sind.
1. VNC-Viewer am Smartphone starten (kein Registrierung notwendig)
1. Per **+** eine Verbindung hinzufügen
1. Bei `Address` die IP-Adresse z.B. `192.168.1.111` oder den Hostname z.B. (`crowdbike1`) eingeben 
1. Namen der Verbindung festlegen z.B. 'crowdbike_1'
1. Nun funktioniert der Touchscreen des Smartphones wie ein Mousepad am Laptop

## Sensor-Kalibrierung
TODO:
- Änderungen im Skript
- Vorheriger Test
## Zusammenbau des Systems mit Gehäuse, Tasche und Strahlungsschutz
TODO:
## Analyse/Darstellung im GIS
TODO:
## Quellen:
**Andreas Christen (2018):** Meteobike - Mapping urban heat islands with bikes. [GitHub](https://github.com/achristen/Meteobike/blob/master/readme.md). [19.01.2020].


