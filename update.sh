#!/usr/bin/env bash

echo "MASSA Acheta update service"
sudo echo

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

source ./bin/activate
git pull && ./bin/pip3 install -r ./requirements.txt
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
