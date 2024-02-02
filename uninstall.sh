#!/usr/bin/env bash


sudo systemctl stop massa_acheta.service
sudo systemctl disable massa_acheta.service

cd ~
rm -rf ./massa_acheta

sudo rm /etc/systemd/system/massa_acheta.service
sudo systemctl daemon-reload

echo
echo "Acheta service uninstalled!"
echo