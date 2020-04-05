kill -s SIGTERM $(ps x | grep '.*python3.*crowdbike_nonGUI.py$' | awk '{print $1}')
