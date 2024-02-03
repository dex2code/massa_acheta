#!/usr/bin/env bash


echo -n "Enter your Telegram bot API Token and press Enter (Ctrl+C to quit): "
read NEW_KEY

echo -n "Enter your own Telegram ID and press Enter (Ctrl+C to quit): "
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
chmod 640 ./.env
echo "Done!"

echo
echo "Printing your new .env file:"
echo "###"
cat ./.env
echo "###"
