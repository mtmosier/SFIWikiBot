#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import json
import os
import re
import time
import requests
import js2py
from diskcache import Cache
from SFIWikiBotLib import Config
from SFIWikiBotLib import GeneralUtils


dataCache = Cache(directory=os.path.join(Config.cacheDir, 'cache.gameData'))



# Found at https://darty11.github.io/common.js
# //very expensive function used to fix a bug in the game that prevents engine ranges from containing their items.
# function fixEngines(weaponRanges, weaponData){
#     for(rangeId in weaponRanges){
#         var range = weaponRanges[rangeId];
#         if(range.items.length == 0 && (range.type == 0 || range.type == 4)){
#             var id = range.id;
#             for(weaponId in weaponData){
#
#                 if(weaponId.startsWith(id+"_") || weaponId==id){
#                     var index = 0;
#                     var end = weaponId.replace(id+"_"," ");
#                     if(!isNaN(end)){
#                         index = end;
#                     }
#                     range.items[Number(index)] = weaponId;
# 					weaponData[weaponId].range = range;
#                 }
#             }
#         }
#     }
# }


def LoadItemDataFromPublicStarfighterWebsite():

    itemList = []
    itemListWeb = LoadDataFromPublicStarfighterWebsite()['itemList']

    for itemWeb in itemListWeb:
        item = json.loads(itemWeb['json'].replace('""', '\"'))
        itemWeb['json'] = ''
        item['__extData'] = itemWeb

        itemList.append(item)

    return itemList


def LoadShipDataFromPublicStarfighterWebsite():
    from SFIWikiBotLib import ShipUtils

    shipList = []
    shipListWeb = LoadDataFromPublicStarfighterWebsite()['shipList']

    for ship in shipListWeb:
        if ship['name'].lower() in ShipUtils.shipTurretMapping:
            ship['turrets'] = ShipUtils.shipTurretMapping[ship['name'].lower()]
        shipList.append(ship)

    return shipList


def RefreshPublicData():
    data = LoadDataFromPublicStarfighterWebsite.__wrapped__()
    dataCache.set(('DataLoader.LoadDataFromPublicStarfighterWebsite',), data, expire=Config.publicDatabaseContentTtl)


def RefreshPrivateData():
    funcList = {
        'LoadWeaponDataFromBenOldingWebsite': LoadWeaponDataFromBenOldingWebsite,
        'LoadWeaponRangesDataFromBenOldingWebsite': LoadWeaponRangesDataFromBenOldingWebsite,
        'LoadWeaponVariantDataFromBenOldingWebsite': LoadWeaponVariantDataFromBenOldingWebsite,
        'LoadWeaponCraftableDataFromBenOldingWebsite': LoadWeaponCraftableDataFromBenOldingWebsite,
        'LoadShipDataFromBenOldingWebsite': LoadShipDataFromBenOldingWebsite,
        'LoadSystemDataFromBenOldingWebsite': LoadSystemDataFromBenOldingWebsite,
        'LoadGateDataFromBenOldingWebsite': LoadGateDataFromBenOldingWebsite,
        'LoadConstantsData': LoadConstantsData,
    }

    for name, func in funcList.items():
        data = func.__wrapped__()
        dataCache.set(('DataLoader.' + name,), data, expire=Config.privateDatabaseContentTtl)





jsonpRegex = re.compile(r'.*?\(\s*(["\']).*?\1\s*,\s*(.*)\)', re.S)
def LoadDataFromBenOldingJsonp(dataType):
    url = Config.privateDataUrlTemplate
    if not '?' in url:  url += '?cb={}'

    response = requests.get(url.format(dataType, time.time()))
    if response.status_code != 200:
        print("Got", response.status_code, 'trying to read content from benoldinggames.co.uk for', dataType)
        return
    content = response.text
    m = jsonpRegex.match(content)
    return json.loads(m.group(2))


@dataCache.memoize(expire=Config.privateDatabaseContentTtl)
def LoadWeaponDataFromBenOldingWebsite():
    return LoadDataFromBenOldingJsonp('weapons')

@dataCache.memoize(expire=Config.privateDatabaseContentTtl)
def LoadWeaponRangesDataFromBenOldingWebsite():
    return LoadDataFromBenOldingJsonp('ranges')

@dataCache.memoize(expire=Config.privateDatabaseContentTtl)
def LoadWeaponVariantDataFromBenOldingWebsite():
    return LoadDataFromBenOldingJsonp('variant_ranges')

@dataCache.memoize(expire=Config.privateDatabaseContentTtl)
def LoadWeaponCraftableDataFromBenOldingWebsite():
    return LoadDataFromBenOldingJsonp('craftable')


@dataCache.memoize(expire=Config.privateDatabaseContentTtl)
def LoadShipDataFromBenOldingWebsite():
    return LoadDataFromBenOldingJsonp('ships')


@dataCache.memoize(expire=Config.privateDatabaseContentTtl)
def LoadSystemDataFromBenOldingWebsite():
    return LoadDataFromBenOldingJsonp('systems')

@dataCache.memoize(expire=Config.privateDatabaseContentTtl)
def LoadGateDataFromBenOldingWebsite():
    return LoadDataFromBenOldingJsonp('gates')

@dataCache.memoize(expire=Config.privateDatabaseContentTtl)
def LoadMineralDataFromBenOldingWebsite():
    return LoadDataFromBenOldingJsonp('minerals')


@dataCache.memoize(expire=Config.privateDatabaseContentTtl)
def LoadConstantsData():

    rtnData = {}

    rtnData['raceData'] = LoadDataFromBenOldingJsonp('races')
    rtnData['effectsData'] = LoadDataFromBenOldingJsonp('effects')
    rtnData['skillsData'] = LoadDataFromBenOldingJsonp('skills')

    lookup = LoadDataFromBenOldingJsonp('lookup')
    rtnData['guidanceLookup'] = lookup['guidance']
    rtnData['fireSideLookup'] = lookup['fireSide']
    rtnData['typeLookup'] = lookup['type']
    rtnData['damageTypeLookup'] = [ v.replace('Extaction', 'Extraction') for v in lookup['damageType'] ]
    rtnData['effectLookup'] = lookup['effect']
    rtnData['augTypeLookup'] = lookup['augType']
    rtnData['weaponTypeLookup'] = lookup['weaponType']
    rtnData['spawnTypeLookup'] = lookup['spawnType']
    rtnData['sectorTypeLookup'] = lookup['sectorType']
    rtnData['extraTypeLookup'] = lookup['extraType']

    return rtnData










@dataCache.memoize(expire=Config.publicDatabaseContentTtl)
def LoadDataFromPublicStarfighterWebsite():
    content = ''

    try:
        response = requests.get('{}?cb={}'.format(Config.publicDatabaseUrl, time.time()))
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        print('HTTP error occurred: {}'.format(http_err))
    except Exception as err:
        print('HTTP error occurred: {}'.format(err))
    else:
        content = response.text

    jsStr = re.sub(r'.*?(var data = \{\};.*)var showing = null;.*', '\\1', content, 0, re.S)
    jsContent = 'function getData(){\n' + jsStr + '\nreturn data;\n}'

    getData = js2py.eval_js(jsContent)
    jsData = getData()

    return {
        'shipList': jsData['Ships'].to_list(),
        'itemList': jsData['Items'].to_list()
    }



@dataCache.memoize(expire=Config.privateDatabaseContentTtl)
def LoadObjectDataFromPrivateStarfighterWebsite():
    from SFIWikiBotLib import GalaxyUtils
    content = ''

    try:
        response = requests.get('{}?cb={}'.format(Config.privateObjectListUrl, time.time()))
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        print('HTTP error occurred: {}'.format(http_err))
    except Exception as err:
        print('HTTP error occurred: {}'.format(err))
    else:
        content = response.text

    imgBaseUrl = Config.privateObjectListUrl
    imgBaseUrl = imgBaseUrl.replace(os.path.basename(imgBaseUrl), '')

    rtnData = {
        'objectList': [],
        'planetList': [],
        'anomalyList': [],
        'relicList': [],
        'structureList': [],
        'unknownList': [],
    }


    objectHtmlList = content.split('<div class="box" style="height:600px;overflow:hidden">')
    objectSectionsRegex = re.compile('.*?<h2>(.*?)</h2>.*?<p>(.*?)</p>(.*?)</div>', re.S)
    objectStatsRegex = re.compile('.*?<b>([^:]*):\s*</b>(.*?)(</span>)?<br />((?=<)|$)', re.S)
    objectImageUrlRegex = re.compile('.*?<img src="(.*?)"', re.S)

    objectList = []
    for objectHtml in objectHtmlList:
        sectionsMatch = objectSectionsRegex.match(objectHtml)
        try:
            object = {}
            object['name'] = sectionsMatch.group(1)
            object['statsData'] = {}
            object['imageUrl'] = None
            statsContent = sectionsMatch.group(2)

            statsMatch = objectStatsRegex.match(statsContent)
            while statsMatch:
                object['statsData'][statsMatch.group(1).strip()] = statsMatch.group(2).strip()
                statsContent = statsContent.replace(statsMatch.group(0), '')
                statsMatch = objectStatsRegex.match(statsContent)
            imageMatch = objectImageUrlRegex.match(sectionsMatch.group(3))
            if imageMatch:
                object['imageUrl'] = "{}{}".format(imgBaseUrl, imageMatch.group(1))

            if object['statsData']['Type'] == 'Object' or object['statsData']['Type'] == 'Objects':
                rtnData['objectList'].append(object)
            elif object['statsData']['Type'] in GalaxyUtils.planetTypeLookup:
                rtnData['planetList'].append(object)
            elif object['statsData']['Type'] == 'Anomaly':
                rtnData['anomalyList'].append(object)
            elif object['statsData']['Type'] == 'Relic':
                rtnData['relicList'].append(object)
            elif object['statsData']['Type'] == 'Structure':
                rtnData['structureList'].append(object)
            else:
                rtnData['unknownList'].append(object)
        except Exception as e:
            pass

    return rtnData
