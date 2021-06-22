#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import pytz
from datetime import datetime
from SFIWikiBotLib import Config
from SFIWikiBotLib import WikiUtils
from SFIWikiBotLib import DataLoader
from SFIWikiBotLib import PresetList
from SFIWikiBotLib import ItemUtils
from SFIWikiBotLib import ShipUtils
from SFIWikiBotLib import GalaxyUtils
from SFIWikiBotLib import SmallConstants

tz = pytz.timezone('America/Chicago')

site = WikiUtils.GetWikiClientSiteObject()
if not site.logged_in:
    print("Not logged in. Please check that your username ({}) and password ({}) are correct.".format(Config.botUsername, '*' * len(Config.botPassword)))
    exit(1)

comment = None


# Make sure we're working with fresh data
print('** Refreshing all cache', datetime.now(tz).strftime("%I:%M %p").lstrip('0'))
WikiUtils.RefreshWikiImageCache()
WikiUtils.RefreshWikiPageCache()
DataLoader.RefreshPublicData()
DataLoader.RefreshPrivateData()
SmallConstants.Initialize()
ItemUtils.Initialize()
ShipUtils.Initialize()
WikiUtils.Initialize()
time.sleep(Config.pauseBetweenContentUpdateStepsInSec)


print('** Upload planet images', datetime.now(tz).strftime("%I:%M %p").lstrip('0'))
WikiUtils.UploadMissingPlanetImages()

print('** Upload item images', datetime.now(tz).strftime("%I:%M %p").lstrip('0'))
WikiUtils.UploadMissingItemImages()

print('** Upload ship images', datetime.now(tz).strftime("%I:%M %p").lstrip('0'))
WikiUtils.UploadMissingShipImages()


print('** Refreshing wiki image cache', datetime.now(tz).strftime("%I:%M %p").lstrip('0'))
WikiUtils.RefreshWikiImageCache()
time.sleep(Config.pauseBetweenContentUpdateStepsInSec)
