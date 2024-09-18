[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/RUBclim/crowdbike/master.svg)](https://results.pre-commit.ci/latest/github/RUBclim/crowdbike/master)

# Crowdbike - Mobile Collection of Climate Data with Low-Cost Sensors

### This is a fork: First established at University of Freiburg, Environmental Meteorology by [Andreas Christen](https://github.com/achristen)

- The original documentation and code can be found [here](https://github.com/achristen/Meteobike)

**A German version of the manual is also available [here](https://github.com/RUBclim/crowdbike/blob/master/de-readme.md)**

## Required Materials

1. Raspberry Pi Zero W
1. Temperature and Humidity Sensor (Adafruit DHT22 or better Sensirion SHT85)
1. GPS Module - Adafruit Ultimate Breakout
1. Nova PM Sensor (optional)
1. UART to USB Adapter (5V) to connect the PM Sensor (optional)
1. Micro-USB to USB adapter to connect the PM Sensor (optional)
1. Cables (colored jumper wires) to connect all sensors
1. Power bank to power the Raspberry Pi
1. Case and bag for mounting on the bike
1. Intake tube for PM Sensor (optional)
1. Adapter board (only for SHT85)

## Required Software/Hardware for Setup

1. Laptop/computer with VNC Viewer (Download [here](https://www.realvnc.com/en/connect/download/viewer/))
1. [Raspberry Pi Imager](https://www.raspberrypi.com/software/) to install the Operating System. Download here for:
   - [Windows](https://downloads.raspberrypi.org/imager/imager_latest.exe)
   - [macOS](https://downloads.raspberrypi.org/imager/imager_latest.dmg)
   - [Ubuntu](https://downloads.raspberrypi.org/imager/imager_latest_amd64.deb)
1. Wi-Fi network with Internet access
1. Smartphone with VNC Viewer (Download for smartphone [Android](https://play.google.com/store/apps/details?id=com.realvnc.viewer.android&hl=en) or [iOS](https://apps.apple.com/en/app/vnc-viewer-remote-desktop/id352019548))

## Setting up the Raspberry Pi - First Use

### System Setup

1. Download and extract the Operating System Image (Link provided on moodle)
1. Insert the MicroSD card (with adapter if necessary) into the computer.
1. Start Raspberry Pi Imager
1. Under `CHOOSE OS` &rarr; `Use custom`, select the image you just downloaded.
1. Under `CHOOSE SD CARD`, select the inserted SD card. **Note: make sure to select the correct drive. The drive will be formatted, and all data will be erased!**
1. Click on the gear (settings) icon
1. Check the box for `Set hostname` and enter `crowdbike13` (number of your Raspberry Pi)
1. Check the box for `Enable SSH` and set the password for authentication
1. Set the password to `Bike4Climate`, leave the user as `pi`
1. Start the writing process with `WRITE`.
1. Once the write and verify process is completed, briefly remove and reinsert the SD card. Then, open the `boot` drive in the file explorer.
1. Open the file `config.txt` and change the following entries as shown. This adjusts the screen resolution to portrait mode suitable for a smartphone screen (this can also be done after setup on the computer).

   ```bash
   # uncomment to force a console size. By default it will be display's size minus
   # overscan.
   framebuffer_width=720
   framebuffer_height=1280
   ```

1. Save and close the file.

#### Wi-Fi Configuration

1. Create a new file named `wpa_supplicant.conf`
   1. Right-click &rarr; New &rarr; Text document &rarr; Enter `wpa_supplicant.conf` as the file name (make sure there's no `.txt` at the end!)
   1. You may need to enable file extensions in Windows first. Do this by going to the View tab and checking the box for file name extensions.
1. When asked "If you change a file name extension, the file might become unusable. Are you sure you want to change it?", click `Yes`.
1. Now right-click &rarr; Open with and select Notepad
1. Insert the following entries:
   ```bash
   ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
   update_config=1
   country=DE
   network={
       ssid="Name of your home Wi-Fi"
       priority=1
       psk="Password of your home Wi-Fi"
   }
   network={
       ssid="Name of your smartphone hotspot"
       priority=2
       psk="Password of your smartphone hotspot"
   }
   ```
1. Make sure that the name and password are enclosed in `""`!
1. There should be no spaces around the `=`!
1. Check 3 times to ensure the password and SSID are correct!
1. Save and close the file.

### Starting the Raspberry Pi

1. Connect the power bank to the Raspberry Pi via the `PWR IN` port.
1. The Raspberry Pi should now boot (green LED will flash).
1. Wait for 2-3 minutes.

## Connecting from a Laptop/Computer

1. Connect the laptop/computer to the same Wi-Fi network as the Raspberry Pi &rarr; Home Wi-Fi as previously configured.
1. Launch VNC Viewer on the laptop/computer.
1. File &rarr; New connection.
1. VNC Server: `crowdbike13` (your number) (or local IP address if known).
1. Name: &rarr; Connection name, e.g., `My Crowdbike` &rarr; `OK`.
1. Double-click the new connection and confirm identity when prompted.
1. The connection should now be established.
1. Enter username `pi` and password `Bike4Climate`, optionally check the box to save the password &rarr; `OK`.

## Installing the Software

### Quick Tips: Navigating the Linux Terminal

- Auto-complete a command or path in the terminal with the <kbd>TAB</kbd> key.
- Confirm commands with <kbd>Enter</kbd>. If successful, there will be no output; otherwise, an error message will explain what went wrong.
- Change directories `cd <directory name>` (in the root directory `/` with `cd /<directory name>`).
- List the contents of a directory `ls` or `ls -l` (for a detailed list).
- Create a directory in the current directory `mkdir <directory name>`.
- Move to the parent directory `cd ..`.
- Use the up/down arrow keys to scroll through previously entered commands.
- Paste text from the clipboard with `Right-click`.

### Completing the Operating System Setup

- Open the terminal (top bar, black icon):

![terminal](docs/terminal_starten.png)

- If the font is too small, increase it in the terminal with <kbd>ctrl</kbd>+<kbd>+</kbd>.

- Enable the serial interface and I2C

  1. Enter `sudo raspi-config`.
  1. Use the arrow keys to navigate to "3 Interface Options" and press <kbd>Enter</kbd>.
  1. Navigate to "P5 I2C" &rarr; <kbd>Enter</kbd>.
     "Would you like the ARM I2C interface to be enabled?" Select `<YES>`.
     "ARM I2C interface is enabled" &rarr; Confirm with `<OK>`.
  1. Again, use the arrow keys to navigate to "3 Interface Options" and press <kbd>Enter</kbd>.
  1. Navigate to "P6 Serial" &rarr; <kbd>Enter</kbd>.
     "Would you like a login shell to be accessible over serial?" Select `<No>`.
  1. "Would you like the serial port hardware to be enabled?" Select `<Yes>`.
  1. "The serial login shell is disabled."
  1. "The serial interface is enabled."
  1. Confirm with `<Ok>`.
  1. Exit with `<Finish>` (use the arrow keys ←/&rarr; or <kbd>TAB</kbd> to jump to `<Finish>`).
  1. "Would you like to reboot now?" Select `<yes>`.
  1. Wait for about 1-2 minutes.

- Reconnect by double-clicking and confirming the identity warning with `Continue`, enter the password again if needed, and check the box to save the password.

### Downloading and Installing the Programs Needed for the Sensors

- Open the terminal again, and if needed, increase the font size with <kbd>ctrl</kbd>+<kbd>+</kbd>.

```bash
sudo pip3 install https://github.com/RUBclim/crowdbike/releases/download/0.10.0/crowdbike-0.10.0-py2.py3-none-any.whl
```

- This process will take a few minutes, as the Raspberry Pi Zero is not very fast.
- Now turn off the Raspberry Pi again to connect the sensors.
  - `sudo shutdown -P now`
  - Wait until the green LED turns off, then disconnect the power supply (power bank).

## Connecting the Sensors

### Temperature and Humidity Sensor DHT-22

1. Connect the cables as follows:

| Sensor |       Pi       | Cable Color |
| :----: | :------------: | :---------: |
|   +    | PIN 1 (3.3 V+) |     red     |
|   -    |  PIN 9 (GND)   |    black    |
|  out   | PIN 7 (GPCLK0) |   yellow    |

![DHT22 connection](docs/pi_dht22.png)

### Temperature and Humidity Sensor SHT-85

1. Connect the cables as follows:

| Sensor |       Pi        | Cable Color |
| :----: | :-------------: | :---------: |
|  SCL   | PIN 3 (SCL1I2C) |   purple    |
|  VDD   | PIN 1 (3.3 V+)  |    white    |
|  VSS   | PIN 9 (Ground)  |    gray     |
|  SDA   | PIN 2 (SDA1I2C) |    green    |

![SHT85 connection](docs/pi_sht85.png)

### Status Light

1. Connect the cables as follows:

| Light |       Pi        | Cable Color |
| :---: | :-------------: | :---------: |
|   G   | PIN 22 (GPIO25) |    green    |
|   Y   | PIN 18 (GPIO24) |   yellow    |
|   R   | PIN 16 (GPIO23) |     red     |
|  GRN  | PIN 14 (Ground) |    black    |

![Status light connection](docs/pi_ampel.png)

### GPS

1. Connect the cables as follows:

| GPS |      Pi      | Cable Color |
| :-: | :----------: | :---------: |
| VIN | PIN 4 (5V+)  |    black    |
| GND | PIN 6 (GND)  |    white    |
| TX  | PIN 10 (RXD) |   purple    |
| RX  | PIN 8 (TXD)  |    gray     |

![GPS connection](docs/pi_gps.png)

### PM Sensor (optional)

1. Connect a Micro-USB to USB adapter to the Micro-USB port labeled `USB`.
1. Plug the UART-USB adapter into the USB-A socket.
1. Insert the white cable from the PM sensor into the UART adapter.
   ![PM sensor connection](docs/pi_pm.png)

## Activating the Sensors

- Reconnect the Raspberry Pi to the power bank and wait for it to boot up.
- Re-establish the connection using VNC Viewer (see steps above).

- **Note:**
  To receive data, the GPS must have reception. You can tell when it has reception if the LED marked `FIX` on the GPS module flashes approximately every 10-15 seconds. If it flashes at shorter intervals, there is no reception yet.

## Configuring/Personalizing the Logger Software

Some minor adjustments must be made to personalize and set up the software.

- Reconnect via VNC and open the terminal again.
- Initialize the software by entering `crowdbike init`.

- Open the configuration file by entering `nano ~/.config/crowdbike/config.json` and press <kbd>Enter</kbd>.
- In the text editor, navigation is only possible using the arrow keys, not the mouse.

```json
{
  "user": {
    "studentname": "insert_username",
    "bike_nr": "01",
    "logfile_path": "/home/pi/crowdbike/logs/",
    "pm_sensor": false,
    "sampling_rate": 5,
    "sensor_type": "SHT85",
    "sensor_id": "1"
  },
  "cloud": {
    "folder_token": "abcde1234",
    "passwd": "my_password",
    "base_url": "https://example.nextcloud.de"
  }
}
```

- For `studentname =` enter your name. No spaces or special characters (umlauts). The name must be in double quotes, e.g., `"firstname_lastname"`. Pay attention to the comma at the end!
- Adjust `bike_nr =` to assign your number (found on the sticker on the SD card slot, e.g., `06`).
- For `pm_sensor` indicate whether you have one connected or not (only `true` or `false` is allowed).
- The `sampling_rate` controls how frequently a measurement is taken, in seconds.
- The `sensor_id` is a unique identifier for the temperature and humidity sensor (sticker on the circuit board).
- Enter the `folder_token` provided in the PPP.
- Similarly, enter the data provided in the PPP for `passwd` and `base_url`.
- Save with <kbd>ctrl</kbd>+<kbd>s</kbd> and close with <kbd>ctrl</kbd>+<kbd>x</kbd>.

## Sensor Calibration

- Sensor calibration must be entered in the file `~/.config/crowdbike/calibration.json`.
- Open the file with `nano ~/.config/crowdbike/calibration.json`.
- Make sure the factors are entered for the corresponding sensor number.

```json
{
  "temp_cal_a1": 1.0,
  "temp_cal_a0": 0.0,
  "hum_cal_a1": 1.0,
  "hum_cal_a0": 0.0
}
```

- Save with <kbd>ctrl</kbd>+<kbd>s</kbd> and close with <kbd>ctrl</kbd>+<kbd>x</kbd>.

## Customizing the GUI Color Scheme (optional)

- The color scheme of the GUI can be customized in `~/.config/crowdbike/theme.json`.
- These keys must be present.
- Colors can be hexadecimal values or standard names like `red`, `green`, etc.
- `b_*` = button
- `bg_*` = background
- `fg_*` = foreground
- `f_*` = font

```json
{
  "font_size": 24,
  "f_family": "Helvetica",
  "bg_col": "#36393f",
  "fg_col": "#ffffff",
  "fg_header": "#AAB8E8",
  "b_col": "#7289da",
  "b_disabled": "#5B6DAE",
  "b_hover": "#546cb2",
  "b_hl_border": "#AAB8E8"
}
```

## First Start of the Logger Software

1. Run the software by entering `crowdbike run` (It may take a moment to start). A window with a graphical user interface should appear.
   ![GUI](docs/crowdbike_GUI.jpg)

### Notes:

- If no values are currently available, they will be displayed as `nan`, and the **'Counter'** will be highlighted in red.
  - This may occur if:
    - The GPS has not yet acquired a signal,
    - The PM sensor is not connected or properly connected
  - If everything is functioning correctly, the counter will be highlighted in green.
- Once the program is started, data will be recorded.
- The current values will be displayed and updated automatically.
- The **'PM-Sensor'** switch toggles the query of the particulate matter sensor on or off and puts it into sleep mode if connected.
  - If no PM sensor is connected, the switch should be off (red).
- Data recording can be stopped by pressing the **'Stop'** button.
- A new recording can be started with **Record**.
- To exit the program and end the recording, use the **'Exit'** button.

#### Status Indicator

- The LEDs on the status indicator are linked to the sensor threads, blinking once for each recorded measurement.
- Keep an eye on these during measurement; if the LEDs stop blinking, check the cable connections and restart the program.
- The GPS (green) will only start blinking when satellites are found.

  |  LED   |      Meaning       | Measurement Active | Measurement Inactive |
  | :----: | :----------------: | :----------------: | :------------------: |
  |  red   | Temperature Sensor |      blinking      |         off          |
  | yellow |     PM Sensor      |      blinking      |         off          |
  | green  |        GPS         |      blinking      |         off          |

## Using on a Smartphone

1. To make it easier to start the program on a smartphone, create a shortcut:
   1. Navigate to the Desktop with `cd ~/Desktop/`
   1. Create a new file with `nano start_crowdbike.sh`
   1. Write the following into the file:
      ```console
      crowdbike run
      ```
   1. Save with <kbd>ctrl</kbd>+<kbd>s</kbd> and close with <kbd>ctrl</kbd>+<kbd>x</kbd>
   1. The script needs to be made executable by entering `chmod +x start_crowdbike.sh` and confirming with `Enter`.
1. Turn on the hotspot on your smartphone; the Raspberry Pi should connect automatically if no other known, stronger Wi-Fi networks are present.
1. Open the VNC Viewer on the smartphone (no registration required!)
1. Add a connection by pressing **+**
1. Enter the hostname, e.g., (`crowdbike1`) under `Address`. If it does not work, check the connected devices under the hotspot settings on your smartphone. Clicking on `crowdbike1` will display the IP address. Note this and enter it instead of the hostname. If the connection created in VNC Viewer does not work the next time, the smartphone might have assigned a different IP address to the Raspberry Pi. Check this as described above and try again.

1. Set the connection name, e.g., `'crowdbike1'`
1. The touchscreen of the smartphone will now function like a touchpad for the laptop.
1. The script we created should now be visible on the Desktop. Double-click and click on Run to start the program after a short delay.

## Updates

- To install a new version if available, use the following command:

```bash
sudo pip3 install git+https://github.com/RUBclim/crowdbike.git@master --upgrade
```

- The current version can be checked via the terminal with `crowdbike --version`.

## Uploading Measured Data to the Cloud

- Data can be uploaded using the **Upload** button in the GUI. The measurement must be stopped with the **Stop** button first.
- The upload may take a few seconds depending on the amount of data. During this time, the displayed measurements will not update because the upload process is not asynchronous (#13).
- A progress bar shows the upload progress and the files uploaded.
- The upload can also be started after closing the program with `crowdbike upload`.

## Debugging Errors

- The program writes a system log to `~/crowdbike.log`, where errors are recorded depending on the log level.
- The location of the log file can be changed with `crowdbike run --logfile /home/pi/Documents`.
- The log level can also be adjusted with `crowdbike run --loglevel DEBUG`.

## Command Line Interface

```console
pi@crowdbike:~ $ crowdbike --help
usage: crowdbike [-h] [-V] [--logfile LOGFILE]
                 [--loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                 {init,run,upload}

positional arguments:
  {init,run,upload}

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  --logfile LOGFILE     file to write the system logs to
  --loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}
```

## References:

**Andreas Christen (2018):** Meteobike - Mapping urban heat islands with bikes. [GitHub](https://github.com/achristen/Meteobike/blob/master/readme.md). [19.01.2020].
