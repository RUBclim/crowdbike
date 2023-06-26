# calibration

when calibrating the SHT-85 sensors, we use an i2c-multiplexer to log multiple sensors.
This needs to be added to `/boot/config.txt` so each sensor shows up as an individual device in `/dev`.

```ini
dtoverlay=i2c-mux,pca9548,i2c1
dtoverlay=i2c-mux,pca9548,i2c1,addr=0x71
```

if multiple multiplexers are connected, you need to change the address of one of them by pulling up one pin to 3.3 V.
