#!/usr/bin/env bash
set -e # Exit immediately if a command exits with a non-zero status.

# Install build-essential to have gcc (necessary to pip install psutil, which is necessary for plotly to generate static images)
# Lots of problems trying to install orca. Solution found thanks to:
# https://github.com/plotly/orca/issues/150
# https://github.com/plotly/orca
apt-get update && apt-get -y install xvfb
mkdir /downloads
cd /downloads
wget "https://github.com/plotly/orca/releases/download/v1.2.1/orca-1.2.1-x86_64.AppImage"
chmod 777 ./orca-1.2.1-x86_64.AppImage
./orca-1.2.1-x86_64.AppImage --appimage-extract
printf '#!/bin/bash \nxvfb-run --auto-servernum --server-args "-screen 0 640x480x24" /downloads/squashfs-root/app/orca "$@"' > /usr/bin/orca
chmod 777 /usr/bin/orca


# When trying (RUN /usr/bin/orca --help), I got error messages. I had to install libs below to not have them any more
apt-get install -y libgtk2.0-0 libgconf-2-4 libxtst6 libxss1 libnss3 libasound2
apt-get clean
rm -rf /var/lib/apt/lists/*
