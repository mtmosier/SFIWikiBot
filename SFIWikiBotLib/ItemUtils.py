#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import json
import os
import html
import re
import decimal
import math
from collections import OrderedDict
from contextlib import suppress
import requests
from SFIWikiBotLib import Config
from SFIWikiBotLib import SmallConstants
from SFIWikiBotLib import GeneralUtils
from SFIWikiBotLib import WikiUtils
from SFIWikiBotLib import GalaxyUtils
from SFIWikiBotLib import DataLoader


itemPurchasePriceModifier = 1.175
# itemPurchasePriceModifier = 1.17645   # I believe this is the correct value but need to re-test to be sure
ammoCostModifier = 0.144



itemsToSkip = [
    "Disheartener Beacon",
    "Double Barrelled Heavy Bolt I",
    "Double Barrelled Heavy Bolt II",
    "Double Barrelled Heavy Bolt III",
    "Double Barrelled Heavy Bolt IV",
    "Double Barrelled Heavy Bolt V",
    "Wabbajack",
    "Big Smoke Screen",
    "Firework Pellet",
    "Cake Slice",
    "Candle Torpedo",
    "Micro Gate TBZ",
    "Tyraan Decay Cannon",
    "Shard Torpedo",
    "Igni Rock Rocket I",
]
itemIdListToSkip = []

beamWeaponOverrideList = [
    'Resonator Beam'
]
beamWeaponOverrideIdList = []

rarePlayerRaceDropList = [
    'Dimensional Clone Bomb',
    'Crate of Meat Patties',
    'Promotional Burger',
]
rarePlayerRaceDropIdList = []


itemData = None
itemDataDict = None
itemRangeData = None
itemVariantData = None
itemCraftableData = None

itemDataPublic = None
itemDataPrivate = None

itemBaseNameList = []


class ItemPageIter:
    """Iterator that takes an item list and groups it by item set."""

    def __init__(self, itemList=...):
        if itemList is ...:
            itemList = itemData
        itemList = itemList.copy()

        self.itemPageList = []
        self.pos = 0

        while len(itemList) > 0:
            curItemList = GetAllItemsSharingItemRange(itemList[-1], itemList)
            curItemList = sorted(curItemList, key=GetItemSortFunc())
            self.itemPageList.append(curItemList)

            for i in curItemList:
                if i in itemList:  itemList.remove(i)

    def __iter__(self):
        return self

    def __len__(self):
        return len(self.itemPageList)

    def __next__(self):
        idx = self.pos
        if idx >= len(self.itemPageList):
            raise StopIteration
        self.pos += 1
        return self.itemPageList[idx]

    def reset(self):
        self.pos = 0


def FindAllObjectsRelatedToId(id):
    ruleSet = {
        'condition': 'OR',
        'rules': [
            { 'id': 'id', 'operator': '==', 'value': id, },
            { 'id': 'range', 'operator': '==', 'value': id, },
            { 'id': 'items', 'operator': 'in_list', 'value': id, },
            { 'id': 'subWeaponID', 'operator': '==', 'value': id, },
        ]
    }

    rtnList = GeneralUtils.SearchObjectListUsingRuleset(itemData, ruleSet)
    rtnList += GeneralUtils.SearchObjectListUsingRuleset(itemRangeData.values(), ruleSet)
    rtnList += GeneralUtils.SearchObjectListUsingRuleset(itemVariantData, ruleSet)
    rtnList += GeneralUtils.SearchObjectListUsingRuleset(itemCraftableData.values(), ruleSet)

    return rtnList


def GetListOfItemsMissingWikiPages(includeHidden=False):
    if includeHidden:
        return [ v for v in itemData if not GetItemWikiArticlePage(v) and v['type'] > 1 ]
    else:
        return [ v for v in itemData if not GetItemWikiArticlePage(v) and v['type'] > 1 and not IsItemHidden(v) ]


def FindItemsByPartialName(name, objList=...):
    if objList is ...:
        objList = itemData
    ruleSet = { "condition": "OR", "rules": [ { "id": "name", "operator": "contains", "value": name } ] }
    return sorted(GeneralUtils.SearchObjectListUsingRuleset(objList, ruleSet), key=GetItemSortFunc())


def GetItemsByRaceName(name, objList=...):
    if objList is ...:
        objList = itemData
    ruleSet = { "condition": "OR", "rules": [ { "id": "ItemUtils.GetRaceForItem", "operator": "equal", "value": name } ] }
    return GeneralUtils.SearchObjectListUsingRuleset(objList, ruleSet)


def DownloadMissingImagesForTheWikiByItemList(itemList):
    rtnVal = 0
    for item in itemList:
        wikiImage = GetItemWikiImage(item)
        if not wikiImage:
            if DownloadImageForItem(item):
                rtnVal += 1

    return rtnVal


def DownloadImagesByItemList(itemList):
    rtnVal = 0
    for item in itemList:
        if DownloadImageForItem(item):
            rtnVal += 1

    return rtnVal


def DownloadImageForItem(item):
    rtnVal = False

    itemType = SmallConstants.typeLookup[item['type']].replace('_WEAPON', '').title()
    iconName = item['id']
    if 'iconName' in item and item['iconName']:
        iconName = item['iconName']

    filedir = os.path.join('public', 'images', itemType)
    os.makedirs(filedir, exist_ok=True)

    filepath = os.path.join(filedir, "{}.png".format(iconName))
    if not os.path.exists(filepath):
        try:
            url = GetItemImageUrl(item)
            r = requests.get(url)
            if r.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(r.content)
                    if Config.verbose >= 1:  print(item['name'], "- Image saved successfully")
                    rtnVal = True
            else:
                if Config.verbose >= 1:  print("Image not found for item", item['name'])
        except:
            print("{} - failed to save the image\nUrl: [{}]\nLocal path [{}]\n\n".format(item['name'], url, filepath))
            raise

    return rtnVal


def UploadImagesToWikiForItemList(itemList):
    itemImageInfoList = [ GetImageUploadDownloadInfoForItem(i) for i in itemList ]
    return WikiUtils.UploadImageListToWiki(itemImageInfoList)


def GetDisplayDataForItemList(itemList, headingList):
    tableData = []

    for item in itemList:
        row = OrderedDict()
        for heading in headingList:
            row[heading] = GetHtmlStatDisplayForObject(heading, item)
        tableData.append(row)

    return tableData


def GetWikiDisplayDataForItemList(itemList, headingList):
    tableData = []

    for item in itemList:
        row = OrderedDict()
        for heading in headingList:
            row[heading] = GetStatDisplayForObject(heading, item)
        tableData.append(row)

    return tableData


def GetStatNameDescriptions(statList, pageType=''):
    descList = []

    for statName in statList:
        descList.append(GetDescriptionForItemStatName(statName, pageType))

    return descList



def GetItemPageContentForItemRangeList(itemList, existingPageValues={}):
    if not itemList:
        return ''

    pageHeader = '__NOTOC__\n'
    pageFooter = '\n{{Template:Equipment}}\n[[Category:Items]]\n'

    primaryItem = itemList[-1]
    nameInfo = SplitNameIntoBaseNameAndItemLevel(primaryItem['name'])

    itemCatList = GetCategoryListForItem(primaryItem)
    for catName in itemCatList:
        pageFooter += '[[Category:{}]]\n'.format(catName)

    source = GetItemSource(primaryItem)
    sourceClass = GetItemSourceClassName(primaryItem)
    if source is not None and sourceClass:
        source = '<span class="{}">{}</span>'.format(sourceClass, source)

    if sourceClass:
        name = '<span class="{}">{}</span>'.format(sourceClass, nameInfo['fullNameMinusLevel'])
    else:
        name = nameInfo['fullNameMinusLevel']


    infoBox = GetWikiInfoboxDataForItemRangeList(itemList)

    itemTemplateData = OrderedDict()

    itemTemplateData["itemname"] = name
    itemTemplateData["methodOfObtaining"] = source
    itemTemplateData["itemSlot"] = ItemDisplayStatItemType(primaryItem, 'itemPage')
    itemTemplateData["description"] = ''
    itemTemplateData["gameDescription"] = "\n\n".join(GetDescriptionForItemRangeList(itemList, "''"))
    itemTemplateData["functionality"] = ''
    itemTemplateData["interactionsAndStrategy"] = ''
    itemTemplateData["trivia"] = ''
    itemTemplateData.update(existingPageValues)

    content = pageHeader
    content += WikiUtils.ConvertDictionaryToWikiTemplate(infoBox['name'], infoBox['data'])
    content += WikiUtils.ConvertDictionaryToWikiTemplate('ItemFormat', itemTemplateData)
    content += pageFooter

    return content


def GetWikiInfoboxDataForItemRangeList(itemList):
    if not itemList:
        return {"Name": None, "data": None}

    itemType = SmallConstants.typeLookup[itemList[-1]['type']].replace('_', ' ').title()

    if itemType == "Mineral":
        return {"Name": None, "data": None}


    rtnVal = {
        "name": "Infobox_{}".format(itemType.replace(' ', '')),
        "data": None,
    }

    if itemType == "Primary Weapon":
        rtnVal['data'] = GetWikiInfoboxDataForPrimaryOrSecondary(itemList)
    elif itemType == "Secondary Weapon":
        rtnVal['data'] = GetWikiInfoboxDataForPrimaryOrSecondary(itemList)
    elif itemType == "Engine":
        rtnVal['data'] = GetWikiInfoboxDataForEngine(itemList)
    elif itemType == "Shield":
        rtnVal['data'] = GetWikiInfoboxDataForShield(itemList)
    elif itemType == "Augmentation":
        rtnVal['data'] = GetWikiInfoboxDataForAugmentation(itemList)
    elif itemType == "Collectible":
        rtnVal['data'] = GetWikiInfoboxDataForCollectible(itemList)

    return rtnVal


def GetWikiInfoboxDataForPrimaryOrSecondary(itemList):
    # Template name is Infobox_PrimaryWeapon, Infobox_SecondaryWeapon

    primaryItem = itemList[-1]
    infobox = OrderedDict()
    damageType = GetItemDamageType(primaryItem)

    isBeam = IsBeamWeapon(primaryItem)
    weaponType = SmallConstants.weaponTypeLookup[primaryItem['weaponType']].title()

    splitItemName = SplitNameIntoBaseNameAndItemLevel(primaryItem['name'])

    source = GetItemSourceExtended(primaryItem, True)
    sourceClass = GetItemSourceClassName(primaryItem)
    if source is not None:
        if sourceClass:
            infobox['source'] = '<span class="{}">{}</span>'.format(sourceClass, source)
        else:
            infobox['source'] = source

    if sourceClass:
        infobox['title1'] = '<span class="{}">{}</span>'.format(sourceClass, splitItemName['fullNameMinusLevel'])
    else:
        infobox['title1'] = splitItemName['fullNameMinusLevel']

    image = GetItemWikiImage(primaryItem)
    if image:
        infobox['image1'] = image

    infobox['weapon_type'] = ItemDisplayStatItemType(primaryItem)

    vdata = [ GetItemSkillLevel(i) for i in itemList ]
    displayData = str(vdata[0]) if len(set(vdata)) == 1 else " / ".join([str(x) for x in vdata])
    if displayData != '999':
        infobox['required_skill'] = "{} {}".format(GetItemSkillName(primaryItem), displayData)


    # vdata = [ ItemDisplayStatDamage(i, False, False) for i in itemList ]
    # if vdata[0] is not None and str(vdata[0]) != '0':
    #     displayData = vdata[0] if len(set(vdata)) == 1 else " / ".join(vdata)
    #     infobox['damage_per_round'] = displayData

    if not DisplayDamageAsPerHit(primaryItem):
        vdata = [ GeneralUtils.NumDisplay(GetDamagePerRoundForItem(i), 1) for i in itemList ]
        if vdata[0] != '0':
            if DisplayDamageAsPerSecond(primaryItem):
                vdata = [ '{}/s'.format(i) for i in vdata ]
            displayData = vdata[0] if len(set(vdata)) == 1 else " / ".join(vdata)
            infobox['damage_per_round'] = '{} {}'.format(displayData, GetDamageTypeIconForItem(primaryItem)).strip()
    else:
        vdata = [ GeneralUtils.NumDisplay(GetDamagePerRoundForItem(i), 1) for i in itemList ]
        if vdata[0] != '0':
            vdata = [ '{}/hit'.format(i) for i in vdata ]
            displayData = vdata[0] if len(set(vdata)) == 1 else " / ".join(vdata)
            infobox['damage_per_hit'] = '{} {}'.format(displayData, GetDamageTypeIconForItem(primaryItem)).strip()

        with suppress(ZeroDivisionError, TypeError):
            vdata = [ GeneralUtils.NumDisplay(GetItemTotalHitCount(i) / GetItemLife(i), 1) for i in itemList ]
            if vdata[0] != '0':
                displayData = vdata[0] if len(set(vdata)) == 1 else " / ".join(vdata)
                infobox['hits_per_second'] = displayData

    with suppress(ZeroDivisionError):
        if weaponType != 'Large':
            vdata = [ GeneralUtils.NumDisplay(i['fireRate'], 1) for i in itemList ]

            aboveOne = 0
            for d in set(vdata):
                aboveOne += 1 if decimal.Decimal(d) >= 1 else 0

            overallUseShotsPerSecond = False
            if aboveOne < len(set(vdata)) - aboveOne:
                overallUseShotsPerSecond = True
                vdata = [ GeneralUtils.NumDisplay(1 / i['fireRate'], 1) for i in itemList ]

            displayData = str(vdata[0]) if len(set(vdata)) == 1 else " / ".join(vdata)
            if displayData != '0':
                if overallUseShotsPerSecond:
                    infobox['fire_rate'] = "{} per sec".format(displayData)
                else:
                    displayData = str(vdata[0]) if len(set(vdata)) == 1 else " / ".join(vdata)
                    infobox['fire_rate'] = "1 per {} sec".format(displayData)

    if 'damage_per_round' in infobox:
        vdata = [ GetNumOfDamagingProjectiles(i, True) for i in itemList ]
        if vdata[-1] > 1:
            displayData = vdata[0] if len(set(vdata)) == 1 else " / ".join([str(v) for v in vdata])
            infobox['amount'] = displayData

    if not DisplayDamageAsPerSecond(primaryItem) or 'damage_per_round' not in infobox:
        vdata = [ ItemDisplayStatTotalDps(i, ..., False) for i in itemList ]
        if vdata[0] is not None:
            displayData = vdata[0] if len(set(vdata)) == 1 else " / ".join(vdata)
            if displayData != '0':
                # if GeneralUtils.floatCmp(GetDamagePerRoundForItem(primaryItem), '>', 0):
                #     displayData = '{} {}'.format(displayData, GetDamageTypeIconForItem(primaryItem)).strip()
                # if GeneralUtils.floatCmp(GetItemEffectDamage(primaryItem), '>', 0):
                #     displayData = '{} {}'.format(displayData, GetEffectIconForItem(primaryItem)).strip()
                infobox['damage_per_second'] = displayData

    damageType = GetDamageTypeForItem(primaryItem)
    if damageType:
        damageTypeCat = GetDamageTypeForItem(primaryItem, True)
        if damageTypeCat:
            infobox['damage_type'] = "[[:Category:Damage:{}|{}]]".format(damageTypeCat, damageType)
        else:
            infobox['damage_type'] = damageType


    vdata = [ ItemDisplayStatTotalDamagePerVolley(i, ..., False) for i in itemList ]
    if vdata[0] is not None and vdata[0] != '0':
        displayData = vdata[0] if len(set(vdata)) == 1 else " / ".join(vdata)
        # if GeneralUtils.floatCmp(GetDamagePerRoundForItem(primaryItem), '>', 0):
        #     displayData = '{} {}'.format(displayData, GetDamageTypeIconForItem(primaryItem)).strip()
        # if GeneralUtils.floatCmp(GetItemEffectDamage(primaryItem), '>', 0):
        #     displayData = '{} {}'.format(displayData, GetEffectIconForItem(primaryItem)).strip()
        if 'damage_per_round' not in infobox or infobox['damage_per_round'] != displayData:
            infobox['total_damage_per_volley'] = displayData

    if primaryItem['energyBased']:
        vdata = [ ItemDisplayStatTotalDpe(i) for i in itemList ]
        if vdata[0] is not None:
            displayData = vdata[0] if len(set(vdata)) == 1 else " / ".join(vdata)
            infobox['damage_per_energy'] = displayData


    if primaryItem['energyBased']:
        vdata = [ GeneralUtils.NumDisplay(i['ammoOrEnergyUsage'], 2) for i in itemList ]
        if vdata[0] != '0':
            displayData = vdata[0] if len(set(vdata)) == 1 else " / ".join(vdata)
            infobox['energy_usage'] = displayData
    else:
        vdata = [ i['ammoOrEnergyUsage'] for i in itemList ]
        if GeneralUtils.floatCmp(vdata[0], '>', 0):
            if weaponType == 'Large':
                displayData = GeneralUtils.NumDisplay(vdata[0], 0) if len(set(vdata)) == 1 else " / ".join([GeneralUtils.NumDisplay(x, 0) for x in vdata])
            else:
                displayData = "{} ({})".format(GeneralUtils.NumDisplay(vdata[0], 0), GeneralUtils.NumDisplay(vdata[0] * 5, 0)) if len(set(vdata)) == 1 else " / ".join(["{} ({})".format(GeneralUtils.NumDisplay(x, 0), GeneralUtils.NumDisplay(x * 5, 0)) for x in vdata])
            infobox['ammo'] = displayData

        vdata = [ (GeneralUtils.NumDisplay(GetItemAmmoCost(i), 0, True) if GetItemAmmoCost(i) > 0 else None) for i in itemList ]
        if vdata[0] is not None:
            displayData = vdata[0] if len(set(vdata)) == 1 else " / ".join(vdata)
            infobox['ammo_cost'] = displayData


    if primaryItem['guidance'] == 1 or primaryItem['guidance'] == 5:
        infobox['requires_lock'] = 'Yes'

        vdata = [ GeneralUtils.NumDisplay(i['lockingRange'], 1) for i in itemList ]
        displayData = vdata[0] if len(set(vdata)) == 1 else " / ".join(vdata)
        infobox['locking_range'] = '{}su'.format(displayData)
    else:
        infobox['requires_lock'] = 'No'


    if 'locking_range' not in infobox:
        vdata = [ GeneralUtils.NumDisplay(GetItemRange(i), 0) for i in itemList ]
        displayData = vdata[0] if len(set(vdata)) == 1 else " / ".join(vdata)
        if displayData and displayData != '0':
            infobox['range'] = '{}su'.format(displayData)


    if primaryItem['guidance'] != 3:
        vdata = [ GeneralUtils.NumDisplay(GetItemMinRange(i), 1) for i in itemList ]
        displayData = vdata[0] if len(set(vdata)) == 1 else " / ".join(vdata)
        if displayData:
            infobox['min_range'] = '{}su'.format(displayData)


    if not isBeam and 'Vortex Bomb' not in primaryItem['name']:
        vdata = [ GeneralUtils.NumDisplay(GetItemMaxSpeed(i), 1) for i in itemList ]
        if vdata[0] != '0' and vdata[0] != '':
            displayData = str(vdata[0]) if len(set(vdata)) == 1 else " / ".join(vdata)
            infobox['speed'] = "{}su/s".format(displayData)


    if 'speed' in infobox:
        vdata = [ GeneralUtils.NumDisplay(GetItemInitialSpeed(i), 1) for i in itemList ]
        if vdata[0] != '0' and vdata[0] != '':
            displayData = str(vdata[0]) if len(set(vdata)) == 1 else " / ".join(vdata)
            initialSpeedDisplay = "{}su/s".format(displayData)
            if initialSpeedDisplay != infobox['speed']:
                infobox['initial_speed'] = initialSpeedDisplay


    if 'initial_speed' in infobox and GeneralUtils.floatCmp(primaryItem['acceleration'], '>', 0):
        vdata = [ GeneralUtils.NumDisplay(i['acceleration'], 2) for i in itemList ]
        if vdata[0] != '0' and vdata[0] != '':
            displayData = str(vdata[0]) if len(set(vdata)) == 1 else " / ".join(vdata)
            infobox['acceleration'] = "{}su/s/s".format(displayData)


    largeWeaponsWithLifetimeList = ['Thunderbomb', 'Tornadian Hurricane', 'Radicane', 'Firestorm', 'Vortex Bomb', 'Ultra Vortex Bomb', 'Anti Vortex Bomb', 'Ghostly Vortex Bomb']
    if not isBeam and (weaponType != 'Large' or primaryItem['name'] in largeWeaponsWithLifetimeList):
        if 'Vortex Bomb' in primaryItem['name']:
            vdata = [ GeneralUtils.NumDisplay(i['effectTime'], 1) for i in itemList ]
        else:
            vdata = [ GeneralUtils.NumDisplay(GetItemLife(i), 1) for i in itemList ]
        if vdata[0] != '0':
            displayData = str(vdata[0]) if len(set(vdata)) == 1 else "s / ".join(vdata)
            infobox['lifetime'] = "{}s".format(displayData)


    if not isBeam and weaponType != 'Mine' and weaponType != 'Proximity':
        vdata = [ GeneralUtils.NumDisplay(i['accuracy'], 1) for i in itemList ]
        displayData = vdata[0] if len(set(vdata)) == 1 else "° / ".join(vdata)
        if weaponType in ['Secondary', 'Primary'] or displayData != '0':
            infobox['accuracy'] = "{}°".format(displayData)



    vdata = [ GeneralUtils.NumDisplay(i['turning'] * Config.turnMultiplier, 1) for i in itemList ]
    if vdata[0] != '0':
        displayData = vdata[0] if len(set(vdata)) == 1 else "° / ".join(vdata)
        infobox['turning'] = "{}°".format(displayData)


    armIsNotLifeExceptionList = ['Thunderbomb', 'Tornadian Hurricane']
    if weaponType == 'Large' and primaryItem['name'] not in armIsNotLifeExceptionList:
        vdata = [ GeneralUtils.NumDisplay(GetItemLife(i), 1) for i in itemList ]
    else:
        vdata = [ GeneralUtils.NumDisplay(i['armingTime'], 1) for i in itemList ]
    displayData = vdata[0] if len(set(vdata)) == 1 else "s / ".join(vdata)
    if displayData != '0':
        infobox['arming_time'] = "{}s".format(displayData)


    effectList = GetEffectNameListForItem(primaryItem)
    if effectList:
        infobox['effect'] = ''
        for effectName in effectList:
            infobox['effect'] += '[[:Category:Effect:{}|{}]]<br>\n'.format(effectName, effectName)


    if 'effect' in infobox and primaryItem['effectTime'] >= 0:
        if len(effectList) > 1 or effectList[0] != 'Negative Impact' or primaryItem['effectTime'] > 0:
            vdata = [ GeneralUtils.NumDisplay(i['effectTime'], 1) for i in itemList ]
            displayData = vdata[0] if len(set(vdata)) == 1 else "s / ".join(vdata)
            infobox['effect_time'] = "{}s".format(displayData)


    vdata = [ ItemDisplayStatBPLocation(i) for i in itemList ]
    if vdata[0]:
        displayData = vdata[0] if len(set(vdata)) == 1 else "<br>\n".join(vdata)
        infobox['blueprint_location'] = displayData


    return infobox



def GetWikiInfoboxDataForEngine(itemList):
    # Template name is Infobox_Engine

    primaryItem = itemList[-1]
    infobox = OrderedDict()


    splitItemName = SplitNameIntoBaseNameAndItemLevel(primaryItem['name'])

    source = GetItemSourceExtended(primaryItem, True)
    sourceClass = GetItemSourceClassName(primaryItem)
    if source is not None:
        if sourceClass:
            infobox['source'] = '<span class="{}">{}</span>'.format(sourceClass, source)
        else:
            infobox['source'] = source

    if sourceClass:
        infobox['title1'] = '<span class="{}">{}</span>'.format(sourceClass, splitItemName['fullNameMinusLevel'])
    else:
        infobox['title1'] = splitItemName['fullNameMinusLevel']

    image = GetItemWikiImage(primaryItem)
    if image:
        infobox['image1'] = image

    vdata = [ GetItemSkillLevel(i) for i in itemList ]
    displayData = str(vdata[0]) if len(set(vdata)) == 1 else " / ".join([str(x) for x in vdata])
    if displayData != '999':
        infobox['required_skill'] = "{} {}".format(GetItemSkillName(primaryItem), displayData)

    vdata = [ GeneralUtils.NumDisplay(i['maxSpeedMod'], 3) for i in itemList ]
    displayData = vdata[0] if len(set(vdata)) == 1 else "x / ".join(vdata)
    if displayData != '0':
        infobox['speed'] = "{}x".format(displayData)

    vdata = [ GeneralUtils.NumDisplay(i['reverseSpeedMod'], 3) for i in itemList ]
    displayData = vdata[0] if len(set(vdata)) == 1 else "x / ".join(vdata)
    if displayData != '0':
        infobox['reverse'] = "{}x".format(displayData)

    vdata = [ GeneralUtils.NumDisplay(i['accelMod'], 3) for i in itemList ]
    displayData = vdata[0] if len(set(vdata)) == 1 else "x / ".join(vdata)
    if displayData != '0':
        infobox['acceleration'] = "{}x".format(displayData)

    vdata = [ GeneralUtils.NumDisplay(i['turningMod'], 3) for i in itemList ]
    displayData = vdata[0] if len(set(vdata)) == 1 else "x / ".join(vdata)
    if displayData != '0':
        infobox['turning'] = "{}x".format(displayData)

    vdata = [ GeneralUtils.NumDisplay(i['propulsionEnhance'], 3) for i in itemList ]
    displayData = vdata[0] if len(set(vdata)) == 1 else "x / ".join(vdata)
    infobox['propulsion'] = "{}x".format(displayData)

    with suppress(KeyError):
        vdata = [ GeneralUtils.NumDisplay(i['propulsionEnhanceTime'], 3) for i in itemList ]
        displayData = vdata[0] if len(set(vdata)) == 1 else "s / ".join(vdata)
        if displayData != '0':
            infobox['boost_duration'] = "{}s".format(displayData)

    with suppress(KeyError):
        vdata = [ GeneralUtils.NumDisplay(i['propulsionEnhanceCooldown'] * i['propulsionEnhanceTime'], 2) for i in itemList ]
        displayData = vdata[0] if len(set(vdata)) == 1 else "s / ".join(vdata)
        if displayData != '0':
            infobox['boost_cooldown'] = "{}s".format(displayData)
        if infobox['boost_cooldown'] == infobox['boost_duration']:
            del infobox['boost_cooldown']

    vdata = [ GeneralUtils.NumDisplay(i['autoPilotSpeedInc'], 3) for i in itemList ]
    displayData = vdata[0] if len(set(vdata)) == 1 else " / +".join(vdata)
    if displayData != '0':
        infobox['autopilot'] = "+{}".format(displayData)

    vdata = [ ItemDisplayStatBPLocation(i) for i in itemList ]
    if vdata[0]:
        displayData = vdata[0] if len(set(vdata)) == 1 else "<br>\n".join(vdata)
        infobox['blueprint_location'] = displayData

    return infobox



def GetWikiInfoboxDataForShield(itemList):
    # Template name is Infobox_Shield

    primaryItem = itemList[-1]
    infobox = OrderedDict()


    splitItemName = SplitNameIntoBaseNameAndItemLevel(primaryItem['name'])

    source = GetItemSourceExtended(primaryItem, True)
    sourceClass = GetItemSourceClassName(primaryItem)
    if source is not None:
        if sourceClass:
            infobox['source'] = '<span class="{}">{}</span>'.format(sourceClass, source)
        else:
            infobox['source'] = source

    if sourceClass:
        infobox['title1'] = '<span class="{}">{}</span>'.format(sourceClass, splitItemName['fullNameMinusLevel'])
    else:
        infobox['title1'] = splitItemName['fullNameMinusLevel']

    image = GetItemWikiImage(primaryItem)
    if image:
        infobox['image1'] = image

    effectIcons = GetShieldEffectIconsForItem(primaryItem, "positive")
    if effectIcons:
        effectIcons += '&nbsp;&nbsp;'
    effectIcons += GetShieldEffectIconsForItem(primaryItem, "negative")
    if effectIcons:
        infobox['effect_icons'] = effectIcons

    vdata = [ GetItemSkillLevel(i) for i in itemList ]
    displayData = str(vdata[0]) if len(set(vdata)) == 1 else " / ".join([str(x) for x in vdata])
    if displayData != '999':
        infobox['required_skill'] = "{} {}".format(GetItemSkillName(primaryItem), displayData)


    vdata = [ GeneralUtils.NumDisplay(i['maxModifier'], 3) for i in itemList ]
    displayData = vdata[0] if len(set(vdata)) == 1 else "x / ".join(vdata)
    if displayData != '0':
        infobox['maximum_charge'] = "{}x".format(displayData)

    vdata = [ GeneralUtils.NumDisplay(i['chargeModifier'], 3) for i in itemList ]
    displayData = vdata[0] if len(set(vdata)) == 1 else "x / ".join(vdata)
    if displayData != '0':
        infobox['recharge_rate'] = "{}x".format(displayData)

    vdata = [ GeneralUtils.NumDisplay(i['chargeDelay'], 3) for i in itemList ]
    displayData = vdata[0] if len(set(vdata)) == 1 else "s / ".join(vdata)
    infobox['recharge_delay'] = "{}s".format(displayData)


    effectList = GetEffectNameListForItem(primaryItem)
    if effectList:
        vdata = [ GeneralUtils.NumDisplay(i['effectAmount'] * 100, 0) for i in itemList ]
        displayData = vdata[0] if len(set(vdata)) == 1 else "% / ".join(vdata)
        if displayData != '0':
            if len(effectList) > 1:
                infobox['effect'] = ''
                for effectName in effectList:
                    infobox['effect'] += '[[:Category:{}|{}]]<br>\n'.format(effectName, effectName)
                infobox['effect'] += '{}%'.format(displayData)
            else:
                infobox['effect'] = "[[:Category:{0}|{0}]] {1}%".format(effectList[0], displayData)


    with suppress(KeyError):
        if primaryItem['resistExtraEffect'] >= 0:
            infobox['additional_resistance'] = "[[:Category:{0}|{0}]]".format(SmallConstants.effectsData[primaryItem['resistExtraEffect']]['name'])

    vdata = [ ItemDisplayStatBPLocation(i) for i in itemList ]
    if vdata[0]:
        displayData = vdata[0] if len(set(vdata)) == 1 else "<br>\n".join(vdata)
        infobox['blueprint_location'] = displayData

    return infobox


def GetWikiInfoboxDataForAugmentation(itemList):
    # Template name is Infobox_Augmentation

    primaryItem = itemList[-1]
    infobox = OrderedDict()


    splitItemName = SplitNameIntoBaseNameAndItemLevel(primaryItem['name'])

    source = GetItemSourceExtended(primaryItem, True)
    sourceClass = GetItemSourceClassName(primaryItem)
    if source is not None:
        if sourceClass:
            infobox['source'] = '<span class="{}">{}</span>'.format(sourceClass, source)
        else:
            infobox['source'] = source

    if sourceClass:
        infobox['title1'] = '<span class="{}">{}</span>'.format(sourceClass, splitItemName['fullNameMinusLevel'])
    else:
        infobox['title1'] = splitItemName['fullNameMinusLevel']

    image = GetItemWikiImage(primaryItem)
    if image:
        infobox['image1'] = image

    vdata = [ GetItemSkillLevel(i) for i in itemList ]
    displayData = str(vdata[0]) if len(set(vdata)) == 1 else " / ".join([str(x) for x in vdata])
    if displayData != '999':
        infobox['required_skill'] = "{} {}".format(GetItemSkillName(primaryItem), displayData)


    effectList = GetEffectNameListForItem(primaryItem)
    if effectList:
        infobox['effect'] = ''
        for effectName in effectList:
            infobox['effect'] += '[[:Category:Effect:{}|{}]]<br>\n'.format(effectName, effectName)

    try:
        if 'effect' in infobox and primaryItem['effectTime'] >= 0:
            vdata = [ GeneralUtils.NumDisplay(i['effectTime'], 1) for i in itemList ]
            displayData = vdata[0] if len(set(vdata)) == 1 else "s / ".join(vdata)
            infobox['effect_time'] = "{}s".format(displayData)
    except:
        pass

    vdata = [ ItemDisplayStatBPLocation(i) for i in itemList ]
    if vdata[0]:
        displayData = vdata[0] if len(set(vdata)) == 1 else "<br>\n".join(vdata)
        infobox['blueprint_location'] = displayData

    return infobox


def GetWikiInfoboxDataForCollectible(itemList):
    # Template name is Infobox_Collectible

    primaryItem = itemList[-1]
    infobox = OrderedDict()


    splitItemName = SplitNameIntoBaseNameAndItemLevel(primaryItem['name'])

    source = GetItemSourceExtended(primaryItem, True)
    sourceClass = GetItemSourceClassName(primaryItem)
    if source is not None:
        if sourceClass:
            infobox['source'] = '<span class="{}">{}</span>'.format(sourceClass, source)
        else:
            infobox['source'] = source

    if sourceClass:
        infobox['title1'] = '<span class="{}">{}</span>'.format(sourceClass, splitItemName['fullNameMinusLevel'])
    else:
        infobox['title1'] = splitItemName['fullNameMinusLevel']

    image = GetItemWikiImage(primaryItem)
    if image:
        infobox['image1'] = image

    bpLoc = ItemDisplayStatBPLocation(primaryItem)
    if bpLoc:
        infobox['blueprint_location'] = image

    return infobox



def GetItemShieldEffect(item, includeEffectLevel=False):
    try:
        if item['type'] != 5 and item['effect'] > 0:
            effect = SmallConstants.effectLookup[item['effect']].replace('_', ' ').title()
    except:
        pass



def IsItemHidden(item, checkItemSource=True):
    with suppress(KeyError):
        if GetRaceForItem(item) in Config.unreleasedRaceList:
            return True

    if item['id'] in itemIdListToSkip:
        return True

    if checkItemSource and GetItemSource(item) == 'Unknown':
        return True

    return False


def IsItemNprExclusive(item):
    try:
        if item['race'] > 1 and item['id'] in SmallConstants.raceData[item['race']]['dontUse']:
            return True
    except:
        pass

    try:
        if item['race'] > 1 and item['id'] in SmallConstants.raceData[item['race']]['omitFromLoot']:
            return True
    except:
        pass

    try:
        if item['equipCategory'] == 7:  # Ultra Rare
            return True
    except:
        pass

    return False


def GetDamagePerRoundForItem(item):
    with suppress(AttributeError, KeyError):
        return Config.weaponDamagePerHitOverride[item['name']]

    ctd = GetItemContinuousDamageTotalDamage(item)
    if ctd:
        return ctd / GetItemLife(item)

    subWeapon = GetItemSubWeapon(item)
    if subWeapon:  return GetDamagePerRoundForItem(subWeapon)

    with suppress(KeyError):
        return item['damage']


def GetAllItemsSharingItemRange(item, funcItemList=...):
    if funcItemList is ...:
        funcItemList = itemData

    skipVariants = True
    range = GetRangeDataForItem(item, skipVariants)
    with suppress(KeyError, TypeError):
        rtnList = []
        for itemId in range['items']:
            if itemDataDict[itemId] in funcItemList:
                rtnList.append(itemDataDict[itemId])

        if len(rtnList) > 1:
            return rtnList

    nameInfo = SplitNameIntoBaseNameAndItemLevel(item['name'])
    if nameInfo['fullNameMinusLevel'] != item['name']:
        return [ v for v in funcItemList if SplitNameIntoBaseNameAndItemLevel(v['name'])['fullNameMinusLevel'] == nameInfo['fullNameMinusLevel']]

    return [ item ]



def GetRangeDataForItem(item, skipVariants=False):
    altItemId = item['id']
    variantIdx = None

    if not skipVariants:
        m = re.match(r'^(.+?)v(\d+)(_\d+)?$', altItemId)
        if m:
            altItemId = m.group(1)
            variantIdx = int(m.group(2))

    for k,v in itemRangeData.items():
        if item['id'] in v['items'] or (variantIdx is not None and altItemId in v['items'] and len(v['variants']) > variantIdx):
            return v
    return None


def GetVariantDataForItem(item):
    try:
        if item['variantID'] >= 0:
            return itemVariantData[item['variantID']]
    except:
        pass
    return None


def GetCraftingDataForItem(item):
    for k,v in itemCraftableData.items():
        if item['id'] in v['items']:
            return v

    if 'micro gate' in item['name'].lower() and 'loca' not in item['name'].lower():
        prefix = item['name'].split(' ')[-1]
        systemInfo = GalaxyUtils.GetSystemByPrefix(prefix)
        if systemInfo:
            return GalaxyUtils.GetCraftingRecipeForSystem(systemInfo)

    return None


def GetItemById(id):
    try:
        return itemDataDict[id]
    except:
        return None


def GetItemByName(name, itemList=...):
    if itemList is ...:
        itemList = itemData

    try:
        for v in itemList:
            if v['name'] == name:
                return v
    except:
        pass

    return None


def SplitNameIntoBaseNameAndItemLevel(input):
    levelList1 = [ "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX" ];
    levelList2 = [ "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE", "TEN" ];
    levelList3 = [ "1", "2", "3", "4", "5", "6", "7", "8", "9", "10" ];
    postfixList = [ "ARRAY", "BARRAGE", "CLOUD", "CLUSTER", "SMALL ARRAY", "STORM", "TORPEDO", "VOLLEY" ];

    input = input.strip()
    parts = input.split(' ')
    name = input

    postfixDisplay = parts[-1].upper().rstrip('S')
    postfix = None
    if postfixDisplay in postfixList and len(parts) > 1:
        postfix = parts[-1]
        levelDisplay = parts[-2].upper().rstrip('S')
        levelDisplayOrig = parts[-2]
        name = name.replace(' {}'.format(postfix), '')
    else:
        levelDisplay = postfixDisplay
        levelDisplayOrig = parts[-1]

    levelIdx = None
    if levelDisplay in levelList1:
        levelIdx = levelList1.index(levelDisplay)
    elif levelDisplay in levelList2:
        levelIdx = levelList2.index(levelDisplay)
    elif levelDisplay in levelList3:
        levelIdx = levelList3.index(levelDisplay)

    if levelIdx is not None:
        name = name[:-1*len(levelDisplayOrig)-1]
    else:
        levelDisplay = ""

    fullNameMinusLevel = name
    if postfix:
        fullNameMinusLevel = '{} {}'.format(name, postfix)

    return { 'name': name, 'fullNameMinusLevel': fullNameMinusLevel, 'levelDisplay': levelDisplayOrig, 'levelIdx': levelIdx, 'namePostfix': postfix }




def IsBeamWeapon(item):
    if "id" in item and item['id'] in beamWeaponOverrideIdList:
        return True
    if "initSpeed" in item and GeneralUtils.floatCmp(item['initSpeed'], '>', 0):
        return False
    if "maxSpeed" in item and GeneralUtils.floatCmp(item['maxSpeed'], '>', 0):
        return False
    if "guidance" not in item or GeneralUtils.floatCmp(item['guidance'], '!=', 1):
        return False
    if "life" not in item or GeneralUtils.floatCmp(GetItemLife(item), '>', 1):
        return False
    if "lockingRange" not in item or GeneralUtils.floatCmp(item['lockingRange'], '>', 100):
        return False
    return True


def GetItemMinRange(item):
    rtnVal = ""
    itemGuidance = SmallConstants.guidanceLookup[item['guidance']] if 'guidance' in item else ''

    try:
        if GeneralUtils.floatCmp(item['armingTime'], '>', 0) and itemGuidance != 'NO_COLLISION':
            acceleration = item['acceleration']
            if GeneralUtils.floatCmp(item['initSpeed'], '>', item['maxSpeed']) and GeneralUtils.floatCmp(acceleration, '>', 0):
                acceleration *= -1

            ttts = abs(item['maxSpeed'] - item['initSpeed']) / abs(item['acceleration'])
            if GeneralUtils.floatCmp(ttts, '>', item['armingTime']):
                rtnVal = item['armingTime']**2 * acceleration / 2 + item['armingTime'] * item['initSpeed']
            else:
                rtnVal = ttts**2 * acceleration / 2 + ttts * item['initSpeed'] + item['maxSpeed'] * (item['armingTime'] - ttts)
    except:
        pass

    return rtnVal


def GetItemRange(item):
    rtnVal = 0

    with suppress(AttributeError, KeyError):
        return Config.weaponRangeOverride[item['name']]

    subWeapon = GetItemSubWeapon(item)

    with suppress(KeyError):
        if item['weaponType'] == 5 and subWeapon:
            return GetItemRange(subWeapon)

    itemGuidance = SmallConstants.guidanceLookup[item['guidance']] if 'guidance' in item else ''
    if 'Smart' not in item['name'] and itemGuidance in ['UNGUIDED', 'ATTACHED']:
        if 'weaponType' not in item or item['weaponType'] != 5:
            try:
                acceleration = item['acceleration']
                if GeneralUtils.floatCmp(item['initSpeed'], '>', item['maxSpeed']) and GeneralUtils.floatCmp(acceleration, '>', 0):
                    acceleration *= -1

                ttts = abs(item['maxSpeed'] - item['initSpeed']) / abs(acceleration)
                if GeneralUtils.floatCmp(ttts, '>', GetItemLife(item)):
                    rtnVal = GetItemLife(item)**2 * acceleration / 2 + GetItemLife(item) * item['initSpeed']
                else:
                    rtnVal = ttts**2 * acceleration / 2 + ttts * item['initSpeed'] + item['maxSpeed'] * (GetItemLife(item) - ttts)
            except:
                if item['maxSpeed'] > 0:
                    if item['maxSpeed'] != item['initSpeed'] and item['initSpeed'] > 0:
                        rtnVal = item['initSpeed'] * GetItemLife(item)
                    else:
                        rtnVal = item['maxSpeed'] * GetItemLife(item)

        try:
            if rtnVal == 0 and subWeapon:
                return GetItemRange(subWeapon)
        except:
            pass

    try:
        if item['augType'] == 15 and rtnVal == 0 and subWeapon:
            return GetItemRange(subWeapon) * 0.5
    except:
        pass

    try:
        if rtnVal == 0 and item['lockingRange'] > 0:
            rtnVal = item['lockingRange']
    except:
        pass

    return rtnVal


def GetTurretSubWeapon(item):
    try:
        rangeData = GetRangeDataForItem(item)
        baseSubWeapon = GetItemById(rangeData['range'])

        nameInfo = SplitNameIntoBaseNameAndItemLevel(item['name'])
        if nameInfo['levelIdx'] is None or nameInfo['levelIdx'] == 0:
            return baseSubWeapon

        m = re.match(r'^(.+?)v(\d+)(_\d+)?$', baseSubWeapon['id'])
        if m:
            realId = '{}_{}'.format(baseSubWeapon['id'], nameInfo['levelIdx'])
            if m.group(3):
                replaceLen = len(m.group(3)) * -1
                realId = baseSubWeapon['id'][0:replaceLen]
                realId += str(nameInfo['levelIdx'])

            subWeapon = GetItemById(realId)
            if subWeapon:
                return subWeapon

        subRangeData = GetRangeDataForItem(baseSubWeapon)
        return GetItemById(subRangeData['items'][nameInfo['levelIdx']])
    except:
        pass


def GetItemSubWeapon(item):
    try:
        return GetItemById(Config.subWeaponIDOverride[item['name']])
    except:
        pass
    try:
        return GetItemById(item['subWeaponID'])
    except:
        pass

    try:
        if item['augType'] == 15:
            return GetTurretSubWeapon(item)
    except:
        pass


def DisplayDamageAsPerSecond(item):

    if GetItemContinuousDamageTotalDamage(item) is not None:
        return True

    if 'fireRate' in item and GeneralUtils.floatCmp(item['fireRate'], '==', 0):
        return True

    nameCmp = item['name'].lower()
    if 'deathtrap' in nameCmp or 'death trap' in nameCmp:
        return False
    if 'thunder' in nameCmp or 'bug zapper' in nameCmp:
        return True
    if 'tornadian hurricane' in nameCmp or 'radicane' in nameCmp or 'firestorm' in nameCmp:
        return True
    if 'tornadian' in nameCmp and 'storm' in nameCmp:
        return True
    if 'light saw' in nameCmp:
        return True

    return False


def DisplayDamageAsPerHit(item):
    return GetItemTotalHitCount(item) is not None


def GetNumOfDamagingProjectiles(item, isForDisplay=False):
    f = GetNumOfDamagingProjectiles
    if "cloudTypeProjCountRegex" not in f.__dict__:
        f.cloudTypeProjCountRegex = re.compile(r'.* fires (\d+) \[subWeapon\]s', re.I)
    cloudTypeProjCountRegex = f.cloudTypeProjCountRegex

    if item['name'] in Config.projectileCountOverride:
        return Config.projectileCountOverride[item['name']]

    try:
        if item['augType'] == 15:
            subWeapon = GetItemSubWeapon(item)
            if subWeapon:  return GetNumOfDamagingProjectiles(subWeapon, isForDisplay)
    except:
        pass

    nameCmp = item['name'].lower()
    amount = item['amount'] if 'amount' in item and item['amount'] > 0 else 1
    lt = GetItemLife(item)
    if 'thunder' in nameCmp or 'bug zapper' in nameCmp:
        if not isForDisplay and lt is not None:
            return lt * amount
        return amount
    if 'light saw' in nameCmp:
        if not isForDisplay and lt is not None:
            return lt * amount
        return amount
    if 'tornadian hurricane' == nameCmp or 'radicane' == nameCmp or 'firestorm' == nameCmp:
        if not isForDisplay:
            return lt
        return amount
    if 'tornadian' in nameCmp and 'storm' in nameCmp:
        if not isForDisplay:
            return lt
        return amount

    varData = GetVariantDataForItem(item)
    if varData and varData['overrideName'].lower() == "cluster [name] torpedo":
        if not isForDisplay:
            return 10 * amount
        return amount

    if 'broadside' in nameCmp:
        if 'dark light' in nameCmp:  return 8
        if 'double' in nameCmp:  return 10
        return 5

    # if 'radial' in nameCmp and 'black light cannon' not in nameCmp:
    if 'radial' in nameCmp and 'black light cannon' not in nameCmp and 'resonite' not in nameCmp:
        if 'plus' in nameCmp:  return 16 * amount
        return 8 * amount

    if 'black light volley' in nameCmp:
        return 8 * amount
    if 'black light bombard' in nameCmp:
        return 8 * 5
    if 'cake bomb' in nameCmp:
        return 16  # Could be 15...  Need to re-test

    if amount > 1:  return amount

    # if isForDisplay and 'cloud' in nameCmp:
    #     return 1

    try:
        varData = GetVariantDataForItem(item)
        match = cloudTypeProjCountRegex.match(varData['descriptionAppend'])
        return int(match.group(1))
    except:
        pass

    try:
        varDesc = item['variant']['deviceOverride']['descriptionOverride']
        match = cloudTypeProjCountRegex.match(varDesc)
        return int(match.group(1))
    except:
        pass

    try:
        desc = GetItemDescription(item, useHtmlForLinks=False, performLinkReplacement=False)
        match = re.match(r'.*\bfires (\d+) ', desc, re.I)
        return int(match.group(1))
    except:
        pass

    return amount


def GetItemTotalHitCount(item):
    with suppress(AttributeError, KeyError):
        return Config.weaponHitCountOverride[item['name']]

    subWeapon = GetItemSubWeapon(item)
    if subWeapon:
        val = GetItemTotalHitCount(subWeapon)
        if val:  return val


def GetItemContinuousDamageTotalDamage(item):
    with suppress(AttributeError, KeyError):
        return Config.weaponContinuousDamageTotalDamageOverride[item['name']]

    subWeapon = GetItemSubWeapon(item)
    if subWeapon:
        val = GetItemContinuousDamageTotalDamage(subWeapon)
        if val:  return val


def GetItemLife(item):
    with suppress(AttributeError, KeyError):
        return Config.weaponLifeOverride[item['name']]

    subWeapon = GetItemSubWeapon(item)
    if subWeapon:
        val = GetItemLife(subWeapon)
        if val:  return val

    with suppress(AttributeError, KeyError):
        return item['life']


def GetItemTotalDamagePerVolley(item):
    effectDamage = None
    message = None
    totalDamage = 0

    ctd = GetItemContinuousDamageTotalDamage(item)
    if ctd:
        totalDamage = ctd
    elif DisplayDamageAsPerHit(item):
        totalDamage = GetDamagePerRoundForItem(item) * GetItemTotalHitCount(item)
    else:
        totalDamage = GetDamagePerRoundForItem(item) * GetNumOfDamagingProjectiles(item)

    itemType = GetItemType(item)
    if itemType != 'Shield':
        effectDamage = GetItemEffectDamage(item)
        if effectDamage:
            totalDamage += effectDamage

    return totalDamage


def GetItemMaxSpeed(item):
    subWeapon = GetItemSubWeapon(item)
    if subWeapon:
        return GetItemMaxSpeed(subWeapon)

    if 'maxSpeed' in item and GeneralUtils.floatCmp(item['maxSpeed'], '>', 0):
        return item['maxSpeed']


def GetItemInitialSpeed(item):
    subWeapon = GetItemSubWeapon(item)
    if subWeapon:
        return GetItemInitialSpeed(subWeapon)

    if 'initSpeed' in item and GeneralUtils.floatCmp(item['initSpeed'], '>', 0):
        return item['initSpeed']


def GetRaceForItem(item):
    return SmallConstants.GetNprNameFromId(item['race'])


def GetItemDamageType(item):
    with suppress(KeyError, IndexError):
        return GeneralUtils.CamelCaseToTitleCase(SmallConstants.damageTypeLookup[item['damageType']])


def GetShieldEffectIconsForItem(item, type="both"):
    rtnVal = ""
    statusList = GetShieldStatusEffectList(item)
    if type == "both" or type == "positive":
        for effectName in statusList['positiveEffects']:
            with suppress(KeyError):
                className = Config.shieldEffectIconClassMapping[effectName]
                if className[:6].lower() == '[html]':
                    iconHtml = className[6:]
                    rtnVal += '<span class="shieldEffectPositive" title="{}">{}</span>'.format(effectName, iconHtml)
                else:
                    rtnVal += '<span class="shieldEffectPositive {}" title="{}"></span>'.format(className, effectName)

    if type == "both" or type == "negative":
        rtnVal += ' '
        for effectName in statusList['negativeEffects']:
            with suppress(KeyError):
                className = Config.shieldEffectIconClassMapping[effectName]
                if className[:6].lower() == '[html]':
                    iconHtml = className[6:]
                    rtnVal += '<span class="shieldEffectNegative" title="{}">{}</span>'.format(effectName, iconHtml)
                else:
                    rtnVal += '<span class="shieldEffectNegative {}" title="{}"></span>'.format(className, effectName)

    return rtnVal.strip()


def GetDamageTypeIconForItem(item):
    damageType = GetItemDamageType(item)
    with suppress(KeyError, AttributeError):
        className = Config.damageTypeIconClassMapping[damageType.title().replace(' ', '')]
        if className[:6].lower() == '[html]':
            iconHtml = className[6:]
            return '<span class="damageType{}" title="Damage Type: {}">{}</span>'.format(damageType.title().replace(' ', ''), damageType, iconHtml)
        else:
            return '<span class="damageType{} {}" title="Damage Type: {}"></span>'.format(damageType.title().replace(' ', ''), className, damageType)
    return ''

def GetEffectIconForItem(item):
    # damageType = GetItemDamageType(item)
    # with suppress(KeyError):
    #     return '<span class="damageType{} {}" title="Damage Type: {}"></span>'.format(damageType.title().replace(' ', ''), Config.damageTypeIconClassMapping[damageType.title().replace(' ', '')], damageType)
    return ''



def GetShieldStatusEffectList(item):
    itemType = SmallConstants.typeLookup[item['type']].replace('_WEAPON', '').title()

    rtnList = { 'positiveEffects': set(), 'negativeEffects': set() }
    if itemType == 'Shield':
        if item['effect'] > 0:
            effectName = GetShieldEffectName(item, False)
            if effectName == 'Tornadian':
                rtnList['positiveEffects'].add('Projectile')
                rtnList['negativeEffects'].add('Electrostatic')
            elif effectName == 'Vampire':
                rtnList['positiveEffects'].add('Gravity')
            elif effectName == 'Devimon':
                rtnList['positiveEffects'].add('Gravity')
                rtnList['positiveEffects'].add('Heat Resist')
            elif effectName == 'Enlightened':
                rtnList['positiveEffects'].add('Heat Resist')
                rtnList['negativeEffects'].add('Projectile')
            elif effectName == 'Solarion':
                rtnList['positiveEffects'].add('Heat Resist')
                rtnList['negativeEffects'].add('Projectile')
                rtnList['negativeEffects'].add('Frozen')
            elif effectName == 'Rock':
                rtnList['positiveEffects'].add('Explosive')
                rtnList['negativeEffects'].add('Laser')
                rtnList['negativeEffects'].add('Photonic')
            elif effectName == 'Refractive':
                rtnList['positiveEffects'].add('Laser')
                rtnList['positiveEffects'].add('Photonic')
                rtnList['negativeEffects'].add('Explosive')
            elif effectName == 'Andromedan':
                rtnList['positiveEffects'].add('Stealth - Andromedan')
                rtnList['negativeEffects'].add('Heat Weakness')
            elif effectName == 'Anti Gravity':
                rtnList['positiveEffects'].add('Gravity')
            elif effectName == 'Anti Nuclear':
                rtnList['positiveEffects'].add('Nuclear')
            elif effectName == 'Insulator':
                rtnList['positiveEffects'].add('Electrostatic')
            elif effectName == 'Human Ghostly':
                rtnList['positiveEffects'].add('Ghostly')
            elif effectName == 'Ascendant':
                rtnList['positiveEffects'].add('NPR Damage')
            elif effectName == 'Dark':
                rtnList['positiveEffects'].add('Gravity')
                rtnList['positiveEffects'].add('Cold Fusion')
            else:
                rtnList['positiveEffects'].add(effectName)

        with suppress(KeyError):
            if item['resistExtraEffect'] >= 0:
                effectName = SmallConstants.effectsData[item['resistExtraEffect']]['name']
                if effectName:
                    rtnList['positiveEffects'].add(effectName)

    rtnList['positiveEffects'] = sorted(list(rtnList['positiveEffects']))
    rtnList['negativeEffects'] = sorted(list(rtnList['negativeEffects']))
    return rtnList


def GetDescriptionForItemRangeList(itemList, enclosureStr=None):
    if not enclosureStr:
        enclosureStr = ''

    vdata = [ GetItemDescription(i) for i in itemList ]
    vdata = [ v for v in vdata if v ]  #  Skip any empty descriptions
    if len(set(vdata)) == 1:
        return [ "{1}{0}{1}".format(vdata[0], enclosureStr) if vdata[0] != '' else '' ]

    rtnList = []

    idx = 0
    for item in itemList:
        if len(vdata) > idx:
            nameInfo = SplitNameIntoBaseNameAndItemLevel(item['name'])
            rtnList.append("{2}{0}{2} -Level {1}".format(vdata[idx], nameInfo['levelDisplay'], enclosureStr))
            idx += 1

    return rtnList



def GetCategoryListForItem(item):
    rtnSet = set()
    itemType = SmallConstants.typeLookup[item['type']].replace('_', ' ').title()

    nprPageName = WikiUtils.GetNprWikiPageByNprName(GetRaceForItem(item))
    if nprPageName:
        rtnSet.add(nprPageName)

    with suppress(KeyError):
        if item['equipCategory'] == 7:
            rtnSet.add('Ultra Rare')


    if itemType == 'Collectible':
        rtnSet.add('Collectible')

    if itemType == 'Primary Weapon':
        rtnSet.add('Energy Based')
    if itemType == 'Secondary Weapon' and 'energyBased' in item:
        if item['energyBased']:
            rtnSet.add('Energy Based')
        else:
            rtnSet.add('Ammo Based')

    if 'seasonal' in item and item['seasonal']:
        rtnSet.add("Seasonal Items")

    damageCat = GetDamageTypeForItem(item, True)
    if damageCat:
        rtnSet.add(damageCat.replace(' Damage', ''))
        rtnSet.add('Damage:{}'.format(damageCat))

    effectList = GetEffectNameListForItem(item)
    for effect in effectList:
        rtnSet.add(effect.replace(' Damage', '').replace(' Resist', '').replace(' Weakness', ''))
        if itemType != 'Shield':
            rtnSet.add('Effect:{}'.format(effect))
        else:
            rtnSet.add(effect)

    with suppress(KeyError):
        if itemType == 'Shield':
            if item['resistExtraEffect'] >= 0:
                effectName = SmallConstants.effectsData[item['resistExtraEffect']]['name']
                if effectName:
                    rtnSet.add(effectName)

    if item['name'] == 'Radii Nanite Repair':
        rtnSet.add('Heat')

    augType = GetItemAugType(item)
    if augType == 'Fire Extinguisher':
        rtnSet.add('Heat')
    elif augType == 'Energy To Shield':
        rtnSet.add('Shield Recharge')
    elif augType == 'Radiation Charging':
        rtnSet.add('Energy Recharge')
        rtnSet.add('Heat')
    elif augType == 'S/E Balancer':
        rtnSet.add('Energy Recharge')
        rtnSet.add('Shield Recharge')
    elif augType in ['Andromedan Power Source', "Dark Energy Charging", "Dartian Converter", 'Solar Panel Upgrade', 'Shield To Energy', 'Devimon Energize']:
        rtnSet.add('Energy Recharge')
    elif augType in ['Dartian Hyperspace', "Hyperspace Recharge Booster"]:
        rtnSet.add('Hyperspace Recharge')


    if 'stealth' in item and item['stealth']:
        rtnSet.add('Stealthed')
    if 'Shield Repair' in rtnSet:
        rtnSet.add('Shield Recharge')

    stealthEffectList = ['Hidden by Smoke', 'Light Bending Stealth', 'Transparent Stealth', 'Absorbing Stealth', 'Reflecting Stealth', 'Stealth - Andromedan']
    for sn in stealthEffectList:
        if sn in rtnSet:
            rtnSet.add('Stealth')
            break


    if 'impact' in item and item['impact'] < 0:
        rtnSet.add('Negative Impact')

    return sorted(list(rtnSet))



def GetDamageTypeForItem(item, forCategoryUse=False):
    # damageTypesRequiringPostfix = ['Electrostatic', 'Explosive', 'Ghostly', 'Heat', 'Laser', 'Photonic', 'Projectile']

    damageType = None
    if ('damage' in item and item['damage'] > 0):
        try:
            damageType = GeneralUtils.CamelCaseToTitleCase(SmallConstants.damageTypeLookup[item['damageType']])
            if forCategoryUse:
                if damageType == 'None' or damageType == 'Unknown' or damageType == 'Other':
                    damageType = None
                elif damageType == 'Hyperspace Harvest':
                    damageType = 'Hyperspace Recharge'
                elif damageType == 'Energy Harvest':
                    damageType = 'Energy Recharge'
                # elif damageType in damageTypesRequiringPostfix:
                #     damageType += ' Damage'
        except:
            pass

    subWeapon = GetItemSubWeapon(item)
    if (not damageType or damageType == 'None') and subWeapon:
        damageType = GetDamageTypeForItem(subWeapon, forCategoryUse)

    return damageType


def GetItemEffectDamage(item, shipMass=..., amount=...):
    if amount is ...:
        amount = GetNumOfDamagingProjectiles(item)
    if shipMass is ...:
        shipMass = Config.shipMassForDamageCalculation

    subWeapon = GetItemSubWeapon(item)
    if subWeapon:  return GetItemEffectDamage(subWeapon, shipMass, amount)

    with suppress(KeyError):
        if item['effect'] >= 0:
            effectInfo = SmallConstants.effectsData[item['effect']]
            effectName = effectInfo['name']
            effectTime = item['effectTime'] * amount
            if 'cap' in effectInfo and GeneralUtils.floatCmp(effectInfo['cap'], '>', 0):
                effectTime = min(round(effectTime), effectInfo['cap'])

            if effectName == 'Radiation Damage':
                # Radiation is (6 * m * t/3) + (4 * m * t/3) + (2 * m * t/3) Where m is ship mass, t is effect time (using highest stacked time)
                # This simplifies down to a short  4 * m * t
                return round(4 * shipMass * effectTime, 2)
            elif effectName == 'Corrosion':
                # Corrosion damage is time remaining as damage per second. So 15 secs of corrosion with no refresh would be 15 + 14 + 13 ... + 1 damage
                return (effectTime + 1) * effectTime / 2
            else:
                return round(SmallConstants.effectDamagesData[effectName] * effectTime, 2)


def GetItemEffectDamagePerSecond(item, shipMass=..., amount=...):
    if amount is ...:
        amount = GetNumOfDamagingProjectiles(item)
    if shipMass is ...:
        shipMass = Config.shipMassForDamageCalculation

    subWeapon = GetItemSubWeapon(item)
    if subWeapon:  return GetItemEffectDamagePerSecond(subWeapon, shipMass, amount)

    totalDamage = 0
    numShotsToTest = None
    with suppress(KeyError):
        if 'weaponType' in item and item['weaponType'] == 5:
            fireRate = 60
        elif 'fireRate' in item and GeneralUtils.floatCmp(item['fireRate'], '>', 0):
            fireRate = item['fireRate']
        else:
            # No fire rate probably means beam type weapon
            fireRate = 1 # For effect purposes, beams are applied at a rate of 1 per second

        if item['energyBased']:
            numShotsToTest = int(100 / item['ammoOrEnergyUsage'])
        else:
            numShotsToTest = int(item['ammoOrEnergyUsage'])

    if Config.debug:  print("GetItemEffectDamagePerSecond: shots to test", numShotsToTest)
    if Config.debug:  print("GetItemEffectDamagePerSecond: fire rate in use", fireRate)

    try:
        if numShotsToTest and item['effect'] >= 0:
            effectInfo = SmallConstants.effectsData[item['effect']]
            effectName = effectInfo['name']
            totalTime = 0
            timeSinceLastCalc = 0
            for i in range(0, numShotsToTest):
                # if Config.debug:  print("testing shot number", i)
                if GeneralUtils.floatCmp(timeSinceLastCalc, '>=', 1):
                    secondsToCalc = math.floor(timeSinceLastCalc)
                    # if Config.debug:  print("secondsToCalc", secondsToCalc)
                    # if Config.debug:  print("totalTime", totalTime)

                    if effectName == 'Radiation Damage':
                        # Radiation is (6 * m * t/3) + (4 * m * t/3) + (2 * m * t/3) Where m is ship mass, t is effect time (using highest stacked time)
                        if GeneralUtils.floatCmp(secondsToCalc, '>', effectTime):
                            # Full damage calculation
                            totalDamage += 4 * shipMass * secondsToCalc
                        else:
                            t2End = totalTime / 3
                            t1End = t2End * 2

                            # tier 1 calculation
                            t1Seconds = min(math.floor(t1End), secondsToCalc)
                            totalDamage += 6 * shipMass * t1Seconds
                            remaining = secondsToCalc - t1Seconds

                            # tier 2 calculation
                            if GeneralUtils.floatCmp(remaining, '>=', 1):
                                t2Seconds = min(math.floor(t1End), math.floor(remaining))
                                totalDamage += 4 * shipMass * t2Seconds
                                remaining -= t2Seconds

                            # tier 3 calculation
                            if GeneralUtils.floatCmp(remaining, '>=', 1):
                                t3Seconds = math.floor(remaining)
                                totalDamage += 2 * shipMass * t3Seconds
                                remaining -= t3Seconds

                        totalTime -= secondsToCalc

                    elif effectName == 'Corrosion':
                        # Corrosion damage is time remaining as damage per second
                        totalDamage += (totalTime + (totalTime - secondsToCalc + 1)) * secondsToCalc / 2
                        totalTime -= secondsToCalc

                    else:
                        # If the effectTime > speedUpIfOver apply a damage multiplier
                        for j in range(0, secondsToCalc):
                            effectDamageMult = 1
                            if 'speedUpIfOver' in effectInfo and GeneralUtils.floatCmp(effectInfo['speedUpIfOver'], '>', 0):
                                if GeneralUtils.floatCmp(effectInfo['speedUpIfOver'], '<', totalTime):
                                    effectDamageMult = totalTime / effectInfo['speedUpIfOver']
                            totalDamage += SmallConstants.effectDamagesData[effectName] * effectDamageMult
                            totalTime -= 1

                    timeSinceLastCalc -= secondsToCalc
                    # if Config.debug:  print("totalDamage", totalDamage)

                effectTime = item['effectTime'] * amount
                totalTime += effectTime

                if 'cap' in effectInfo and GeneralUtils.floatCmp(effectInfo['cap'], '>', 0):
                    totalTime = min(totalTime, effectInfo['cap'])

                timeSinceLastCalc += fireRate


            if GeneralUtils.floatCmp(timeSinceLastCalc, '>=', 1):
                secondsToCalc = math.floor(timeSinceLastCalc)
                # if Config.debug:  print("secondsToCalc", secondsToCalc)
                # if Config.debug:  print("totalTime", totalTime)

                if effectName == 'Radiation Damage':
                    # Radiation is (6 * m * t/3) + (4 * m * t/3) + (2 * m * t/3) Where m is ship mass, t is effect time (using highest stacked time)
                    if GeneralUtils.floatCmp(secondsToCalc, '>', effectTime):
                        # Full damage calculation
                        totalDamage += 4 * shipMass * secondsToCalc
                        timeSinceLastCalc = 0
                    else:
                        t2End = totalTime / 3
                        t1End = t1End * 2

                        # tier 1 calculation
                        t1Seconds = min(math.floor(t1End), secondsToCalc)
                        totalDamage += 6 * shipMass * t1Seconds
                        remaining = secondsToCalc - t1Seconds

                        # tier 2 calculation
                        if GeneralUtils.floatCmp(remaining, '>=', 1):
                            t2Seconds = min(math.floor(t1End), math.floor(remaining))
                            totalDamage += 4 * shipMass * t2Seconds
                            remaining -= t2Seconds

                        # tier 3 calculation
                        if GeneralUtils.floatCmp(remaining, '>=', 1):
                            t3Seconds = math.floor(remaining)
                            totalDamage += 2 * shipMass * t3Seconds
                            remaining -= t3Seconds

                elif effectName == 'Corrosion':
                    # Corrosion damage is time remaining as damage per second
                    totalDamage += (totalTime + (totalTime - secondsToCalc + 1)) * secondsToCalc / 2

                else:
                    # If the effectTime > speedUpIfOver apply a damage multiplier
                    for j in range(0, secondsToCalc):
                        effectDamageMult = 1
                        if 'speedUpIfOver' in effectInfo and GeneralUtils.floatCmp(effectInfo['speedUpIfOver'], '>', 0):
                            if GeneralUtils.floatCmp(effectInfo['speedUpIfOver'], '<', totalTime):
                                effectDamageMult = totalTime / effectInfo['speedUpIfOver']
                        totalDamage += SmallConstants.effectDamagesData[effectName] * effectDamageMult
                        totalTime -= 1

                # if Config.debug:  print("totalDamage", totalDamage)
    except KeyError:
        pass
    except:
        if Config.debug:
            raise

    if totalDamage:
        return round(totalDamage / (numShotsToTest * fireRate), 4)


def GetEffectNameListForItem(item):
    rtnList = set()
    itemType = GetItemType(item)

    try:
        if item['name'] == 'Red Mist Slammer':
            rtnList.add('Red Mist Haze')
            rtnList.add('Concussion')
        elif item['name'] == 'Radii Nanite Repair':
            rtnList.add('Fire Suppression')
            rtnList.add('Shield Repair')
            rtnList.add('Energy Recharge')
            rtnList.add('Magnetic Disruption')
            rtnList.add('Slow Down')
        elif item['name'] == 'Radii Nanite Attack':
            rtnList.add('Hard Light Decay')
            rtnList.add('Propulsion Dehance')
            rtnList.add('Corrosion')
            rtnList.add('Energy Drain')
            rtnList.add('Slow Down')
            rtnList.add('Drift')
        elif item['name'] == 'Ascendant Recovery Kit':
            rtnList.add('Weapon Repel')
            rtnList.add('Energy Recharge')
            rtnList.add('Absorbing Stealth')
            rtnList.add('Scanner Jammed')
            rtnList.add('Slow Down')
        elif item['effect'] > 0 or (item['effectTime'] > 0 and item['effect'] == 0):
            if itemType == 'Shield':
                effectName = GetShieldEffectName(item, False)
                if effectName is None:
                    pass
                elif effectName == 'Tornadian':
                    rtnList.add('Projectile Resist')
                    rtnList.add('Electrostatic Weakness')
                elif effectName == 'Vampire':
                    rtnList.add('Anti Gravity')
                elif effectName == 'Devimon':
                    rtnList.add('Anti Gravity')
                    rtnList.add('Heat Resist')
                elif effectName == 'Enlightened':
                    rtnList.add('Heat Resist')
                    rtnList.add('Projectile Weakness')
                elif effectName == 'Solarion':
                    rtnList.add('Heat Resist')
                    rtnList.add('Projectile Weakness')
                    rtnList.add('Freezing Weakness')
                elif effectName == 'Rock':
                    rtnList.add('Explosive Resist')
                    rtnList.add('Laser Weakness')
                    rtnList.add('Photonic Weakness')
                elif effectName == 'Refractive':
                    rtnList.add('Laser Resist')
                    rtnList.add('Photonic Resist')
                    rtnList.add('Explosive Weakness')
                elif effectName == 'Andromedan':
                    rtnList.add('Stealth - Andromedan')
                    rtnList.add('Heat Weakness')
                elif effectName == 'Dark':
                    rtnList.add('Anti Gravity')
                    rtnList.add('Cold Fusion Resist')
                else:
                    rtnList.add(effectName)
            else:
                effectName = SmallConstants.effectsData[item['effect']]['name']
                if effectName:
                    if effectName == 'Hellfire':
                        rtnList.add('Hellfire')
                        rtnList.add('Anti Stealth')
                    elif effectName == 'Holographic Disguise':
                        rtnList.add('Holographic Disguise')
                        rtnList.add('Drift')
                    else:
                        rtnList.add(effectName)
    except:
        pass

    try:
        if item['addEffect'] > 0 and item['effectTime'] > 0:
            effectName = SmallConstants.effectsData[item['addEffect']]['name']
            if effectName:
                if effectName == 'Hellfire':
                    rtnList.add('Hellfire')
                    rtnList.add('Anti Stealth')
                elif effectName == 'Holographic Disguise':
                    rtnList.add('Holographic Disguise')
                    rtnList.add('Drift')
                else:
                    rtnList.add(effectName)
    except:
        pass


    augType = GetItemAugType(item)
    if augType == 'Self Torture':
        rtnList.add('Heat Damage')
    elif augType == 'Red Mist':
        rtnList.add('Red Mist Haze')
    elif augType == 'Fire Extinguisher':
        rtnList.add('Fire Suppression')
    elif augType == 'Fire Extinguisher':
        rtnList.add('Fire Suppression')
    elif augType == 'Drift':
        rtnList.add('Drift')

    return sorted(list(rtnList))


def GetRangeDataByRangeId(rangeId):
    for rangeInfo in itemRangeData.values():
        if rangeInfo['id'] == rangeId:
            return rangeInfo


def GetItemDescription(item, useHtmlForLinks=False, performLinkReplacement=True):
    from SFIWikiBotLib import ShipUtils
    description = ''
    skipVariants = False

    if 'Mine Torpedo' not in item['name']:
        skipVariants = True if 'Cloud' in item['name'] or 'Array' in item['name'] else False
        itemRangeData = GetRangeDataForItem(item, skipVariants)
        if itemRangeData and 'description' in itemRangeData:
            description = itemRangeData['description'].replace('\r', ' ')

        if description:
            itemVariantData = GetVariantDataForItem(item)
            if itemVariantData and 'descriptionAppend' in itemVariantData and itemVariantData['descriptionAppend']:
                lchar = description[-1]
                if lchar in ['.', '!', '?']:
                    description += ' '
                else:
                    description += '. '
                description += itemVariantData['descriptionAppend']

    if not description:
        if '__extData' in item and 'description' in item['__extData']:
            description = item['__extData']['description']
            description = re.sub('(Has [^:]* Effect)', '. \\1', description, re.S)
            description = description.replace('.. Has', '. Has').replace('!. Has', '! Has').replace('?. Has', '? Has')

            description = re.sub('Also depletes', '. Also depletes', description, re.S)
            description = description.replace('.. Also depletes', '. Also depletes').replace('!. Also depletes', '! Also depletes').replace('?. Also depletes', '? Also depletes')

    if not description:
        skipVariants = False
        itemRangeData = GetRangeDataForItem(item, skipVariants)
        if itemRangeData and 'description' in itemRangeData:
            description = itemRangeData['description'].replace('\r', ' ')

        itemVariantData = GetVariantDataForItem(item)
        if itemVariantData and 'descriptionAppend' in itemVariantData and itemVariantData['descriptionAppend']:
            if description:
                lchar = description[-1]
                if lchar in ['.', '!', '?']:
                    description += ' '
                else:
                    description += '. '

            description += itemVariantData['descriptionAppend']


    if not description:
        return ''

    lrange = ''
    rangeWeaponName = ''
    subWeaponName = ''
    subWeaponLRange = ''
    lifeTime = ''
    amount = ''
    level = ''
    levelPlusTwo = ''
    effect = ''
    effectTime = ''
    effectPerc = ''
    invEffectPerc = ''
    subShipName = ''


    lifeTime = GetItemLife(item)
    if lifeTime is not None:
        lifeTime = GeneralUtils.NumDisplay(lifeTime, 1)
    else:
        lifeTime = ''
    if 'amount' in item:
        amount = item['amount']
    if 'level' in item:
        level = item['level'] + 1
        levelPlusTwo = item['level'] + 2
    if 'effectTime' in item:
        effectTime = item['effectTime']
    if 'effectAmount' in item:
        effectPerc = "{}%".format(GeneralUtils.NumDisplay(item['effectAmount'] * 100, 0))
        invEffectPerc = "{}%".format(GeneralUtils.NumDisplay((1-item['effectAmount']) * 100, 0))
    try:
        if 'effect' in item and item['effect'] >= 0:
            effect = SmallConstants.effectsData[item['effect']]['name']
    except:
        print('Unable to get effect for id {} ({})'.format(item['effect'], item['name']))

    try:
        lrange = GeneralUtils.NumDisplay(GetItemRange(item))
        if lrange:
            lrange = "{}su".format(lrange)
    except:
        pass

    try:
        realRangeData = None
        if itemRangeData and 'range' in itemRangeData:
            realRangeData = GetRangeDataForItem(GetItemById(itemRangeData['range']))

        if realRangeData and 'level' in item and item['level'] > 0 and item['level'] < len(realRangeData['items']):
            rangeWeaponName = GetItemById(realRangeData['items'][item['level']])['name']
        else:
            rangeWeaponName = GetItemById(itemRangeData['range'])['name']
    except:
        pass

    try:
        subItem = GetItemSubWeapon(item)
        nameObj = SplitNameIntoBaseNameAndItemLevel(subItem['name'])
        subWeaponName = nameObj['fullNameMinusLevel']
        subWeaponLRange = subItem['lockingRange']
        if not subWeaponLRange:  subWeaponLRange = GetItemRange(subItem)
        if not subWeaponLRange:  subWeaponLRange = 0

        # Turrets only get half the range of their sub weapon
        if 'augType' in item and item['augType'] == 15:  subWeaponLRange *= 0.5

        subWeaponLRange = GeneralUtils.NumDisplay(subWeaponLRange, 1)
        if subWeaponLRange:
            lrange = "{}".format(subWeaponLRange)
    except:
        pass

    try:
        subShip = ShipUtils.GetShipById(item['subWeaponID'])
        subShipName = subShip['name']
    except:
        pass

    description = description.replace('[lockingRange]', str(lrange))
    description = description.replace('[weapon]', str(rangeWeaponName))
    description = description.replace('[subWeapon]', str(subWeaponName))
    description = description.replace('[subWeaponLockingRange]', str(subWeaponLRange))
    description = description.replace('[lifeTime]', str(lifeTime))
    description = description.replace('[life]', str(lifeTime))
    description = description.replace('[amount]', str(amount))
    description = description.replace('[level]', str(level))
    description = description.replace('[levelPlusTwo]', str(levelPlusTwo))
    description = description.replace('[effect]', str(effect))
    description = description.replace('[effectPerc]', str(effectPerc))
    description = description.replace('[invEffectPerc]', str(invEffectPerc))
    description = description.replace('[effectTime]', str(effectTime))
    description = description.replace('[subShip]', str(subShipName))

    if performLinkReplacement:
        description = GeneralUtils.AddWikiLinksToText(description, useHtmlForLinks)

    return description


def GetItemSourceExtended(item, includeLink=False):
    with suppress(AttributeError, KeyError):
        return Config.itemSourceOverride[item['name']]

    with suppress(AttributeError, KeyError):
        nameObj = SplitNameIntoBaseNameAndItemLevel(item['name'])
        itemName = nameObj['fullNameMinusLevel']
        return Config.itemSourceOverride[itemName]

    source = None
    if IsItemHidden(item):
        source = "Unavailable"
    elif 'seasonal' in item and item['seasonal']:
        source = "Purchased ([[:Category:Seasonal_Items|Seasonal]])"
    elif 'buyable' in item and item['buyable'] and ('uniqueToShipID' not in item or not item['uniqueToShipID']):
        source = "Purchased"
    elif 'race' in item and item['race'] <= 1 and item['name'] != 'Micro Gate TBZ' and GetItemBPLocation(item):
        source = "Crafted"
        if includeLink and Config.craftingPageName:
            if source != Config.craftingPageName:
                source = "[[{}|{}]]".format(Config.craftingPageName, source)
            else:
                source = "[[{}]]".format(source)
    elif 'race' in item and item['race'] > 1:
        source = "Rare Drop"
        if 'equipCategory' in item and item['equipCategory'] == 7:
            source = "Ultra Rare"
        elif IsItemNprExclusive(item):
            source = "NPR Exclusive"

        nprName = GetRaceForItem(item)
        if not includeLink:
            source += " ({})".format(nprName)
        else:
            wikiPage = WikiUtils.GetNprWikiPageByNprName(nprName)
            if wikiPage == nprName:
                source += " ([[{}]])".format(nprName)
            else:
                source += " ([[{}|{}]])".format(wikiPage, nprName)
    elif item['id'] in rarePlayerRaceDropIdList:
        source = "Rare Drop"

    return source


def GetItemSource(item):
    with suppress(AttributeError, KeyError):
        return Config.itemSourceOverride[item['name']]

    with suppress(AttributeError, KeyError):
        nameObj = SplitNameIntoBaseNameAndItemLevel(item['name'])
        itemName = nameObj['fullNameMinusLevel']
        return Config.itemSourceOverride[itemName]

    source = "Unknown"
    if 'seasonal' in item and item['seasonal']:
        source = "Purchased (Seasonal)"
    elif 'buyable' in item and item['buyable'] and ('uniqueToShipID' not in item or not item['uniqueToShipID']):
        source = "Purchased"
    elif 'race' in item and item['race'] <= 1 and item['name'] != 'Micro Gate TBZ' and (GetItemBPLocation(item)):
        source = "Crafted"
    elif 'race' in item and item['race'] > 1:
        source = "Rare Drop"
        if 'equipCategory' in item and item['equipCategory'] == 7:
            source = "Ultra Rare"
        elif IsItemNprExclusive(item):
            source = "NPR Exclusive"
    elif item['id'] in rarePlayerRaceDropIdList:
        source = "Rare Drop"
    return source


def GetItemSourceClassName(item):
    source = GetItemSource(item)
    if source == "Purchased (Seasonal)":
        return 'seasonalItem'
    elif source == "Purchased":
        return 'storeItem'
    elif source == "Crafted":
        return 'craftedItem'
    elif source == "Rare Drop":
        return 'nprItem'
    elif source == "NPR Exclusive":
        return 'nprExclusiveItem'
    elif source == "Ultra Rare":
        return 'nprUltraRareItem'
    elif source == "Turret Only":
        return 'aiOnlyItem'
    elif source == "Weapon Projectile":
        return 'weaponProjectiveItem'
    return None

def GetItemSkillName(item):
    try:
        return SmallConstants.skillsData[item['skillRequirement']['skill']]['name']
    except:
        return ""

def GetItemSkillLevel(item):
    try:
        return item['skillRequirement']['level']
    except:
        return 999

def ShortenSkillName(skillName):
    skillName = skillName.upper()
    if skillName == "EXPLOSIVES":
        return "EX"
    if skillName == "LIGHT":
        return "LT"
    if skillName == "PROGRAMMING":
        return "PR"
    if skillName == "SHIELDS":
        return "SH"
    return skillName[0:1]


def GetItemDps(item):
    dps = None
    with suppress(ZeroDivisionError, KeyError):
        if IsBeamWeapon(item) and GeneralUtils.floatCmp(item['fireRate'], '==', 0):
            dps = GetDamagePerRoundForItem(item)
        elif DisplayDamageAsPerHit(item):
            dps = GetItemTotalHitCount(item) * GetDamagePerRoundForItem(item) / item['fireRate']
        else:
            dps = GetDamagePerRoundForItem(item) / item['fireRate']
            dps *= GetNumOfDamagingProjectiles(item)

    return dps


def GetItemDpsIncludingEffectDamage(item):
    with suppress(KeyError):
        if item['augType'] == 15:
            subWeapon = GetItemSubWeapon(item)
            if subWeapon:
                return GetItemDpsIncludingEffectDamage(subWeapon)

    dps = None
    if DisplayDamageAsPerSecond(item):
        dps = GetDamagePerRoundForItem(item)
        if 'amount' in item and item['amount'] > 1:
            dps *= item['amount']
    elif DisplayDamageAsPerHit(item):
        dps = GetItemTotalHitCount(item) * GetDamagePerRoundForItem(item) / item['life']
    else:
        dps = GetDamagePerRoundForItem(item) / item['fireRate']
        dps *= GetNumOfDamagingProjectiles(item)

    effectDps = GetItemEffectDamagePerSecond(item)
    if effectDps:
        try:
            dps += effectDps
        except:
            dps = effectDps

    return dps


def GetItemDpe(item):
    dpe = None
    with suppress(KeyError):
        damage = GetDamagePerRoundForItem(item)
        if damage > 0 and GeneralUtils.floatCmp(item['ammoOrEnergyUsage'], '>', 0) and item['energyBased']:
            if DisplayDamageAsPerHit(item):
                damage *= GetItemTotalHitCount(item)
            else:
                damage *= GetNumOfDamagingProjectiles(item)

            dpe = damage / item['ammoOrEnergyUsage']

    return dpe


def GetItemDpeIncludingEffectDamage(item):
    dpe = None
    with suppress(KeyError):
        damage = GetDamagePerRoundForItem(item)
        if damage and GeneralUtils.floatCmp(item['ammoOrEnergyUsage'], '>', 0) and item['energyBased']:
            if DisplayDamageAsPerHit(item):
                damage *= GetItemTotalHitCount(item)
            else:
                damage *= GetNumOfDamagingProjectiles(item)

            effectDamage = GetItemEffectDamage(item)
            if effectDamage:
                damage += effectDamage

            dpe = damage / item['ammoOrEnergyUsage']

    return dpe


def GetItemAugType(item):
    augType = None
    try:
        if item['augType'] >= 0:
            augType = SmallConstants.augTypeLookup[item['augType']]
            if augType == 'SEBalancer':
                augType = 'S/E Balancer'
            else:
                augType = GeneralUtils.CamelCaseToTitleCase(augType.replace('_', ''))
    except:
        pass

    return augType



def GetItemBPLocation(item):
    f = GetItemBPLocation
    if "locRegex" not in f.__dict__:
        f.locRegex = re.compile(r'^([A-Z][a-zA-Z0-9]*-[0-9]+-[0-9]+) \(')
    locRegex = f.locRegex

    with suppress(AttributeError, KeyError):
        return Config.bpLocationOverride[item['name']]

    rtnVal = ''
    craftingData = GetCraftingDataForItem(item)
    if craftingData:
        if 'isSystemMicroGate' in craftingData and craftingData['isSystemMicroGate']:
            itemIdx = 0
        else:
            itemIdx = craftingData['items'].index(item['id'])
        if len(craftingData['locations']) > itemIdx:
            rtnVal = craftingData['locations'][itemIdx]

    if not rtnVal:
        with suppress(KeyError):
            loc = item['__extData']['blueprintlocation']
            if loc.lower() == 'not yet available':
                rtnVal = 'N/A'
            else:
                rtnVal = loc

    m = locRegex.match(rtnVal)
    if m:
        rtnVal = m.group(1)

    return rtnVal


def GetItemEffectTime(item):
    effectTime = -1
    try:
        if item['effect'] >= 0:
            effectTime = item['effectTime']
    except:
        pass
    return effectTime


def GetItemPurchasePrice(item):
    if 'weaponType' in item and item['weaponType'] == 5:
        return int(GeneralUtils.RoundToSignificantAmount(item['price'] * itemPurchasePriceModifier, False, False, True))
    return int(GeneralUtils.RoundToSignificantAmount(item['price'] * itemPurchasePriceModifier))


def GetItemAmmoCost(item):
    if 'energyBased' in item and item['energyBased']:
        return 0
    if 'weaponType' in item and item['weaponType'] == 5:
        return item['price']
    return int(GeneralUtils.RoundToSignificantAmount(item['price'] * ammoCostModifier, True))


def GetWeaponEffectName(item):
    effect = None
    try:
        if item['effect'] >= 0 and (item['type'] == 2 or item['type'] == 3):
            effect = SmallConstants.effectsData[item['effect']]['name']
    except:
        pass
    return effect


def GetItemCraftingRecipe(item):
    """Determine the crafting cost for an item and return a dictionary with the values"""
    rtnInfo = {
        'creditCost': 0,
        'ingredientList': {},
    }
    smallValue = True

    itemCraftingData = GetCraftingDataForItem(item)
    if itemCraftingData:
        rtnInfo['creditCost'] = GetCraftingCreditCostForItem(item)
        for ingredient in itemCraftingData['ingredients']:
            qty = ingredient['quantityRequired'] * (1 + (item['level'] * 0.333334))
            rtnInfo['ingredientList'][ingredient['mineralID']] = GeneralUtils.RoundToSignificantAmount(qty, smallValue)
        return rtnInfo


def GetCraftingCreditCostForItem(item):
    item = GetAllItemsSharingItemRange(item)[0]
    itemCraftingData = GetCraftingDataForItem(item)
    if itemCraftingData:
        if 'creditCost' in itemCraftingData:
            return itemCraftingData['creditCost']

        priceMult = 0.281
        amountToAddPerIngredient = 150

        price = GetItemPurchasePrice(item)
        mineralCount = len(itemCraftingData['ingredients'])
        calculatedValue = price * priceMult + (amountToAddPerIngredient * mineralCount)

        smallValue = True
        allowDec = False
        largeValue = True
        return GeneralUtils.RoundToSignificantAmount(calculatedValue, smallValue, allowDec, largeValue)


def GetShieldEffectName(item, includeEffectLevel=False):
    rtnVal = None
    try:
        if item['effect'] > 0 and item['type'] == 5:
            effect = SmallConstants.effectLookup[item['effect']].replace('_', ' ').title()
            effectPercentage = GeneralUtils.NumDisplay(item['effectAmount'] * 100, 0)
            if effectPercentage != '0':
                if includeEffectLevel:
                    rtnVal = '{} ({}%)'.format(effect, effectPercentage)
                else:
                    rtnVal = effect
    except:
        pass

    return rtnVal


def GetImageUploadDownloadInfoForItem(item):
    itemType = SmallConstants.typeLookup[item['type']].replace('_WEAPON', '').title()
    iconName = item['id']
    if 'iconName' in item and item['iconName']:
        iconName = item['iconName']


    filepath = os.path.join('public', 'images', itemType, "{}.png".format(iconName))
    rtnVal = {
        'description': '{} - {}'.format(ItemDisplayStatItemType(item), item['name']),
        'exists': os.path.exists(filepath),
        'filepath': filepath,
        'filename': "{}.png".format(iconName),
        'name': "{}_{}.png".format(itemType, iconName),
        'url': GetItemImageUrl(item),
        'subDir': itemType,
    }

    return rtnVal


def GetItemType(item):
    rtnVal = ""

    if item['type'] == 3:
        rtnVal = SmallConstants.weaponTypeLookup[item['weaponType']]
        # rtnVal += " Secondary"
    else:
        rtnVal = SmallConstants.typeLookup[item['type']]

    rtnVal = rtnVal.replace('_', ' ').title()

    return rtnVal


def GetWikiPageForItemType(type):
    # Cheating since I already know the relevant page names
    # Todo - expand this section to cover several possibilities, in case of future name changes
    if type in ['Primary Weapon', 'Mine', 'Engine', 'Shield', 'Augmentation']:
        return WikiUtils.GetWikiArticlePageForNameList([type + 's'])
    if type == 'Utility':
        return WikiUtils.GetWikiArticlePageForNameList(['Utilities'])
    if type == 'Standard':
        return WikiUtils.GetWikiArticlePageForNameList(['Standard Weapons', 'Standard Secondary Weapons'])
    return WikiUtils.GetWikiArticlePageForNameList([type + ' Weapons'])


def GetItemImageUrl(item):
    rtnVal = ''

    itemType = SmallConstants.typeLookup[item['type']].replace('_WEAPON', '').title()
    iconName = item['id']
    if 'iconName' in item and item['iconName']:
        iconName = item['iconName']

    # rtnVal = "https://www.benoldinggames.co.uk/sfi/gamedata/icons/{}/{}.png".format(itemType, iconName)
    rtnVal = "https://www.benoldinggames.co.uk/sfi/gamedata/icons/allItems/{}.png".format(iconName)

    return rtnVal


def GetItemWikiImage(item):
    rtnVal = ''

    itemType = SmallConstants.typeLookup[item['type']].replace('_WEAPON', '').title()
    iconName = item['id']

    if 'iconName' in item and item['iconName']:
        iconName = item['iconName']

    itemNameList = []
    itemNameList.append("{} {}".format(itemType, iconName))
    itemNameList.append(item['name'])

    splitItemName = SplitNameIntoBaseNameAndItemLevel(item['name'])
    if splitItemName['fullNameMinusLevel'] != item['name']:
        itemNameList.append(splitItemName['fullNameMinusLevel'])

    rtnVal = WikiUtils.GetWikiImageForNameList(itemNameList)
    return rtnVal


def GetItemWikiArticlePage(item, p=...):
    type = GetItemType(item)
    itemNameList = [
        item['name'],
        "{} {}".format(item['name'], type),
        "{} {}".format(item['name'], GeneralUtils.GetPluralForm(type)),
    ]
    splitItemName = SplitNameIntoBaseNameAndItemLevel(item['name'])
    if splitItemName['fullNameMinusLevel'] != item['name'] :
        itemNameList.insert(0, splitItemName['fullNameMinusLevel'])
        itemNameList.insert(0, "{} {}".format(splitItemName['fullNameMinusLevel'], GeneralUtils.GetPluralForm(type)))
        itemNameList.insert(0, "{} {}".format(splitItemName['fullNameMinusLevel'], type))

    itemArticlePage = WikiUtils.GetWikiArticlePageForNameList(itemNameList)
    if itemArticlePage:
        return itemArticlePage



def GetDefaultTableInfoByItemType(itemType, weaponType=..., pageType=''):
    rtnInfo = {
        'tableHeader': None,
        'tableCaption': None,
        'tableClassNames': 'wikitable sortable',
        'tableColumnList': [],
        'tableColumnTitleList': [],
    }

    if itemType == 1:  # Mineral
        rtnInfo['tableHeader'] = 'Minerals'
        rtnInfo['tableColumnList'] = [ 'Name', 'Image' ]

    elif itemType == 2:  # Primary Weapon
        rtnInfo['tableHeader'] = 'Primary Weapons'
        rtnInfo['tableColumnList'] = ['Item','Dmg','TD','DPS','ROF','EU','DPE','Rng','Lt','MS','Ac','Effect','Sk']

    elif itemType == 3:  # Secondary Weapon
        if weaponType == 1:  # Standard
            rtnInfo['tableHeader'] = 'Standard Secondary Weapons'
            rtnInfo['tableColumnList'] = ['Item','Dmg','TD','DPS','ROF','Am','EU','Rng','MS','Trn','Effect','Sk']

        elif weaponType == 2:  # Utility
            rtnInfo['tableHeader'] = 'Utilities'
            rtnInfo['tableColumnList'] = ['Item','Dmg','Ammo','EU','Rng','Turn','Effect','Notes','Sk']

        elif weaponType == 3:  # Mine
            rtnInfo['tableHeader'] = 'Mines'
            rtnInfo['tableColumnList'] = ['Item','Dmg','TD','ROF','Am','EU','Arm','Lt','Effect','Sk']

        elif weaponType == 4:  # Proximity
            rtnInfo['tableHeader'] = 'Proximity Weapons'
            rtnInfo['tableColumnList'] = ['Item','Dmg','TD','ROF','Am','EU','Lt','Rng','Effect','Notes','Sk']

        elif weaponType == 5:  # Large
            rtnInfo['tableHeader'] = 'Large Weapons'
            rtnInfo['tableColumnList'] = ['Item','Dmg','TD','Range','Lt','Ammo','Cost','Ammo Cost','Notes','Sk']

    elif itemType == 4:  # Engine
        rtnInfo['tableHeader'] = 'Engines'
        rtnInfo['tableColumnList'] = ['Item','Speed','Reverse','Accel','Turning','Prop','Prop Time','Sk']

    elif itemType == 5:  # Shield
        rtnInfo['tableHeader'] = 'Shields'
        rtnInfo['tableColumnList'] = ['Item','Maximum Charge Multiplier','Charge Rate','Charge Delay','Effect Icons','Secondary Effects','Sk']

    elif itemType == 6:  # Augmentation
        rtnInfo['tableHeader'] = 'Augmentations'
        rtnInfo['tableColumnList'] = ['Item','Notes','Cost','Sk']

    elif itemType == 14:  # Collectible
        rtnInfo['tableHeader'] = 'Collectibles'
        rtnInfo['tableColumnList'] = ['Name','Image']


    if pageType and pageType is not ...:  pageType = pageType.lower()
    if pageType == 'crafting':
        rtnInfo['tableColumnList'].append('BP Location')
        if itemType == 2:  # Primary Weapon
            try:
                index = rtnInfo['tableColumnList'].index('Ac')
                rtnInfo['tableColumnList'] = rtnInfo['tableColumnList'][:index] + rtnInfo['tableColumnList'][index+1:]
                rtnInfo['tableColumnTitleList'] = rtnInfo['tableColumnTitleList'][:index] + rtnInfo['tableColumnTitleList'][index+1:]
            except ValueError:
                pass
            try:
                index = rtnInfo['tableColumnList'].index('Effect')
                rtnInfo['tableColumnList'] = rtnInfo['tableColumnList'][:index] + rtnInfo['tableColumnList'][index+1:]
                rtnInfo['tableColumnTitleList'] = rtnInfo['tableColumnTitleList'][:index] + rtnInfo['tableColumnTitleList'][index+1:]
            except ValueError:
                pass

        try:
            index = rtnInfo['tableColumnList'].index('Cost')
            rtnInfo['tableColumnList'] = rtnInfo['tableColumnList'][:index] + rtnInfo['tableColumnList'][index+1:]
            rtnInfo['tableColumnTitleList'] = rtnInfo['tableColumnTitleList'][:index] + rtnInfo['tableColumnTitleList'][index+1:]
        except ValueError:
            pass

    elif pageType == 'npr':
        try:
            index = rtnInfo['tableColumnList'].index('Skill')
            rtnInfo['tableColumnList'] = rtnInfo['tableColumnList'][:index] + rtnInfo['tableColumnList'][index+1:]
            rtnInfo['tableColumnTitleList'] = rtnInfo['tableColumnTitleList'][:index] + rtnInfo['tableColumnTitleList'][index+1:]
        except ValueError:
            pass

        try:
            index = rtnInfo['tableColumnList'].index('Sk')
            rtnInfo['tableColumnList'] = rtnInfo['tableColumnList'][:index] + rtnInfo['tableColumnList'][index+1:]
            rtnInfo['tableColumnTitleList'] = rtnInfo['tableColumnTitleList'][:index] + rtnInfo['tableColumnTitleList'][index+1:]
        except ValueError:
            pass

    rtnInfo['tableColumnTitleList'] = GetStatNameDescriptions(rtnInfo['tableColumnList'], pageType)

    return rtnInfo



def ItemDisplayStatDamage(item, p=..., includeProjectileDisplay=True):
    damagePerRound = GetDamagePerRoundForItem(item)

    if GeneralUtils.floatCmp(damagePerRound, '==', 0):
        return ''

    rtnVal = GeneralUtils.NumDisplay(damagePerRound, 1)
    if DisplayDamageAsPerSecond(item):
        rtnVal = "{}/s".format(rtnVal)
    elif DisplayDamageAsPerHit(item):
        rtnVal = "{}/hit".format(rtnVal)

    if includeProjectileDisplay:
        amount = GetNumOfDamagingProjectiles(item, True)
        if amount > 1:
            rtnVal = "{} x{}".format(rtnVal, amount)

    rtnVal = '{} {}'.format(rtnVal, GetDamageTypeIconForItem(item))

    return rtnVal.strip()


def ItemDisplayStatTotalDamagePerVolley(item, p=..., includeIcons=False):
    rtnVal = None
    message = None
    totalDamage = 0

    effectName = None
    try:
        subWeapon = GetItemSubWeapon(item)
        if subWeapon:
            effectName = SmallConstants.effectsData[subWeapon['effect']]['name']
        else:
            effectName = SmallConstants.effectsData[item['effect']]['name']
    except:
        pass

    totalDamage = GetItemTotalDamagePerVolley(item)
    rtnVal = GeneralUtils.NumDisplay(totalDamage, 2)
    effectDamage = GetItemEffectDamage(item)
    if GeneralUtils.floatCmp(effectDamage, '>', 0):
        message = "Includes {} damage from {}".format(GeneralUtils.NumDisplay(effectDamage, 1), effectName)
        if effectName == 'Radiation Damage':
            message += '.\nDamage is approximate depending on the mass of the target ship as well as whether the effect is refreshed. Estimation is for no refresh, ship mass of {}'.format(GeneralUtils.NumDisplay(Config.shipMassForDamageCalculation, 2))
        elif effectName == 'Corrosion':
            message += '.\nDamage is approximate depending on whether the effect is refreshed. Estimation is for no refresh'

        if DisplayDamageAsPerHit(item):
            message += ' and assumes all hits land on the target.'
        elif GetNumOfDamagingProjectiles(item, True) > 1:
            message += ' and assumes all projectiles hit the target.'
        else:
            message += '.'

    if message:
        rtnVal = '<span class="itemStatDetails" title="{}">{}</span>'.format(message, rtnVal)

    if includeIcons:
        if GeneralUtils.floatCmp(GetDamagePerRoundForItem(item), '>', 0):
            rtnVal = '{} {}'.format(rtnVal, GetDamageTypeIconForItem(item)).strip()
        if GeneralUtils.floatCmp(effectDamage, '>', 0):
            rtnVal = '{} {}'.format(rtnVal, GetEffectIconForItem(item)).strip()

    return rtnVal


def ItemDisplayStatRateOfFire(item, p=...):
    try:
        if item['augType'] == 15:
            subWeapon = GetItemSubWeapon(item)
            if subWeapon:  return ItemDisplayStatRateOfFire(subWeapon, p)
    except:
        pass

    if item['fireRate'] > 0:
        fireRate = item['fireRate']
        if fireRate <= 1:
            return "{} per sec".format(GeneralUtils.NumDisplay(1/fireRate, 1))
        return "1 per {} sec".format(GeneralUtils.NumDisplay(fireRate, 1))


def ItemDisplayStatRateOfFireShort(item, p=...):
    try:
        if item['augType'] == 15:
            subWeapon = GetItemSubWeapon(item)
            if subWeapon:  return ItemDisplayStatRateOfFire(subWeapon, p)
    except:
        pass

    if item['fireRate'] > 0:
        fireRate = item['fireRate']
        if fireRate <= 1:
            return "{}/s".format(GeneralUtils.NumDisplay(1/fireRate, 1))
        return "1/{}s".format(GeneralUtils.NumDisplay(fireRate, 1))


def ItemDisplayStatDps(item, p=...):
    return GeneralUtils.NumDisplay(GetItemDps(item), 1)


def ItemDisplayStatTotalDps(item, p=..., includeIcons=False):
    rtnVal = None
    message = None
    totalDps = 0

    effectName = None
    try:
        subWeapon = GetItemSubWeapon(item)
        if subWeapon:
            effectName = SmallConstants.effectsData[subWeapon['effect']]['name']
        else:
            effectName = SmallConstants.effectsData[item['effect']]['name']
    except:
        pass

    totalDps = GetItemDpsIncludingEffectDamage(item)
    rtnVal = GeneralUtils.NumDisplay(totalDps, 1)
    effectDps = GetItemEffectDamagePerSecond(item)
    if GeneralUtils.floatCmp(effectDps, '>', 0):
        message = "Includes {} dps from {}".format(GeneralUtils.NumDisplay(effectDps, 1), effectName)
        if effectName == 'Radiation Damage':
            message += '.\nDamage is approximate depending on the mass of the target ship. Estimation assumes a target ship mass of {}, with only this weapon applying the effect, firing as often as possible'.format(GeneralUtils.NumDisplay(Config.shipMassForDamageCalculation, 2))
        else:
            message += '.\nDamage is approximate and assumes only this weapon is applying the effect, firing as often as possible'

        if GetNumOfDamagingProjectiles(item, True) > 1:
            message += ' and assumes all projectiles hit the target.'
        else:
            message += '.'

    if message:
        rtnVal = '<span class="itemStatDetails" title="{}">{}</span>'.format(message, rtnVal)

    if includeIcons:
        if GeneralUtils.floatCmp(GetDamagePerRoundForItem(item), '>', 0):
            rtnVal = '{} {}'.format(rtnVal, GetDamageTypeIconForItem(item)).strip()
        if GeneralUtils.floatCmp(effectDps, '>', 0):
            rtnVal = '{} {}'.format(rtnVal, GetEffectIconForItem(item)).strip()


    return rtnVal


def ItemDisplayStatDpe(item, p=...):
    return GeneralUtils.NumDisplay(GetItemDpe(item), 2)


def ItemDisplayStatTotalDpe(item, p=...):
    rtnVal = None

    totalDpe = GetItemDpeIncludingEffectDamage(item)
    if totalDpe:
        message = None
        effectName = None
        try:
            subWeapon = GetItemSubWeapon(item)
            if subWeapon:
                effectName = SmallConstants.effectsData[subWeapon['effect']]['name']
            else:
                effectName = SmallConstants.effectsData[item['effect']]['name']
        except:
            pass

        rtnVal = GeneralUtils.NumDisplay(totalDpe, 2)
        effectDamage = GetItemEffectDamage(item)
        if effectDamage:
            message = "{} of this amount comes from {}".format(GeneralUtils.NumDisplay(effectDamage / item['ammoOrEnergyUsage'], 1), effectName)
            if effectName == 'Radiation Damage':
                message += '.\nDamage is approximate depending on the mass of the target ship as well as whether the effect is refreshed. Estimation is for no refresh, ship mass of {}'.format(GeneralUtils.NumDisplay(Config.shipMassForDamageCalculation, 2))
            elif effectName == 'Corrosion':
                message += '.\nDamage is approximate depending on whether the effect is refreshed. Estimation is for no refresh'

            if GetNumOfDamagingProjectiles(item, True) > 1:
                message += ' and assumes all projectiles hit the target.'
            else:
                message += '.'

        if message:
            rtnVal = '<span class="itemStatDetails" title="{}">{}</span>'.format(message, rtnVal)

    return rtnVal


def ItemDisplayStatEnergyRequired(item, p=...):
    rtnVal = ""
    if 'energyUsage' in item and GeneralUtils.floatCmp(item['energyUsage'], '>', 0):
        rtnVal = GeneralUtils.NumDisplay(item['energyUsage'], 2)

    if not rtnVal and GeneralUtils.floatCmp(item['ammoOrEnergyUsage'], '>', 0) and item['energyBased']:
        rtnVal = GeneralUtils.NumDisplay(item['ammoOrEnergyUsage'], 2)
        if IsBeamWeapon(item):
            rtnVal = "{}/s".format(item['ammoOrEnergyUsage'])

    return rtnVal


def ItemDisplayStatImage(item, p=...):
    rtnVal = ""

    title = item['name']
    splitItemName = SplitNameIntoBaseNameAndItemLevel(item['name'])
    if splitItemName['fullNameMinusLevel'] != item['name']:
        title = splitItemName['fullNameMinusLevel']

    imageName = GetItemWikiImage(item)
    if imageName:
        rtnVal = '[[File:{}|thumb|55x55px]]'.format(imageName)

    return rtnVal


def ItemDisplayStatImageHtml(item, p=...):
    rtnVal = ''

    wikiImage = GetItemWikiImage(item)
    if wikiImage:
        iconUrl = GetItemImageUrl(item)
        if iconUrl:
            rtnVal = '<img src="{}" width="55" height="55" onError="this.onerror = \'\';this.style.visibility=\'hidden\';">'.format(iconUrl)

    return rtnVal


def ItemDisplayStatAmmo(item, p=...):
    rtnVal = ""
    if GeneralUtils.floatCmp(item['ammoOrEnergyUsage'], '>', 0) and not item['energyBased']:
        rtnVal = GeneralUtils.NumDisplay(item['ammoOrEnergyUsage'], 0)
        if item['weaponType'] != 5:
            rtnVal = "{} ({})".format(GeneralUtils.NumDisplay(item['ammoOrEnergyUsage'], 0), GeneralUtils.NumDisplay(item['ammoOrEnergyUsage'] * 5, 0))
    return rtnVal


def ItemDisplayStatAmmoReserve(item, p=...):
    rtnVal = ""
    if GeneralUtils.floatCmp(item['ammoOrEnergyUsage'], '>', 0) and not item['energyBased'] and item['weaponType'] != 5:
        rtnVal = GeneralUtils.NumDisplay(item['ammoOrEnergyUsage'] * 5, 0)
    return rtnVal


def ItemDisplayStatEffect(item, p=...):
    rtnVal = ""
    try:
        if item['effect'] >= 0:
            if item['type'] == 5:
                rtnVal = GetShieldEffectName(item, True)
            else:
                rtnVal = SmallConstants.effectsData[item['effect']]['name']

            if item['effectTime'] > 0:
                rtnVal = "{} ({}s)".format(rtnVal, GeneralUtils.NumDisplay(item['effectTime'], 0))
    except:
        pass

    if rtnVal == "" and item['name'].lower().find('chain laser') >= 0:
        rtnVal = GetItemDescription(item)
    return rtnVal


def ItemDisplayStatEffectHtml(item, p=...):
    rtnVal = ""
    try:
        if item['effect'] >= 0:
            if item['type'] == 5:
                rtnVal = GetShieldEffectName(item, True)
            else:
                rtnVal = SmallConstants.effectsData[item['effect']]['name']

            if item['effectTime'] > 0:
                rtnVal = "{} ({}s)".format(rtnVal, GeneralUtils.NumDisplay(item['effectTime'], 0))
    except:
        pass

    if rtnVal == "" and item['name'].lower().find('chain laser') >= 0:
        useHtmlForLinks = True
        rtnVal = GetItemDescription(item, useHtmlForLinks)
    return rtnVal


def ItemDisplayStatSkill(item, p=...):
    rtnVal = ""
    if item['skillRequirement']['skill'] >= 0:
        rtnVal = "N/A"
        if item['skillRequirement']['level'] > 0:
            rtnVal = "{} {}".format(
                ShortenSkillName(SmallConstants.skillsData[item['skillRequirement']['skill']]['name']),
                item['skillRequirement']['level']
            )
    return rtnVal


def ItemDisplayStatSkillFull(item, p=...):
    rtnVal = ""
    if item['skillRequirement']['level'] > 0:
        rtnVal = "{} {}".format(
            SmallConstants.skillsData[item['skillRequirement']['skill']]['name'],
            item['skillRequirement']['level']
        )
    return rtnVal


def ItemDisplayStatName(item, p=...):
    displayName = item['name']

    itemArticlePage = GetItemWikiArticlePage(item)
    if itemArticlePage:
        if WikiUtils.PageNamesEqual(itemArticlePage, item['name']):
            displayName = '[[{}]]'.format(item['name'])
        else:
            displayName = '[[{}|{}]]'.format(itemArticlePage, item['name'])

    rtnVal = displayName
    sourceClass = GetItemSourceClassName(item)
    if sourceClass:
        rtnVal = ' class="{}" | {}'.format(sourceClass, displayName)

    return rtnVal


def ItemDisplayStatNameHtml(item, p=...):
    displayName = html.escape(item['name'])

    itemArticlePage = GetItemWikiArticlePage(item)
    if itemArticlePage:
        displayName = '<a href="{}">{}</a>'.format(
            WikiUtils.GetWikiLink(itemArticlePage),
            displayName
        )

    rtnVal = displayName
    sourceClass = GetItemSourceClassName(item)
    if sourceClass:
        rtnVal = '<span class="{}">{}</span>'.format(sourceClass, displayName)

    return rtnVal


def ItemDisplayStatNameAndImage(item, p=...):
    rtnVal = ""

    imageName = GetItemWikiImage(item)
    pageName = GetItemWikiArticlePage(item)
    if not pageName:  pageName = SplitNameIntoBaseNameAndItemLevel(item['name'])['fullNameMinusLevel']
    itemName = item['name']

    sourceClass = GetItemSourceClassName(item)
    sourceClass = sourceClass if sourceClass is not None else ""
    if imageName:
        rtnVal = 'align="center" style="font-size: smaller;" class="{}" | [[File:{}|centre|thumb|60x60px|link={}]]<br/>[[{}{}]]'.format(sourceClass, imageName, pageName, '' if WikiUtils.PageNamesEqual(pageName, itemName) else '{}|'.format(pageName), itemName)
    else:
        rtnVal = 'align="center" style="font-size: smaller;" class="{}" | [[{}{}]]'.format(sourceClass, '' if WikiUtils.PageNamesEqual(pageName, itemName) else '{}|'.format(pageName), itemName)

    # iconHtml = GetShieldEffectIconsForItem(item)
    # if iconHtml:
    #     rtnVal = "{}<br />{}".format(rtnVal, iconHtml)

    return rtnVal


def ItemDisplayStatNameAndImageHtml(item, p=...):
    rtnVal = ""

    pageName = GetItemWikiArticlePage(item)
    if not pageName:  pageName = SplitNameIntoBaseNameAndItemLevel(item['name'])['fullNameMinusLevel']
    wikiUrl = WikiUtils.GetWikiLink(pageName)

    imageName = GetItemWikiImage(item)
    itemName = item['name']

    sourceClass = GetItemSourceClassName(item)
    sourceClass = sourceClass if sourceClass is not None else ""
    if imageName:
        iconUrl = GetItemImageUrl(item)
        rtnVal = '<div style="text-align:center; font-size:smaller;" class="{}"><a href="{}"><img src="{}" width="60" height="60" onError="this.onerror = \'\';this.style.visibility=\'hidden\';"><br />{}</a></div>'.format(sourceClass, wikiUrl, iconUrl, itemName)
    else:
        rtnVal = '<div style="text-align:center; font-size:smaller;" class="{}"><a href="{}">{}</a></div>'.format(sourceClass, wikiUrl, itemName)

    return rtnVal


def ItemDisplayStatDamageType(item, p=...):
    dtype = GetItemDamageType(item)
    return dtype if dtype else ''


def ItemDisplayStatEffectIcons(item, p=...):
    rtnVal = GetShieldEffectIconsForItem(item, "positive")
    if rtnVal:
        rtnVal += "<br>"
    rtnVal += GetShieldEffectIconsForItem(item, "negative")
    return rtnVal


def ItemDisplayStatPurchaseCost(item, p=...):
    source = GetItemSource(item)

    rtnVal = "N/A ({})".format(source)
    if 'Purchase' in source:
        rtnVal = GeneralUtils.NumDisplay(GetItemPurchasePrice(item), 0, True)

    return rtnVal


def ItemDisplayStatBPLocation(item, p=...):
    loc = GetItemBPLocation(item)
    loc = GeneralUtils.AddWikiLinksToText(loc, False, False, { 'Stars': False })
    return loc


def ItemDisplayStatBPLocationHtml(item, p=...):
    loc = GetItemBPLocation(item)
    loc = GeneralUtils.AddHtmlLinksToText(loc, True, False, { 'Stars': False })
    return loc


def ItemDisplayStatSpeed(item, p=...):
    maxSpd = GetItemMaxSpeed(item)
    initSpd = GetItemInitialSpeed(item)
    rtnVal = ''

    if maxSpd and initSpd and maxSpd != initSpd:
        rtnVal = "{} &#8594; {}".format(GeneralUtils.NumDisplay(initSpd, 1), GeneralUtils.NumDisplay(maxSpd, 1))
    elif maxSpd:
        rtnVal = "{}su/s".format(GeneralUtils.NumDisplay(maxSpd, 1))

    return rtnVal


def ItemDisplayStatObtain(item, p=...):
    source = GetItemSource(item)
    sourceClass = GetItemSourceClassName(item)

    rtnVal = source
    if sourceClass:
        rtnVal = ' class="{}" | {}'.format(sourceClass, source)

    return rtnVal


def ItemDisplayStatObtainHtml(item, p=...):
    source = GetItemSource(item)
    sourceClass = GetItemSourceClassName(item)

    rtnVal = source
    if sourceClass:
        rtnVal = '<span class="{}">{}</span>'.format(sourceClass, source)

    return rtnVal


def ItemDisplayStatDestination(item, p=...):
    rtnVal = ""

    if 'micro gate' in item['name'].lower() and 'local' not in item['name'].lower():
        prefix = item['name'].split(' ')[-1]
        systemName = GalaxyUtils.GetSystemNameByPrefix(prefix)
        rtnVal = systemName

        wikiPageName = WikiUtils.GetWikiArticlePageForNameList([ systemName ])
        if wikiPageName:
            if wikiPageName == systemName:
                rtnVal = '[[{}]]'.format(systemName)
            else:
                rtnVal = '[[{}|{}]]'.format(wikiPageName, systemName)

    return rtnVal


def ItemDisplayStatDestinationHtml(item, p=...):
    rtnVal = ""

    if 'micro gate' in item['name'].lower() and 'local' not in item['name'].lower():
        prefix = item['name'].split(' ')[-1]
        systemName = GalaxyUtils.GetSystemNameByPrefix(prefix)
        rtnVal = systemName

        wikiPageName = WikiUtils.GetWikiArticlePageForNameList([ systemName ])
        if wikiPageName:
            rtnVal = '<a href="{}" title="{} Star System">{}</a>'.format(
                WikiUtils.GetWikiLink(wikiPageName),
                systemName,
                systemName
            )

    return rtnVal


def ItemDisplayStatItemType(item, p=...):
    itemType = GetItemType(item)
    displayItemType = itemType
    if p == "itemPage":
        if displayItemType == "Standard":
            displayItemType = "Standard Secondary Weapon"
        elif displayItemType == "Proximity" or displayItemType == "Large":
            displayItemType = "{} Weapon".format(displayItemType)
    wikiPageName = GetWikiPageForItemType(itemType)
    if wikiPageName:
        if wikiPageName == itemType:
            return '[[{}]]'.format(displayItemType)
        return '[[{}|{}]]'.format(wikiPageName, displayItemType)
    return itemType


def ItemDisplayStatItemTypeHtml(item, p=...):
    itemType = GetItemType(item)
    wikiPageName = GetWikiPageForItemType(itemType)
    if wikiPageName:
        return '<a href="{}" title="Equipment - {}">{}</a>'.format(
            WikiUtils.GetWikiLink(wikiPageName),
            itemType,
            itemType
        )
    return itemType

def ItemDisplayStatArmTime(item, p=...):
    rtnVal = ""

    lt = GetItemLife(item)
    if item['weaponType'] == 5 and lt is not None and lt > 0:
        rtnVal = "{}s".format(GeneralUtils.NumDisplay(lt, 2))
    if not rtnVal and item['armingTime'] > 0:
        rtnVal = "{}s".format(GeneralUtils.NumDisplay(item['armingTime'], 2))

    return rtnVal

def ItemDisplayStatAcceleration(item, p=...):
    rtnVal = ""

    if GetItemType(item) == 'Engine':
        return "x{}".format(GeneralUtils.NumDisplay(item['accelMod'], 4)) if item['accelMod'] > 0 else ""

    return "{}su/s/s".format(GeneralUtils.NumDisplay(item['acceleration'], 2))


### Generic stat display
def ItemDisplayStatGeneric(item, p=...):
    try:
        return item[p]
    except:
        print("{} not found".format(p))
    return ""


itemDisplayStatSwitcher = {
    'acceleration': ItemDisplayStatAcceleration,
    'accel': ItemDisplayStatAcceleration,
    'ac': (lambda obj, p: GeneralUtils.NumDisplay(obj['accuracy'], 2)),
    'acc': (lambda obj, p: GeneralUtils.NumDisplay(obj['accuracy'], 2)),
    'accuracy': (lambda obj, p: GeneralUtils.NumDisplay(obj['accuracy'], 2)),
    'acquisition': ItemDisplayStatObtain,
    'am': ItemDisplayStatAmmo,
    'ammo cost': (lambda obj, p: GeneralUtils.NumDisplay(GetItemAmmoCost(obj), 0, True) if GetItemAmmoCost(obj) > 0 else ""),
    'ammo': ItemDisplayStatAmmo,
    'amount': (lambda obj, p: obj['amount'] if obj['amount'] > 0 else ""),
    'amt': (lambda obj, p: GetNumOfDamagingProjectiles(obj, True)),
    'ar': ItemDisplayStatAmmoReserve,
    'arming time': ItemDisplayStatArmTime,
    'arm': ItemDisplayStatArmTime,
    'aug type': (lambda obj, p: GetItemAugType(obj)),
    'autopilot': (lambda obj, p: "+{}".format(GeneralUtils.NumDisplay(obj['autoPilotSpeedInc'], 4)) if obj['autoPilotSpeedInc'] > 0 else ""),
    'base dpe': ItemDisplayStatDpe,
    'base dps': ItemDisplayStatDps,
    'bdpe': ItemDisplayStatDpe,
    'bdps': ItemDisplayStatDps,
    'bp location': ItemDisplayStatBPLocation,
    'charge delay': (lambda obj, p: "{}s".format(GeneralUtils.NumDisplay(obj['chargeDelay'], 4)) if obj['chargeDelay'] > 0 else ""),
    'charge rate': (lambda obj, p: "x{}".format(GeneralUtils.NumDisplay(obj['chargeModifier'], 4)) if obj['chargeModifier'] > 0 else ""),
    'cost': ItemDisplayStatPurchaseCost,
    'damage': ItemDisplayStatDamage,
    'destination': ItemDisplayStatDestination,
    'dmg': ItemDisplayStatDamage,
    'dmg type': ItemDisplayStatDamageType,
    'dpe': ItemDisplayStatTotalDpe,
    'dph': ItemDisplayStatDamage,
    'dps': ItemDisplayStatTotalDps,
    'effect': ItemDisplayStatEffect,
    'effect icons': ItemDisplayStatEffectIcons,
    'effects': ItemDisplayStatEffect,
    'energy': ItemDisplayStatEnergyRequired,
    'energy usage': ItemDisplayStatEnergyRequired,
    'engine name': ItemDisplayStatName,
    'et': (lambda obj, p: "{}s".format(GeneralUtils.NumDisplay(obj['effectTime'], 0)) if obj['effectTime'] > 0 else ""),
    'eu': ItemDisplayStatEnergyRequired,
    'fire rate': ItemDisplayStatRateOfFire,
    'image': ItemDisplayStatImage,
    'img': ItemDisplayStatImage,
    'init spd': (lambda obj, p: GeneralUtils.NumDisplay(GetItemInitialSpeed(obj), 1) if GetItemInitialSpeed(obj) else ""),
    'init speed': (lambda obj, p: GeneralUtils.NumDisplay(GetItemInitialSpeed(obj), 1) if GetItemInitialSpeed(obj) else ""),
    'is': (lambda obj, p: GeneralUtils.NumDisplay(GetItemInitialSpeed(obj), 1) if GetItemInitialSpeed(obj) else ""),
    'item': ItemDisplayStatNameAndImage,
    'is passive': (lambda obj, p: 'Yes' if 'passive' in obj and obj['passive'] else 'No'),
    'lifetime': (lambda obj, p: "{}s".format(GeneralUtils.NumDisplay(GetItemLife(obj)), 1) if GetItemLife(obj) else ""),
    'lifetime (s)': (lambda obj, p: GeneralUtils.NumDisplay(GetItemLife(obj), 1) if GetItemLife(obj) > 0 else ""),
    'lrng': (lambda obj, p: "{}su".format(GeneralUtils.NumDisplay(GetItemRange(obj), 1)) if obj['guidance'] == 1 or IsBeamWeapon(obj) or 'Smart' in obj['name'] else ''),
    'lt': (lambda obj, p: "{}s".format(GeneralUtils.NumDisplay(GetItemLife(obj), 1)) if GetItemLife(obj) > 0 else ""),
    'max spd': (lambda obj, p: GeneralUtils.NumDisplay(GetItemMaxSpeed(obj), 1) if GetItemMaxSpeed(obj) else ""),
    'max speed': (lambda obj, p: GeneralUtils.NumDisplay(GetItemMaxSpeed(obj), 1) if GetItemMaxSpeed(obj) else ""),
    'maximum charge multiplier': (lambda obj, p: "x{}".format(GeneralUtils.NumDisplay(obj['maxModifier'], 4)) if obj['maxModifier'] > 0 else ""),
    'maximum charge mult': (lambda obj, p: "x{}".format(GeneralUtils.NumDisplay(obj['maxModifier'], 4)) if obj['maxModifier'] > 0 else ""),
    'min rng': (lambda obj, p: "{}su".format(GeneralUtils.NumDisplay(GetItemMinRange(obj), 1)) if GetItemMinRange(obj) else ''),
    'mrng': (lambda obj, p: "{}su".format(GeneralUtils.NumDisplay(GetItemMinRange(obj), 1)) if GetItemMinRange(obj) else ''),
    'ms': (lambda obj, p: GeneralUtils.NumDisplay(GetItemMaxSpeed(obj), 1) if GetItemMaxSpeed(obj) else ""),
    'name': ItemDisplayStatName,
    'notes': (lambda obj, p: GetItemDescription(obj)),
    'obtained': ItemDisplayStatObtain,
    'obtaining': ItemDisplayStatObtain,
    'obtain': ItemDisplayStatObtain,
    'pd': (lambda obj, p: "{} sec".format(GeneralUtils.NumDisplay(obj['propulsionEnhanceTime'], 4)) if obj['propulsionEnhanceTime'] > 0 else ""),
    'price unmodified': (lambda obj, p: GeneralUtils.NumDisplay(obj['price'], 0, True)),
    'prop': (lambda obj, p: "x{}".format(GeneralUtils.NumDisplay(obj['propulsionEnhance'], 4)) if obj['propulsionEnhance'] > 0 else ""),
    'prop time': (lambda obj, p: "{} sec".format(GeneralUtils.NumDisplay(obj['propulsionEnhanceTime'], 4)) if obj['propulsionEnhanceTime'] > 0 else ""),
    'propulsion': (lambda obj, p: "x{}".format(GeneralUtils.NumDisplay(obj['propulsionEnhance'], 4)) if obj['propulsionEnhance'] > 0 else ""),
    'purchase cost': ItemDisplayStatPurchaseCost,
    'race': (lambda obj, p: GetRaceForItem(obj)),
    'range': (lambda obj, p: "{}su".format(GeneralUtils.NumDisplay(GetItemRange(obj), 1)) if GetItemRange(obj) else ''),
    'rebuy cost': (lambda obj, p: GeneralUtils.NumDisplay(GetItemAmmoCost(obj), 0, True) if GetItemAmmoCost(obj) > 0 else ""),
    'required_skill': ItemDisplayStatSkillFull,
    'reverse': (lambda obj, p: "{}%".format(GeneralUtils.NumDisplay(obj['reverseSpeedMod'] * 100, 1)) if obj['reverseSpeedMod'] > 0 else ""),
    'rng': (lambda obj, p: GeneralUtils.NumDisplay(GetItemRange(obj), 1) if GetItemRange(obj) else ''),
    'rate of fire': ItemDisplayStatRateOfFire,
    'rof': ItemDisplayStatRateOfFireShort,
    'secondary effects': (lambda obj, p: GetItemDescription(obj)),
    'sk': ItemDisplayStatSkill,
    'skill': ItemDisplayStatSkill,
    'spd': ItemDisplayStatSpeed,
    'speed': (lambda obj, p: "x{}".format(GeneralUtils.NumDisplay(obj['maxSpeedMod'], 4)) if obj['maxSpeedMod'] > 0 else ""),
    'td': ItemDisplayStatTotalDamagePerVolley,
    'tdpe': ItemDisplayStatTotalDpe,
    'tdpv': ItemDisplayStatTotalDamagePerVolley,
    'tdps': ItemDisplayStatTotalDps,
    'total dmg': ItemDisplayStatTotalDamagePerVolley,
    'total ammo': ItemDisplayStatAmmo,
    'trn': (lambda obj, p: "{}°".format(GeneralUtils.NumDisplay(obj['turning'] * Config.turnMultiplier, 2)) if obj['turning'] > 0 else ""),
    'turning': (lambda obj, p: "x{}".format(GeneralUtils.NumDisplay(obj['turningMod'], 4)) if obj['turningMod'] > 0 else ""),
    'trn': (lambda obj, p: "{}°".format(GeneralUtils.NumDisplay(obj['turning'] * Config.turnMultiplier, 1)) if obj['turning'] > 0 else ""),
    'turn': (lambda obj, p: "{}°".format(GeneralUtils.NumDisplay(obj['turning'] * Config.turnMultiplier, 2)) if obj['turning'] > 0 else ""),
    'type': ItemDisplayStatItemType,
    'velocity': ItemDisplayStatSpeed,
    'volley': (lambda obj, p: obj['amount'] if obj['amount'] > 0 else ""),
    'weapon_type': ItemDisplayStatItemType,
}

itemDisplayStatSwitcherHtml = itemDisplayStatSwitcher.copy()
itemDisplayStatSwitcherHtml['engine name'] = ItemDisplayStatNameHtml
itemDisplayStatSwitcherHtml['name'] = ItemDisplayStatNameHtml
itemDisplayStatSwitcherHtml['img'] = ItemDisplayStatImageHtml
itemDisplayStatSwitcherHtml['image'] = ItemDisplayStatImageHtml
itemDisplayStatSwitcherHtml['obtain'] = ItemDisplayStatObtainHtml
itemDisplayStatSwitcherHtml['obtaining'] = ItemDisplayStatObtainHtml
itemDisplayStatSwitcherHtml['obtained'] = ItemDisplayStatObtainHtml
itemDisplayStatSwitcherHtml['acquisition'] = ItemDisplayStatObtainHtml
itemDisplayStatSwitcherHtml['destination'] = ItemDisplayStatDestinationHtml
itemDisplayStatSwitcherHtml['type'] = ItemDisplayStatItemTypeHtml
itemDisplayStatSwitcherHtml['item'] = ItemDisplayStatNameAndImageHtml
itemDisplayStatSwitcherHtml['effect'] = ItemDisplayStatEffectHtml
itemDisplayStatSwitcherHtml['effects'] = ItemDisplayStatEffectHtml
itemDisplayStatSwitcherHtml['bp location'] = ItemDisplayStatBPLocationHtml
itemDisplayStatSwitcherHtml['notes'] = (lambda obj, p: GetItemDescription(obj, useHtmlForLinks=True))
itemDisplayStatSwitcherHtml['secondary effects'] = (lambda obj, p: GetItemDescription(obj, useHtmlForLinks=True))


def GetStatDisplayForObject(propName, obj):
    rtnVal = ""
    try:
        # print(propName)
        func = itemDisplayStatSwitcher.get(propName.lower(), ItemDisplayStatGeneric)
        rtnVal = func(obj, propName)
    except:
        pass
    return rtnVal


def GetHtmlStatDisplayForObject(propName, obj):
    rtnVal = ""

    try:
        func = itemDisplayStatSwitcherHtml.get(propName.lower(), ItemDisplayStatGeneric)
        rtnVal = func(obj, propName)
    except:
        pass
    return rtnVal


# Get relevant stat descriptions
itemStatDescriptionSwitcher = {
    'acceleration': (lambda s, pt: "Engine acceleration modifier. The higher acceleration a ship has the quicker it gets up to max speed (100 accel = 1 second to max)"),
    'accel': (lambda s, pt: "Engine acceleration modifier. The higher acceleration a ship has the quicker it gets up to max speed (100 accel = 1 second to max)"),
    'ac': (lambda s, pt: "Accuracy or spread measured in degrees"),
    'acc': (lambda s, pt: "Accuracy or spread measured in degrees"),
    'accuracy': (lambda s, pt: "Accuracy or spread measured in degrees"),
    'acquisition': (lambda s, pt: "How you can obtain the item"),
    'am': (lambda s, pt: "Ammo per clip (Reserve ammo)"),
    'ammo cost': (lambda s, pt: "Ammo cost per magazine"),
    'ammo': (lambda s, pt: "Ammo per clip (Reserve ammo)"),
    'amount': (lambda s, pt: "Number of projectiles fired per volley"),
    'amt': (lambda s, pt: "Number of projectiles fired per volley"),
    'ar': (lambda s, pt: "Reserve Ammo"),
    'arming time': (lambda s, pt: "The delay in seconds before the item activates and is able to hit a target"),
    'arm': (lambda s, pt: "The delay in seconds before the item activates and is able to hit a target"),
    'aug type': (lambda s, pt: "The type of augmentation"),
    'autopilot': (lambda s, pt: "Additional speed applied when using auto-pilot. Typically this is a flat rate added to max speed measured in su/s"),
    'base dpe': (lambda s, pt: "Damage per energy spent only counting the base weapon damage (no effect damage)"),
    'base dps': (lambda s, pt: "Damage per second only counting the base weapon damage (no effect damage)"),
    'bdpe': (lambda s, pt: "Damage per energy spent only counting the base weapon damage (no effect damage)"),
    'bdps': (lambda s, pt: "Damage per second only counting the base weapon damage (no effect damage)"),
    'bp location': (lambda s, pt: "Location of the station where you can hack or dock to get this blueprint"),
    'charge delay': (lambda s, pt: "How long it takes a ship to start recharging its shields"),
    'charge rate': (lambda s, pt: "How fast a ship can recharge its shields"),
    'cost': (lambda s, pt: "The item cost when purchasing from the store"),
    'damage': (lambda s, pt: "Base damage per projectile hit"),
    'destination': (lambda s, pt: "The system/location where a Micro Gate will take you"),
    'dmg': (lambda s, pt: "Base damage per projectile hit"),
    'dmg type': (lambda s, pt: "Type of direct damage done by the item"),
    'dpe': (lambda s, pt: "Damage per energy spent, including effect damage"),
    'dph': (lambda s, pt: "Base damage per projectile hit"),
    'dps': (lambda s, pt: "Damage per second, including effect damage"),
    'effect': (lambda s, pt: "Status effect applied"),
    # 'effect icons': (lambda s, pt: ""),
    'effects': (lambda s, pt: "Status effect applied"),
    'energy': (lambda s, pt: "Energy used per shot"),
    'energy usage': (lambda s, pt: "Energy used per shot"),
    # 'engine name': (lambda s, pt: ""),
    'et': (lambda s, pt: "Effect Time"),
    'eu': (lambda s, pt: "Energy used per shot"),
    'fire rate': (lambda s, pt: "Rate of fire"),
    # 'image': (lambda s, pt: ""),
    'img': (lambda s, pt: "Item image"),
    'init spd': (lambda s, pt: "Projectile initial speed measured in su/s"),
    'init speed': (lambda s, pt: "Projectile initial speed measured in su/s"),
    'is': (lambda s, pt: "Projectile initial speed measured in su/s"),
    # 'item': (lambda s, pt: ""),
    'is passive': (lambda s, pt: "Whether or not this augmentation is passive"),
    'lifetime': (lambda s, pt: "Lifetime measured in seconds"),
    'lifetime (s)': (lambda s, pt: "Lifetime measured in seconds"),
    'lrng': (lambda s, pt: "Locking range"),
    'lt': (lambda s, pt: "Lifetime measured in seconds"),
    'max spd': (lambda s, pt: "Projectile max speed measured in su/s"),
    'max speed': (lambda s, pt: "Projectile max speed measured in su/s"),
    'maximum charge multiplier': (lambda s, pt: "The multiplier for a ship's maximum shielding"),
    'maximum charge mult': (lambda s, pt: "The multiplier for a ship's maximum shielding"),
    'min rng': (lambda s, pt: "Minimum range measured in su. Before this range is reached the projectile is not yet active and will bounce off targets"),
    'mrng': (lambda s, pt: "Minimum range measured in su. Before this range is reached the projectile is not yet active and will bounce off targets"),
    'ms': (lambda s, pt: "Projectile max speed measured in su/s"),
    # 'name': (lambda s, pt: ""),
    # 'notes': (lambda s, pt: ""),
    'obtained': (lambda s, pt: "How you can obtain the item"),
    'obtaining': (lambda s, pt: "How you can obtain the item"),
    'obtain': (lambda s, pt: "How you can obtain the item"),
    'pd': (lambda s, pt: "The time in seconds the engine will continue to boost. While the boost is active the ship cannot decelerate"),
    'price unmodified': (lambda s, pt: "Raw price of the item, without being adjusted for buying or selling"),
    'prop': (lambda s, pt: "Engine propulsion speed modifier. Applied to the max speed, this is how fast your ship will go when boosting"),
    'prop time': (lambda s, pt: "The time in seconds the engine will continue to boost. While the boost is active the ship cannot decelerate"),
    'propulsion': (lambda s, pt: "Engine propulsion speed modifier. Applied to the max speed, this is how fast your ship will go when boosting"),
    # 'purchase cost': (lambda s, pt: ""),
    'race': (lambda s, pt: "The race which owns the item. In the case of NPR races this will be who you need to farm for the drop"),
    'range': (lambda s, pt: "Range of the weapon measured in su"),
    'rebuy cost': (lambda s, pt: "Ammo cost (each)"),
    'required_skill': (lambda s, pt: "The required skill to purchase or craft the item"),
    'reverse': (lambda s, pt: "The max speed the ship can reach while reversing, as a percentage of the max speed"),
    'rng': (lambda s, pt: "Range of the weapon measured in su"),
    # 'rate of fire': (lambda s, pt: ""),
    'rof': (lambda s, pt: "Rate of fire"),
    # 'secondary effects': (lambda s, pt: ""),
    'sk': (lambda s, pt: "The required skill to purchase or craft the item"),
    'skill': (lambda s, pt: "The required skill to purchase or craft the item"),
    'spd': (lambda s, pt: "Projectile speed measured in su/s. May include initial speed"),
    'speed': (lambda s, pt: "Engine max speed multiplier"),
    'td': (lambda s, pt: "Total damage per volley, including effect damage"),
    'tdpe': (lambda s, pt: "Total damage per energy spent, including effect damage"),
    'tdpv': (lambda s, pt: "Total damage per volley, including effect damage"),
    'tdps': (lambda s, pt: "Total damage per second, including effect damage"),
    'total dmg': (lambda s, pt: "Total damage per volley, including effect damage"),
    'total ammo': (lambda s, pt: "Ammo per clip (Reserve ammo)"),
    'trn': (lambda s, pt: "Turning rate - rate at which the projectile rotates measured in degrees per second"),
    'turning': (lambda s, pt: "Turn rate modifier - the higher a ship's turn rate the more agile it is"),
    'trn': (lambda s, pt: "Turning rate - rate at which the projectile rotates measured in degrees per second"),
    'turn': (lambda s, pt: "Turning rate - rate at which the projectile rotates measured in degrees per second"),
    'type': (lambda s, pt: "The type of item this is (Mineral, Primary Weapon, Collectible, etc)"),
    'velocity': (lambda s, pt: "Projectile speed measured in su/s. May include initial speed"),
    'volley': (lambda s, pt: "Number of projectiles fired per volley"),
    'weapon_type': (lambda s, pt: "The type of weapon this is (primary, utility, large, etc)"),
}


def GetDescriptionForItemStatName(statName, pageType):
    rtnVal = ""

    try:
        func = itemStatDescriptionSwitcher.get(statName.lower(), (lambda s, pt: ""))
        rtnVal = func(statName, pageType)
        if rtnVal and pageType == 'crafting':
            rtnVal = rtnVal.replace('to purchase or craft the item', 'to craft the item')
    except:
        pass
    return rtnVal



# Begin Sorting Functions

def SortByNameAndRangeId(item):
    nameInfo = SplitNameIntoBaseNameAndItemLevel(item['name'])
    rtnVal = nameInfo['fullNameMinusLevel']
    if nameInfo['levelIdx'] is not None:
        rtnVal = "{}-{}".format(rtnVal, nameInfo['levelIdx'])
    return rtnVal


def GetItemSortFunc(sortBy="Default"):
    try:
        if sortBy.lower() == "name":
            return lambda v : v['name'].lower()
        if sortBy.lower() == "race":
            return lambda v : "{:03d}-{}".format(v['race'], v['name'].lower())
        if sortBy.lower() == 'skilllevel':
            return lambda v: "{:03d}-{}-{}".format(GetItemSkillLevel(v), GetItemSkillName(v), v['name'].lower())
    except:
        pass

    return SortByNameAndRangeId




# Begin Data Initialization Functions

def PrepareItemDataPrimaryList():
    global itemDataDict, itemData, itemBaseNameList

    itemDataDict = {}

    #  itemDataPublic is updated quite regularly, at least as often as the game is patched
    #  It is incomplete however. No NPR items are included, and no equivalent of the range and crafting data
    for item in itemDataPublic:
        item['__dataSource'] = 'public'
        itemDataDict[item['id']] = item

        nameParts = SplitNameIntoBaseNameAndItemLevel(item['name'])
        nameLower = nameParts['fullNameMinusLevel'].lower().replace('_', ' ')
        if not nameLower in itemBaseNameList:
            itemBaseNameList.append(nameLower)

    #  itemDataPrivate is updated often, often updated when the game is patched
    for item in itemDataPrivate.values():
        if item['id'] not in itemDataDict:
            item['__dataSource'] = 'private'
            # Fix for a bug. This should only be needed short term until the data is updated next.
            if item['name'] == 'Devimon Fire Blast' and item['race'] == 8:
                item['__bugfixActive'] = True
                item['race'] = 25
            itemDataDict[item['id']] = item

            nameParts = SplitNameIntoBaseNameAndItemLevel(item['name'])
            nameLower = nameParts['fullNameMinusLevel'].lower().replace('_', ' ')
            if not nameLower in itemBaseNameList:
                itemBaseNameList.append(nameLower)

    #  Generate the item data list from the data dictionary
    itemData = [ v for k,v in itemDataDict.items() ]


def ApplyCraftingDataWorkarounds():
    item = GetItemById('pcdv1')  # Double Positronic Convergence Disc
    craftingData = GetCraftingDataForItem(item)
    if craftingData is None:
        loc = GetItemBPLocation(item)
        ingredients = []
        ingredients.append({ "name": "300 x Yttrium", "mineralID": "Yt", "quantityRequired": 300.0 })
        ingredients.append({ "name": "500 x Silicon", "mineralID": "Si", "quantityRequired": 500.0 })
        ingredients.append({ "name": "50 x Gold", "mineralID": "Au", "quantityRequired": 50.0 })
        itemCraftableData['Double_Positronic_Convergence_Disc_(Unlocked_0)'] = {'name': 'Double Positronic Convergence Disc (Unlocked 0)', 'levels': 1, 'locations': [loc], 'ingredients': ingredients, 'items': ['pcdv1'], '__dataSource': 'override'}

def Initialize():
    global itemIdListToSkip, beamWeaponOverrideIdList, rarePlayerRaceDropIdList
    LoadItemInformation()
    PrepareItemDataPrimaryList()
    ApplyCraftingDataWorkarounds()

    beamWeaponOverrideIdList = [ GetItemByName(n)['id'] for n in beamWeaponOverrideList ]
    rarePlayerRaceDropIdList = [ GetItemByName(n)['id'] for n in rarePlayerRaceDropList ]

    for item in itemData:
        if GetItemBPLocation(item) == 'N/A':
            itemIdListToSkip.append(item['id'])
            continue

        if 'equipCategory' in item and item['equipCategory'] == 7:
            itemIdListToSkip.append(item['id'])
            continue

        for skipItem in itemsToSkip:
            if item['name'].lower() == skipItem.lower():
                itemIdListToSkip.append(item['id'])

    # for race in SmallConstants.raceData:
    #     itemIdListToSkip += race['omitFromLoot']
    #     itemIdListToSkip += race['dontUse']



def LoadItemInformation():
    global itemDataPrivate, itemDataPublic, itemRangeData, itemVariantData, itemCraftableData

    # Load item data provided publicly on the Starfighter: Infinity website
    itemDataPublic = DataLoader.LoadItemDataFromPublicStarfighterWebsite()

    # Load item data provided by Ben Olding
    itemDataPrivate = DataLoader.LoadWeaponDataFromBenOldingWebsite()
    itemRangeData = DataLoader.LoadWeaponRangesDataFromBenOldingWebsite()
    itemVariantData = DataLoader.LoadWeaponVariantDataFromBenOldingWebsite()
    itemCraftableData = DataLoader.LoadWeaponCraftableDataFromBenOldingWebsite()

    return True


Initialize()
