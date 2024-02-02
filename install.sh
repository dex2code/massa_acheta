#!/usr/bin/env bash


DESTDIR="massa_acheta"
clear

# Check OS distro
hostnamectl | grep -i "ubuntu" > /dev/null
if [[ $? -ne 0 ]]
then
    echo "Error: this installation uses Ubuntu-compatible commands and cannot be used in other Linux distros."
    echo "You can try to install service manually using this scenario: https://github.com/dex2code/massa_acheta/blob/main/README.md"
    exit 1
else
    cd ~
fi

echo
echo "::::::::::::::::::::::::::::::::::::::::::::::::::::::::"
echo "::'##::::'##::::'###:::::'######:::'######:::::'###:::::"
echo ":::###::'###:::'## ##:::'##... ##:'##... ##:::'## ##::::"
echo ":::####'####::'##:. ##:: ##:::..:: ##:::..:::'##:. ##:::"
echo ":::## ### ##:'##:::. ##:. ######::. ######::'##:::. ##::"
echo ":::##. #: ##: #########::..... ##::..... ##: #########::"
echo ":::##:.:: ##: ##.... ##:'##::: ##:'##::: ##: ##.... ##::"
echo ":::##:::: ##: ##:::: ##:. ######::. ######:: ##:::: ##::"
echo "::..:::::..::..:::::..:::......::::......:::..:::::..:::"
echo "::::::::::::::::::::::::::::::::::::::::::::::::::::::::"
echo
echo "[ MASSA 🦗 Acheta Telebot ] -- https://github.com/dex2code/massa_acheta/"
echo
echo "This script will configure your system and install all neccessary software:"
echo "  - python3-full"
echo "  - python3-venv"
echo "  - python3-pip"
echo "  - git"
echo
echo "New Python virtual environment will be deployed in '$HOME/$DESTDIR' and new systemd unit 'massa_acheta.service' will be created."
echo -n "If you are ok with this please hit Enter, otherwise Ctrl+C to quit the installation... "
read _
echo
echo -n "First we update your repository and install all packages. Press Enter to continue... "
read _
echo

sudo apt-get update
if [[ $? -eq 0 ]]
then
    echo "*** Updating finished!"
    echo
else
    echo
    echo "Some error occured during updating. Please check your settings."
    exit 1
fi

sudo apt-get -y install git python3-full python3-venv python3-pip
if [[ $? -eq 0 ]]
then
    echo "*** All dependecies installed!"
    echo
else
    echo
    echo "Some error occured during installation. Please check your settings."
    exit 1
fi

echo -n "Now we clone repo to download service software. Press Enter to continue... "
read _
echo

git clone https://github.com/dex2code/massa_acheta.git
if [[ $? -eq 0 ]]
then
    echo "*** Repo cloned successfully!"
    echo
else
    echo
    echo "Some error occured during repo cloning. Please check your settings."
    exit 1
fi

echo -n "Now we are ready to create and configure Python virtual environment. Press Enter to continue... "
read _
echo

cd $DESTDIR && python3 -m venv .
if [[ $? -eq 0 ]]
then
    echo "*** Virtual environment created successfully! Configureng venv..."
    echo
else
    echo
    echo "Some error occured during venv creating. Please check your settings."
    exit 1
fi

source ./bin/activate && ./bin/pip3 install pip --upgrade && ./bin/pip3 install -r ./requirements.txt
if [[ $? -eq 0 ]]
then
    echo "*** Virtual environment configured successfully!"
    echo
else
    echo
    echo "Some error occured during venv configuring. Please check your settings."
    exit 1
fi

echo -n "It's time to create systemd unit. Press Enter to continue... "
read _
echo

./service.sh

echo -n "Now let's configure your Telegram bot. Press Enter to continue... "
read _
echo

./setkey.sh

echo -n "We are ready to start service. Press Enter to continue..."
read _
echo

echo -n "*** Installation done! Press Enter to continue... "
read _


clear
sudo systemctl status massa_acheta.service
echo
echo "Please note if you watch remote MASSA node you MUST open firewall on your node host."
echo "You can do it with command 'sudo ufw allow 33035/tcp'. If your firewall is closed for 33035/tcp port - your node will be unavailable for monitoring service."
echo "You don't need to open firewall if you watch localhost (127.0.0.1)."
echo
echo "More information here: https://github.com/dex2code/massa_acheta/"
echo

