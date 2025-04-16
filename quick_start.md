# Getting started with an already deployed version

1. Install the [RVNC-viewer app](https://play.google.com/store/apps/details?id=com.realvnc.viewer.android) on your phone
1. Change your wifi hotspot to have this SSID: `crowdbike-<your number>` and the password `Bike4Climate-<your number>` e.g. SSID: `crowdbike-19` and password: `Bike4Climate-19`.
1. enable the hotspot and make sure it runs on 2.4 GHz - the pi does not support 5 GHz.
1. look up the Pi's IP-Address in your hotspot settings, you will likely find this where you can see the devices connected
1. Please have a thorough read of the [manual](https://github.com/RUBclim/crowdbike?tab=readme-ov-file#crowdbike---mobile-collection-of-climate-data-with-low-cost-sensors) you don't have to do any setup though!
1. The Pi only logs data when the GPS has a signal (see the LED indicators)
1. Data is stored on the Pi at `/home/pi/crowdbike/logs/`
