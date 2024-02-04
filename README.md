# MASSA 🦗 Acheta

Acheta is a genus of crickets. It most notably contains the house cricket (Acheta domesticus).

"MASSA Acheta" is a service that will notify you about events occurring on your MASSA node and your wallet.\
Just like a little cricket!

>
>First of all let's define that this is not a public Telegram Bot, but opensource software that you can install on your own server to get a personal Bot that will be accessible only to you.
>

Before we jump to a detailed description of the service, please watch the video:

[![MASSA Acheta service video](https://img.youtube.com/vi/gdvuhe2iRyY/0.jpg)](https://www.youtube.com/watch?v=gdvuhe2iRyY)



## Just one command to start:

Copy the following command and paste it into your shell prompt:
```
cd ~ && bash <(wget -qO- https://raw.githubusercontent.com/dex2code/massa_acheta/main/install.sh)
```

This command will install, configure and start your Bot automatically.


> !! Please check if you have a **Telegram Bot API KEY** and you do know your own **Telegram ID** before start installation
>
> How to create a new Telegam Bot and its API KEY: https://www.youtube.com/watch?v=UQrcOj63S2o
>
> How to get your own Telegram ID value: https://www.youtube.com/watch?v=e_d3KqI6zkI


You can stop the process anywhere by pressing Ctrl+C, but before starting the installation again, run the following command to clear all changes made:
```
cd ~ && bash <(wget -qO- https://raw.githubusercontent.com/dex2code/massa_acheta/main/uninstall.sh)
```



## Update Acheta:

Acheta automatically checks for its updates, and if you receive the message “A new version of ACHETA has been released” - please update your installation.

You can do it with one command:
```
cd ~ && bash <(wget -qO- https://raw.githubusercontent.com/dex2code/massa_acheta/main/update.sh)
```

This command stops Acheta, deploys all updates ans starts Acheta again.



## Uninstall Acheta:

You can clean your system with the following command:
```
cd ~ && bash <(wget -qO- https://raw.githubusercontent.com/dex2code/massa_acheta/main/uninstall.sh)
```



## What can Acheta do:

First of all it can observe MASSA explorer and display wallets info:
> Command:
> /view_address
>


Acheta also checks for the latest published version of the MASSA and automatically notifies you if a new version is available.\
You can see the latest version with:
>
> /massa_release
>


In order for the Acheta to watch your node, you need to add it to the service configuration. To do this use the command:
>
> /add_node
>
Acheta will ask you for a node nickname (any value) and API URL to connect the node using MASSA public API.\
Use `http://127.0.0.1:33035/api/v2` if you installed Acheta on the same host with MASSA node, otherwise replace `127.0.0.1` with your real MASSA node IP address.\
!!! Please make sure if you opened TCP port 33035 on your MASSA node! Use `sudo ufw allow 33035/tcp` on Ubuntu hosts.

Once you have added a node, Acheta will try to connect to it and display its current status.\
If the node is available, Acheta will start monitoring the node and will notify you if the node's status changes (`Alive -> Dead` or `Dead -> Alive`).\
Every time the status changes, you will receive warning messages about it.
You also can display actual node info using command:
>
> /view_node
>

In order for the Acheta to watch your wallet and staking activity, you need to add it to the service configuration. To do this use the command:
>
> /add_wallet
>
Acheta will prompt you to select which node this wallet belongs to and will ask you to enter its address.
You can display current 

After adding a wallet, Acheta will try to obtain information about it from the node and display the status of this attempt.\
If the attempt was successful, Acheta begins to monitor your wallet and will send notifications about the following events:\
- Decrease wallet balance\
- Missed blocks\
- Increase candidate rolls\
- Increase active rolls\
You also can display actual wallet info using command:
>
> /view wallet
> 