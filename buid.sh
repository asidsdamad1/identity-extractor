#!/bin/bash
apt-get update
apt-get install -y libzbar0 libzbar-dev
pip install zbar pyzbar opencv-python-headless pillow
pip install -r requirements.txt