#!/usr/bin/env bash

echo "MASSA Acheta update service"
echo

sudo systemctl stop massa_acheta.service
if [[ $? -eq 0 ]]
then
    echo "✅ Service stopped"
else
    echo
    echo "‼ Some error occured. Please check your settings."
    exit 1
fi

cd ~/massa_acheta
if [[ $? -eq 0 ]]
then
    echo "✅ Ready to update"
else
    echo
    echo "‼ Some error occured. Please check your settings."
    exit 1
fi

git pull
if [[ $? -eq 0 ]]
then
    echo "✅ Service updated"
else
    echo
    echo "‼ Some error occured. Please check your settings."
    exit 1
fi

sudo systemctl start massa_acheta.service
if [[ $? -eq 0 ]]
then
    echo "✅ Service started"
    echo
else
    echo
    echo "‼ Some error occured. Please check your settings."
    exit 1
fi

exit 0