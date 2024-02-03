#!/usr/bin/env bash


sudo systemctl stop massa_acheta.service &> /dev/null
sudo systemctl disable massa_acheta.service &> /dev/null

cd ~
rm -rf ~/massa_acheta &> /dev/null

sudo rm /etc/systemd/system/massa_acheta.service &> /dev/null
sudo systemctl daemon-reload &> /dev/null

echo
echo "MASSA Acheta service uninstalled!"
echo
