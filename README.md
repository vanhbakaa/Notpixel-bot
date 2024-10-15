## Table of Contents
- [Recommendation before use](#recommendation-before-use)
- [Features](#features)
- [Settings](#settings)
- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Obtaining API Keys](#obtaining-api-keys)
- [Installation](#installation)
- [Support](#support-this-project)
- [Contacts](#contacts)

> [!WARNING]
> ⚠️ I do my best to avoid detection of bots, but using bots is forbidden in all airdrops. i cannot guarantee that you will not be detected as a bot. Use at your own risk. I am not responsible for any consequences of using this software.


# Join the bot [here](https://t.me/notpixel/app?startapp=f6624523270)


# 🔥🔥 Use PYTHON 3.10 - 3.11.5 🔥🔥

## Features  
| Feature                                                     | Supported  |
|---------------------------------------------------------------|:----------------:|
| Multithreading                                                |        ✅        |
| Proxy binding to session                                      |        ✅        |
| Auto ref                                                      |        ✅        |
| Auto claim                                                    |        ✅        |
| Auto paint                                                    |        ✅        |
| Auto paint specific pixel to get 3x px                        |        ✅        |
| Auto task                                                     |        ✅        |
| Auto UPGRADE                                                  |        ✅        |
| Night mode                                                    |        ✅        |
| Support for pyrogram .session / Query                         |        ✅        |

## [Settings](https://github.com/vanhbakaa/Notpixel-bot/blob/main/.env-example)
| Settings | Description |
|----------------------------|:-------------------------------------------------------------------------------------------------------------:|
| **API_ID / API_HASH**      | Platform data from which to run the Telegram session (default - android)                                      |       
| **REF_LINK**               | Put your ref link here (default: my ref link)                                                                 |
| **AUTO_TASK**              |  Auto do tasks (default: True)                                                                                  |
| **AUTO_UPGRADE_PAINT_REWARD** | AUTO upgrade paint reward if possible (default: True)                                                                      |
| **AUTO_UPGRADE_RECHARGE_SPEED** | AUTO upgrade recharge speed if possible (default: True)                                                                      |
| **AUTO_UPGRADE_RECHARGE_ENERGY** | AUTO upgrade energy limit if possible (default: True)                                                                      |
| **USE_CUSTOM_TEMPLATE** | Use custom template if it's disabled global template will be used (default: True)                                                    |
| **CUSTOM_TEMPLATE_ID** | your custom template id (default: my template id)                                                                      |
| **USE_RANDOM_TEMPLATES** | Option to use random templates on catalog (default: False)                                                                      |
| **RANDOM_TEMPLATES_ID** |List of templates id (default: list of templates on catalog )                                                                      |
| **NIGHT_MODE** | Sleep time for the bot (default: True)                                                                      |
| **SLEEP_TIME** | Sleep in your timezone for the bot (default: [0, 7] 0am to 7am)                                                                     |
| **SLEEP_BETWEEN_EACH_ROUND** | Sleep time in second between each round (default: [1000, 1500])                                                                     |
| **USE_PROXY_FROM_FILE**    | Whether to use a proxy from the bot/config/proxies.txt file (True / False)                                    |


## Quick Start

To install libraries and run bot - open run.bat on Windows

## Prerequisites
Before you begin, make sure you have the following installed:
- [Python](https://www.python.org/downloads/) **IMPORTANT**: Make sure to use **Python 3.10 - 3.11.5**. 

## Obtaining API Keys
1. Go to my.telegram.org and log in using your phone number.
2. Select "API development tools" and fill out the form to register a new application.
3. Record the API_ID and API_HASH provided after registering your application in the .env file.

## Installation
You can download the [**repository**](https://github.com/vanhbakaa/Notpixel-bot) by cloning it to your system and installing the necessary dependencies:
```shell
git clone https://github.com/vanhbakaa/Notpixel-bot.git
cd Notpixel-bot
```

Then you can do automatic installation by typing:

Windows:
```shell
run.bat
```

Linux:
```shell
run.sh
```

# Linux manual installation
```shell
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env  # Here you must specify your API_ID and API_HASH, the rest is taken by default
python3 main.py
```

You can also use arguments for quick start, for example:
```shell
~/Notpixel-bot >>> python3 main.py --action (1/2)
# Or
~/Notpixel-bot >>> python3 main.py -a (1/2)

# 1 - Run clicker
# 2 - Creates a session
```

# Windows manual installation
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env-example .env
# Here you must specify your API_ID and API_HASH, the rest is taken by default
python main.py
```
You can also use arguments for quick start, for example:
```shell
~/Notpixel-bot >>> python3 main.py --action (1/2)
# Or
~/Notpixel-bot >>> python3 main.py -a (1/2)

# 1 - Run clicker
# 2 - Creates a session
```

# Termux manual installation
```
> pkg update && pkg upgrade -y
> pkg install python rust git -y
> git clone https://github.com/vanhbakaa/Notpixel-bot.git
> cd Notpixel-bot
> cp .env-example .env
> nano .env
# edit your api_id and api_hash
> pip install -r requirements.txt
> python main.py
```

You can also use arguments for quick start, for example:
```termux
~/Notpixel-bot > python main.py --action (1/2)
# Or
~/Notpixel-bot > python main.py -a (1/2)

# 1 - Run clicker
# 2 - Creates a session 
```
# Support This Project

If you'd like to support the development of this project, please consider making a donation. Every little bit helps!

👉 **[Click here to view donation options](https://github.com/vanhbakaa/Donation/blob/main/README.md)** 👈

Your support allows us to keep improving the project and bring more features!

Thank you for your generosity! 🙌

### Contacts

For support or questions, you can contact me [![Static Badge](https://img.shields.io/badge/Telegram-Channel-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/airdrop_tool_vanh)
