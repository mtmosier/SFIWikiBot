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
SmallConstants.LoadConstantInformation()
ItemUtils.Initialize()
ShipUtils.Initialize()
GalaxyUtils.Initialize()
WikiUtils.Initialize()
time.sleep(Config.pauseBetweenContentUpdateStepsInSec)

print('** Upload planet images', datetime.now(tz).strftime("%I:%M %p").lstrip('0'))
WikiUtils.UploadMissingPlanetImages()

print('** Refreshing wiki image cache', datetime.now(tz).strftime("%I:%M %p").lstrip('0'))
WikiUtils.RefreshWikiImageCache()
time.sleep(Config.pauseBetweenContentUpdateStepsInSec)

print('** Update/add planet pages', datetime.now(tz).strftime("%I:%M %p").lstrip('0'))
WikiUtils.UpdateIndividualPagesForAllPlanets(comment)
time.sleep(Config.pauseBetweenContentUpdateStepsInSec)

print('** Update star system pages', datetime.now(tz).strftime("%I:%M %p").lstrip('0'))
WikiUtils.UpdateStarSystemPages(comment)

print('** Update lore page', datetime.now(tz).strftime("%I:%M %p").lstrip('0'))
WikiUtils.UpdateLorePage(comment)

print('** Exit', datetime.now(tz).strftime("%I:%M %p").lstrip('0'))
