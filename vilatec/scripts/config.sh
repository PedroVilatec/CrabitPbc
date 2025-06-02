#!/bin/sh
apt update
apt install -y nginx
cd /home/pi/Crabit/instance/nginx
cp vilatec /etc/nginx/sites-available
rm /etc/nginx/sites-enabled/default
ln -s /etc/nginx/sites-available/vilatec /etc/nginx/sites-enabled/vilatec
nginx -t
service nginx restart
