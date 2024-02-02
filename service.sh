#!/usr/bin/env bash

echo -n "Generating service file... "

echo "
[Unit]
Description=MASSA Acheta
Wants=network.target
After=network.target

[Service]
Type=idle
User=$USER
WorkingDirectory=$HOME/massa_acheta
ExecStart=$HOME/massa_acheta/bin/python3 main.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
" > ./massa_acheta.service

if [[ $? -eq 0 ]]
then
        echo "Done!"
else
        echo "Error!"
        exit 1
fi


echo -n "Copying service file to /etc/systemd/system/massa_acheta.service... "
sudo cp ./massa_acheta.service /etc/systemd/system/massa_acheta.service

if [[ $? -eq 0 ]]
then
        echo "Done!"
else
        echo "Error!"
        exit 1
fi


echo -n "Reloading systemd daemon configuration... "
sudo systemctl daemon-reload

if [[ $? -eq 0 ]]
then
        echo "Done!"
else
        echo "Error!"
        exit 1
fi

exit 0