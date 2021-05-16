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


print('** Add missing item pages', datetime.now(tz).strftime("%I:%M %p").lstrip('0'))
res = WikiUtils.AddMissingItemWikiPages()

print('** Refreshing wiki article cache', datetime.now(tz).strftime("%I:%M %p").lstrip('0'))
WikiUtils.RefreshWikiPageCache()
WikiUtils.Initialize()
time.sleep(Config.pauseBetweenContentUpdateStepsInSec)

print('** Updating equipment and crafting pages', datetime.now(tz).strftime("%I:%M %p").lstrip('0'))
res = WikiUtils.UpdateWikiEquipmentPagesForPresetList(PresetList.itemPresetList, comment)
time.sleep(Config.pauseBetweenContentUpdateStepsInSec)

print('** Updating skills page', datetime.now(tz).strftime("%I:%M %p").lstrip('0'))
res = WikiUtils.UpdateWikiSkillsPage(comment)
time.sleep(Config.pauseBetweenContentUpdateStepsInSec)

print('** Updating NPR pages', datetime.now(tz).strftime("%I:%M %p").lstrip('0'))
res = WikiUtils.UpdateWikiNPRPages(comment)
time.sleep(Config.pauseBetweenContentUpdateStepsInSec)

print('** Updating item pages', datetime.now(tz).strftime("%I:%M %p").lstrip('0'))
res = WikiUtils.UpdateIndividualPagesForAllItems(comment)

print('** Exit', datetime.now(tz).strftime("%I:%M %p").lstrip('0'))
