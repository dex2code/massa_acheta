#!/usr/bin/env bash

echo -n "Restarting MASSA 🦗 Acheta service... "

sudo systemctl restart massa_acheta.service
if [[ $? -eq 0 ]]
then
    echo "✅ Done!"
    echo
else
    echo
    echo "‼ Error occured!"
    exit 1
fi
