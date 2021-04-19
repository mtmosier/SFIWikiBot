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
WikiUtils.Initialize()
time.sleep(Config.pauseBetweenContentUpdateStepsInSec)

print('** Upload ship images', datetime.now(tz).strftime("%I:%M %p").lstrip('0'))
WikiUtils.UploadMissingShipImages()

print('** Refreshing wiki image cache', datetime.now(tz).strftime("%I:%M %p").lstrip('0'))
WikiUtils.RefreshWikiImageCache()
time.sleep(Config.pauseBetweenContentUpdateStepsInSec)

print('** Add missing ship pages', datetime.now(tz).strftime("%I:%M %p").lstrip('0'))
res = WikiUtils.AddMissingShipWikiPages()
WikiUtils.RefreshWikiPageCache()
WikiUtils.Initialize()
time.sleep(Config.pauseBetweenContentUpdateStepsInSec)

print('** Updating ships category page', datetime.now(tz).strftime("%I:%M %p").lstrip('0'))
res = WikiUtils.UpdateWikiShipDetailedListPagesForPresetList([ PresetList.shipPresetList['Category:Ships'] ], comment)
time.sleep(Config.pauseBetweenContentUpdateStepsInSec)

print('** Updating human/aralien/restricted ship category pages', datetime.now(tz).strftime("%I:%M %p").lstrip('0'))
res = WikiUtils.UpdateAllWikiMainShipPages(comment)
time.sleep(Config.pauseBetweenContentUpdateStepsInSec)

print('** Updating ship navboxes', datetime.now(tz).strftime("%I:%M %p").lstrip('0'))
res = WikiUtils.UpdateWikiShipNavboxTemplates(comment)
time.sleep(Config.pauseBetweenContentUpdateStepsInSec)

print('** Updating individual ship pages', datetime.now(tz).strftime("%I:%M %p").lstrip('0'))
res = WikiUtils.UpdateIndividualPagesForAllShips(comment)

print('** Exit', datetime.now(tz).strftime("%I:%M %p").lstrip('0'))
