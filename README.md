# Starfighter: Infinity WikiBot

- [Introduction](#introduction)
    - [Who should be running the wiki site update scripts?](#who-should-use-this)
- [Quick Start (Docker)](#quick-start-docker)
- [Manual Installation](#manual-installation)
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

If you decide to go ahead with wiki site updates you will require an account on the wiki [set up with a bot password](https://starfighter-infinity.fandom.com/wiki/Special:BotPasswords).


## Quick Start (Docker)

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


<a name="manual-installation"></a>
## Manual Installation

#### Requirements
Python 3.5+ is required to run the bot.

A list of external modules needed can be found in requirements.txt. These can be installed via:
```bash
cd SFIWikiBot
pip3 install --trusted-host pypi.python.org -r requirements.txt
```


#### Library Install

The main portion of the code installs as a module.
```bash
cd SFIWikiBot
python3 setup.py install
```


#### Configuration

By default the settings file will be looked for at **/etc/sfWikiBot/settings.ini**, followed by your current working directory.  It's suggested that you take the included **settings.ini.minExample**, (or **settings.ini.example** if you prefer) edit as needed, and copy it to **/etc/sfWikiBot/settings.ini**.

Note that the **botUsername** and **botPassword** settings are only needed if performing wiki site updates. **([Learn More](#who-should-use-this))**


## Usage

#### Wiki Site Update ####

When you run the update script the latest exported game data will be downloaded from the [Ben Olding Games](http://www.benoldinggames.co.uk/) website, which will be used to update the [Starfighter: Infinity Wiki](https://starfighter-infinity.fandom.com/wiki/Starfighter:_Infinity_Wiki). **([Learn More](#who-should-use-this))**

Make sure the update script is marked as executable:
```bash
cd SFIWikiBot
chmod +x scripts/updateWikiContent.sh
```

After that just run the update script:
```bash
scripts/updateWikiContent.sh
```

The goal should be to run the update shortly after Ben exports the game data, which generally happens within a couple of hours of a new version being pushed to Steam.  

As there's no harm in running the update when there are no changes to make, it's easiest to just automate the site update using a cron entry.%$

```bash
echo "0 */6 * * * *    /path/to/SFIWikiBot/scripts/updateWikiContent.sh" >> ~/.crontab
crontab ~/.crontab
```

Executing the above (after updating the file path) will add a cron job running the Wiki update script every 6 hours.


#### Item / Ship Data Filtering Website ####

The website portion of this software is provided via [Passenger](https://www.phusionpassenger.com/).

If you do not have Passenger installed you'll need to do that first.  As there a multiple OS/Web server options I won't try to cover them all myself.  I would suggest following the ["Deploy to production"](https://www.phusionpassenger.com/docs/tutorials/deploy_to_production/) section of the Passenger documentation.




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
- The [Lore](https://starfighter-infinity.fandom.com/wiki/Lore) page (Lore for each faction listed)
