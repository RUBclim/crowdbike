# check if the script is running

if ! pgrep -f "python3 /home/pi/crowdbike/Code/log_multiple_sensors.py" > /dev/null
then
    echo "#********** $(date +'%Y-%m-%d %H:%M:%S') **********" >> /home/pi/check_run.log
    python3 /home/pi/crowdbike/Code/log_multiple_sensors.py >> /home/pi/log_multiple_sensors.log 2>&1 &
    echo "log_multiple_sensors.py was not running and was started" >> /home/pi/check_run.log
fi
