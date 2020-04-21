#!/usr/bin/env bash
set -e # Exit immediately if a command exits with a non-zero status.

# install 32bits C and C++ math lib
dpkg --add-architecture i386 \
    && apt-get -y update \
    && dpkg --configure -a \
    && apt-get -y -f install \
        libc6:i386 \
        libstdc++6:i386 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install FMU dependencies
apt-get update && apt-get -y install liblapack3 wget gnupg2
for deb in deb deb-src; do echo "$deb http://build.openmodelica.org/apt buster stable"; done | tee /etc/apt/sources.list.d/openmodelica.list
wget -q http://build.openmodelica.org/apt/openmodelica.asc -O- | apt-key add -
apt-get update
apt-get install -y libomcsimulation
