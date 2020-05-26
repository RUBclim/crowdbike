[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
# Crowdbike - Mobile Erfassung von Klimadaten mit Low-Cost-Sensoren

### First established at University of Freiburg, Enviromental Meteorology by [Andreas Christen](https://github.com/achristen)

- The original documentation and code  can be found [here](https://github.com/achristen/Meteobike)

## Benötigtes Material
1. Raspberry Pi Zero W
1. Temperatur- und Feuchte-Sensor (Adafruit DHT22)
1. GPS Modul - Adafruit Ultimate Breakout
1. Nova PM-Sensor (optional)
1. UART zu USB Adapter (5V) zum Anschluss des PM-Sensors (optional)
1. Adapter Micro-USB zu USB zum Anschluss des PM-Sensors (optional)
1. Kabel (bunte Steckbrücken) zum Anschluss aller Sensoren
1. Powerbank zur Stromversorgung des Raspberry Pi's
1. Gehäuse und Tasche zur Montage am Fahrrad
1. Ansaugschlauch für PM-Sensor (optional)

## Benötigte Software/Hardware zur Einrichtung
1. Laptop/Computer mit MobaXterm (Download [hier](https://mobaxterm.mobatek.net/download-home-edition.html) Installer Edition oder Portable Edition)
1. Raspberry Pi Imager um das Operating System zu installieren. Download hier für:
    - [Windows](https://downloads.raspberrypi.org/imager/imager.exe)
    - [macOS](https://downloads.raspberrypi.org/imager/imager.dmg)
    - [Ubuntu](https://downloads.raspberrypi.org/imager/imager_amd64.deb)
1. WLAN-Netzwerk mit Zugang zum Internet
1. Smartphone mit VNC-Viewer (Download über Smartphone [Android](https://play.google.com/store/apps/details?id=com.realvnc.viewer.android&hl=de) oder [iOS](https://apps.apple.com/de/app/vnc-viewer-remote-desktop/id352019548))

## Einrichtung des Raspberry Pi - Erstmalige Verwendung

### Systemsetup
1. Operating System Image herunterladen und entpacken (Link siehe PPP)
1. Die MicroSD-Karte mit Adapter in den Computer einlegen.
1. Raspberry Pi Imager starten
1. Bei `CHOOSE OS` &rarr; `Use custom` das eben heruntergeladene Image auswählen.
1. Bei `CHOOSE SD CARD` die eingeschobene SD-Karte wählen. **Hinweis: genau kontrollieren dass das richtige Laufwerk ausgewählt ist. Es wird im Verlauf formatiert und alle Daten werden überschrieben!**
1. Mit `WRITE` den Schreibvorgang starten.
1. Wenn der Schreib- und Verify-Vorgang nach einiger Zeit abgeschlossen ist, SD-Karte kurz entnehmen und wieder einstecken. Dann das Laufwerk `boot` im Explorer öffnen.
1. Hier die Datei `config.txt` öffnen und folgende Einträge so verändern wie hier dargestellt. Dies ändert die Bildschirmauflösung, sodass sie hochkant und für den Smartphone-Bildschirm passend ist.
    ```bash
    # uncomment to force a console size. By default it will be display's size minus
    # overscan.
    framebuffer_width=720
    framebuffer_height=1280
    ```
1. Die Datei speichern und schließen.
#### WLAN Konfiguration
1. Eine neue Datei mit dem exakten Namen `wpa_supplicant.conf` anlegen
    1. Rechtsklick &rarr; Neu &rarr; Textdokument &rarr; `wpa_supplicant.conf` als Dateinamen eingeben (darauf achten, dass kein `.txt` mehr am Ende steht!))
    1. Eventuell müssen in Windows erst die Dateinamenerweiterungen aktiviert werden. Dies geschieht über Ansicht und dann einen Haken bei Dateinamenerweiterungen setzen.
1. Bei der Frage "Wollen Sie die Dateinamenerweiterung ändern, wird die Datei möglicherweise unbrauchbar" mit `Ja` bestätigen.
1. Nun mit Rechtsklick &rarr; Öffnen mit den Editor auswählen
1. Es müssen nun Folgende Einträge eingefügt werden:
    ```bash
    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
    update_config=1
    country=DE

    network={
        ssid="Name eures Heim-WLANs"
        psk="Passwort eures Heim-WLANs"
    }

    network={
        ssid="Name eures Smartphone-Hotspots"
        psk="Passwort eures Smartphone-Hotspots"
    }
    ```
1. Darauf achten, dass Name und Passwort in `""` stehen!
1. Es dürfen keine Leerzeichen das `=` umgeben!
1. 3x kontrollieren dass das Passwort und die SSID stimmt!!
1. Die Datei speichern und schließen.

### Starten des Raspberry Pi
1. Falls der Smartphone-Hotspot im Verlauf eingeschaltet wurde, darauf achten, dass
1. Anschließen der Powerbank an den Raspberry Pi an den Eingang `PWR IN`
1. Raspberry pi sollte nun booten (grüne LED blinkt)
1. Ca. eine Minute warten

## Herstellen einer Verbindung vom Laptop/Computer via SSH
1. Verbinden des Laptops/Computers mit dem gleichem WLAN-Netzwerk wie der Raspberry Pi &rarr; Heim-WLAN wie zuvor eingestellt.
1. Starten von MobaXterm am Laptop/Computer
1. Session &rarr; SSH &rarr; Basic SSH settings &rarr; Remote host: `crowdbike`
1. Specify username: `pi`
1. port: `22` &rarr; OK
1. Passwort eingeben: `siehe PPP`

## Installieren der Software
### Kurztipp: Navigation im Linux-Terminal
- Automatisches Ergänzen des Ausdrucks oder Pfads im Terminal immer mit der `TAB-Taste`
- Bestätigen von Befehlen immer mit `Enter`. Wenn erfolgreich, keine Rückgabe, ansonsten erscheint eine Error-Mitteilung anhand derer festgestellt werden kann, was nicht funktioniert hat.
- Verzeichnis/Ordner wechseln `cd Verzeichnis Name` (im Stammverzeichnis `'/'` mit `cd /Verzeichnis-Name`)
- Ordnerinhalt anzeigen `ls` oder `ls -l` (-l für Liste)
- Order in aktuellem Verzeichnis erstellen `mkdir <Ordnername>`
- In übergeordnetes Verzeichnis wechseln `cd ..`
- Letzte eingegebene Befehle wieder aufrufen mit &uarr; und &darr; (Pfeiltasten rauf/runter)
- Einfügen von sich im Zwischenspeicher befindlichen Text mit `Rechtsklick`

### Einrichtung des Betriebssystems abschließen
- Hostnamen setzen
    1. Eingabe von `sudo raspi-config`
    1. mit Pfeiltasten zu "2 Network Options" navigieren und mit `Enter` bestätigen
    1. Zu "Hostname" navigieren &rarr; `Enter` &rarr; Hinweis mit `<Ok>` bestätigen
    1. Nun den Namen zu `crowdbike13` (Die euch zugewiesene Nummer) ändern
    1. Mit `<Ok>` bestätigen (Hinweis: Pfeiltasten &larr;/&rarr; oder `TAB` nutzen um zu `<Ok>` zu springen)


- Serielle Schnittstelle aktivieren
    1. mit Pfeiltasten zu "5 Interfacing Options" navigieren und mit `Enter` bestätigen
    1. Zu "P6 Serial" navigieren &rarr; `Enter`
    "Would you like to a login shell to be accessible over serial?" hier `<Nein>` auswählen
    1. "Would you like the serial port hardware to be enabled?" hier `<Yes>` auswählen
    1. "The serial login shell is disabled"
    1. "The serial interface is enabled"
    1. Mit `<Ok>` bestätigen
    1. Mit `<Finish>` beenden (Hinweis: Pfeiltasten &larr;/&rarr; oder `TAB` nutzen um zu `<Finish>` zu springen)
    1. "Would you like to reboot now?" mit `<yes>` bestätigen
    1. Ca. 1-2 Minuten warten

- Nun muss die Verbindung mit den neu vergebenen Hostnamen hergestellt werden wie in (Herstellen einer Verbindung vom Laptop/Computer via SSH) beschrieben.
- Nun nutzt ihr jedoch nicht mehr den Hostnamen `crowdbike`, sondern den neu vergebenen z.B. `crowdbike13`.

### Für die Sensoren benötigte Programme herunterladen und installieren
- Installieren von Systemanwendungen
- Alle Rückfragen wie `"Es werden zusätzlich 10MB Plattenspeicher genutzt"` mit `J`+`Enter` bestätigen
    - `sudo apt-get install libgpiod2`
- Installieren der Python Libraries
    - `sudo pip3 install adafruit-circuitpython-gps`
    - `sudo pip3 install adafruit-circuitpython-dht`
    - `pip3 install retry`

- Benötigte Dateien von GitHub herunterladen
    - Prüfen ob man sich im home-Verzeichnis befindet durch Eingaben von `cd ~` und Bestätigen mit `Enter`
    - Crowdbike Software: `git clone https://github.com/theendlessriver13/Meteobike --depth=1 crowdbike`

- Nun den Raspberry Pi erneut ausschalten, um die Sensoren anzuschließen.
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

## Erste Tests der Sensoren (optional)
### GPS
1. In Verzeichnis crowdbike navigieren `cd ~/crowdbike`
1. Anlegen eines Test-Scripts für das GPS
1. Eingabe von `nano gps_test.py`
1. Kopieren (Einfügen in den Editor erfolgt durch `Rechtsklick`) oder abtippen des unten stehenden Codes
1. Durch `Strg + s` speichern und mit `Strg + x` den Texteditor wieder verlassen
    ```python
    import time
    from Code.FUN import GPS


    # initialize GPS
    my_gps = GPS()

    # start GPS
    my_gps.start()

    # get a reading every second, 10 times
    for i in range(10):
        try:
            print(' GPS readings '.center(79, '*'))
            print(f'Time UTC: {my_gps.timestamp}')
            print(f'Latitude: {my_gps.latitude}')
            print(f'Longitude: {my_gps.longitude}')
            print(f'Altitude: {my_gps.alt}')
            time.sleep(1)
        except Exception:
            time.sleep(1)

    # stop requests
    my_gps.running = False

    # close uart port
    my_gps.stop()

    # stop thread
    my_gps.join()
    ```
    - **Hinweis:**
    - Einrückungen durch `TAB` **oder** 4-Leerzeichen am Anfang der Zeile beachten! Keine
    Mischung beider! Es führt zwangsläufig zu einem Syntax-Error!
    - Starten des Scripts durch Eingabe von `python3 gps_test.py`
    - Um Werte zu erhalten, muss das GPS Empfang haben. Dies ist erkennbar, wenn die mit `FIX` gekennzeichnete LED auf dem GPS-Modul nur noch ca. alle 10-15 Sekunden blinkt. Blinkt sie in kürzeren Intervallen, ist noch kein Empfang vorhanden.
    - Hier ist es meist nötig, den Raspberry Pi bei geöffneten Fenster auf die Fensterbank zu legen
    - Ggf. das Testskript mehrfach starten

### Temperatur- und Feuchtesensor
1. In Verzeichnis crowdbike navigieren `cd ~/crowdbike`
1. Anlegen eines Test-Scripts für Temperatur- und Feuchtesensor
1. Eingabe von `nano temp_hum_test.py`
1. Kopieren (Einfügen in den Editor erfolgt durch `Rechtsklick`) oder abtippen des unten stehenden Codes
1. Durch `Strg + s` speichern und mit `Strg + x` den Texteditor wieder verlassen
    ```python
    import adafruit_dht
    import board
    import time

    # initialize sensor
    dht22_sensor = adafruit_dht.DHT22(board.D4)

    # get a reading every second, 10 times
    for i in range(10):
        try:
            temp = dht22_sensor.temperature
            hum = dht22_sensor.humidity
            print(temp, hum)
            time.sleep(1)
        except Exception:
            time.sleep(1)
    ```
- **Hinweis:** Einrückungen durch `TAB` **oder** 4-Leerzeichen am Anfang der Zeile beachten! Keine Mischung beider! Es führt zwangsläufig zu einem Sytax-Error!
- Starten des Scripts durch Eingabe von `python3 temp_hum_test.py`
- Es ist Möglich, dass zunächst `None None` als Ausgabe erscheint. Sollte das der Fall sein, einfach erneut probieren und Verkabelung prüfen.

### PM-Sensor (optional)
1. Navigieren in Ordner durch `cd ~/crowdbike`
1. Anlegen eines Test-Scripts für den PM-Sensor
1. Eingabe von `nano pm_test.py`
1. Kopieren oder abtippen des unten stehenden Codes
1. Durch `Strg + s` speichern und mit `Strg + x` den Texteditor wieder verlassen
    ```python
    from Code.FUN import pm_sensor


    # initialize sensor
    nova_sensor = pm_sensor(dev='/dev/ttyUSB0')

    # get a reading every second, 10 times
    for i in range(10):
        print(nova_sensor.read_pm())
    ```
- **Hinweis:** Einrückungen durch `TAB` **oder** 4-Leerzeichen am Anfang der Zeile beachten
- Starten des Scripts durch Eingabe von `python3 pm_test.py`
## Anpassen/Personalisieren der Logger-Software
Es müssen im Folgenden noch einige kleinere Anpassungen vorgenommen werden, um die Software zu personalisieren und einzurichten
- Navigieren zum config-File durch `cd ~/crowdbike/Code`
- Öffnen des Files durch Eingabe von `nano config.json` und Bestätigen durch `Enter`
```json
{
    "user": {
        "studentname": "insert_username",
        "bike_nr": "01",
        "logfile_path": "/home/pi/crowdbike/logs/",
        "pm_sensor": false,
        "sampling_rate": 5
    },
    "cloud": {
        "folder_token": "abcde1234",
        "passwd": "my_password",
        "base_url": "https://example.nextcloud.de/"
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
1. Um das Programm am Smartphone einfacher starten zu können, müssen wir noch eine Art Verknüpfung erstellen
    1. Navigieren auf den Desktop mit `cd ~/Desktop/`
    1. Erstellen einer neuen Datei mit `nano start_crowdbike.sh`
    1. In die Datei folgendes schreiben:
        ```console
        python3 ~/crowdbike/Code/crowdbike.py
        ```
    1. Speichern wieder mit `Strg + s` und Schließen mit `Strg + x`
    1. Nun muss das kleine Skript noch ausführbar gemacht werden. Diese geschieht durch Eingabe von `chmod +x start_crowdbike.sh` und Bestätigen mit `Enter`.
1. Hotspot am Smartphone einschalten, der Raspberry Pi sollte sich automatisch verbinden, wenn keine anderen bekannten, stärkeren WLAN-Netzwerke vorhanden sind.
1. VNC-Viewer am Smartphone starten (es ist **keine** Registrierung notwendig!)
1. Per **+** eine Verbindung hinzufügen
1. Bei `Address` den Hostname z.B. (`crowdbike6`) eingeben sollte das nicht funktionieren, kann man in den Smartphoneeinstellungen unter Hotspot die verbundenen Geräte anzeigen lassen und bei einem Klick auf `crowdbike1` kann die IP-Adresse angezeigt werden. Notiert diese und gebt diese statt dem Hostname ein. Sollte die in VNC-Viewer erstellte Verbindung beim nächsten mal nicht funktionieren, kann es sein, dass das Smartphone dem Raspberry Pi eine andere IP-Adresse zugewiesen hat. Kontrolliert dies wie oben beschrieben und versucht es erneut.

1. Namen der Verbindung festlegen z.B. `'crowdbike1'`
1. Nun funktioniert der Touchscreen des Smartphones wie ein Mousepad am Laptop
1. Auf dem Desktop sollte das Skript jetzt sichtbar sein, das wir eben erstellt haben. Mit einem Doppelklick und einem Klick auf Ausführen sollte nach kurzer Zeit das Programm starten.

## Variante ohne GUI nutzen
1. Die Variante ohne GUI befindet sich in `~/crowdbike/Code/crowdbike_nonGUI.py`
1. Es sind keine neuen Einstellungen notwendig, da die Anwendung auf die gleichen config-Files zugreift.

### Manueller Start
- für den manuellen Start kann wie schon für die GUI-Version geschehen ein Start-Skript geschrieben werden
    1. Das Skript wieder auf dem Desktop anlegen `cd ~/Desktop/`
    1. Erstellen der Datei durch `nano start_nonGUI_crowdbike.sh`
    1. In die Datei folgendes schreiben (Erklärung siehe unten):
        ```sh
        python3 ~/crowdbike/Code/crowdbike_nonGUI.py & >> ~/crowdbike_nonGUI.log 2>&1
        ```
    1. Speichern wieder mit `Strg + s` und Schließen mit `Strg + x`
    1. Nun muss das kleine Skript noch ausführbar gemacht werden. Diese geschieht durch Eingabe von `chmod +x start_nonGUI_crowdbike.sh` und Bestätigen mit `Enter`.


### Automatischer Start beim Einschalten des Raspberry Pi für die `nonGUI`-Variante einrichten (optional)
- Eingabe von `crontab -e`
- Unten folgendes ergänzen: `@reboot sleep 10 && python3 /home/pi/crowdbike/Code/crowdbike_nonGUI.py >> /home/pi/crowdbike_nonGUI.log 2>&1` (alles in eine Zeile!)
#### Erklärung:
- `sleep 10` stellt sicher, dass die Software erst gestartet wird wenn der Raspberry Pi vollständig gebootet hat
- `python3` besagt dass das File danach mit Python 3 gestartet werden soll
- `/home/pi/crowdbike/Code/crowdbike_nonGUI.py` ist der absolute Pfad zum Skript
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
    @reboot sleep 10 && python3 /home/pi/crowdbike/Code/crowdbike_nonGUI.py >> /home/pi/crowdbike_nonGUI.log 2>&1
    ```
- Beim folgenden Neustart sollte das Skript nun automatisch starten
- Ob das Skript läuft kann durch Navigieren zu `~/crwodbike/logs` und aufrufen von `tail -f my_logfilename.csv` geprüft werden.
- Das Beobachten wieder mit `Strg + c` abbrechen
### Nutzungshinweise zur `nonGUI` Version
- Es muss sich darauf verlassen werden, dass das Programm ordnungsgemäß gestartet ist. Es besteht die Möglichkeit dass es aufgrund eines Fehlers zu keiner Datenaufzeichnung gekommen ist.
- Die Kontrolle ob das Programm tatsächlich ordnungsgemäß läuft, kann z.B. unter Android mit einer Verbindung per `SSH` mithilfe der App [JuiceSSH](https://play.google.com/store/apps/details?id=com.sonelli.juicessh&hl=de) durchgeführt werden.
- Hier kann dann wie oben beschrieben das log-File beobachtet werden.
- Das Abbrechen der Datenaufzeichnung kann schonungslos durch trennen der Stromversorgung erreicht werden (nicht empfohlen) es kann zur Beschädigung des OS führen.
- Korrekt beendet wird es durch ausführen von `bash ~/crowdbike/Code/stop_nonGUI.sh`
## Updates
- Um evtl. Updates und Bug-Fixes herunterzuladen muss folgendes ausgeführt werden:
1. Navigieren in den Ordner durch `cd ~/crowdbike/Code`
1. Ausführen von `git fetch`
1. Ausführen von `git checkout origin/master crowdbike.py` oder eben des Files für das eine neue Version verfügbar ist.
## Sensor-Kalibrierung
- Die Kalibrierung der Sensoren kann im File `~/crowdbike/Code/calibration.json` eingetragen werden.
    ```json
    {
        "temp_cal_a1": 1.00000,
        "temp_cal_a0": 0.00000,
        "vappress_cal_a1": 1.00000,
        "vappress_cal_a0": 0.00000
    }
    ```
## Upload der Daten
- Um die gemessenen Werte zu sammeln, gibt es ein kleines Skript, das die Daten in einen geteilten Ordner einer NextCloud hochlädt
- Das Skript sollte nur ausgeführt werden, wenn parallel kein crowdbike Prozess läuft (GUI oder nonGUI Variante)
- Bei Ausführen von `python3 ~/crowdbike/Code/send2cloud.py` wird der gesamte Inhalt des zuvor definierten log-Ordners zur Cloud gesendet
- Voraussetzung dafür ist, dass die Angaben in `config.json` richtig sind
- Bei Problemen kann durch `python3 ~/crowdbike/Code/send2cloud.py -v` die Vebosity erhöht werden.
- Es kann auch wieder eine Verknüpfung auf dem Desktop erstellt werden
- Eingabe von `nano ~/Desktop/send2cloud.sh`
- In das File schreiben:
    ```bash
    python3 ~/crowdbike/Code/send2cloud.py
    ```
- Nun muss das File wieder durch `chmod +x ~/Desktop/send2cloud.sh` ausführbar gemacht werden.
- Zum Ausführen kann nun einfach z.B. vom Smartphone aus das Programm gestartet werden.
- Im nach dem Doppelklick auftauchenden Dialog `Im Terminal ausführen` auswählen.
- Nun werden die Files hochgeladen.
## Quellen:
**Andreas Christen (2018):** Meteobike - Mapping urban heat islands with bikes. [GitHub](https://github.com/achristen/Meteobike/blob/master/readme.md). [19.01.2020].
