# Starfighter: Infinity WikiBot

- [Introduction](#introduction)
    - [Who should be running the wiki site update scripts?](#who-should-use-this)
- [Quick Start](#quick-start)
- [Installation](#install)
    - [Requirements](#requirements)
    - [Local Install](#local-install)
    - [Configuration](#configuration)
- [Usage](#basic-usage)
- [Pages Maintained](#pages-maintained)


## Introduction

This is a bot designed to import game data from [Starfighter: Infinity](http://www.starfighterinfinity.com/) and use it to update the [Starfighter: Infinity Wiki](https://starfighter-infinity.fandom.com/wiki/).  Item pages, ship pages, planet pages, and various pages which interact with these are set up to be maintained by the bot by default. ([More complete list here.](#pages-maintained))

In addition to being able to update game information on the wiki, the bot also includes a web interface which will allow you to filter and customize the display of item and ship information.  I find this interface useful for setting up new pages for the bot to maintain, or to aid in debugging possible issues with the data being written to the wiki.

<a name="who-should-use-this"></a>
#### Who should be running the wiki site update scripts?
Please note it's not really helpful to have multiple people running the default version of the bot site update in parallel. If the wiki appears out of date and you believe running the bot can fix it please consider joining [Discord](https://discordapp.com/invite/DCnp3Vp) and coordinating with us in the #wiki-discussion channel.


## Quick Start

If you already have [Docker](https://www.docker.com/get-started) all you need to do is run these commands to launch the appropriate containers.

To launch a container running the website ui for data filtering and display:
```bash
docker run -dit -p 8080:80 mtmosier/sfiwikibot_website
```
The container will automatically download and cache the game data upon launch.  It can take a couple of minutes before it responds to requests.  After initialization is complete connect to the instance at:

```
http://localhost:8080/
```

If you instead want to update the game data stats on the live wiki, try doing:
```bash
docker run \
    -e "botUsername=exampleBotUsername" \
    -e "botPassword=abc123" \
    mtmosier/sfiwikibot_siteupdate
```
In order to get a bot username and password visit the wiki [Bot Passwords](https://starfighter-infinity.fandom.com/wiki/Special:BotPasswords) page. This container is set up to be run as a one-off.  When run it will go through a full site update and then exit out.  In my experience a site update takes about an hour and a half.

**Note: Before running the site update please think about whether you should be running it.** [(Read this)](#who-should-use-this)


## Installation
**Work in progress**

#### Requirements
Python 3.5+ is required to run the bot.

A list of external modules needed can be found in requirements.txt. These can be installed via:
```
pip3 install --trusted-host pypi.python.org -r requirements.txt
```


#### Local Install

The main portion of the code installs as a module.
```
python3 setup.py install
```


#### Configuration
**Work in progress**


## Usage
**Work in progress**


## Pages Maintained
- Individual [ship](https://starfighter-infinity.fandom.com/wiki/Starfighter) pages (Infobox and game description)
- Individual [item](https://starfighter-infinity.fandom.com/wiki/HV_Projectile) pages (Infobox and game description)
- Individual [planet](https://starfighter-infinity.fandom.com/wiki/Ferenginar) pages (Planet stats and game description)
- Individual [star system](https://starfighter-infinity.fandom.com/wiki/Alpha_Crucis) pages (Planet list)
- Individual [NPR](https://starfighter-infinity.fandom.com/wiki/Null_Dwellers) pages (Ship/Item table data)
- All [equipment list](https://starfighter-infinity.fandom.com/wiki/Category:Equipment) pages (Table data)
- The [crafting](https://starfighter-infinity.fandom.com/wiki/Crafting) page (Item table data)
- The [skills](https://starfighter-infinity.fandom.com/wiki/Skills) page (Item lists)
- The [ship navbox template](https://starfighter-infinity.fandom.com/wiki/Template:Human_Ships) pages (Human Ships, Aralien Ships, Restricted Ships, NPR Ships)
- The [Human](https://starfighter-infinity.fandom.com/wiki/Category:Human_Ships), [Aralien](https://starfighter-infinity.fandom.com/wiki/Category:Aralien_Ships) and [Restricted](https://starfighter-infinity.fandom.com/wiki/Restricted_Ships) ship list pages (Ship Listing Tables)
- The [Ships Category](https://starfighter-infinity.fandom.com/wiki/Category:Ships) page (Detailed Ship Listing)
