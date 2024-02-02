#!/usr/bin/env bash


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
echo "[ MASSA 🦗 Acheta telebot ] -- https://github.com/dex2code/massa_acheta/"
echo

echo "This script configures .env file to store your Bot API Token and Chat ID for runtime environment."
echo "Warning! Your existing .env file will be moved to .oldenv file."
echo -n "Press Enter to continue or Ctrl+C to quit... "
read _

echo
echo -n "Unsetting old environment variables ... "
unset ACHETA_KEY
unset ACHETA_CHAT
echo "Done!"

echo
echo -n "Enter your Telegram bot API Token and press Enter (Ctrl+C to quit): "
read NEW_KEY

echo -n "Enter your Telegram ID and press Enter (Ctrl+C to quit): "
read NEW_CHAT

echo
echo -n "Moving .env file to .oldenv ... "
if [[ -f ./.env ]]
then
    mv ./.env ./.oldenv
fi
echo "Done!"

echo -n "Creating new .env file ... "
echo "ACHETA_KEY=$NEW_KEY" > ./.env
echo "ACHETA_CHAT=$NEW_CHAT" >> ./.env
echo "Done!"

echo -n "Exporting new environment variables... "
set ACHETA_KEY=$NEW_KEY
export ACHETA_KEY
set ACHETA_CHAT=$NEW_CHAT
export ACHETA_CHAT
echo "Done!"

echo
echo "Printing your new .env file:"
echo "###"
cat ./.env
echo "###"
echo
