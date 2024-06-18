#!/bin/bash

# Update and install required packages
sudo apt update
sudo apt install -y python3-pip python3-venv nginx

# Setup the project environment
cd /path/to/galliard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup systemd service
sudo cp deployment/gunicorn.service /etc/systemd/system/gunicorn.service
sudo systemctl start gunicorn
sudo systemctl enable gunicorn

# Configure Nginx
sudo cp deployment/nginx.conf /etc/nginx/sites-available/galliard
sudo ln -s /etc/nginx/sites-available/galliard /etc/nginx/sites-enabled
sudo systemctl restart nginx
