#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import json
import os
import html
import decimal
import requests
from collections import OrderedDict
from contextlib import suppress
from SFIWikiBotLib import Config
from SFIWikiBotLib import SmallConstants
from SFIWikiBotLib import GeneralUtils
from SFIWikiBotLib import WikiUtils
from SFIWikiBotLib import DataLoader
from SFIWikiBotLib import PresetList



shipBaseSpeedMult = 1.25;
shipAccelMult = 80;
# shipPurchasePriceModifier = 1.17645
shipPurchasePriceModifier = 1 / 0.85

shipTypeLookup = [ 'Small Ship', 'Turret', 'Drone', 'Boss Ship', 'Escape Pod', 'CC / Elite Ship', 'Capital Ship', 'Dogfighter', 'Warship', 'Mining Ship', 'Special Non-Player Ship', 'Megaboss', 'Converted Drone' ]


shipData = None
shipDataDict = None
shipDataPublic = None


shipTurretMapping = {
    'accumulator': 3,
    'demeter': 3,
    'annihilator': 3,
    'imposer': 2,
    'diomedes': 2,
}


def DownloadMissingImagesForTheWikiByShipList(shipList):
    rtnVal = 0
    for ship in shipList:
        wikiImage = GetShipWikiImage(ship)
        if not wikiImage:
            if DownloadImageForShip(ship):
                rtnVal += 1

    return rtnVal


def DownloadImagesByShipList(shipList):
    rtnVal = 0
    for ship in shipList:
        if DownloadImageForShip(ship):
            rtnVal += 1

    return rtnVal


def DownloadImageForShip(ship):
    rtnVal = False
    fileName = ship['name'].lower()

    filedir = os.path.join('public', 'images', 'Ship')
    os.makedirs(filedir, exist_ok=True)

    filepath = os.path.join(filedir, "{}.png".format(fileName))
    if not os.path.exists(filepath):
        try:
            url = GetShipImageUrl(ship)
            r = requests.get(url)
            if r.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(r.content)
                    if Config.verbose >= 1:  print(ship['name'], "- Image saved successfully")
                    rtnVal = True
            else:
                if Config.verbose >= 1:  print("Image not found for ship", ship['name'])

        except:
            print("{} - failed to save the image\nUrl: [{}]\nLocal path [{}]\n\n".format(ship['name'], url, filepath))
            raise

    return rtnVal


def FindShipsByPartialName(name, objList=...):
    if objList is ...:
        objList = shipData
    ruleSet = { "condition": "OR", "rules": [ { "id": "name", "operator": "contains", "value": name } ] }
    return GeneralUtils.SearchObjectListUsingRuleset(objList, ruleSet)


def GetAralienPlayerShipList(sortBy='name'):
    ruleSet = PresetList.shipPresetList['Aralien Ships']['ruleSet']
    return sorted(GeneralUtils.SearchObjectListUsingRuleset(shipData, ruleSet), key=GetShipSortFunc(sortBy))


def GetCategoryListForShip(ship):
    rtnSet = set()

    nprName = GetRaceForShip(ship)
    if nprName.lower() == 'meteor burger':
        rtnSet.add('Meteor Burger')
    else:
        nprPageName = WikiUtils.GetNprWikiPageByNprName(nprName)
        if nprPageName:
            rtnSet.add(nprPageName)

    shipType = GetShipUseCategory(ship)
    if shipType == 'Human':
        rtnSet.add('Human Ships')
        rtnSet.add('Ships')
    elif shipType == 'Aralien':
        rtnSet.add('Aralien Ships')
        rtnSet.add('Ships')
    elif shipType == 'NPC':
        rtnSet.add('Restricted Ships')
    elif shipType == 'NPR':
        rtnSet.add('NPR Ships')

    return sorted(list(rtnSet))


def GetDefaultTableInfo(pageType=''):
    rtnInfo = {
        'tableHeader': None,
        'tableCaption': None,
        'tableClassNames': 'wikitable sortable',
        # 'tableColumnList': [ "Name", "Shields", "Lock Angle", "Speed", "Accel", "Turn", "Shield Size", "Mass", "Slots (S/U/M/P/L/A)", "Drop %" ],
        'tableColumnList': ['Ship','Sh','Sp','T','Ac','La','Ma','C','Tu','Ra','Le','S','U','M','P','L','A'],
        'tableColumnTitleList': [],
    }


    if pageType:  pageType = pageType.lower()
    if pageType == 'npr':
        try:
            index = rtnInfo['tableColumnList'].index('Tu')
            rtnInfo['tableColumnList'] = rtnInfo['tableColumnList'][:index] + rtnInfo['tableColumnList'][index+1:]
            rtnInfo['tableColumnTitleList'] = rtnInfo['tableColumnTitleList'][:index] + rtnInfo['tableColumnTitleList'][index+1:]
        except ValueError:
            pass

        try:
            index = rtnInfo['tableColumnList'].index('Le')
            rtnInfo['tableColumnList'] = rtnInfo['tableColumnList'][:index] + rtnInfo['tableColumnList'][index+1:]
            rtnInfo['tableColumnTitleList'] = rtnInfo['tableColumnTitleList'][:index] + rtnInfo['tableColumnTitleList'][index+1:]
        except ValueError:
            pass
        rtnInfo['tableColumnList'].append('D')

    rtnInfo['tableColumnTitleList'] = GetStatNameDescriptions(rtnInfo['tableColumnList'], pageType)

    return rtnInfo


def GetDisplayDataForShipList(shipList, headingList):
    tableData = []

    for ship in shipList:
        row = OrderedDict()
        for heading in headingList:
            row[heading] = GetHtmlStatDisplayForObject(heading, ship)
        tableData.append(row)

    return tableData


def GetHumanPlayerShipList(sortBy='name'):
    ruleSet = PresetList.shipPresetList['Human Ships']['ruleSet']
    return sorted(GeneralUtils.SearchObjectListUsingRuleset(shipData, ruleSet), key=GetShipSortFunc(sortBy))


def GetImageUploadDownloadInfoForShip(ship):
    filepath = os.path.join('public', 'images', 'Ship', "{}.png".format(ship['name'].lower()))
    rtnVal = {
        'description': 'Ship - {}'.format(ship['name']),
        'exists': os.path.exists(filepath),
        'filepath': filepath,
        'filename': "{}.png".format(ship['name'].lower()),
        'name': "Ship_{}.png".format(ship['name'].replace(' ', '_')),
        'url': GetShipImageUrl(ship),
        'subDir': "Ship",
    }

    return rtnVal


def GetListOfShipsMissingWikiPages(includeHidden=False):
    if includeHidden:
        return [ v for v in shipData if not GetShipWikiPageName(v) ]
    else:
        return [ v for v in shipData if not GetShipWikiPageName(v) and not IsShipHidden(v) ]


def GetMaxSpeedForShip(ship):
    try:
        return ship['maxSpeed'] * shipBaseSpeedMult
    except:
        return 0



def GetNPRShipList(race, includeHidden=True):
    if includeHidden:
        if race == 'Ghost':
            ruleSet = {'condition': 'AND', 'rules': [{'condition': 'OR', 'rules': [{'field': 'ShipUtils.GetRaceForShip', 'type': 'string', 'input': 'select', 'id': 'ShipUtils.GetRaceForShip', 'value': 'Human Ghost', 'operator': 'equal'}, {'field': 'ShipUtils.GetRaceForShip', 'type': 'string', 'input': 'select', 'id': 'ShipUtils.GetRaceForShip', 'value': 'Aralien Ghost', 'operator': 'equal'}]}], 'valid': True}
        else:
            ruleSet = {'condition': 'AND', 'rules': [{'field': 'ShipUtils.GetRaceForShip', 'type': 'string', 'input': 'select', 'id': 'ShipUtils.GetRaceForShip', 'value': race, 'operator': 'equal'}], 'valid': True}
    else:
        if race == 'Ghost':
            ruleSet = {'condition': 'AND', 'rules': [{'field': 'ShipUtils.IsShipHidden', 'type': 'boolean', 'input': 'radio', 'id': 'ShipUtils.IsShipHidden', 'value': False, 'operator': 'equal'}, {'condition': 'OR', 'rules': [{'field': 'ShipUtils.GetRaceForShip', 'type': 'string', 'input': 'select', 'id': 'ShipUtils.GetRaceForShip', 'value': 'Human Ghost', 'operator': 'equal'}, {'field': 'ShipUtils.GetRaceForShip', 'type': 'string', 'input': 'select', 'id': 'ShipUtils.GetRaceForShip', 'value': 'Aralien Ghost', 'operator': 'equal'}]}], 'valid': True}
        else:
            ruleSet = {'condition': 'AND', 'rules': [{'field': 'ShipUtils.IsShipHidden', 'type': 'boolean', 'input': 'radio', 'id': 'ShipUtils.IsShipHidden', 'value': False, 'operator': 'equal'}, {'field': 'ShipUtils.GetRaceForShip', 'type': 'string', 'input': 'select', 'id': 'ShipUtils.GetRaceForShip', 'value': race, 'operator': 'equal'}], 'valid': True}

    filteredShipList = GeneralUtils.SearchObjectListUsingRuleset(shipData, ruleSet)
    filteredShipList = sorted(filteredShipList, key=GetShipSortFunc(''))

    return filteredShipList


def GetFullNPRShipList(sortBy='name'):
    ruleSet = PresetList.shipPresetList['NPR Ships']['ruleSet']
    return sorted(GeneralUtils.SearchObjectListUsingRuleset(shipData, ruleSet), key=GetShipSortFunc(sortBy))


def GetNPRBossShipList(raceId):
    ruleList = [
        { 'id': 'race', 'op': '==', 'val': raceId, },
        { 'id': 'shipType', 'op': '==', 'val': 3, },
    ]
    return sorted(GeneralUtils.SearchObjectListUsingSimpleRules(shipData, ruleList), key=GetShipSortFunc())


def GetPublicDatabaseShipData():
    shipListMinimalInfo = DataLoader.LoadShipDataFromPublicStarfighterWebsite()
    shipList = []
    for ship in shipListMinimalInfo:
        fullShipInfo = ExpandMinimalShipInformation(ship)
        shipList.append(fullShipInfo)

    return shipList


def GetRaceForShip(ship):
    return SmallConstants.GetNprNameFromId(ship['race'])


def GetRestrictedShipList(sortBy='name'):
    ruleSet = PresetList.shipPresetList['Restricted Ships']['ruleSet']
    return sorted(GeneralUtils.SearchObjectListUsingRuleset(shipData, ruleSet), key=GetShipSortFunc(sortBy))


def GetShipById(id, objList=...):
    if objList is ...:
        objList = shipData

    for v in objList:
        if v['id'] == id:
            return v

    return None


def GetShipDescription(ship, useHtmlForLinks=False):
    if 'description' in ship:
        return GeneralUtils.AddWikiLinksToText(ship['description'], useHtmlForLinks, allowExtraWeaponCheck=False)


def GetShipImageUrl(ship):
    return "https://www.benoldinggames.co.uk/sfi/gamedata/icons/allitems/{}.png".format(ship['name'].lower().replace(' ', '%20'))


def GetShipUseCategory(ship):
    if ship in GetHumanPlayerShipList():
        return 'Human'
    elif ship in GetAralienPlayerShipList():
        return 'Aralien'
    elif ship in GetRestrictedShipList():
        return 'NPC'
    elif ship in GetFullNPRShipList():
        return 'NPR'


def GetShipPageContent(ship):
    if not ship:
        return ''

    shipType = GetShipUseCategory(ship)

    pageHeader = '__NOTOC__\n'
    pageFooter = ''
    mainPageTemplateName = ''

    if shipType == 'Human' or shipType == 'Aralien':
        pageFooter = '\n{{Template:Human Ships}}\n{{Template:Aralien Ships}}\n'
        mainPageTemplateName = 'PlayerShipLayout'
    elif shipType == 'NPC':
        pageFooter = '\n{{Template:Restricted Ships}}\n'
        mainPageTemplateName = ''
    elif shipType == 'NPR':
        pageFooter = '\n{{Template:NPR Ships}}\n'
        mainPageTemplateName = 'NPRShip'

    shipCatList = GetCategoryListForShip(ship)
    for catName in shipCatList:
        pageFooter += '[[Category:{}]]\n'.format(catName)

    infoBox = GetWikiInfoboxDataForShip(ship)

    mainPage = OrderedDict()
    if mainPageTemplateName == 'PlayerShipLayout':
        mainPage['GameDescription'] = GetShipDescription(ship)
        mainPage['Traits'] = ''
        mainPage['Equipment'] = ''
        mainPage['Notes'] = ''
        mainPage['Trivia'] = ''
    elif mainPageTemplateName == 'NPRShip':
        nprPageName = WikiUtils.GetNprWikiPageByNprName(GetRaceForShip(ship))
        mainPage['shipName'] = ship['name']
        mainPage['nprName'] = nprPageName
        mainPage['Description'] = ''  # Where NPR ships have descriptions in the exported data it tends to be wrong, a copy of playable ships
        mainPage['Combat and Strategy'] = ''
        mainPage['Notes'] = ''

    if not mainPageTemplateName:
        introSection = ''
        gameDescriptionSection = "== Game Description ==\n{}\n".format(GeneralUtils.AddWikiLinksToText(ship['description'], useHtml=False, allowExtraWeaponCheck=False) if 'description' in ship else '')
        overviewSection = "== Overview ==\n"
        npcCombatSection = "== NPC Combat ==\n"
        purchaseLocationsSection = "== Purchase Locations ==\n"
        notesSection = "== Notes ==\n"
        gallerySection = '== Gallery ==\n{| class="article-table"\n!\n!\n!\n|}\n'

    content = pageHeader
    content += WikiUtils.ConvertDictionaryToWikiTemplate('Infobox_Ship', infoBox).strip()
    if mainPageTemplateName:
        content += WikiUtils.ConvertDictionaryToWikiTemplate(mainPageTemplateName, mainPage).strip()
    else:
        content += introSection
        content += gameDescriptionSection
        content += overviewSection
        content += npcCombatSection
        content += purchaseLocationsSection
        content += notesSection
        content += gallerySection
    content += pageFooter

    return content



def GetShipPurchasePrice(ship):
    if 'price' not in ship:
        return ''
    return int(GeneralUtils.RoundToSignificantAmount(ship['price'] * shipPurchasePriceModifier))


def GetShipWikiImage(ship):
    # shipNameList = [ "Ship {}".format(ship['name']), ship['name'], "{} (Ship)".format(ship['name']), ship['name'].replace(' ', '') ]
    shipNameList = [ "Ship {}".format(ship['name']) ]
    return WikiUtils.GetWikiImageForNameList(shipNameList)


def GetShipWikiImageForInfobox(ship):
    shipNameList = [ "{} Standard".format(ship['name']) ]
    rtnVal = WikiUtils.GetWikiImageForNameList(shipNameList)
    if not rtnVal:
        rtnVal = GetShipWikiImage(ship)
    return rtnVal


def GetShipWikiPageName(ship):
    shipNameList = [ ship['name'], "Ship {}".format(ship['name']), "{} (Ship)".format(ship['name']), ship['name'].replace(' ', '') ]
    return WikiUtils.GetWikiArticlePageForNameList(shipNameList)



def GetWikiDisplayDataForShipPage(ship):
    tableData = []

    for ship in shipList:
        row = OrderedDict()
        for heading in headingList:
            row[heading] = GetStatDisplayForObject(heading, ship)
        tableData.append(row)

    return tableData


def GetWikiDisplayDataForShipList(shipList, headingList):
    tableData = []

    for ship in shipList:
        row = OrderedDict()
        for heading in headingList:
            row[heading] = GetStatDisplayForObject(heading, ship)
        tableData.append(row)

    return tableData


def GetWikiInfoboxDataForShip(ship):
    # Template name is   Infobox_Ship
    infobox = OrderedDict()
    infobox['race'] = GetRaceForShip(ship)
    infobox['title1'] = ship['name']

    image = GetShipWikiImageForInfobox(ship)
    if image:
        infobox['image1'] = image
    if ShipCanBeBoughtByPlayers(ship) and 'Pod' not in ship['name']:
        if ship['unlockLevel'] == 0:
            infobox['unlock_level'] = "Available Immediately"
        else:
            infobox['unlock_level'] = ship['unlockLevel']
    if 'price' in ship and ship['race'] <= 1:
        infobox['price'] = GeneralUtils.NumDisplay(GetShipPurchasePrice(ship), 0, True)
    if 'lifePrice' in ship and ship['race'] <= 1:
        infobox['life_cost'] = GeneralUtils.NumDisplay(ship['lifePrice'], 0, True)
    infobox['shields'] = GeneralUtils.NumDisplay(ship['maxShield'], 3, True)
    infobox['speed'] = GeneralUtils.NumDisplay(GetMaxSpeedForShip(ship), 3)
    infobox['acceleration'] = GeneralUtils.NumDisplay(ship['accel'] * shipAccelMult, 1)
    infobox['turning'] = "{}°/s".format(GeneralUtils.NumDisplay(ship['turning'] * 30, 3))
    infobox['locking'] = "{}°".format(GeneralUtils.NumDisplay(ship['lockingAngle'], 0))
    infobox['mass'] = GeneralUtils.NumDisplay(ship['mass'], 1)
    if ship['race'] <= 1 and 'buyable' in ship and ship['buyable']:
        if 'isHighMass' in ship and ship['isHighMass']:
            infobox['mass'] += "&nbsp;&nbsp;&nbsp;&nbsp; [[:Category:Mass-Restricted_Systems|(High Mass Ship)]]"
        elif 'isLowMass' in ship and ship['isLowMass']:
            infobox['mass'] += "&nbsp;&nbsp;&nbsp;&nbsp; [[:Category:Mass-Restricted_Systems|(Low Mass Ship)]]"
    if 'shieldSize' in ship and GeneralUtils.floatCmp(ship['shieldSize'], '>', 0):
        infobox['shield_radius'] = GeneralUtils.NumDisplay(ship['shieldSize'], 2)
    if 'cargoAmount' in ship and ship['race'] <= 1:
        infobox['cargo'] = GeneralUtils.NumDisplay(ship['cargoAmount'], 0)
    if ship['standardSecondary'] > 0:
        infobox['standard'] = str(ship['standardSecondary'])
    if ship['utilitySecondary'] > 0:
        infobox['utility'] = str(ship['utilitySecondary'])
    if ship['mineSecondary'] > 0:
        infobox['mine'] = str(ship['mineSecondary'])
    if ship['proximitySecondary'] > 0:
        infobox['proximity'] = str(ship['proximitySecondary'])
    if ship['largeSecondary'] > 0:
        infobox['large'] = str(ship['largeSecondary'])
    infobox['augmentations'] = str(ship['augmentations'])
    if 'turrets' in ship:
        infobox['turrets'] = ship['turrets']
    elif 'turretSlot' in ship:
        infobox['turrets'] = 'Yes' if ship['turretSlot'] else 'No'

    return infobox


def GetTypeForShip(ship):
    try:
        return shipTypeLookup[ship['shipType']]
    except:
        return None


def IsShipHidden(ship):
    with suppress(KeyError):
        if SmallConstants.GetNprNameFromId(ship['race']) in Config.unreleasedRaceList:
            return True

    if ship['name'].lower() in [ v.lower() for v in Config.unreleasedShipList ]:
        return True

    return False


def NormalizeShipName(name):
    return name.lower().replace(' ', '_')


def ShipCanBeBoughtByPlayers(ship):
    return ship['race'] <= 1 \
            and (ship['buyable'] or 'Pod' in ship['name']) \
            and (GetTypeForShip(ship) not in ['Drone', 'Turret', 'Special Non-Player Ship', 'Megaboss']) \
            and not IsShipHidden(ship)



def UploadImagesToWikiForShipList(shipList):
    shipImageInfoList = [ GetImageUploadDownloadInfoForShip(s) for s in shipList ]
    return WikiUtils.UploadImageListToWiki(shipImageInfoList)





### Ship stat display functions

def ShipDisplayStatName(ship, p=...):
    displayName = ship['name']

    shipArticlePage = GetShipWikiPageName(ship)
    if shipArticlePage:
        if WikiUtils.PageNamesEqual(shipArticlePage, ship['name']):
            displayName = '[[{}]]'.format(ship['name'])
        else:
            displayName = '[[{}|{}]]'.format(shipArticlePage, ship['name'])

    return displayName


def ShipDisplayStatImage(ship, p=...):
    rtnVal = ""

    imageName = GetShipWikiImage(ship)
    if imageName:
        rtnVal = '[[File:{}|thumb|55x55px]]'.format(imageName)

    return rtnVal


def ShipDisplayStatImageAndName(ship, p=...):
    rtnVal = ""

    imageName = GetShipWikiImage(ship)
    pageName = GetShipWikiPageName(ship)
    if not pageName:  pageName = ship['name']

    shipName = ship['name'].replace("Commander Class Escape", "CC E")
    shipName = shipName.replace("Commander Class", "CC")
    shipName = shipName.replace("Admiral Class", "AC")
    shipName = shipName.replace("Converted Armoured", "CAr")
    shipName = shipName.replace("Converted Attack", "CAt")
    shipName = shipName.replace("Converted Weapon", "CW")
    shipName = shipName.replace("Converted Heavy", "CH")
    shipName = shipName.replace("Elite Survivor", "E S")
    if imageName:
        rtnVal = 'align="center" style="font-size: smaller" | [[File:{}|centre|thumb|60x60px|link={}]]<br/>[[{}{}]]'.format(imageName, pageName, pageName, '' if pageName == shipName else '|{}'.format(shipName))
    else:
        rtnVal = 'align="center" style="font-size: smaller" | [[{}{}]]'.format(pageName, '' if WikiUtils.PageNamesEqual(pageName, ship['name']) else '|{}'.format(ship['name']))

    return rtnVal


def ShipDisplayStatNameHtml(ship, p=...):
    displayName = html.escape(ship['name'])

    shipArticlePage = GetShipWikiPageName(ship)
    if shipArticlePage:
        displayName = '<a href="{}">{}</a>'.format(
            WikiUtils.GetWikiLink(shipArticlePage),
            displayName
        )

    return displayName


def ShipDisplayStatImageHtml(ship, p=...):
    rtnVal = ''

    wikiImage = GetShipWikiImage(ship)
    if wikiImage:
        iconUrl = GetShipImageUrl(ship)
        if iconUrl:
            rtnVal = '<img src="{}" width="55" height="55" onError="this.onerror = \'\';this.style.visibility=\'hidden\';">'.format(iconUrl)

    return rtnVal


def ShipDisplayStatImageAndNameHtml(ship, p=...):
    rtnVal = ""

    pageName = GetShipWikiPageName(ship)
    if not pageName:  pageName = ship['name']
    wikiUrl = WikiUtils.GetWikiLink(pageName)

    imageName = GetShipWikiImage(ship)

    shipName = ship['name'].replace("Commander Class Escape", "CC E")
    shipName = shipName.replace("Commander Class", "CC")
    shipName = shipName.replace("Admiral Class", "AC")
    shipName = shipName.replace("Converted Armoured", "CAr")
    shipName = shipName.replace("Converted Attack", "CAt")
    shipName = shipName.replace("Converted Weapon", "CW")
    shipName = shipName.replace("Converted Heavy", "CH")
    shipName = shipName.replace("Elite Survivor", "E S")
    if imageName:
        iconUrl = GetShipImageUrl(ship)
        rtnVal = '<div style="text-align:center; font-size:smaller"><a href="{}"><img src="{}" width="60" height="60" onError="this.onerror = \'\';this.style.visibility=\'hidden\';"><br />{}</a></div>'.format(wikiUrl, iconUrl, shipName)
    else:
        rtnVal = '<div style="text-align:center;"><a href="{}">{}</a></div>'.format(wikiUrl, shipName)

    return rtnVal


def ShipDisplayStatPurchasePrice(ship, p=...):
    rtnVal = ""
    return rtnVal



### Generic stat display
def ShipDisplayStatGeneric(ship, p=...):
    try:
        return ship[p]
    except:
        print("{} not found".format(p))
    return ""


shipDisplayStatSwitcher = {
    'ac': (lambda obj, p: GeneralUtils.NumDisplay(obj['accel'] * shipAccelMult, 1)),
    'accel': (lambda obj, p: GeneralUtils.NumDisplay(obj['accel'] * shipAccelMult, 1)),
    'a': (lambda obj, p: obj['augmentations']),
    'augmentations': (lambda obj, p: obj['augmentations']),
    'buyable': (lambda obj, p: "Yes" if ShipCanBeBoughtByPlayers(obj) else "No"),
    'c': (lambda obj, p: obj['cargoAmount']),
    'cargo': (lambda obj, p: obj['cargoAmount']),
    'cockpit': (lambda obj, p: "Normal" if obj['cockpit'] == 0 else "Capital"),
    'description': (lambda obj, p: GeneralUtils.AddWikiLinksToText(obj['description'], useHtml=False, allowExtraWeaponCheck=False)),
    'drop %': (lambda obj, p: "{}%".format(GeneralUtils.NumDisplay(obj['specialDropLikelihood'] * 100, 1)) if obj['race'] > 1 else ""),
    'd': (lambda obj, p: "{}%".format(GeneralUtils.NumDisplay(obj['specialDropLikelihood'] * 100, 1)) if obj['race'] > 1 else ""),
    'high mass': (lambda obj, p: "Yes" if obj['isHighMass'] else "No"),
    'image': ShipDisplayStatImage,
    'img': ShipDisplayStatImageAndName,
    'l': (lambda obj, p: obj['largeSecondary']),
    'large slots': (lambda obj, p: obj['largeSecondary']),
    'le': (lambda obj, p: obj['unlockLevel']),
    'level': (lambda obj, p: obj['unlockLevel']),
    'life cost': (lambda obj, p: GeneralUtils.NumDisplay(obj['lifePrice'], 0, True)),
    'la': (lambda obj, p: "{}°".format(GeneralUtils.NumDisplay(obj['lockingAngle'], 2)) if obj['lockingAngle'] > 0 else ""),
    'lock angle': (lambda obj, p: "{}°".format(GeneralUtils.NumDisplay(obj['lockingAngle'], 2)) if obj['lockingAngle'] > 0 else ""),
    'low mass': (lambda obj, p: "Yes" if obj['isLowMass'] else "No"),
    'ma': (lambda obj, p: GeneralUtils.NumDisplay(obj['mass'], 2)),
    'mass': (lambda obj, p: GeneralUtils.NumDisplay(obj['mass'], 2)),
    'm': (lambda obj, p: obj['mineSecondary']),
    'mine slots': (lambda obj, p: obj['mineSecondary']),
    'name': ShipDisplayStatName,
    'price unmodified': (lambda obj, p: GeneralUtils.NumDisplay(obj['price'], 0, True)),
    'p': (lambda obj, p: obj['proximitySecondary']),
    'proximity slots': (lambda obj, p: obj['proximitySecondary']),
    'race': (lambda obj, p: SmallConstants.GetNprNameFromId(obj['race'])),
    'sh': (lambda obj, p: GeneralUtils.NumDisplay(obj['maxShield'], 0, True)),
    'shields': (lambda obj, p: GeneralUtils.NumDisplay(obj['maxShield'], 0, True)),
    'ra': (lambda obj, p: GeneralUtils.NumDisplay(obj['shieldSize'], 2)),
    'shield size': (lambda obj, p: GeneralUtils.NumDisplay(obj['shieldSize'], 2)),
    'ship': ShipDisplayStatImageAndName,
    'ship cost': (lambda obj, p: GeneralUtils.NumDisplay(GetShipPurchasePrice(obj), 0, True)),
    'ship type': (lambda obj, p: GetTypeForShip(obj)),
    'slots (s/u/m/p/l/a)': (lambda obj, p: "{} / {} / {} / {} / {} / {}".format(obj['standardSecondary'], obj['utilitySecondary'], obj['mineSecondary'], obj['proximitySecondary'], obj['largeSecondary'], obj['augmentations'])),
    'sp': (lambda obj, p: GeneralUtils.NumDisplay(GetMaxSpeedForShip(obj), 3)),
    'speed': (lambda obj, p: GeneralUtils.NumDisplay(GetMaxSpeedForShip(obj), 3)),
    's': (lambda obj, p: obj['standardSecondary']),
    'standard slots': (lambda obj, p: obj['standardSecondary']),
    'turn': (lambda obj, p: "{}°/s".format(GeneralUtils.NumDisplay(obj['turning'] * 30, 2)) if obj['turning'] > 0 else ""),
    't': (lambda obj, p: "{}°".format(GeneralUtils.NumDisplay(obj['turning'] * 30, 2)) if obj['turning'] > 0 else ""),
    'tu': (lambda obj, p: obj['turrets'] if 'turrets' in obj else ("1" if obj['turretSlot'] else "0")),
    'turret': (lambda obj, p: "Yes" if obj['turretSlot'] else "No"),
    'u': (lambda obj, p: obj['utilitySecondary']),
    'utility slots': (lambda obj, p: obj['utilitySecondary']),
}

shipDisplayStatSwitcherHtml = shipDisplayStatSwitcher.copy()
shipDisplayStatSwitcherHtml['name'] = ShipDisplayStatNameHtml
shipDisplayStatSwitcherHtml['img'] = ShipDisplayStatImageAndNameHtml
shipDisplayStatSwitcherHtml['ship'] = ShipDisplayStatImageAndNameHtml
shipDisplayStatSwitcherHtml['image'] = ShipDisplayStatImageHtml
shipDisplayStatSwitcherHtml['description'] = (lambda obj, p: GeneralUtils.AddWikiLinksToText(obj['description'], useHtml=True, allowExtraWeaponCheck=False))


def GetStatDisplayForObject(propName, obj):
    rtnVal = ""
    try:
        func = shipDisplayStatSwitcher.get(propName.lower(), ShipDisplayStatGeneric)
        rtnVal = func(obj, propName)
    except:
        pass
    return rtnVal


def GetHtmlStatDisplayForObject(propName, obj):
    rtnVal = ""

    try:
        func = shipDisplayStatSwitcherHtml.get(propName.lower(), ShipDisplayStatGeneric)
        rtnVal = func(obj, propName)
    except:
        pass
    return rtnVal




# Get relevant stat descriptions
shipStatDescriptionSwitcher = {
    'ac': (lambda s, pt: "Acceleration"),
    'accel': (lambda s, pt: "Acceleration"),
    'a': (lambda s, pt: "Augmentation Slots"),
    'augmentations': (lambda s, pt: "Augmentation Slots"),
    'buyable': (lambda s, pt: "Can be Purchased by Players (Yes/No)"),
    'c': (lambda s, pt: "Cargo Space"),
    'cargo': (lambda s, pt: "Cargo Space"),
    'cockpit': (lambda s, pt: "The cockpit style this ship uses"),
    'description': (lambda s, pt: "Game description for this ship"),
    'drop %': (lambda s, pt: "Special Drop Likelihood"),
    'd': (lambda s, pt: "Special Drop Likelihood"),
    'high mass': (lambda s, pt: "Ship is considered High Mass (Yes/No)"),
    # 'image': (lambda s, pt: ""),
    'img': (lambda s, pt: "Ship Image"),
    'l': (lambda s, pt: "Large Slots"),
    'large slots': (lambda s, pt: "Large Slots"),
    'le': (lambda s, pt: "Unlock Level"),
    'level': (lambda s, pt: "Unlock Level"),
    # 'life cost': (lambda s, pt: ""),
    'la': (lambda s, pt: "Locking Angle in Degrees"),
    'lock angle': (lambda s, pt: "Locking Angle in Degrees"),
    'low mass': (lambda s, pt: "Ship is considered Low Mass (Yes/No)"),
    'ma': (lambda s, pt: "Ship Mass"),
    'mass': (lambda s, pt: "Ship Mass"),
    'm': (lambda s, pt: "Mine Slots"),
    # 'mine slots': (lambda s, pt: ""),
    # 'name': (lambda s, pt: ""),
    'price unmodified': (lambda s, pt: "Price as it appears in the data"),
    'p': (lambda s, pt: "Proximity Slots"),
    # 'proximity slots': (lambda s, pt: ""),
    'race': (lambda s, pt: "The race which uses this ship"),
    'sh': (lambda s, pt: "Shields"),
    # 'shields': (lambda s, pt: ""),
    'ra': (lambda s, pt: "Shield Radius"),
    'shield size': (lambda s, pt: "Shield Radius"),
    'ship': (lambda s, pt: "Ship Name/Image"),
    'ship cost': (lambda s, pt: "The price to purchase this ship"),
    'ship type': (lambda s, pt: "Type of ship"),
    'slots (s/u/m/p/l/a)': (lambda s, pt: "Ship slots (Standard, Utility, Mine, Proximity, Large, Augmentation)"),
    'sp': (lambda s, pt: "Max Ship Speed"),
    # 'speed': (lambda s, pt: ""),
    's': (lambda s, pt: "Standard Secondary Slots"),
    # 'standard slots': (lambda s, pt: ""),
    'turn': (lambda s, pt: "Turning (Degrees/sec)"),
    't': (lambda s, pt: "Turning (Degrees/sec)"),
    'tu': (lambda s, pt: "Number of Turret Mountpoints"),
    'turret': (lambda s, pt: "Can use Turret Augs (Yes/No)"),
    'u': (lambda s, pt: "Utility Slots"),
    # 'utility slots': (lambda s, pt: ""),
}


def GetStatNameDescriptions(statList, pageType=''):
    descList = []

    for statName in statList:
        descList.append(GetDescriptionForShipStatName(statName, pageType))

    return descList


def GetDescriptionForShipStatName(statName, pageType):
    rtnVal = ""

    try:
        func = shipStatDescriptionSwitcher.get(statName.lower(), (lambda s, pt: ""))
        rtnVal = func(statName, pageType)
    except:
        pass
    return rtnVal




# Begin Sorting Functions

def SortShipsByDefault(ship):
    if ship['race'] <= 1 and 'unlockLevel' in ship:
        if ship['unlockLevel'] > 0:
            myKey = "{:03d}-{:03d}-{}".format(ship['race'], ship['unlockLevel'], ship['name'].lower())
            # print(ship['name'], myKey)
            return myKey
        else:
            myKey = "{:03d}-000-{}".format(ship['race'], ship['name'].lower() if not 'Pod' in ship['name'] else 'aaaaaa-{}'.format(ship['name'].lower()))
            # print(ship['name'], myKey)
            return myKey
    else:
        if 'specialDropLikelihood' in ship:
            myKey = "{:03d}-{:06d}-{:03d}-{}".format(
                ship['race'],
                int(ship['maxShield']),
                int(GeneralUtils.NumDisplay(ship['specialDropLikelihood'] * 100, 0)),
                ship['name'].lower() if not 'Turret' in ship['name'] else 'zzzzzz-{}'.format(ship['name'])
            )
            # print(ship['name'], myKey)
            return myKey

    key = '999-999-{}'.format(ship['name'].lower())
    # print(ship['name'], myKey)
    return myKey


def SortShipsByUnlockLevel(ship):
    if ship['race'] <= 1:
        if 'unlockLevel' in ship and ship['unlockLevel'] > 0:
            myKey = "{:03d}-{}".format(ship['unlockLevel'], ship['name'].lower())
            return myKey
        else:
            myKey = "000-{}".format(ship['name'].lower() if not 'Pod' in ship['name'] else 'aaaaaa-{}'.format(ship['name'].lower()))
            return myKey
    myKey = "999-{}".format(ship['name'].lower())
    return myKey


def GetShipSortFunc(sortBy=''):
    try:
        if sortBy.lower() == "name":
            return lambda v : v['name'].lower()
        if sortBy.lower() == "race":
            return lambda v : "{:03d}-{}".format(v['race'], v['name'].lower())
        if sortBy.lower() == "unlocklevel":
            return SortShipsByUnlockLevel
    except:
        pass

    return SortShipsByDefault



# Begin Data Initialization Functions



def ExpandMinimalShipInformation(minShipInfo):
    massCmp = decimal.Decimal(minShipInfo['mass'])
    fullShipInfo = {
        'accel': minShipInfo['acceleration'] / shipAccelMult,
        'augmentations': minShipInfo['augmentations'],
        'buyable': True,
        'cargoAmount': minShipInfo['cargo'],
        'id': str(minShipInfo['shipid']),
        'isHighMass': massCmp >= 2,
        'isLowMass': massCmp <= 1.5,
        'lockingAngle': minShipInfo['locking'],
        'mass': float(minShipInfo['mass']),
        'maxShield': minShipInfo['shield'],
        'maxSpeed': minShipInfo['speed'] / shipBaseSpeedMult,
        'name': minShipInfo['name'],
        'race': minShipInfo['race'],
        'shieldSize': float(minShipInfo['shieldradius']),
        'turning': minShipInfo['turning'] / Config.turnMultiplier,
        'unlockLevel': minShipInfo['unlock'],
    }

    if 'turrets' in minShipInfo:
        fullShipInfo['turrets'] = minShipInfo['turrets']

    testName = fullShipInfo['name'].lower()
    if 'escape pod' in testName or 'turret' in testName:
        fullShipInfo['buyable'] = False

    shipSlotInfo = ExpandSecondaryWeaponsList(minShipInfo['secondaryweapons'])
    fullShipInfo.update(shipSlotInfo)

    return fullShipInfo


def ExpandSecondaryWeaponsList(weaponsStr):
    rtnVal = {
        '__dataSource': 'public',
        'standardSecondary': 0,
        'utilitySecondary': 0,
        'mineSecondary': 0,
        'proximitySecondary': 0,
        'largeSecondary': 0,
    }

    slotList = weaponsStr.split(', ')
    for slotInfo in slotList:
        slotInfo = slotInfo.split(' ')
        if slotInfo[1].lower() == 'standard':
            rtnVal['standardSecondary'] = int(slotInfo[0])
        elif slotInfo[1].lower() == 'utility':
            rtnVal['utilitySecondary'] = int(slotInfo[0])
        elif slotInfo[1].lower() == 'mine':
            rtnVal['mineSecondary'] = int(slotInfo[0])
        elif slotInfo[1].lower() == 'proximity':
            rtnVal['proximitySecondary'] = int(slotInfo[0])
        elif slotInfo[1].lower() == 'large':
            rtnVal['largeSecondary'] = int(slotInfo[0])

    return rtnVal


def Initialize():
    LoadShipInformation()



def LoadShipInformation():
    global shipData, shipDataDict

    shipDataDict = DataLoader.LoadShipDataFromBenOldingWebsite()
    for k,v in shipDataDict.items():
        shipDataDict[k]['description'] = v['description'].replace('Ã¢â‚¬Â?', '"').replace('Ã¢â‚¬Å“', '"')
        shipDataDict[k]['description'] = v['description'].replace('â€™', "'")
        shipDataDict[k]['description'] = v['description'].replace('\u00c3\u00a2\u00e2\u201a\u00ac\u00e2\u201e\u00a2', "'")
        shipDataDict[k]['description'] = v['description'].replace('\u00c3\u00af\u00c2\u00bf\u00c2\u00bd', "'")
        shipDataDict[k]['description'] = v['description'].replace('\u00e2\u20ac\u00a6', ".")

    shipData = [ v for k,v in shipDataDict.items() ]

    return True



Initialize()
