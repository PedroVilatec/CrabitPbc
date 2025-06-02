sudo lxterminal -e gunicorn --worker-class eventlet -w 1 --reload --chdir /home/pi/Crabit/vilatec app:app
