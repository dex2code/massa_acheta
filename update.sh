#!/usr/bin/env bash


sudo systemctl stop massa_acheta.service
cd ~/massa_acheta
git pull
sudo systemctl start massa_acheta.service
cd -
