#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import json
import os
import time
import imghdr
import re
import urllib
import http.client
import requests
from collections import OrderedDict
from contextlib import suppress
from datetime import date, datetime
from diskcache import Cache
import mwclient
from SFIWikiBotLib import Config
from SFIWikiBotLib import SmallConstants
from SFIWikiBotLib import GeneralUtils
from pprint import pprint as pp
import pytz

tz = pytz.timezone('America/Chicago')


siteBackupPath = '/var/www/sf-wiki-mirror'


wikiClientSite = None

wikiServerName = 'starfighter-infinity.fandom.com'
wikiCache = Cache(directory=os.path.join(Config.cacheDir, 'cache.wiki'))





def GetPageInfoFromWiki(pageName):
    pageInformation = {
        "page": pageName,
        "hasNoTocFlag": None,
        "pageSectionList": [],
        "pageTemplateList": [],
        "pageTableList": [],
        "categoryList": [],
    }

    site = GetWikiClientSiteObject()
    page = site.pages[pageName]
    content = page.text()

    updatedContent = content.replace('__NOTOC__', '')
    if updatedContent != content:
        pageInformation['hasNoTocFlag'] = True
        content = updatedContent

    pageInformation['categoryList'] = GetCategoryListFromWikiPageContent(content)
    for category in pageInformation['categoryList']:
        content = content.replace(category['content'], '')

    pageInformation['pageTableList'] = GetTableListFromWikiPageContent(content)
    for table in pageInformation['pageTableList']:
        content = content.replace(table['content'], '')

    pageInformation['pageTemplateList'] = GetTemplateListFromWikiPageContent(content)
    for template in pageInformation['pageTemplateList']:
        content = content.replace(template['content'], '')

    pageInformation['pageSectionList'] = GetWikiPageSectionsFromContent(content.strip())

    return pageInformation


def PageNamesEqual(i1, i2):
    return NormalizePageName(i1) == NormalizePageName(i2)

def NormalizePageName(input):
    input = re.sub('[^a-zA-Z0-9\(\):-]', '_', str(input))
    return input


def GetNprWikiPageByNprName(nprName):
    if not nprName:  return None
    if type(nprName) != str:  return None

    if nprName.lower() == 'aralien ghost' or nprName.lower() == 'human ghost':
        nprName = 'ghost';

    for pageName, npr in Config.nprPageNameMapping.items():
        if npr.lower() == nprName.lower():
            return pageName



def ConvertNPRPageToNewFormat(race, content):
    rtnVal = None

    headerFields = [ 'Min Level Accessible', 'Lore Text', 'Credit Amount', 'Mineral', 'Mineral Amount', 'Commissioned By' ]
    footerFields = [ 'NPR Name', 'Name of hotspot/spawning relic', 'Systems/Sectors Found In', 'Associated relics', 'Misc Info', 'Trivia' ]
    templateList = GetTemplateListFromWikiPageContent(content)
    for template in templateList:
        if template['name'] == 'NPR':
            NPRHeader = OrderedDict()
            for field in headerFields:
                if field in template['data']:
                    NPRHeader[field] = template['data'][field]
            NPRFooter = OrderedDict()
            for field in footerFields:
                if field in template['data']:
                    NPRFooter[field] = template['data'][field]

            replacement = ConvertDictionaryToWikiTemplate('NPRHeader', NPRHeader)
            replacement += GetContentForNprPage(race)
            replacement += ConvertDictionaryToWikiTemplate('NPRFooter', NPRFooter)
            rtnVal = content.replace(template['content'], replacement)
            break

    return rtnVal


def GetContentSignatureListForNprPage(race):
    shipResult = GetRenderedNprPageShipList(race)
    itemResult = GetRenderedNprPageItemList(race)

    nprExclusiveItemList = True
    exclusiveItemResult = GetRenderedNprPageItemList(race, nprExclusiveItemList)

    rtnVal = {}
    try:
        rtnVal.update(shipResult['idSignatureMapping'])
    except:
        rtnVal[shipResult['id']] = shipResult['signature']
    try:
        rtnVal.update(itemResult['idSignatureMapping'])
    except:
        rtnVal[itemResult['id']] = itemResult['signature']
    try:
        rtnVal.update(exclusiveItemResult['idSignatureMapping'])
    except:
        rtnVal[exclusiveItemResult['id']] = exclusiveItemResult['signature']

    return rtnVal



def GetContentForNprPage(race):
    shipResult = GetRenderedNprPageShipList(race)
    itemResult = GetRenderedNprPageItemList(race)

    nprExclusiveItemList = True
    exclusiveItemResult = GetRenderedNprPageItemList(race, nprExclusiveItemList)

    rtnVal = """
== '''Ships''' ==
{}

== '''Drops ({})''' ==
{}
""".format(shipResult['content'], itemResult['resultCount'], itemResult['content'])

    if exclusiveItemResult['resultCount'] > 0:
        displayName = GetNprWikiPageByNprName(race)
        if 'the ' not in displayName.lower():
            displayName = 'the {}'.format(displayName)
        rtnVal += """
== '''NPR Exclusive Items ({})''' ==
These items are not obtainable by players. They can only be used by {}.
{}
""".format(exclusiveItemResult['resultCount'], displayName, exclusiveItemResult['content'])

    return rtnVal.strip()



def GetRenderedNprPageShipList(race):
    if race == 'Ghost':
        shipPs = {'tableColumnList': [], 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ShipUtils.IsShipHidden', 'type': 'boolean', 'input': 'radio', 'id': 'ShipUtils.IsShipHidden', 'value': False, 'operator': 'equal'}, {'condition': 'OR', 'rules': [{'field': 'ShipUtils.GetRaceForShip', 'type': 'string', 'input': 'select', 'id': 'ShipUtils.GetRaceForShip', 'value': 'Human Ghost', 'operator': 'equal'}, {'field': 'ShipUtils.GetRaceForShip', 'type': 'string', 'input': 'select', 'id': 'ShipUtils.GetRaceForShip', 'value': 'Aralien Ghost', 'operator': 'equal'}]}], 'valid': True}, 'tableCaption': '', 'name': 'NPR Ships', 'tableHeader': '', 'pageType': 'npr', 'useCustomTableOptions': 0, 'tableClassNames': ''}
    else:
        shipPs = {'tableColumnList': [], 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ShipUtils.IsShipHidden', 'type': 'boolean', 'input': 'radio', 'id': 'ShipUtils.IsShipHidden', 'value': False, 'operator': 'equal'}, {'field': 'ShipUtils.GetRaceForShip', 'type': 'string', 'input': 'select', 'id': 'ShipUtils.GetRaceForShip', 'value': race, 'operator': 'equal'}], 'valid': True}, 'tableCaption': '', 'name': 'NPR Ships', 'tableHeader': '', 'pageType': 'npr', 'useCustomTableOptions': 0, 'tableClassNames': ''}

    return RenderShipPreset(shipPs)


def GetRenderedNprPageItemList(race, nprExclusiveItemList=False):
    if not nprExclusiveItemList:
        if race == 'Ghost':
            itemPs = {'tableColumnList': [], 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsItemHidden', 'type': 'boolean', 'input': 'radio', 'id': 'ItemUtils.IsItemHidden', 'value': False, 'operator': 'equal'}, {'field': 'ItemUtils.IsItemNprExclusive', 'type': 'boolean', 'input': 'radio', 'id': 'ItemUtils.IsItemNprExclusive', 'value': False, 'operator': 'equal'}, {'condition': 'OR', 'rules': [{'field': 'ItemUtils.GetRaceForItem', 'type': 'string', 'input': 'select', 'id': 'ItemUtils.GetRaceForItem', 'value': 'Human Ghost', 'operator': 'equal'}, {'field': 'ItemUtils.GetRaceForItem', 'type': 'string', 'input': 'select', 'id': 'ItemUtils.GetRaceForItem', 'value': 'Aralien Ghost', 'operator': 'equal'}]}], 'valid': True}, 'tableCaption': '', 'name': 'NPR Items', 'tableHeader': '', 'pageType': 'npr', 'useCustomTableOptions': 0, 'tableClassNames': ''}
        else:
            itemPs = {'tableColumnList': [], 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsItemHidden', 'type': 'boolean', 'input': 'radio', 'id': 'ItemUtils.IsItemHidden', 'value': False, 'operator': 'equal'}, {'field': 'ItemUtils.IsItemNprExclusive', 'type': 'boolean', 'input': 'radio', 'id': 'ItemUtils.IsItemNprExclusive', 'value': False, 'operator': 'equal'}, {'field': 'ItemUtils.GetRaceForItem', 'type': 'string', 'input': 'select', 'id': 'ItemUtils.GetRaceForItem', 'value': race, 'operator': 'equal'}], 'valid': True}, 'tableCaption': '', 'name': 'NPR Items', 'tableHeader': '', 'pageType': 'npr', 'useCustomTableOptions': 0, 'tableClassNames': ''}
    else:
        if race == 'Ghost':
            itemPs = {'tableColumnList': [], 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsItemNprExclusive', 'type': 'boolean', 'input': 'radio', 'id': 'ItemUtils.IsItemNprExclusive', 'value': True, 'operator': 'equal'}, {'condition': 'OR', 'rules': [{'field': 'ItemUtils.GetRaceForItem', 'type': 'string', 'input': 'select', 'id': 'ItemUtils.GetRaceForItem', 'value': 'Human Ghost', 'operator': 'equal'}, {'field': 'ItemUtils.GetRaceForItem', 'type': 'string', 'input': 'select', 'id': 'ItemUtils.GetRaceForItem', 'value': 'Aralien Ghost', 'operator': 'equal'}]}], 'valid': True}, 'tableCaption': '', 'name': 'NPR Items', 'tableHeader': '', 'pageType': 'npr', 'useCustomTableOptions': 0, 'tableClassNames': ''}
        else:
            itemPs = {'tableColumnList': [], 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsItemNprExclusive', 'type': 'boolean', 'input': 'radio', 'id': 'ItemUtils.IsItemNprExclusive', 'value': True, 'operator': 'equal'}, {'field': 'ItemUtils.GetRaceForItem', 'type': 'string', 'input': 'select', 'id': 'ItemUtils.GetRaceForItem', 'value': race, 'operator': 'equal'}], 'valid': True}, 'tableCaption': '', 'name': 'NPR Items', 'tableHeader': '', 'pageType': 'npr', 'useCustomTableOptions': 0, 'tableClassNames': ''}

    includeHtml = False
    includeResultObjList = False
    removeUltraRaresFromResultCount = False
    return RenderItemPreset(itemPs, includeHtml, includeResultObjList, removeUltraRaresFromResultCount)


def GetRenderedSkillPageItemList(skillName, additionalClass=None, includeTableHeader=False):
    itemPsJson = '{"name":"Skill Item List","sortBy":"skillLevel","ruleSet":{"condition":"AND","rules":[{"id":"ItemUtils.IsItemHidden","field":"ItemUtils.IsItemHidden","type":"boolean","input":"radio","operator":"equal","value":false},{"id":"ItemUtils.GetItemSkillName","field":"ItemUtils.GetItemSkillName","type":"string","input":"select","operator":"equal","value":"' + skillName + '"},{"id":"ItemUtils.GetItemSkillLevel","field":"ItemUtils.GetItemSkillLevel","type":"integer","input":"number","operator":"greater","value":0},{"id":"ItemUtils.GetItemSource","field":"ItemUtils.GetItemSource","type":"string","input":"select","operator":"not_equal","value":"Rare Drop"},{"condition":"OR","rules":[{"id":"ItemUtils.GetRaceForItem","field":"ItemUtils.GetRaceForItem","type":"string","input":"select","operator":"equal","value":"Humans"},{"id":"ItemUtils.GetRaceForItem","field":"ItemUtils.GetRaceForItem","type":"string","input":"select","operator":"equal","value":"Aralien"}]}],"valid":true},"useCustomTableOptions":1,"tableHeader":"","tableCaption":"","tableClassNames":"wikitable sortable","tableColumnList":["Name","Type","Skill"]}'
    itemPs = json.loads(itemPsJson)
    if includeTableHeader:
        itemPs['tableHeader'] = skillName

    if additionalClass:
        itemPs['tableClassNames'] = '{} {}'.format(itemPs['tableClassNames'], additionalClass).strip()

    return RenderItemPreset(itemPs)


# For those times you only need read access
def GetWikiPageContent(pageName):
    site = GetWikiClientSiteObject()
    page = site.pages[pageName]
    if not page.exists:
        return False

    return page.text()


def GetWikiCategoryMemberList(catName):
    site = GetWikiClientSiteObject()
    cat = site.categories[catName]

    rtnList = []
    for page in cat.members():
        rtnList.append(page.name)

    return rtnList


def RenderShipPreset(preset, includeHtml=False, includeResultObjList=False, includeTableHeaders=True):
    from SFIWikiBotLib import ShipUtils

    if not includeTableHeaders:
        preset['tableHeader'] = ''
        preset['tableCaption'] = ''

    rtnVal = {
        'content': '',
        'resultCount': 0,
        'id': '',
        'signature': '',
    }
    if includeHtml:
        rtnVal['htmlContent'] = ''

    if 'pageType' not in preset:
        preset['pageType'] = ''
    if 'sortBy' not in preset:
        preset['sortBy'] = ''

    filteredShipList = GeneralUtils.SearchObjectListUsingRuleset(ShipUtils.shipData, preset['ruleSet'])
    filteredShipList = sorted(filteredShipList, key=ShipUtils.GetShipSortFunc(preset['sortBy']))
    rtnVal['resultCount'] = len(filteredShipList)
    if includeResultObjList:
        rtnVal['objList'] = filteredShipList

    tableId = GeneralUtils.GenerateDataSignature(preset['ruleSet'])
    rtnVal['id'] = tableId

    if str(preset['useCustomTableOptions']) == '1' and preset['tableColumnList']:
        tableData = ShipUtils.GetWikiDisplayDataForShipList(filteredShipList, preset['tableColumnList'])
        dataSignature = GeneralUtils.GenerateDataSignature(tableData)
        preset['tableClassNames'] += " data-{} generated-{}".format(dataSignature, date.today().isoformat())
        preset['tableClassNames'] = preset['tableClassNames'].strip()

        rtnVal['content'] = ConvertListToWikiTable(tableData, preset['tableHeader'], preset['tableCaption'], preset['tableClassNames'], tableId)
        rtnVal['signature'] = dataSignature

        if includeHtml:
            tableData = ShipUtils.GetDisplayDataForShipList(filteredShipList, preset['tableColumnList'])
            rtnVal['htmlContent'] = GeneralUtils.ConvertListToHtmlTable(tableData, preset['tableHeader'], preset['tableCaption'], preset['tableClassNames'], tableId)

    else:
        tableInfo = ShipUtils.GetDefaultTableInfo(preset['pageType'])
        if len(filteredShipList) > 7:
            tableInfo['tableClassNames'] += " floatheader"
            tableInfo['tableClassNames'] = tableInfo['tableClassNames'].strip()

        tableData = ShipUtils.GetWikiDisplayDataForShipList(filteredShipList, tableInfo['tableColumnList'])
        dataSignature = GeneralUtils.GenerateDataSignature(tableData)
        tableInfo['tableClassNames'] += " data-{} generated-{}".format(dataSignature, date.today().isoformat())
        tableInfo['tableClassNames'] = tableInfo['tableClassNames'].strip()

        rtnVal['content'] = ConvertListToWikiTable(tableData, tableInfo['tableHeader'], tableInfo['tableCaption'], tableInfo['tableClassNames'], tableId, tableInfo['tableColumnTitleList'])
        rtnVal['signature'] = dataSignature

        if includeHtml:
            tableData = ShipUtils.GetDisplayDataForShipList(filteredShipList, tableInfo['tableColumnList'])
            rtnVal['htmlContent'] = GeneralUtils.ConvertListToHtmlTable(tableData, tableInfo['tableHeader'], tableInfo['tableCaption'], tableInfo['tableClassNames'], tableId, tableInfo['tableColumnTitleList'])

    return rtnVal



def RenderItemPreset(preset, includeHtml=False, includeResultObjList=False, removeUltraRaresFromResultCount=False, includeTableHeaders=True):
    from SFIWikiBotLib import ItemUtils

    if not includeTableHeaders:
        preset['tableHeader'] = ''
        preset['tableCaption'] = ''

    rtnVal = {
        'content': '',
        'resultCount': 0,
        'id': '',
        'signature': '',
    }
    if includeHtml:
        rtnVal['htmlContent'] = ''

    if 'pageType' not in preset:
        preset['pageType'] = ''
    if 'sortBy' not in preset:
        preset['sortBy'] = ''

    tableId = GeneralUtils.GenerateDataSignature(preset['ruleSet'])
    rtnVal['id'] = tableId

    filteredItemList = GeneralUtils.SearchObjectListUsingRuleset(ItemUtils.itemData, preset['ruleSet'])
    filteredItemList = sorted(filteredItemList, key=ItemUtils.GetItemSortFunc(preset['sortBy']))
    if removeUltraRaresFromResultCount:
        rtnVal['resultCount'] = len([v for v in filteredItemList if 'equipCategory' not in v or v['equipCategory'] != 7])
    else:
        rtnVal['resultCount'] = len(filteredItemList)
    if includeResultObjList:
        rtnVal['objList'] = filteredItemList

    if str(preset['useCustomTableOptions']) == '1' and preset['tableColumnList']:
        tableColumnTitleList = ItemUtils.GetStatNameDescriptions(preset['tableColumnList'])
        tableData = ItemUtils.GetWikiDisplayDataForItemList(filteredItemList, preset['tableColumnList'])
        dataSignature = GeneralUtils.GenerateDataSignature(tableData)
        preset['tableClassNames'] += " data-{} generated-{}".format(dataSignature, date.today().isoformat())
        preset['tableClassNames'] = preset['tableClassNames'].strip()
        rtnVal['content'] = ConvertListToWikiTable(tableData, preset['tableHeader'], preset['tableCaption'], preset['tableClassNames'], tableId, tableColumnTitleList)
        rtnVal['signature'] = dataSignature

        if includeHtml:
            tableData = ItemUtils.GetDisplayDataForItemList(filteredItemList, preset['tableColumnList'])
            rtnVal['htmlContent'] = GeneralUtils.ConvertListToHtmlTable(tableData, preset['tableHeader'], preset['tableCaption'], preset['tableClassNames'], tableId, tableColumnTitleList)

    else:
        itemTypeList = [ 2, 3, 4, 5, 6, 14, 1 ]
        weaponTypeList = [ 1, 2, 3, 4, 5 ]
        rtnVal['idSignatureMapping'] = {}

        for itemType in itemTypeList:
            if itemType == 3:
                for weaponType in weaponTypeList:
                    itemList = [ item for item in filteredItemList if 'type' in item and item['type'] == itemType and 'weaponType' in item and item['weaponType'] == weaponType ]
                    if itemList:
                        myTableId = { 'Item Type': ItemUtils.ItemDisplayStatItemType(itemList[0]), 'rsId': tableId }
                        myTableId = GeneralUtils.GenerateDataSignature(myTableId)
                        tableInfo = ItemUtils.GetDefaultTableInfoByItemType(itemType, weaponType, preset['pageType'])
                        tableClassNames = tableInfo['tableClassNames']
                        if len(itemList) > 7:
                            tableClassNames += " floatheader"
                            tableClassNames = tableClassNames.strip()

                        tableData = ItemUtils.GetWikiDisplayDataForItemList(itemList, tableInfo['tableColumnList'])
                        dataSignature = GeneralUtils.GenerateDataSignature(tableData)
                        tableClassNames += " data-{} generated-{}".format(dataSignature, date.today().isoformat())
                        tableClassNames = tableClassNames.strip()
                        rtnVal['content'] += ConvertListToWikiTable(tableData, tableInfo['tableHeader'], tableInfo['tableCaption'], tableClassNames, myTableId, tableInfo['tableColumnTitleList'])
                        rtnVal['idSignatureMapping'][myTableId] = dataSignature
                        if not rtnVal['signature']:
                            rtnVal['signature'] = dataSignature

                        if includeHtml:
                            tableData = ItemUtils.GetDisplayDataForItemList(itemList, tableInfo['tableColumnList'])
                            rtnVal['htmlContent'] += GeneralUtils.ConvertListToHtmlTable(tableData, tableInfo['tableHeader'], tableInfo['tableCaption'], tableClassNames, myTableId, tableInfo['tableColumnTitleList'])

            else:
                itemList = [ item for item in filteredItemList if 'type' in item and item['type'] == itemType ]
                if itemList:
                    myTableId = { 'Item Type': ItemUtils.ItemDisplayStatItemType(itemList[0]), 'rsId': tableId }
                    myTableId = GeneralUtils.GenerateDataSignature(myTableId)
                    tableInfo = ItemUtils.GetDefaultTableInfoByItemType(itemType, ..., preset['pageType'])
                    tableClassNames = tableInfo['tableClassNames']
                    if len(itemList) > 7:
                        tableClassNames += " floatheader"
                        tableClassNames = tableClassNames.strip()

                    tableData = ItemUtils.GetWikiDisplayDataForItemList(itemList, tableInfo['tableColumnList'])
                    dataSignature = GeneralUtils.GenerateDataSignature(tableData)
                    tableClassNames += " data-{} generated-{}".format(dataSignature, date.today().isoformat())
                    tableClassNames = tableClassNames.strip()
                    rtnVal['content'] += ConvertListToWikiTable(tableData, tableInfo['tableHeader'], tableInfo['tableCaption'], tableClassNames, myTableId, tableInfo['tableColumnTitleList'])
                    rtnVal['idSignatureMapping'][myTableId] = dataSignature
                    if not rtnVal['signature']:
                        rtnVal['signature'] = dataSignature

                    if includeHtml:
                        tableData = ItemUtils.GetDisplayDataForItemList(itemList, tableInfo['tableColumnList'])
                        rtnVal['htmlContent'] += GeneralUtils.ConvertListToHtmlTable(tableData, tableInfo['tableHeader'], tableInfo['tableCaption'], tableClassNames, myTableId, tableInfo['tableColumnTitleList'])



    return rtnVal



def RevertRecentChanges(pageList, contentDiffThreshold=200):
    site = GetWikiClientSiteObject()
    pagesReverted = []

    for pageName in pageList:
        page = site.pages[pageName]
        revisionList = page.revisions(prop="timestamp|user|comment|content", limit=5)
        currentContent = next(revisionList)['*']
        for revision in revisionList:
            if len(revision['*']) - len(currentContent) > 200:
                page.edit(revision['*'], 'Reverting previous change')
                pagesReverted.append(pageName)
                print("Reverting change on {}".format(pageName))
                time.sleep(2.5)
                break

    return pagesReverted


def UpdateWikiShipNavboxTemplates(comment=None):
    from SFIWikiBotLib import ShipUtils
    rtnVal = {
        'pagesUpdated': [],
        'pagesAlreadyUpToDate': [],
        'pagesFailedToUpdate': [],
        'pagesNotFound': [],
    }

    site = GetWikiClientSiteObject()

    templatePageList = {
        'Template:Human Ships': ShipUtils.GetHumanPlayerShipList(),
        'Template:Aralien Ships': ShipUtils.GetAralienPlayerShipList(),
        'Template:Restricted Ships': ShipUtils.GetRestrictedShipList(),
        'Template:NPR Ships': ShipUtils.GetNPRShipList(),
    }

    for templatePageName, shipList in templatePageList.items():
        page = site.pages[templatePageName]
        if page.exists:
            bodyContent = ' - '.join([ '[[{}]]'.format(v['name']) for v in shipList ])

            content = page.text()
            newContent = content

            templateList = GetTemplateListFromWikiPageContent(content)
            for template in templateList:
                if template['name'] == 'Navbox':
                    newContent = content.replace(template['data']['body'].strip(), bodyContent.strip())

            if content != newContent:
                loopComment = comment
                if not loopComment:
                    loopComment = 'Adding new ships to the navbox'

                try:
                    page.edit(newContent, loopComment)
                    if Config.verbose >= 1:  print("Page Updated: {} - {}".format(templatePageName, loopComment))
                    rtnVal['pagesUpdated'].append(templatePageName)
                except:
                    if Config.debug or Config.verbose >= 1:  print("Failed to update: {} - {}".format(templatePageName, loopComment))
                    rtnVal['pagesFailedToUpdate'].append(templatePageName)
            else:
                rtnVal['pagesAlreadyUpToDate'].append(templatePageName)
        else:
            rtnVal['pagesNotFound'].append(templatePageName)

    return rtnVal


def UpdateWikiShipDetailedListPagesForPresetList(presetList, comment=None):
    rtnVal = {
        'pagesUpdated': [],
        'pagesAlreadyUpToDate': [],
        'pagesFailedToUpdate': [],
        'pagesNotFound': [],
    }

    site = GetWikiClientSiteObject()

    pageList = set()
    for preset in presetList:
        pageList.add(preset['targetPage'])

    for pageName in pageList:
        page = site.pages[pageName]
        if page.exists:
            updatesIncluded = []

            content = page.text()
            tableList = GetTableListFromWikiPageContent(content)
            for preset in presetList:
                if preset['targetPage'] == pageName:
                    renderInfo = RenderShipPreset(preset, includeHtml=False, includeResultObjList=False, includeTableHeaders=False)

                    # Individual table preset
                    validIdList = [ renderInfo['id'] ]
                    if 'id' in preset and preset['id']:
                        validIdList.append(preset['id'][3:])

                    for tblInfo in tableList:
                        if tblInfo['id'] in validIdList:
                            if tblInfo['signature'] != renderInfo['signature']:
                                content = content.replace(tblInfo['content'].strip(), renderInfo['content'].strip())
                                updateName = preset['name']
                                try:
                                    updateName = preset['name'].split(' - ', 1)[1]
                                except:
                                    pass
                                updatesIncluded.append(updateName)
                                # print("Updating {} on {}".format(preset['name'], pageName))
                            else:
                                rtnVal['pagesAlreadyUpToDate'].append(preset['name'])

            if updatesIncluded:
                loopComment = comment
                if not loopComment:
                    loopComment = "Updating data table{} ({})".format('s' if len(updatesIncluded) != 1 else '', ', '.join(updatesIncluded))

                try:
                    page.edit(content, loopComment)
                    if Config.verbose >= 1:  print("Page Updated: {} - {}".format(pageName, loopComment))
                    rtnVal['pagesUpdated'].append(pageName)
                except:
                    if Config.debug or Config.verbose >= 1:  print("Failed to update: {} - {}".format(pageName, loopComment))
                    rtnVal['pagesFailedToUpdate'].append(pageName)
                    raise
        else:
            rtnVal['pagesNotFound'].append(pageName)

        time.sleep(2.5)  # We're not in a hurry.  Don't overwhelm the wiki

    return rtnVal


def UpdateWikiEquipmentPagesForPresetList(presetList, comment=None):
    rtnVal = {
        'pagesUpdated': [],
        'pagesAlreadyUpToDate': [],
        'pagesFailedToUpdate': [],
        'pagesNotFound': [],
    }

    site = GetWikiClientSiteObject()

    pageList = set()
    for preset in presetList:
        pageList.add(preset['targetPage'])

    for pageName in pageList:
        page = site.pages[pageName]
        if page.exists:
            updatesIncluded = []

            content = page.text()
            tableList = GetTableListFromWikiPageContent(content)
            for preset in presetList:
                if preset['targetPage'] == pageName:
                    renderInfo = RenderItemPreset(preset, includeHtml=False, includeResultObjList=False, removeUltraRaresFromResultCount=False, includeTableHeaders=False)
                    if 'idSignatureMapping' in renderInfo:
                        # Multiple table preset
                        newTableList = GetTableListFromWikiPageContent(renderInfo['content'])

                        # We will only be updating tables here, not adding any (unlike the npr pages)
                        for newTblInfo in newTableList:
                            for tblInfo in tableList:
                                if tblInfo['id'] == newTblInfo['id']:
                                    if tblInfo['signature'] != newTblInfo['signature']:
                                        content = content.replace(tblInfo['content'].strip(), newTblInfo['content'].strip())
                                        updatesIncluded.append('Item stats/locations')
                                        if Config.debug:  print("Updating Item stats/locations on {}".format(pageName))
                                    else:
                                        rtnVal['pagesAlreadyUpToDate'].append(preset['name'])
                                        if Config.debug:  print("Signatures match for {} on {}".format(preset['name'], pageName))

                    else:
                        # Individual table preset
                        validIdList = [ renderInfo['id'] ]
                        if 'id' in preset and preset['id']:
                            validIdList.append(preset['id'][3:])

                        found = False
                        tblIdList = []
                        for tblInfo in tableList:
                            tblIdList.append(tblInfo['id'])
                            if tblInfo['id'] in validIdList:
                                found = True
                                if tblInfo['signature'] != renderInfo['signature']:
                                    content = content.replace(tblInfo['content'].strip(), renderInfo['content'].strip())
                                    updateName = preset['name']
                                    try:
                                        updateName = preset['name'].split(' - ', 1)[1]
                                    except:
                                        pass
                                    updatesIncluded.append(updateName)
                                    if Config.debug:  print("Updating {} on {} ({})".format(preset['name'], pageName, tblInfo['id']))
                                else:
                                    rtnVal['pagesAlreadyUpToDate'].append(preset['name'])
                                    if Config.debug:  print("Signatures match for {} on {} ({})".format(preset['name'], pageName, tblInfo['id']))
                        if not found:
                            if Config.debug:  print("No table found for preset {} ({} || {})".format(preset['name'], ', '.join(validIdList), ', '.join(tblIdList)))

            if updatesIncluded:
                loopComment = comment
                if not loopComment:
                    loopComment = "Updating data table{} ({})".format('s' if len(updatesIncluded) != 1 else '', ', '.join(updatesIncluded))

                try:
                    page.edit(content, loopComment)
                    if Config.verbose >= 1:  print("Page Updated: {} - {}".format(pageName, loopComment))
                    rtnVal['pagesUpdated'].append(pageName)
                except:
                    rtnVal['pagesFailedToUpdate'].append(pageName)
                    if Config.debug or Config.verbose >= 1:  print("Failed to update: {} - {}".format(pageName, loopComment))
                    raise
        else:
            rtnVal['pagesNotFound'].append(pageName)
            if Config.debug:  print("Page not found {}".format(pageName))

        time.sleep(2.5)  # We're not in a hurry.  Don't overwhelm the wiki

    return rtnVal



def UpdateWikiNPRPages(comment=None, forceUpdate=False):
    rtnVal = {
        'pagesUpdated': [],
        'pagesAlreadyUpToDate': [],
        'pagesFailedToUpdate': [],
        'pagesNotFound': [],
    }

    site = GetWikiClientSiteObject()

    for pageName in Config.nprPageNameMapping.keys():
        nprName = Config.nprPageNameMapping[pageName]

        page = site.pages[pageName]
        if page.exists:
            updateRequired = False
            if forceUpdate:  updateRequired = True

            content = page.text()
            tableList = GetTableListFromWikiPageContent(content)

            newNprSignatureList = GetContentSignatureListForNprPage(nprName)
            for curNprId, curNprSig in newNprSignatureList.items():
                found = False
                for tblInfo in tableList:
                    if curNprId == tblInfo['id']:
                        found = True
                        if curNprSig != tblInfo['signature']:
                            updateRequired = True
                if not found:
                    updateRequired = True

            if updateRequired:
                templateList = GetTemplateListFromWikiPageContent(content)
                searchStart = ''
                searchEnd = '\n{{NPRFooter'
                for template in templateList:
                    if template['name'] == 'NPRHeader':
                        searchStart = template['content'][-20:] + '\n'
                        break

                if searchStart:
                    newContent = content
                    curNprContent = GetContentForNprPage(nprName)

                    regexStr = '.*?' + re.escape(searchStart) + '(.*?)' + re.escape(searchEnd)
                    m = re.match(regexStr, content, re.S)
                    if m:
                        newContent = content.replace(m.group(1), curNprContent)

                    if newContent != content:
                        loopComment = comment
                        if not loopComment:
                            loopComment = "Updating data tables with fresh item/ship stats"

                        try:
                            page.edit(newContent, loopComment)
                            if Config.verbose >= 1:  print("Page Updated: {} - {}".format(pageName, loopComment))
                            rtnVal['pagesUpdated'].append(pageName)
                        except Exception as e:
                            if Config.debug or Config.verbose >= 1:  print("Failed to update: {} - {}".format(pageName, loopComment))
                            rtnVal['pagesFailedToUpdate'].append("{} - {}".format(pageName, e))
                    else:
                        rtnVal['pagesFailedToUpdate'].append("{} - Failed to update content".format(pageName))
                else:
                    rtnVal['pagesFailedToUpdate'].append("{} - Invalid page format".format(pageName))
            else:
                rtnVal['pagesAlreadyUpToDate'].append(pageName)
        else:
            rtnVal['pagesNotFound'].append(pageName)

        time.sleep(2.5)  # We're not in a hurry.  Don't overwhelm the wiki

    return rtnVal



def TouchIndividualPagesForAllItems(comment=''):
    from SFIWikiBotLib import ItemUtils
    rtnVal = True

    itemList = [ v for v in ItemUtils.itemData if ItemUtils.GetItemWikiArticlePage(v) and v['type'] > 1 and not ItemUtils.IsItemHidden(v) ]
    for curItemList in ItemUtils.ItemPageIter(itemList):
        primaryItem = curItemList[-1]

        pageName = ItemUtils.GetItemWikiArticlePage(primaryItem)
        if not pageName:
            continue

        site = GetWikiClientSiteObject()
        page = site.pages[pageName]
        if page.exists:
            try:
                page.touch()
                time.sleep(Config.pauseAfterSuccessfullyUpdatingWikiPageInSec)
            except:
                rtnVal = False
                time.sleep(Config.pauseAfterSkippingWikiPageUpdateInSec)

    return rtnVal


def UpdatePresetListWithUpdatedIdsFromWiki(presetList):
    with open('PresetList.py', 'r') as file:
        presetFileData = file.read()
        newPresetData = presetFileData
    if not presetFileData:
        print("Unable to read preset list file")
        return False
    site = GetWikiClientSiteObject()
    pageList = set()
    for preset in presetList:
        pageList.add(preset['targetPage'])
    for pageName in pageList:
        page = site.pages[pageName]
        if page.exists:
            updatesIncluded = []
            content = page.text()
            tableList = GetTableListFromWikiPageContent(content)
            for preset in presetList:
                if preset['targetPage'] == pageName:
                    renderInfo = RenderItemPreset(preset)
                    if 'idSignatureMapping' in renderInfo:
                        print("Preset", preset['name'], 'contains multiple tables. Skipping.')
                    else:
                        # Individual table preset
                        validIdList = [ renderInfo['id'] ]
                        if 'id' in preset and preset['id']:
                            validIdList.append(preset['id'][3:])
                        for tblInfo in tableList:
                            if tblInfo['id'] in validIdList:
                                if 'id' in preset and preset['id'] and tblInfo['id'] != preset['id'][3:]:
                                    # print("Preset", preset['name'], 'matched against table with id', tblInfo['id'], 'despite having id of', preset['id'][3:], 'set.')
                                    print(preset['name'], '::', preset['id'][3:], '->', tblInfo['id'])
                                    presetFileData = presetFileData.replace(preset['id'][3:], tblInfo['id'])
    if newPresetData != presetFileData:
        with open('PresetList.py', 'w') as file:
            file.write(presetFileData)


def UpdateWikiSkillsPage(comment=None):
    rtnVal = {
        'pagesUpdated': [],
        'pagesAlreadyUpToDate': [],
        'pagesFailedToUpdate': [],
        'pagesNotFound': [],
    }

    site = GetWikiClientSiteObject()

    page = site.pages['Skills']
    if page.exists:
        updateRequired = False

        skillList = [ v['name'] for v in SmallConstants.skillsData ]

        content = page.text()
        tableList = GetTableListFromWikiPageContent(content)

        for skill in skillList:
            skillInfo = GetRenderedSkillPageItemList(skill)

            for tableInfo in tableList:
                if tableInfo['id'] == skillInfo['id']:
                    if tableInfo['signature'] != skillInfo['signature']:
                        content = content.replace(tableInfo['content'], skillInfo['content'])
                        updateRequired = True
                    break

        if updateRequired:
            try:
                if not comment:
                    comment = "Updating item lists"
                page.edit(content, comment)
                if Config.verbose >= 1:  print("Page Updated: Skills - {}".format(comment))
                rtnVal['pagesUpdated'].append('Skills')
            except Exception as e:
                if Config.debug or Config.verbose >= 1:  print("Failed to update: Skills - {}".format(comment))
                rtnVal['pagesFailedToUpdate'].append("Skills - {}".format(e))
        else:
            rtnVal['pagesAlreadyUpToDate'].append('Skills')
    else:
        rtnVal['pagesNotFound'].append('Skills')

    return rtnVal



def UpdateIndividualPagesForAllItems(comment=''):
    from SFIWikiBotLib import ItemUtils
    rtnVal = {
        'pagesUpdated': [],
        'pagesAlreadyUpToDate': [],
        'pagesFailedToUpdate': [],
        'pagesNotFound': [],
    }

    itemList = [ v for v in ItemUtils.itemData if ItemUtils.GetItemWikiArticlePage(v) and v['type'] > 1 and not ItemUtils.IsItemHidden(v) ]
    for curItemList in ItemUtils.ItemPageIter(itemList):
        if Config.debug:  print("Got", itemList[0]['name'], 'with', len(curItemList), 'members.')
        primaryItem = curItemList[-1]
        nameInfo = ItemUtils.SplitNameIntoBaseNameAndItemLevel(primaryItem['name'])
        if Config.debug:
            print(datetime.now(tz).strftime("%H:%M").lstrip('0'), "Processing item", nameInfo['fullNameMinusLevel'])

        res = UpdateIndividualItemPageByItemRange(curItemList, comment)
        if not res:
            rtnVal['pagesFailedToUpdate'].append(nameInfo['fullNameMinusLevel'])
        else:
            rtnVal['pagesUpdated'].append(nameInfo['fullNameMinusLevel'])

    return rtnVal


def UpdateIndividualItemPageByItemRange(itemList, comment=None, allowRetry=True):
    from SFIWikiBotLib import ItemUtils
    rtnVal = False

    if not itemList:
        return rtnVal

    fullEffectList = [ v.lower() for v in SmallConstants.GetFullEffectNameList() ]

    primaryItem = itemList[-1]
    pageName = ItemUtils.GetItemWikiArticlePage(primaryItem)
    if not pageName:
        return rtnVal

    site = GetWikiClientSiteObject()
    page = site.pages[pageName]
    if page.exists:
        updatesIncluded = []
        nameInfo = ItemUtils.SplitNameIntoBaseNameAndItemLevel(primaryItem['name'])

        infoBox = ItemUtils.GetWikiInfoboxDataForItemRangeList(itemList)
        if not infoBox:
            return rtnVal

        itemCatList = ItemUtils.GetCategoryListForItem(primaryItem)
        itemCatListCmp = [v.lower().strip() for v in itemCatList]

        content = page.text().strip()

        catChanges = False

        curCatList = []
        catList = GetCategoryListFromWikiPageContent(content)
        for catInfo in catList:
            # Remove any effect categories which don't apply to this item
            catName = catInfo['name'].lower()
            if catName not in itemCatListCmp and catName in fullEffectList:
                content = content.replace(catInfo['content'], '')
                catChanges = True
            else:
                curCatList.append(catInfo['name'].lower())


        for catName in itemCatList:
            if catName.lower() not in curCatList:
                content += '\n[[Category:{}]]'.format(catName)
                catChanges = True

        if catChanges:
            updatesIncluded.append("Categories")

        templateList = GetTemplateListFromWikiPageContent(content)
        for template in templateList:
            if template['name'].lower() == 'itemformat':
                updateTemplate = False
                replacementTemplate = template['data']

                source = ItemUtils.GetItemSource(primaryItem)
                sourceClassName = ItemUtils.GetItemSourceClassName(primaryItem)
                if source == 'Ultra Rare' or source == 'NPR Exclusive':
                    trivia = 'As an <span class="{}">{}</span> item, {} does not drop and is unobtainable to players.'.format(sourceClassName, source, nameInfo['fullNameMinusLevel'])
                    if trivia.lower() not in template['data']['trivia'].lower():
                        templateTrivia = template['data']['trivia']
                        if templateTrivia.strip():
                            templateTrivia += "\n"
                        templateTrivia += "* " + trivia
                        replacementTemplate['trivia'] = templateTrivia
                        updateTemplate = True
                        updatesIncluded.append("Trivia")

                if sourceClassName:
                    name = '<span class="{}">{}</span>'.format(sourceClassName, nameInfo['fullNameMinusLevel'])
                else:
                    name = splitItemName['fullNameMinusLevel']
                if name.lower() != template['data']['itemname'].lower():
                    replacementTemplate['itemname'] = name
                    updateTemplate = True
                    updatesIncluded.append("Item Name")

                itemSlot = ItemUtils.ItemDisplayStatItemType(primaryItem, 'itemPage').strip()
                if itemSlot.lower() != template['data']['itemSlot'].lower():
                    replacementTemplate['itemSlot'] = itemSlot
                    updateTemplate = True
                    updatesIncluded.append("Item Slot")


                if source is not None and sourceClassName:
                    source = '<span class="{}">{}</span>'.format(sourceClassName, source)
                if source.lower() != template['data']['methodOfObtaining'].lower():
                    replacementTemplate['methodOfObtaining'] = source
                    updateTemplate = True
                    updatesIncluded.append("Method of Obtaining")

                sourceOnPage = GeneralUtils.StripTags(replacementTemplate['methodOfObtaining'])
                if sourceOnPage[0].lower() in ['a', 'e', 'i', 'o', 'u'] or sourceOnPage[0:4].lower() == 'npr ':
                    if 'aOrAnForMethodOfObtaining' not in replacementTemplate or replacementTemplate['aOrAnForMethodOfObtaining'].strip() != 'an':
                        replacementTemplate['aOrAnForMethodOfObtaining'] = 'an'
                        updateTemplate = True
                        updatesIncluded.append("Grammar fix")

                gameDescription = "\n\n".join(ItemUtils.GetDescriptionForItemRangeList(itemList, "''"))
                if gameDescription.strip() != template['data']['gameDescription'].strip():
                    replacementTemplate = template['data']
                    replacementTemplate['gameDescription'] = gameDescription
                    updateTemplate = True
                    updatesIncluded.append("Game description")

                if updateTemplate:
                    templateContent = ConvertDictionaryToWikiTemplate(template['name'], replacementTemplate)
                    content = content.replace(template['content'], templateContent.strip())


            if template['name'].replace(' ', '_').lower() == infoBox['name'].replace(' ', '_').lower():
                if 'image1' in template['data'] and template['data']['image1']:
                    infoBox['image1'] = template['data']['image1']

                if GeneralUtils.GenerateDataSignature(infoBox['data']) != GeneralUtils.GenerateDataSignature(template['data']):
                    updatedTemplate = ConvertDictionaryToWikiTemplate(infoBox['name'], infoBox['data'])
                    newContent = content.replace(template['content'].strip(), updatedTemplate.strip())
                    if newContent and newContent != content:
                        content = newContent
                        updatesIncluded.append("Infobox stats")
                    else:
                        print("Unable to get new content for {}".format(pageName))

        if updatesIncluded:
            try:
                if not comment:
                    comment = "Updating {}".format(', '.join(updatesIncluded))
                # print('Updating page', updatesIncluded)
                page.edit(content, comment)
                if Config.verbose >= 1:  print("Page Updated: {} - {}".format(pageName, comment))
                rtnVal = True
                time.sleep(Config.pauseAfterSuccessfullyUpdatingWikiPageInSec)

            except mwclient.errors.AssertUserFailedError as ex:
                time.sleep(Config.pauseAfterFailingToUpdateWikiPageInSec)

                if allowRetry:
                    if Config.debug:  print("Retrying update: {} - {}".format(pageName, comment))
                    GetWikiClientSiteObject(True)
                    return UpdateIndividualItemPageByItemRange(itemList, comment, False)

                if Config.debug or Config.verbose >= 1:  print("Failed to update: {} - {}".format(pageName, comment))
                raise ex
        else:
            time.sleep(Config.pauseAfterSkippingWikiPageUpdateInSec)

    return rtnVal




def UpdateIndividualPagesForAllShips(comment=None):
    from SFIWikiBotLib import ShipUtils
    rtnVal = {
        'pagesUpdated': [],
        'pagesAlreadyUpToDate': [],
        'pagesFailedToUpdate': [],
        'pagesNotFound': [],
    }

    for ship in ShipUtils.shipData:
        if Config.debug:
            print(datetime.now(tz).strftime("%H:%M").lstrip('0'), "Processing ship", ship['name'])

        res = UpdateIndividualShipPage(ship, comment)
        if not res:
            rtnVal['pagesFailedToUpdate'].append(ship['name'])
        else:
            rtnVal['pagesUpdated'].append(ship['name'])

    return rtnVal


def UpdateIndividualShipPage(ship, comment=None, allowRetry=True):
    from SFIWikiBotLib import ShipUtils
    rtnVal = False
    pageName = ship['name']

    managedCategoryList = [ v.lower() for v in SmallConstants.GetFullShipManagedCategoryList() ]

    site = GetWikiClientSiteObject()
    page = site.pages[pageName]
    if page.exists:
        updatesIncluded = []
        content = page.text().strip()

        shipCatList = ShipUtils.GetCategoryListForShip(ship)
        shipCatListCmp = [v.lower().strip() for v in shipCatList]

        catChanges = False

        curCatList = []
        catList = GetCategoryListFromWikiPageContent(content)
        for catInfo in catList:
            # Remove any categories which don't apply to this ship
            catName = catInfo['name'].lower()
            if catName not in shipCatListCmp and catName in managedCategoryList:
                content = content.replace(catInfo['content'], '')
                catChanges = True
            else:
                curCatList.append(catInfo['name'].lower())

        for catName in shipCatList:
            if catName.lower() not in curCatList:
                content += '\n[[Category:{}]]'.format(catName)
                catChanges = True

        if catChanges:
            updatesIncluded.append("Categories")


        templateList = GetTemplateListFromWikiPageContent(content)
        for template in templateList:
            if template['name'].replace(' ', '_').lower() == 'infobox_ship':
                infoBox = ShipUtils.GetWikiInfoboxDataForShip(ship)
                if 'image1' in template['data'] and template['data']['image1']:
                    if 'image1' not in infoBox or not infoBox['image1']:
                        infoBox['image1'] = template['data']['image1']

                if GeneralUtils.GenerateDataSignature(infoBox) != GeneralUtils.GenerateDataSignature(template['data']):
                    updatedTemplate = ConvertDictionaryToWikiTemplate('Infobox_Ship', infoBox)
                    updatedTemplate = updatedTemplate.strip()
                    newContent = content.replace('{}\n\n'.format(template['content']), updatedTemplate)
                    if newContent == content:
                        newContent = content.replace('{}\n'.format(template['content']), updatedTemplate)
                    if newContent == content:
                        newContent = content.replace('{}'.format(template['content']), updatedTemplate)
                    if newContent and newContent != content:
                        content = newContent
                        updatesIncluded.append("Infobox stats")
                    else:
                        print("Unable to get new content for {}".format(ship['name']))

        if 'description' in ship and ship['description'].strip():
            pageSectionList = GetWikiPageSectionsFromContent(content)
            if 'Game Description' in pageSectionList and pageSectionList['Game Description']:
                newContent = "{}\n''{}''".format(pageSectionList['Game Description']['nameContent'].strip(), ShipUtils.GetShipDescription(ship)).strip()
                if pageSectionList['Game Description']['content'].strip() != newContent.strip():
                    content = content.replace(pageSectionList['Game Description']['content'].strip(), newContent)
                    updatesIncluded.append("Game description")
            else:
                if Config.verbose >= 1:  print("Game Description section not found for {} - Unable to update".format(pageName))

        if updatesIncluded:
            try:
                if not comment:
                    comment = "Updating {}".format(', '.join(updatesIncluded))
                page.edit(content, comment)
                if Config.verbose >= 1:  print("Page Updated: {} - {}".format(pageName, comment))
                rtnVal = True
                time.sleep(Config.pauseAfterSuccessfullyUpdatingWikiPageInSec)

            except mwclient.errors.AssertUserFailedError as ex:
                time.sleep(Config.pauseAfterFailingToUpdateWikiPageInSec)

                if allowRetry:
                    if Config.debug:  print("Retrying update: {} - {}".format(pageName, comment))
                    GetWikiClientSiteObject(True)
                    return UpdateIndividualShipPage(ship, comment, False)

                if Config.debug or Config.verbose >= 1:  print("Failed to update: {} - {}".format(pageName, comment))
                raise ex
        else:
            time.sleep(Config.pauseAfterSkippingWikiPageUpdateInSec)

    return rtnVal





def UpdateStarSystemPages(comment=None, systemList=...):
    from SFIWikiBotLib import GalaxyUtils
    rtnVal = {
        'pagesUpdated': [],
        'pagesAlreadyUpToDate': [],
        'pagesFailedToUpdate': [],
        'pagesNotFound': [],
    }

    if systemList is ...:
        systemList = GalaxyUtils.GetSystemList()

    for systemInfo in systemList:
        if Config.debug:
            print(datetime.now(tz).strftime("%H:%M").lstrip('0'), "Processing star system", systemInfo['name'])

        res = UpdateStarSystemPage(systemInfo, comment)
        if not res:
            rtnVal['pagesFailedToUpdate'].append(systemInfo['name'])
        else:
            rtnVal['pagesUpdated'].append(systemInfo['name'])

    return rtnVal


def UpdateStarSystemPage(systemInfo, comment=None, allowRetry=True):
    from SFIWikiBotLib import GalaxyUtils
    rtnVal = False
    pageName = systemInfo['name']

    site = GetWikiClientSiteObject()
    page = site.pages[pageName]
    if page.exists:
        updatesIncluded = []

        content = page.text()
        templateList = GetTemplateListFromWikiPageContent(content)
        for template in templateList:
            if template['name'].lower().replace('_', ' ') == 'star system page':

                curPlanetList = sorted([ v.strip('*[]').lower() for v in template['data']['Planet List Here'].strip().split('\n') ])
                expectedPlanetList = sorted(GalaxyUtils.GetSystemPlanetList(systemInfo['prefix']))
                if curPlanetList != [v.lower() for v in expectedPlanetList]:
                    template['data']['Planet List Here'] = '*[[{}]]'.format(']]\n*[['.join(expectedPlanetList))

                    updatedTemplate = ConvertDictionaryToWikiTemplate('Star System Page', template['data'])
                    updatedTemplate = updatedTemplate.strip()
                    content = content.replace('{}'.format(template['content'].strip()), updatedTemplate)
                    updatesIncluded.append("Planet List")

        if updatesIncluded:
            try:
                if not comment:
                    comment = "Updating {}".format(', '.join(updatesIncluded))
                page.edit(content, comment)
                if Config.verbose >= 1:  print("Page Updated: {} - {}".format(pageName, comment))
                # print(content, '\n\n')
                rtnVal = True
                time.sleep(Config.pauseAfterSuccessfullyUpdatingWikiPageInSec)

            except mwclient.errors.AssertUserFailedError as ex:
                time.sleep(Config.pauseAfterFailingToUpdateWikiPageInSec)

                if allowRetry:
                    if Config.debug:  print("Retrying update: {} - {}".format(pageName, comment))
                    GetWikiClientSiteObject(True)
                    return UpdateStarSystemPage(systemInfo, comment, False)
                if Config.debug or Config.verbose >= 1:  print("Failed to update: {} - {}".format(pageName, comment))
                raise ex
        else:
            time.sleep(Config.pauseAfterSkippingWikiPageUpdateInSec)

    else:
        print(pageName, 'not found')

    return rtnVal





def UpdateIndividualPagesForAllPlanets(comment=None):
    from SFIWikiBotLib import GalaxyUtils
    rtnVal = {
        'pagesUpdated': [],
        'pagesAlreadyUpToDate': [],
        'pagesFailedToUpdate': [],
        'pagesNotFound': [],
    }

    planetList = GalaxyUtils.GetSystemPlanetList('all', True)
    for planetName in planetList:
        if Config.debug:
            print(datetime.now(tz).strftime("%H:%M").lstrip('0'), "Processing planet", planetName)

        res = UpdateIndividualPlanetPage(planetName, comment)
        if not res:
            rtnVal['pagesFailedToUpdate'].append(planetName)
        else:
            rtnVal['pagesUpdated'].append(planetName)

    return rtnVal


matchWSRegex = re.compile(r'\s')
def UpdateIndividualPlanetPage(planetName, comment=None, allowRetry=True):
    from SFIWikiBotLib import GalaxyUtils
    rtnVal = False
    pageName = planetName
    tableSeachContent = '{|class="article-table"!|}'


    site = GetWikiClientSiteObject()
    page = site.pages[pageName]
    if page.exists:
        updatesIncluded = []

        content = page.text()
        templateList = GetTemplateListFromWikiPageContent(content)
        for template in templateList:
            if template['name'].lower() == 'planet':
                templateData = GalaxyUtils.FindPlanet(planetName)
                if 'Trivia' in template['data'] and template['data']['Trivia']:
                    templateData['Trivia'] = template['data']['Trivia']
                if 'Description' in templateData and templateData['Description']:
                    templateData['Description'] = templateData['Description'].replace("\n\n", "\n")
                    templateData['Description'] = templateData['Description'].replace("\n", "<br/>\n")
                elif 'Description' in template['data'] and template['data']['Description']:
                    templateData['Description'] = template['data']['Description']

                if GeneralUtils.GenerateDataSignature(templateData) != GeneralUtils.GenerateDataSignature(template['data']):
                    updatedTemplate = ConvertDictionaryToWikiTemplate('Planet', templateData)
                    updatedTemplate = updatedTemplate.strip()
                    newContent = content.replace(template['content'].strip(), updatedTemplate)
                    if newContent and newContent != content:
                        content = newContent
                        updatesIncluded.append("Planet Info")
                    else:
                        print("Unable to get new content for {}".format(planetName))

        wikiImage = GalaxyUtils.GetPlanetWikiImage(planetName)
        if wikiImage:
            tableList = GetTableListFromWikiPageContent(content)
            for tableInfo in tableList:
                if matchWSRegex.sub('', tableInfo['content']) == tableSeachContent:
                    planetImageInfo = '[[File:{}|thumb|220x220px]]'.format(wikiImage)
                    replacement = '{{| class="article-table"\n! {}\n|}}'.format(planetImageInfo)
                    content = content.replace(tableInfo['content'].strip(), replacement)
                    updatesIncluded.append("Planet Image")

        if updatesIncluded:
            try:
                if not comment:
                    comment = "Updating {}".format(', '.join(updatesIncluded))
                page.edit(content, comment)
                if Config.verbose >= 1:  print("Page Updated: {} - {}".format(pageName, comment))
                rtnVal = True
                time.sleep(Config.pauseAfterSuccessfullyUpdatingWikiPageInSec)

            except mwclient.errors.AssertUserFailedError as ex:
                time.sleep(Config.pauseAfterFailingToUpdateWikiPageInSec)

                if allowRetry:
                    if Config.debug:  print("Retrying update: {} - {}".format(pageName, comment))
                    GetWikiClientSiteObject(True)
                    return UpdateIndividualPlanetPage(planetName, comment, False)

                if Config.debug or Config.verbose >= 1:  print("Failed to update: {} - {}".format(pageName, comment))
                raise ex
        else:
            time.sleep(Config.pauseAfterSkippingWikiPageUpdateInSec)

    else:
        return AddMissingPlanetWikiPage(planetName)

    return rtnVal


def AddMissingPlanetWikiPage(planetName, comment=None, allowRetry=True):
    from SFIWikiBotLib import GalaxyUtils
    rtnVal = False
    pageName = planetName

    site = GetWikiClientSiteObject()
    page = site.pages[pageName]
    if not page.exists:
        templateData = GalaxyUtils.FindPlanet(planetName)
        if not templateData:  return rtnVal

        planetTemplate = ConvertDictionaryToWikiTemplate('Planet', templateData)
        planetTemplate = planetTemplate.strip()

        planetImageInfo = ''
        planetImage = GalaxyUtils.GetPlanetWikiImage(planetName)
        if planetImage:
            planetImageInfo = '[[File:{}|thumb|220x220px]]'.format(planetImage)

        content = '''
{}

== Gallery ==

{{| class="article-table"
! {}
|}}
'''.format(planetTemplate, planetImageInfo)

        try:
            if not comment:
                comment = "Adding planet page {}".format(planetName)
            page.edit(content, comment)
            if Config.verbose >= 1:  print("Page added: {} - {}".format(pageName, comment))
            rtnVal = True
            time.sleep(Config.pauseAfterSuccessfullyUpdatingWikiPageInSec)

        except mwclient.errors.AssertUserFailedError as ex:
            time.sleep(Config.pauseAfterFailingToUpdateWikiPageInSec)

            if allowRetry:
                if Config.debug:  print("Retrying page addition: {} - {}".format(pageName, comment))
                GetWikiClientSiteObject(True)
                return AddMissingPlanetWikiPage(planetName, comment, False)

            if Config.debug or Config.verbose >= 1:  print("Failed to add page: {} - {}".format(pageName, comment))
            raise ex

    return rtnVal



def FollowWikiPageRedirect(pageName):
    pass


def GetWikiPageRedirect(content):
    matches = re.match(r'^#REDIRECT\s+\[\[(.*?)\]\]\s*$', content, re.M)
    try:
        return matches.group(1)
    except:
        return None


def GetTableListFromWikiPageContent(content):
    tableList = []

    regexOuter = re.compile(r'.*?(\{\|(.*?)\|\})', re.S)
    regexId = re.compile(r'.*?id="sf-(S?[a-f0-9]{32})"')
    regexSignature = re.compile(r'.*?class="[^"]*?data-(S?[a-f0-9]{32})["\s]')
    regexGenDate = re.compile(r'.*?class="[^"]*?generated-(\d{4}-\d\d-\d\d)["\s]')

    input = content
    result = regexOuter.match(input)
    while result:
        tableData = {
            'content': result.group(1),
            'signature': '',
            'generatedOn': '',
            'id': '',
        }
        innerContent = result.group(2)
        try:
            tableData['signature'] = regexSignature.match(innerContent).group(1)
        except:
            pass
        try:
            tableData['generatedOn'] = regexGenDate.match(innerContent).group(1)
        except:
            pass
        try:
            tableData['id'] = regexId.match(innerContent).group(1)
        except:
            pass

        input = input.replace(tableData['content'], '')
        tableList.append(tableData)
        result = regexOuter.match(input)

    return tableList


def GetTemplateListFromWikiPageContent(content):
    templateList = []


    resLink = ReplaceWikiLinksWithPlaceholders(content)
    content = resLink['content']

    resVar = ReplaceWikiVariablesWithPlaceholders(content)
    content = resVar['content']

    resInvoke = ReplaceModuleInvokationsWithPlaceholders(content)
    content = resInvoke['content']


    regex = re.compile(r'.*?(\{\{(.*?)(?<!\{\{!)\}\})', re.S)
    input = content
    result = regex.match(input)
    while result:
        templateData = {
            'content': result.group(1),
            'name': '',
            'data': OrderedDict(),
            # 'placeholderName': '',
            # 'contentWithPlaceholders': '',
        }

        input = input.replace(templateData['content'], '')

        if resInvoke['placeholderMap']:  templateData['content'] = ReplacePlaceholdersWithWikiContent(templateData['content'], resInvoke['placeholderMap'])
        if resVar['placeholderMap']:  templateData['content'] = ReplacePlaceholdersWithWikiContent(templateData['content'], resVar['placeholderMap'])
        if resLink['placeholderMap']:  templateData['content'] = ReplacePlaceholdersWithWikiContent(templateData['content'], resLink['placeholderMap'])

        content =result.group(2)

        if '|' in content:
            dataLines = content.split('|')
            templateData['name'] = dataLines[0].strip()
            for i in range(1, len(dataLines)):
                lineContent = dataLines[i]
                if resInvoke['placeholderMap']:  lineContent = ReplacePlaceholdersWithWikiContent(lineContent, resInvoke['placeholderMap'])
                if resVar['placeholderMap']:  lineContent = ReplacePlaceholdersWithWikiContent(lineContent, resVar['placeholderMap'])
                if resLink['placeholderMap']:  lineContent = ReplacePlaceholdersWithWikiContent(lineContent, resLink['placeholderMap'])
                lineParts = lineContent.split('=', 1)
                key = lineParts[0].strip()
                try:
                    val = lineParts[1].replace('{{!}}', '|').strip()
                except:
                    val = ''
                templateData['data'][key] = val
        elif ':' in content:
            lineContent = content
            if resInvoke['placeholderMap']:  lineContent = ReplacePlaceholdersWithWikiContent(lineContent, resInvoke['placeholderMap'])
            if resVar['placeholderMap']:  lineContent = ReplacePlaceholdersWithWikiContent(lineContent, resVar['placeholderMap'])
            if resLink['placeholderMap']:  lineContent = ReplacePlaceholdersWithWikiContent(lineContent, resLink['placeholderMap'])
            lineParts = lineContent.split(':', 1)
            templateData['name'] = lineParts[0].strip()
            try:
                templateData['data'][templateData['name']] = lineParts[1].strip()
            except:
                pass

        templateList.append(templateData)
        result = regex.match(input)

    return templateList


def GetTemplateListFromWikiPageContentRecursive(content):
    templateList = []
    pageholderMap = {}

    resLink = ReplaceWikiLinksWithPlaceholders(content)
    content = resLink['content']

    resVar = ReplaceWikiVariablesWithPlaceholders(content)
    content = resVar['content']

    resInvoke = ReplaceModuleInvokationsWithPlaceholders(content)
    content = resInvoke['content']

    regex = re.compile(r'.*?(\{\{(((?<!\{)\{|[^\{])*?)\}\})', re.S)
    input = content
    result = regex.match(input)
    templateIdx = 0
    while result:
        templateData = {
            'content': result.group(1),
            'name': '',
            'data': OrderedDict(),
            'placeholderName': '^^^TEMPLATE_PLACEHOLDER_{}^^^'.format(templateIdx),
            'contentWithPlaceholders': result.group(1),
            'placeholderMap': {},
        }
        templateIdx += 1

        if Config.debug:
            templateData['placeholderMap'].update(pageholderMap)
            if resInvoke['placeholderMap']:  templateData['placeholderMap'].update(resInvoke['placeholderMap'])
            if resVar['placeholderMap']:  templateData['placeholderMap'].update(resVar['placeholderMap'])
            if resLink['placeholderMap']:  templateData['placeholderMap'].update(resLink['placeholderMap'])
        else:
            del templateData['placeholderMap']

        input = input.replace(templateData['content'], templateData['placeholderName'])

        templateData['content'] = ReplacePlaceholdersWithWikiContent(templateData['content'], pageholderMap)
        if resInvoke['placeholderMap']:  templateData['content'] = ReplacePlaceholdersWithWikiContent(templateData['content'], resInvoke['placeholderMap'])
        if resVar['placeholderMap']:  templateData['content'] = ReplacePlaceholdersWithWikiContent(templateData['content'], resVar['placeholderMap'])
        if resLink['placeholderMap']:  templateData['content'] = ReplacePlaceholdersWithWikiContent(templateData['content'], resLink['placeholderMap'])


        content =result.group(2)

        if '|' in content:
            dataLines = content.split('|')
            templateData['name'] = dataLines[0].strip()
            for i in range(1, len(dataLines)):
                lineContent = dataLines[i]
                lineContent = ReplacePlaceholdersWithWikiContent(lineContent, pageholderMap)
                if resInvoke['placeholderMap']:  lineContent = ReplacePlaceholdersWithWikiContent(lineContent, resInvoke['placeholderMap'])
                if resVar['placeholderMap']:  lineContent = ReplacePlaceholdersWithWikiContent(lineContent, resVar['placeholderMap'])
                if resLink['placeholderMap']:  lineContent = ReplacePlaceholdersWithWikiContent(lineContent, resLink['placeholderMap'])
                lineParts = lineContent.split('=', 1)
                key = lineParts[0].strip()
                try:
                    val = lineParts[1].replace('{{!}}', '|').strip()
                except:
                    val = ''
                templateData['data'][key] = val
        elif ':' in content:
            lineContent = content
            lineContent = ReplacePlaceholdersWithWikiContent(lineContent, pageholderMap)
            if resInvoke['placeholderMap']:  lineContent = ReplacePlaceholdersWithWikiContent(lineContent, resInvoke['placeholderMap'])
            if resVar['placeholderMap']:  lineContent = ReplacePlaceholdersWithWikiContent(lineContent, resVar['placeholderMap'])
            if resLink['placeholderMap']:  lineContent = ReplacePlaceholdersWithWikiContent(lineContent, resLink['placeholderMap'])
            lineParts = lineContent.split(':', 1)
            templateData['name'] = lineParts[0].strip()
            try:
                templateData['data'][templateData['name']] = lineParts[1].strip()
            except:
                pass

        pageholderMap[templateData['placeholderName']] = templateData['contentWithPlaceholders']
        templateList.append(templateData)
        result = regex.match(input)

    return templateList



def GetWikiTextLink(wikiPageName, linkText=...):
    if linkText is ...:  linkText = wikiPageName
    wikiPageName = wikiPageName.replace(' ', '_')
    return '[[{}{}]]'.format('' if PageNamesEqual(wikiPageName, linkText) else wikiPageName+'|', linkText)

def GetLoreblurbTemplateDataForRaceOrOrgCodexEntry(raceOrOrgName, wikiPageName, desc, wikiLinkOverride=None):
    if not wikiLinkOverride:
        wikiLinkOverride = wikiPageName

    data = {
        'loreSubjectLinkName': wikiLinkOverride,
        'loreSubjectName': '{} Codex Entry'.format(raceOrOrgName),
        'loreText': desc.strip() if desc else '',
    }
    data['loreText'] = GeneralUtils.AddWikiLinksToText(GeneralUtils.CleanupImportedText(data['loreText']))
    return data

def GetLoreblurbTemplateDataForPlanet(planetInfo):
    data = {
        'loreSubjectLinkName': planetInfo['name'].strip(),
        'loreSubjectName': planetInfo['name'].strip(),
        'loreText': planetInfo['info'].strip() if planetInfo['info'] else '',
    }
    data['loreText'] = GeneralUtils.AddWikiLinksToText(GeneralUtils.CleanupImportedText(data['loreText']))
    return data

def GetLoreblurbTemplateDataForObject(objectInfo):
    data = {
        'loreSubjectLinkName': objectInfo['name'].strip(),
        'loreSubjectName': objectInfo['name'].strip(),
        'loreText': objectInfo['scanText'].strip() if objectInfo['scanText'] else (objectInfo['info'].strip() if objectInfo['info'] else ''),
    }
    data['loreText'] = GeneralUtils.AddWikiLinksToText(GeneralUtils.CleanupImportedText(data['loreText']))
    return data


def GetLoreTemplateDataForRaceOrOrg(raceOrOrgName, wikiPageName=None, wikiLinkOverride=None):
    from SFIWikiBotLib import GalaxyUtils

    if not wikiPageName:
        wikiPageName = raceOrOrgName

    if not wikiLinkOverride:
        wikiLinkOverride = wikiPageName

    data = {
        'LoreCategory': wikiPageName,
        'loreCategoryIntro': 'This category contains information regarding lore related to the {}.'.format(GetWikiTextLink(wikiLinkOverride, wikiPageName)),
        'planetsLore': '',
        'objectsLore': '',
        'codexLore': '',
        'miscLore': '',
    }

    desc = ''
    raceId = SmallConstants.GetNprIdFromName(raceOrOrgName)
    if raceId:
        desc = SmallConstants.GetRaceDescriptionById(raceId)
    if not desc:
        orgInfo = SmallConstants.GetOrgInfoByName(raceOrOrgName)
        if orgInfo:
            desc = orgInfo['intro']
    loreBlurb = GetLoreblurbTemplateDataForRaceOrOrgCodexEntry(raceOrOrgName, wikiPageName, desc, wikiLinkOverride)
    if loreBlurb['loreText']:
        data['codexLore'] = ConvertDictionaryToWikiTemplate('Loreblurb', loreBlurb, False)

    raceObjData = GalaxyUtils.GetPlanetsAndObjectsAssociatedWithRaceOrOrg(wikiPageName)
    for planetInfo in raceObjData['planets']:
        loreBlurb = GetLoreblurbTemplateDataForPlanet(planetInfo)
        if loreBlurb['loreText']:
            data['planetsLore'] += ConvertDictionaryToWikiTemplate('Loreblurb', loreBlurb, False)
        else:
            if Config.verbose > 0:  print("Skipping planet", planetInfo['name'], 'due to lack of lore')

    for objectInfo in raceObjData['objects']:
        loreBlurb = GetLoreblurbTemplateDataForObject(objectInfo)
        if loreBlurb['loreText']:
            data['objectsLore'] += ConvertDictionaryToWikiTemplate('Loreblurb', loreBlurb, False)
        else:
            if Config.verbose > 0:  print("Skipping object", objectInfo['name'], 'due to lack of lore')

    return data


def GetWikiContentsForLorePage():
    content = ''
    for orgName, orgLink in Config.mainFactionList.items():
        loreData = GetLoreTemplateDataForRaceOrOrg(orgName, orgName, orgLink)
        content += ConvertDictionaryToWikiTemplate('Lore', loreData, False)
        content += "\n\n"

    for wikiPageName, nprName in Config.nprPageNameMapping.items():
        if nprName in Config.unreleasedRaceList:
            continue
        loreData = GetLoreTemplateDataForRaceOrOrg(nprName, wikiPageName)
        content += ConvertDictionaryToWikiTemplate('Lore', loreData, False)
        content += "\n\n"

    return content







def UpdateLorePage(comment=None, allowRetry=True):
    from SFIWikiBotLib import GalaxyUtils
    rtnVal = False
    pageName = 'Lore'


    site = GetWikiClientSiteObject()
    page = site.pages[pageName]
    if page.exists:
        updatesIncluded = []

        testOrgNameList = [ v.strip().lower() for v in Config.mainFactionList.keys() ]
        testRaceWikiPageList = [ v.strip().lower() for v in Config.nprPageNameMapping.keys() ]

        content = page.text()
        templateList = GetTemplateListFromWikiPageContentRecursive(content)

        for template in templateList:
            if template['name'].lower() == 'lore':

                with suppress(KeyError):
                    testLoreCategory = template['data']['LoreCategory'].strip().lower()
                    loreData = None

                    for orgName, orgLink in Config.mainFactionList.items():
                        if orgName.strip().lower() == testLoreCategory:
                            loreData = GetLoreTemplateDataForRaceOrOrg(orgName, orgName, orgLink)
                            break

                    if not loreData:
                        for wikiPageName, nprName in Config.nprPageNameMapping.items():
                            if wikiPageName.strip().lower() == testLoreCategory:
                                loreData = GetLoreTemplateDataForRaceOrOrg(nprName, wikiPageName)

                    if not loreData:
                        if Config.debug or Config.verbose >= 1:
                            print("Lore for", template['data']['LoreCategory'], "could not be matched to an existing organization or race. Skipping.")
                        continue

                    if 'miscLore' in template['data'] and template['data']['miscLore']:
                        loreData['miscLore'] = template['data']['miscLore']

                    if GeneralUtils.GenerateDataSignature(loreData) != GeneralUtils.GenerateDataSignature(template['data']):
                        # if template['data']['LoreCategory'] == 'Alliance Science Corps':
                        #     td = dict(template['data'])
                        #     pp(td)
                        #     print("\n-------------------\n\n")
                        #     pp(loreData)
                        #     return
                        updatedTemplate = ConvertDictionaryToWikiTemplate('Lore', loreData, False)
                        updatedTemplate = updatedTemplate.strip()
                        newContent = content.replace(template['content'].strip(), updatedTemplate)
                        if newContent and newContent != content:
                            content = newContent
                            updatesIncluded.append(template['data']['LoreCategory'])
                        else:
                            if Config.debug:  print("Lore content update failed for", template['data']['LoreCategory'])

        if updatesIncluded:
            try:
                if not comment:
                    comment = "Updating {}".format(', '.join(updatesIncluded))
                page.edit(content, comment)
                if Config.verbose >= 1:  print("Page Updated: Lore -", comment)
                rtnVal = True
                time.sleep(Config.pauseAfterSuccessfullyUpdatingWikiPageInSec)

            except mwclient.errors.AssertUserFailedError as ex:
                time.sleep(Config.pauseAfterFailingToUpdateWikiPageInSec)

                if allowRetry:
                    if Config.debug or Config.verbose >= 1:  print("Retrying update: Lore -", comment)
                    GetWikiClientSiteObject(True)
                    return UpdateLorePage(comment, False)

                if Config.debug or Config.verbose >= 1:  print("Failed to update: Lore -", comment)
                raise ex
        else:
            time.sleep(Config.pauseAfterSkippingWikiPageUpdateInSec)

    else:
        if Config.debug or Config.verbose >= 1:  print("Lore page not found")

    return rtnVal





def GetCategoryListFromWikiPageContent(content):
    categoryList = []

    regex = re.compile(r'.*?(\[\[\s*Category\s*:\s*([^\]]*?)\]\])', re.S | re.I)
    input = content
    result = regex.match(input)
    while result:
        categoryData = {
            'content': result.group(1),
            'name': result.group(2),
        }

        input = input.replace(categoryData['content'], '')
        categoryList.append(categoryData)
        result = regex.match(input)

    return categoryList


def GetWikiLinksFromContent(content):
    wikiLinkList = {}
    idx = 0

    regex = re.compile(r'.*?\[\[([^\|\]]+)(\|([^\]]*))?\]\]', re.S)
    result = regex.match(content)
    while result:
        idx += len(result.group(0))

        pageName = result.group(1)
        linkDisplay = result.group(3)
        if not linkDisplay:  linkDisplay = pageName
        wikiLinkList[linkDisplay] = pageName

        result = regex.match(content[idx:])

    return wikiLinkList


def GetWikiPageSectionsFromContent(content):
    pageSectionList = OrderedDict()
    pageSectionList['__INTRO__'] = ''

    regex = re.compile(r'.*?(\n|^)((=={1,3}\s*(.*?)\s*=={1,3}(\n|$))(.*?))((?<=\n)==|$)', re.S)
    input = content
    result = regex.match(input)
    while result:
        section = {
            'content': result.group(2),
            'name': result.group(4).strip("'").strip(),
            'nameContent': result.group(3),
            'value': result.group(6).strip(),
        }
        if section['value'] == '*':
            section['value'] = ''
        input = input.replace(section['content'], '')
        pageSectionList[section['name']] = section
        result = regex.match(input)

    input = input.strip()
    if input:
        section = {
            'content': input,
            'name': '__INTRO__',
            'value': input,
        }
        pageSectionList['__INTRO__'] = section

    return pageSectionList



def ReplaceWikiLinksWithPlaceholders(content):
    placeholderMap = {}

    regex = re.compile(r'.*?(\[\[(.*?)\]\])', re.S)

    result = regex.match(content)
    idx = 0
    while result:
        wikiLink = result.group(1)
        placeholder = '^^^LINK_PLACEHOLDER_{}^^^'.format(idx)
        content = content.replace(wikiLink, placeholder)
        placeholderMap[placeholder] = wikiLink

        result = regex.match(content)
        idx += 1


    return {
        'content': content,
        'placeholderMap': placeholderMap,
    }


def ReplaceWikiVariablesWithPlaceholders(content):
    placeholderMap = {}

    regex = re.compile(r'.*?(\{\{\s*([a-zA-Z0-9_-]*)\s*\}\})', re.S)

    result = regex.match(content)
    idx = 0
    while result:
        wikiLink = result.group(1)
        placeholder = '^^^VAR_PLACEHOLDER_{}^^^'.format(idx)
        content = content.replace(wikiLink, placeholder)
        placeholderMap[placeholder] = wikiLink

        result = regex.match(content)
        idx += 1


    return {
        'content': content,
        'placeholderMap': placeholderMap,
    }


def ReplaceModuleInvokationsWithPlaceholders(content):
    placeholderMap = {}

    regex = re.compile(r'.*?(\{\{#invoke:(.*?)}\})', re.S)

    result = regex.match(content)
    idx = 0
    while result:
        wikiLink = result.group(1)
        placeholder = '^^^INV_PLACEHOLDER_{}^^^'.format(idx)
        content = content.replace(wikiLink, placeholder)
        placeholderMap[placeholder] = wikiLink

        result = regex.match(content)
        idx += 1


    return {
        'content': content,
        'placeholderMap': placeholderMap,
    }


def ReplacePlaceholdersWithWikiContent(content, placeholderMap):
    for placeholder, wikiContent in placeholderMap.items():
        prevContent = ""
        while prevContent != content:
            prevContent = content
            content = content.replace(placeholder, wikiContent)

    return content


def UploadMissingItemImages():
    from SFIWikiBotLib import ItemUtils

    raceList = [ v['name'] for v in SmallConstants.raceData if v['name'] not in Config.unreleasedRaceList ]
    for race in raceList:
        itemRsJson = '{"condition":"AND","rules":[{"id":"ItemUtils.GetRaceForItem","field":"ItemUtils.GetRaceForItem","type":"string","input":"select","operator":"equal","value":"' + race + '"},{"condition":"OR","rules":[{"id":"ItemUtils.IsItemHidden","field":"ItemUtils.IsItemHidden","type":"boolean","input":"radio","operator":"equal","value":false},{"condition":"AND","rules":[{"id":"ItemUtils.GetRaceForItem","field":"ItemUtils.GetRaceForItem","type":"string","input":"select","operator":"not_equal","value":"Humans"},{"id":"ItemUtils.GetRaceForItem","field":"ItemUtils.GetRaceForItem","type":"string","input":"select","operator":"not_equal","value":"Aralien"}]}]}],"valid":true}'
        itemRs = json.loads(itemRsJson)
        fullItemList = GeneralUtils.SearchObjectListUsingRuleset(ItemUtils.itemData, itemRs)

        ItemUtils.DownloadMissingImagesForTheWikiByItemList(fullItemList)
        ItemUtils.UploadImagesToWikiForItemList(fullItemList)


def UploadAllItemImagesToWiki():
    from SFIWikiBotLib import ItemUtils

    raceList = [ v['name'] for v in SmallConstants.raceData if v['name'] not in Config.unreleasedRaceList ]
    for race in raceList:
        itemRsJson = '{"condition":"AND","rules":[{"id":"ItemUtils.GetRaceForItem","field":"ItemUtils.GetRaceForItem","type":"string","input":"select","operator":"equal","value":"' + race + '"},{"condition":"OR","rules":[{"id":"ItemUtils.IsItemHidden","field":"ItemUtils.IsItemHidden","type":"boolean","input":"radio","operator":"equal","value":false},{"condition":"AND","rules":[{"id":"ItemUtils.GetRaceForItem","field":"ItemUtils.GetRaceForItem","type":"string","input":"select","operator":"not_equal","value":"Humans"},{"id":"ItemUtils.GetRaceForItem","field":"ItemUtils.GetRaceForItem","type":"string","input":"select","operator":"not_equal","value":"Aralien"}]}]}],"valid":true}'
        itemRs = json.loads(itemRsJson)
        fullItemList = GeneralUtils.SearchObjectListUsingRuleset(ItemUtils.itemData, itemRs)

        ItemUtils.DownloadImagesByItemList(fullItemList)
        ItemUtils.UploadImagesToWikiForItemList(fullItemList)


def UploadMissingPlanetImages():
    from SFIWikiBotLib import GalaxyUtils

    planetList = GalaxyUtils.GetFullPlanetList()
    GalaxyUtils.DownloadMissingImagesForTheWikiByPlanetList(planetList)
    GalaxyUtils.UploadImagesToWikiForPlanetList(planetList)


def UploadMissingShipImages():
    from SFIWikiBotLib import ShipUtils

    shipList = [ v for v in ShipUtils.shipData if not ShipUtils.IsShipHidden(v) ]
    ShipUtils.DownloadMissingImagesForTheWikiByShipList(shipList)
    ShipUtils.UploadImagesToWikiForShipList(shipList)


def UploadAllShipImagesToWiki():
    from SFIWikiBotLib import ShipUtils

    shipList = [ v for v in ShipUtils.shipData if not ShipUtils.IsShipHidden(v) ]
    ShipUtils.DownloadImagesByShipList(shipList)
    ShipUtils.UploadImagesToWikiForShipList(shipList)


def RefreshWikiImageCache():
    data = GetWikiImageFileList.__wrapped__()
    if len(data) > 1000:  # Sanity check - Do not overwrite with truncated data
        wikiCache.set(('WikiUtils.GetWikiImageFileList',), data, expire=Config.wikiImageAndPageListTtl)


def RefreshWikiPageCache():
    data = GetWikiArticlePageList.__wrapped__()
    if len(data) > 250:  # Sanity check - Do not overwrite with truncated data
        wikiCache.set(('WikiUtils.GetWikiArticlePageList',), data, expire=Config.wikiImageAndPageListTtl)


def UploadImageListToWiki(imageList):
    backupDir = os.path.join('public', 'images', 'backup')

    for imageInfo in imageList:
        if not os.path.exists(imageInfo['filepath']):
            continue
        if 'png' != imghdr.what(imageInfo['filepath']):
            continue

        res = UploadImageToWiki(imageInfo['filepath'], imageInfo['name'], imageInfo['description'])
        if res is True:
            backupPath = os.path.join(backupDir, imageInfo['subDir'])
            GeneralUtils.mkdirr(backupPath)
            backupPath = os.path.join(backupPath, imageInfo['filename'])
            os.replace(imageInfo['filepath'], backupPath)
        else:
            print("Failed to upload {}".format(imageInfo['name']))
            pp(res)

        time.sleep(1.5)  # We're not in a hurry.  Don't overwhelm the wiki

    return True


def UploadImageToWiki(path, name, desc='', allowOverwrite=True):
    rtnVal = False
    site = GetWikiClientSiteObject()

    if not desc:
        desc = name


    with open(path, 'rb') as f:
        retryUploadReq = False
        try:
            result = site.upload(
                file=f,
                comment="Adding image for {}".format(desc),
                description=desc,
                filename=name
            )

            if result['result'].lower() == 'warning' and ('exists' in result['warnings'] or 'duplicate' in result['warnings'] or 'was-deleted' in result['warnings']):
                if 'nochange' not in result['warnings']:
                    retryUploadReq = True
        except:
            raise

        if allowOverwrite and retryUploadReq:
            time.sleep(Config.pauseAfterFailingToUpdateWikiPageInSec)

            #  Image already exists or there's a duplicate - confirm we want to overrwrite/add by uploading again using the image session
            ses = result['sessionkey']
            result = site.upload(filename=name, filekey=ses, ignore=True, comment="Updating image")

        if result['result'].lower() == 'success':
            rtnVal = True
            time.sleep(Config.pauseAfterSuccessfullyUpdatingWikiPageInSec)
        else:
            rtnVal = result
            if 'nochange' in result['warnings']:
                rtnVal = True
            time.sleep(Config.pauseAfterFailingToUpdateWikiPageInSec)

    return rtnVal


def AddMissingItemWikiPages():
    from SFIWikiBotLib import ItemUtils

    rtnVal = {
        'pagesAdded': [],
        'pagesAlreadyExist': [],
        'pagesFailedToSave': [],
    }

    site = GetWikiClientSiteObject()

    itemList = [ v for v in ItemUtils.itemData if not ItemUtils.GetItemWikiArticlePage(v) and v['type'] > 1 and not ItemUtils.IsItemHidden(v) ]
    for curItemList in ItemUtils.ItemPageIter(itemList):
        primaryItem = curItemList[-1]

        nameInfo = ItemUtils.SplitNameIntoBaseNameAndItemLevel(primaryItem['name'])
        pageName = nameInfo['fullNameMinusLevel']

        page = site.pages[pageName]
        if not page.exists:
            content = ItemUtils.GetItemPageContentForItemRangeList(curItemList)
            try:
                page.edit(content, 'Adding item page')
                if Config.verbose >= 1:  print("Page added: {}".format(pageName))
                rtnVal['pagesAdded'].append(pageName)
                time.sleep(Config.pauseAfterSuccessfullyUpdatingWikiPageInSec)

            except:
                if Config.debug or Config.verbose >= 1:  print("Failed to add: {}".format(pageName))
                time.sleep(Config.pauseAfterFailingToUpdateWikiPageInSec)
                rtnVal['pagesFailedToSave'].append(pageName)
        else:
            rtnVal['pagesAlreadyExist'].append(pageName)
            time.sleep(Config.pauseAfterSkippingWikiPageUpdateInSec)

    return rtnVal


def AddMissingShipWikiPages():
    from SFIWikiBotLib import ShipUtils

    rtnVal = {
        'pagesAdded': [],
        'pagesAlreadyExist': [],
        'pagesFailedToSave': [],
    }

    site = GetWikiClientSiteObject()

    shipList = [ v for v in ShipUtils.shipData if not ShipUtils.GetShipWikiPageName(v) and not ShipUtils.IsShipHidden(v) ]
    for ship in shipList:
        pageName = ship['name']

        page = site.pages[pageName]
        if not page.exists:
            content = ShipUtils.GetShipPageContent(ship)
            try:
                page.edit(content, 'Adding ship page')
                if Config.verbose >= 1:  print("Page added: {}".format(pageName))
                rtnVal['pagesAdded'].append(pageName)
                time.sleep(Config.pauseAfterSuccessfullyUpdatingWikiPageInSec)

            except:
                if Config.debug or Config.verbose >= 1:  print("Failed to add: {}".format(pageName))
                time.sleep(Config.pauseAfterFailingToUpdateWikiPageInSec)
                rtnVal['pagesFailedToSave'].append(pageName)
        else:
            rtnVal['pagesAlreadyExist'].append(pageName)
            time.sleep(Config.pauseAfterSkippingWikiPageUpdateInSec)

    return rtnVal


def UpdateAllWikiMainShipPages(comment=None):
    from SFIWikiBotLib import ShipUtils
    rtnVal = {
        'pagesUpdated': [],
        'pagesAlreadyUpToDate': [],
    }

    shipPageList = {
        'Category:Human Ships': ShipUtils.GetHumanPlayerShipList('default'),
        'Category:Aralien Ships': ShipUtils.GetAralienPlayerShipList('default'),
        'Restricted Ships': ShipUtils.GetRestrictedShipList('race'),
    }

    for pageName, shipList in shipPageList.items():
        if UpdateWikiMainShipPage(pageName, shipList, comment):
            rtnVal['pagesUpdated'].append(pageName)
            time.sleep(Config.pauseAfterSuccessfullyUpdatingWikiPageInSec)
        else:
            rtnVal['pagesAlreadyUpToDate'].append(pageName)
            time.sleep(Config.pauseAfterSkippingWikiPageUpdateInSec)

    return rtnVal


def UpdateWikiMainShipPage(pageName, shipList, comment=None):
    rtnVal = False

    site = GetWikiClientSiteObject()
    page = site.pages[pageName]
    content = page.text()
    newContent = content

    sectionList = GetWikiPageSectionsFromContent(content)
    for sectionInfo in sectionList.values():
        tableList = GetTableListFromWikiPageContent(sectionInfo['content'])
        if not tableList:  continue

        rs = None
        if sectionInfo['name'] == 'Drones':
            rs = {'condition': 'AND', 'rules': [{'id': 'ShipUtils.GetTypeForShip', 'field': 'ShipUtils.GetTypeForShip', 'type': 'string', 'input': 'select', 'operator': 'equal', 'value': 'Drone'}], 'valid': True}
        elif sectionInfo['name'] == 'Turrets':
            rs = {'condition': 'AND', 'rules': [{'id': 'ShipUtils.GetTypeForShip', 'field': 'ShipUtils.GetTypeForShip', 'type': 'string', 'input': 'select', 'operator': 'equal', 'value': 'Turret'}], 'valid': True}
        elif sectionInfo['name'] == 'Fighters':
            rs = {'condition': 'AND', 'rules': [{'id': 'isLowMass', 'field': 'isLowMass', 'type': 'boolean', 'input': 'radio', 'operator': 'equal', 'value': True}], 'valid': True}
        elif sectionInfo['name'] == 'Medium Ships':
            # rs = {'condition': 'AND', 'rules': [{'id': 'isLowMass', 'field': 'isLowMass', 'type': 'boolean', 'input': 'radio', 'operator': 'equal', 'value': False}, {'id': 'isHighMass', 'field': 'isHighMass', 'type': 'boolean', 'input': 'radio', 'operator': 'equal', 'value': False}], 'valid': True}
            rs = {'condition': 'AND', 'rules': [{'id': 'isLowMass', 'field': 'isLowMass', 'type': 'boolean', 'input': 'radio', 'operator': 'equal', 'value': False}, {'condition': 'OR', 'rules': [{'id': 'largeSecondary', 'field': 'largeSecondary', 'type': 'integer', 'input': 'number', 'operator': 'equal', 'value': 0}, {'id': 'mass', 'field': 'mass', 'type': 'double', 'input': 'number', 'operator': 'less', 'value': 2.3}, {'condition': 'AND', 'rules': [{'id': 'unlockLevel', 'field': 'unlockLevel', 'type': 'integer', 'input': 'number', 'operator': 'less', 'value': 50}, {'id': 'ShipUtils.ShipCanBeBoughtByPlayers', 'field': 'ShipUtils.ShipCanBeBoughtByPlayers', 'type': 'boolean', 'input': 'radio', 'operator': 'equal', 'value': True}]}]}], 'valid': True}
        elif sectionInfo['name'] == 'Heavy Ships':
            # rs = {'condition': 'AND', 'rules': [{'id': 'isHighMass', 'field': 'isHighMass', 'type': 'boolean', 'input': 'radio', 'operator': 'equal', 'value': True}], 'valid': True}
            rs = {'condition': 'AND', 'rules': [{'id': 'largeSecondary', 'field': 'largeSecondary', 'type': 'integer', 'input': 'number', 'operator': 'greater_or_equal', 'value': 1}, {'id': 'mass', 'field': 'mass', 'type': 'double', 'input': 'number', 'operator': 'greater_or_equal', 'value': 2.3}, {'condition': 'OR', 'rules': [{'id': 'unlockLevel', 'field': 'unlockLevel', 'type': 'integer', 'input': 'number', 'operator': 'greater_or_equal', 'value': 50}, {'id': 'ShipUtils.ShipCanBeBoughtByPlayers', 'field': 'ShipUtils.ShipCanBeBoughtByPlayers', 'type': 'boolean', 'input': 'radio', 'operator': 'equal', 'value': False}]}], 'valid': True}
        if not rs:  continue

        sectionShipList = GeneralUtils.SearchObjectListUsingRuleset(shipList, rs)
        newContent = newContent.replace(tableList[0]['content'].strip(), GetMainShipPageTableForShipList(sectionShipList).strip())

    if content != newContent:
        if not comment:
            comment = 'Updating Ship Lists'
        page.edit(newContent, comment)
        if Config.verbose >= 1:  print("Page Updated: {} - {}".format(pageName, comment))
        rtnVal = True

    return rtnVal



def FixShipPages(replacementList={}, comment=None, shipList=..., allowRetry=True, pageStatusSoFar=None):
    from SFIWikiBotLib import ShipUtils

    if not pageStatusSoFar:
        rtnVal = {
            'pagesUpdated': [],
            'pagesAlreadyUpToDate': [],
            'pagesFailedToUpdate': [],
            'pagesNotFound': [],
        }
    else:
        rtnVal = pageStatusSoFar


    if shipList is ...:
        hpShips = ShipUtils.GetHumanPlayerShipList()
        alShips = ShipUtils.GetAralienPlayerShipList()
        npcShips = ShipUtils.GetRestrictedShipList()
        nprShips = ShipUtils.GetNPRShipList()
        shipList = hpShips + alShips + npcShips + nprShips

    site = GetWikiClientSiteObject()
    for ship in shipList:
        pageName = ship['name']
        if pageName in rtnVal['pagesUpdated'] \
            or pageName in rtnVal['pagesAlreadyUpToDate'] \
            or pageName in rtnVal['pagesFailedToUpdate'] \
            or pageName in rtnVal['pagesNotFound']:
            continue;

        page = site.pages[ship['name']]
        if page.exists:
            content = page.text()
            newContent = content

            for searchStr, replaceStr in replacementList.items():
                newContent = newContent.replace(searchStr, replaceStr)

            if content != newContent:
                loopComment = comment
                if not loopComment:
                    loopComment = 'Fixing an issue on the ship pages.'

                try:
                    page.edit(newContent, loopComment)
                    if Config.verbose >= 1:  print("Page Updated: {} - {}".format(pageName, loopComment))
                    rtnVal['pagesUpdated'].append(pageName)
                    time.sleep(Config.pauseAfterSuccessfullyUpdatingWikiPageInSec)

                except mwclient.errors.AssertUserFailedError as ex:
                    time.sleep(Config.pauseAfterFailingToUpdateWikiPageInSec)
                    if allowRetry:
                        if Config.debug:  print("Retrying update: {} - {}".format(pageName, loopComment))
                        GetWikiClientSiteObject(True)
                        return FixShipPages(replacementList, comment, shipList, False, rtnVal)
                    if Config.debug or Config.verbose >= 1:  print("Failed to update: {} - {}".format(pageName, loopComment))
                    raise ex
            else:
                rtnVal['pagesAlreadyUpToDate'].append(pageName)
                time.sleep(Config.pauseAfterSkippingWikiPageUpdateInSec)
        else:
            rtnVal['pagesNotFound'].append(pageName)
            time.sleep(Config.pauseAfterSkippingWikiPageUpdateInSec)

    return rtnVal





def GetWikiClientSiteObject(forceLogin=False):
    global wikiClientSite

    if not wikiClientSite:
        forceLogin=True
        wikiClientSite = mwclient.Site( 'starfighter-infinity.fandom.com', path='/', scheme='https' )

    if forceLogin and Config.botUsername and Config.botPassword:
        wikiClientSite.login(Config.botUsername, Config.botPassword)

    return wikiClientSite


#  Simulate the output from  mw.util.wikiGetlink()
def GetWikiLink(input):
    safeChars = '/:-_.'
    return 'https://{}/wiki/{}'.format(
        wikiServerName,
        urllib.parse.quote(input.replace(' ', '_').replace('~', '%7E'), safeChars)
    )



def GetWikiImageForNameList(nameList):
    try:
        primaryItemNameList = [v.lower() for v in nameList]
        altItemNameList = []
        for name in primaryItemNameList:
            altItemNameList.append(name)

            altName = name.replace(' ', '_')
            if altName not in altItemNameList:
                altItemNameList.append(altName)
            altName = name.replace('_', ' ')
            if altName not in altItemNameList:
                altItemNameList.append(altName)
            altName = name.replace(' ', '')
            if altName not in altItemNameList:
                altItemNameList.append(altName)
            altName = name.replace(' ', '-')
            if altName not in altItemNameList:
                altItemNameList.append(altName)

        wikiImageList = GetWikiImageFileList()
        cmpWikiImageList = {}
        for wikiImage in wikiImageList:
            imageWithoutExt = os.path.splitext(wikiImage)[0]
            cmpWikiImageList[imageWithoutExt.lower()] = wikiImage

        for searchImage in altItemNameList:
            if searchImage in cmpWikiImageList:
                return cmpWikiImageList[searchImage]
    except:
        pass

    return None


def GetWikiArticlePageForNameList(nameList, finalRedirect=False):
    rtnVal = None
    try:
        primaryItemNameList = nameList
        altItemNameList = []
        for name in nameList:
            name = name.lower()
            altName = name.replace(' ', '_')
            if altName not in altItemNameList:
                altItemNameList.append(altName)
            altName = name.replace(' ', '')
            if altName not in altItemNameList:
                altItemNameList.append(altName)
            altName = name.replace(' ', '-')
            if altName not in altItemNameList:
                altItemNameList.append(altName)

        wikiPageList = GetWikiArticlePageList()
        for wikiPage in wikiPageList:
            if wikiPage in primaryItemNameList:
                rtnVal = wikiPage
            if not rtnVal:
                wikiPageLower = wikiPage.lower()
                if wikiPageLower in primaryItemNameList:
                    rtnVal = wikiPage
                elif wikiPageLower in altItemNameList:
                    rtnVal = wikiPage
    except:
        pass

    if rtnVal and finalRedirect:
        site = GetWikiClientSiteObject()
        page = site.pages[rtnVal]
        redirect = GetWikiPageRedirect(page.text())
        if redirect:
            rtnVal = redirect

    return rtnVal




def CreateWikiSiteBackup(includeImages=True, includeTemplates=True, subDirName=None):
    backupFilepath = os.path.join(siteBackupPath, date.today().isoformat() if not subDirName else subDirName)
    os.makedirs(backupFilepath, exist_ok=True)

    if includeImages:
        imageBackupFilepath = os.path.join(backupFilepath, 'images')
        os.makedirs(imageBackupFilepath, exist_ok=True)

    if includeTemplates:
        templateBackupFilepath = os.path.join(backupFilepath, 'templates')
        os.makedirs(templateBackupFilepath, exist_ok=True)

    site = GetWikiClientSiteObject()

    if includeTemplates:
        for page in site.allpages(namespace=10):
            fname = urllib.parse.quote(page.normalize_title(page.name), '')
            fpath = os.path.join(templateBackupFilepath, fname)
            if not os.path.isfile(fpath):
                with open(fpath, 'w') as f:
                    f.write(page.text())
                    time.sleep(0.75)
            else:
                time.sleep(0.25)

    wikiPageList = GetWikiArticlePageList()
    for page in site.allpages():
        fname = urllib.parse.quote(page.normalize_title(page.name), '')
        fpath = os.path.join(backupFilepath, fname)
        if not os.path.isfile(fpath):
            with open(fpath, 'w') as f:
                f.write(page.text())
                time.sleep(0.75)
        else:
            time.sleep(0.25)

    if includeImages:
        wikiImageList = GetWikiImageFileList()
        for img in site.allimages():
            fname = urllib.parse.quote(img.normalize_title(img.name.replace('File:', '')), '')
            fpath = os.path.join(imageBackupFilepath, fname)

            if not os.path.isfile(fpath):
                hist = img.imagehistory()
                imageInfo = hist.next()

                r = requests.get(imageInfo['url'])
                with open(fpath, 'wb') as f:
                    f.write(r.content)

                time.sleep(0.75)

        else:
            time.sleep(0.25)






@wikiCache.memoize(expire=Config.wikiImageAndPageListTtl)
def GetWikiImageFileList():
    site = GetWikiClientSiteObject()

    imageList = []
    for img in site.allimages():
        imageList.append(img.normalize_title(img.page_title))

    return imageList


@wikiCache.memoize(expire=Config.wikiImageAndPageListTtl)
def GetWikiArticlePageList():
    site = GetWikiClientSiteObject()

    pageList = []
    for page in site.allpages():
        pageList.append(page.normalize_title(page.page_title))

    return pageList




def GetMainShipPageTableForShipList(shipList):
    from SFIWikiBotLib import ShipUtils

    colCount = 4 if len(shipList) > 6 else 3
    idx = 0

    content = '{| class="article-table"\n'
    for ship in shipList:
        if idx and idx % colCount == 0:  content += '|-\n'

        imageName = ShipUtils.GetShipWikiImage(ship)
        pageName = ShipUtils.GetShipWikiPageName(ship)
        if not pageName:  pageName = ship['name']

        if imageName:
            content += '![[File:{}|centre|thumb|145x145px|link={}]]<p style="text-align:center;">[[{}{}]]</p>\n'.format(imageName, pageName, pageName, '' if pageName == ship['name'] else '|{}'.format(ship['name']))
        else:
            content += '!<p style="text-align:center;">[[{}{}]]</p>\n'.format(pageName, '' if PageNamesEqual(pageName, ship['name']) else '|{}'.format(ship['name']))
        idx += 1

    if idx % colCount:
        for i in range(0, colCount - (idx % colCount)):
            content += '!\n'

    content += '|}'
    return content



def ConvertDictionaryToWikiTemplate(templateName, templateData, escapeTemplateData=True):
    rtnVal = "{{" + templateName + "\n"
    for key, val in templateData.items():
        res = ReplaceWikiLinksWithPlaceholders(str(val))
        valContent = res['content']
        if escapeTemplateData:  valContent = valContent.replace('|', '{{!}}')
        val = ReplacePlaceholdersWithWikiContent(valContent, res['placeholderMap'])
        rtnVal += "| {} = {}\n".format(key, val)

    rtnVal += "}}\n"
    return rtnVal


def ConvertListToWikiTable(tableData, tableHeader = None, tableTitle = None, tableClass = None, tableId = None, tableColumnTitleList = None):
    rtnVal = ""
    if len(tableData) > 0:
        if tableHeader:
            rtnVal += '==={}===\n\n'.format(tableHeader)
        if tableTitle:
            rtnVal += '====<div class="tableCaption">{}</div>====\n\n'.format(tableTitle)

        rtnVal += "{|"
        if tableId:
            rtnVal += ' id="sf-{}"'.format(tableId)
        if tableClass:
            rtnVal += ' class="' + tableClass + '"'
        rtnVal += "\n"

        first = True
        for row in tableData:
            values = "|-\n"
            headings = ""
            if first:
                headings += "|-\n"

            idx = 0
            for key, val in row.items():
                if first:
                    if tableColumnTitleList and len(tableColumnTitleList) > idx and tableColumnTitleList[idx]:
                        headings += '! <span title="{}">{}</span>\n'.format(tableColumnTitleList[idx], key)
                    else:
                        headings += "! " + key + "\n"
                values += "| " + str(val) + "\n"
                idx += 1

            rtnVal += headings
            rtnVal += values
            first = False

        rtnVal += "|}\n"

    return rtnVal



def Initialize():
    pass


Initialize()
