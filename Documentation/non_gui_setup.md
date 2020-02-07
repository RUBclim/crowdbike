# Einstellungen für die Non-GUI-Version

## Software personalisieren
- Navigieren zu `cd /home/pi/Dokumente/crowdbike/Meteobike/Code`
- Öffnen des Config-Files mit `nano config.json`
```json
{
    "user": {
        "studentname":   "insert_username",
        "bike_nr":       "01",
        "logfile_path": "/home/pi/Dokumente/crowdbike/data/",
        "pm_sensor": true,
        "sampling_rate": 5
    }
}
```
- Bei `insert_username` euren Namen eingeben. Möglichst ohne Leerzeichen und Sonderzeichen (ß, ä, ö, ü). Z.B. so `Vorname_Nachnahme`
- Bei `bike_nr` eure Nummer eintragen (Aufkleber auf SD-Karten-Slot)
- Bei `logfile_path` muss nun der Dateipfad eingestellt werden, an dem die Logs gespeichert werden sollen. Z. B. so: `logfile_path = "/home/pi/Dokumente/crowdbike/"`. **Hinweis:** auf exakte Positionen von `/` und `""` achten; `json`unterstützt keine `''` nur `""` !
- Ist kein PM-senor angeschlossen, `pm_senor` zu `false` ändern
- Bei Bedarf kann noch die Log-Rate geändert werden.  Dafür muss `sampling_rate = ` geändert werden

## Automatischer Start beim Einschalten des Raspberry Pi einrichten
- Eingabe von `crontab -e`
- Unten folgendes ergänzen: `@reboot sleep 10 && python3 /home/pi/Dokumente/crowdbike/Meteobike/Code/crowdbike_nonGUI.py /home/pi/Dokumente/crowdbike/Meteobike/Code/config.json >> /home/pi/crowdbike.log 2>&1` (alles in eine Zeile!)
#### Erklärung:
- `sleep 10` stellt sicher, dass die Software nach `gps.sock` gestartet wird
- `python3` besagt dass das danach File mit Python 3 gestartet werden soll
- `/home/pi/Dokumente/crowdbike/Meteobike/Code/crowdbike_nonGUI.py` ist der absolute Pfad zum Skript
- `/home/pi/Dokumente/crowdbike/Meteobike/Code/config.json` teilt dem Python_skript mit, an welchen Ort sich das `config.json` File befindet
- `> /home/pi/crowdbike.log 2>&1` schreibt evtl. auftretende Error-Meldungen in das angegeben log-file. Sollten Probleme auftreten, ist dies die erste Anlaufstelle!
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
@reboot sleep 10 && python3 /home/pi/Dokumente/crowdbike/Meteobike/Code/crowdbike_nonGUI.py /home/pi/Dokumente/crowdbike/Meteobike/Code/config.json >> /home/pi/crowdbike.log 2>&1
```
- Beim folgenden Neustart sollte das Skript nun automatisch starten
- Ob das Skript läuft kann durch Navigieren zum in `config.json` gesetzten `logfile_path` und aufrufen von `tail -f <my_logfilename.csv`geprüft werden.
- Das Beobachten wieder mit `Strg + c` abbrechen
