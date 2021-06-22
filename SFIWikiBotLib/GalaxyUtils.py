#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import json
import os
import re
import requests
from collections import OrderedDict
from contextlib import suppress
from SFIWikiBotLib import DataLoader
from SFIWikiBotLib import Config
from SFIWikiBotLib import WikiUtils
from SFIWikiBotLib import GeneralUtils

galaxyData = None
gatesAndWormHoles = None
mineralData = None


def GetPlanetDiameter(scale):
    earthDiameter = 12742
    rtnVal = round(earthDiameter * scale)
    return "{}km".format(rtnVal)


def GetDisplayLocation(location):
    prefix = ''
    for galaxy, galaxyInfo in galaxyData.items():
        if galaxyInfo['id'] == location['starSystemID'] + 1:
            prefix = galaxyInfo['prefix']
            break

    return "{}-{}-{}".format(prefix, location['x'], location['y'])


def GetSystemName(id):
    with suppress(TypeError):
        return GetSystemInfo(id)['name']


def GetSystemInfo(id):
    for galaxy, galaxyInfo in galaxyData.items():
        if galaxyInfo['id'] == id + 1:
            return galaxyInfo


def GetSystemByPrefix(prefix):
    prefix = prefix.lower()
    for sysName, systemInfo in galaxyData.items():
        if systemInfo['prefix'].lower() == prefix or (prefix == 'ara' and systemInfo['name'].lower() == prefix):
            return systemInfo


def GetSystemNameByPrefix(prefix):
    with suppress(TypeError):
        return GetSystemByPrefix(prefix)['name']


def GetSystemPrefixList():
    resultList = []

    for galaxy, systemInfo in galaxyData.items():
        resultList.append(systemInfo['prefix'])

    return resultList


def GetSystemList(skipUnreleasedSystems=True):
    unreleasedSystemList = [ v.lower() for v in Config.unreleasedSystemList ]
    return [ v for v in galaxyData.values() if not skipUnreleasedSystems or v['prefix'].lower() not in unreleasedSystemList ]



planetTypeLookup = [
    "Rocky Planet",
    "Lava Planet",
    "Ocean Planet",
    "Desert Planet",
    "Earthlike Planet",
    "Artificial Planet",
    "Gas Giant",
    "Dwarf Planet",
    "Unclassified",
]



def GetPlanetType(type):
    with suppress(KeyError):
        return planetTypeLookup[type]


def GetPlanetInfoByName(planetName):
    planetName = planetName.lower()
    for galaxy, galaxyInfo in galaxyData.items():
        for planetInfo in galaxyInfo['planets']:
            if (planetInfo['name'].lower() == planetName):
                planetInfo['info'] = GeneralUtils.CleanupImportedText(planetInfo['info'])
                return planetInfo


def FindPlanet(searchPlanetName):
    resultPlanetInfo = OrderedDict()
    searchPlanetName = searchPlanetName.lower()

    for galaxy, galaxyInfo in galaxyData.items():
        for planetInfo in galaxyInfo['planets']:
            if (planetInfo['name'].lower() == searchPlanetName):
                resultPlanetInfo["Planet Name"] = planetInfo['name']
                resultPlanetInfo["Classification"] = GetPlanetType(planetInfo['planetType'])
                resultPlanetInfo["System Found In"] = GetSystemName(planetInfo['location']['starSystemID'])
                resultPlanetInfo["Sector Location (X-X)"] = "{}-{}".format(planetInfo['location']['x'], planetInfo['location']['y'])
                resultPlanetInfo["Discoverer"] = planetInfo['discoveredBy']
                resultPlanetInfo["Description"] = GeneralUtils.CleanupImportedText(planetInfo['info'])
                resultPlanetInfo["Location (Shorthand)"] = GetDisplayLocation(planetInfo['location'])
                resultPlanetInfo["Diameter (km)"] = GetPlanetDiameter(planetInfo['scale'])
                resultPlanetInfo["Water Present"] = "Yes" if planetInfo['hasWater'] else "No"
                resultPlanetInfo["Life"] = planetInfo['lifeType']
                resultPlanetInfo["Trivia"] = ""
                # if planetInfo['notes']:
                #     resultPlanetInfo["Trivia"] = "* {}".format(planetInfo['notes'])

    return resultPlanetInfo


def GetFullPlanetList(skipUnreleasedSystems=True):
    return GetSystemPlanetList('all', skipUnreleasedSystems)


def GetSystemPlanetList(systemPrefix, skipUnreleasedSystems=False):
    resultPlanetList = []
    unreleasedSystemList = [ v.lower() for v in Config.unreleasedSystemList ]

    for galaxy, systemInfo in galaxyData.items():
        if systemPrefix.lower() == "all" or systemInfo['prefix'].lower() == systemPrefix.lower():
            if skipUnreleasedSystems and systemInfo['prefix'].lower() in unreleasedSystemList:
                continue
            for planetInfo in systemInfo['planets']:
                resultPlanetList.append(planetInfo['name'])

    return resultPlanetList


def GetObjectListByName(objectName, skipUnreleasedSystems=False):
    resultList = []
    objectName = objectName.lower()

    for objInfo in GetFullObjectList(skipUnreleasedSystems):
        if objInfo['name'].lower() == objectName:
            resultList.append(objInfo)

    return resultList

def GetFullObjectList(skipUnreleasedSystems=True):
    return GetSystemObjectList('all', skipUnreleasedSystems)

def GetSystemObjectList(systemPrefix, skipUnreleasedSystems=True):
    resultList = []
    unreleasedSystemList = [ v.lower() for v in Config.unreleasedSystemList ]
    systemPrefix = systemPrefix.lower()

    for systemInfo in galaxyData.values():
        if systemPrefix == "all" or systemInfo['prefix'].lower() == systemPrefix:
            if skipUnreleasedSystems and systemInfo['prefix'].lower() in unreleasedSystemList:
                continue
            for objectInfo in systemInfo['otherObjects']:
                resultList.append(objectInfo)

    return resultList


def GetPlanetsAndObjectsAssociatedWithRaceOrOrg(raceOrOrgName):
    rtnInfo = {
        'planets': [],
        'objects': [],
    }
    pageName = raceOrOrgName
    possibleObjectsToCheck = set()
    stripRegex = re.compile('[^a-zA-Z0-9]')

    content = WikiUtils.GetWikiPageContent(pageName)
    if content:
        templateList = WikiUtils.GetTemplateListFromWikiPageContentRecursive(content)
        for templateInfo in templateList:
            if templateInfo['name'].lower() == 'nprfooter':
                with suppress(KeyError):
                    linkList = WikiUtils.GetWikiLinksFromContent(templateInfo['data']['Associated relics'])
                    possibleObjectsToCheck.update(linkList.keys())

    possibleObjectsToCheck.update(WikiUtils.GetWikiCategoryMemberList(pageName))

    for searchName in possibleObjectsToCheck:
        planetInfo = GetPlanetInfoByName(searchName)
        if planetInfo:
            rtnInfo['planets'].append(planetInfo)
            continue

        descFound = []
        objList = GetObjectListByName(searchName)
        for objInfo in objList:
            desc = ''
            with suppress(KeyError):
                if objInfo['scanText']:
                    desc = objInfo['scanText']
            with suppress(KeyError):
                if not desc and objInfo['info']:
                    desc = objInfo['info']

            # Avoiding duplicates due to typos
            if objInfo['name'] == 'Andromeda Gate' and 'Non-the less' in desc:
                continue
            if objInfo['name'] == 'Splicer Station' and 'live among the stars.The squat, grumpy,' in desc:
                continue
            if objInfo['name'] == 'Red Mist Station' and 'crestline,' in desc:
                continue

            desc = stripRegex.sub('', desc).lower()
            if desc not in descFound:
                rtnInfo['objects'].append(objInfo)
                descFound.append(desc)

    rtnInfo['planets'] = sorted(rtnInfo['planets'], key=lambda x: x['name'])
    rtnInfo['objects'] = sorted(rtnInfo['objects'], key=lambda x: x['name'])
    return rtnInfo


def GetSpawnInformationForRace(raceId):

    # Show Ascendant location spawns
    p = re.compile(r'.* ([a-z]{1,4}-\d{1,3}-\d{1,3}) ', re.I)
    spawnList = []
    locList = []
    for k,sys in galaxyData.items():
        for spawn in sys['otherRaceSpawns']:
            if abs(spawn['orgID']) == raceId:
                spawnList.append(spawn)

    spawnList = sorted(spawnList, key=lambda v: v['rotationalFromDay'])

    locList = []
    for spawn in spawnList:
        m = p.match(spawn['name'])
        if m:
            locList.append(m.group(1))

    return { 'spawnList': spawnList, 'locationList': locList }


def GetPlanetImageUrl(planetName):
    return 'https://benoldinggames.co.uk/sfi/files/planets/planets/{}.png'.format(planetName)


def DownloadImageForPlanet(planetName):
    rtnVal = False
    fileName = planetName

    filedir = os.path.join('public', 'images', 'Planet')
    os.makedirs(filedir, exist_ok=True)

    filepath = os.path.join(filedir, "{}.png".format(fileName))
    if not os.path.exists(filepath):
        try:
            url = GetPlanetImageUrl(planetName)
            r = requests.get(url)
            if r.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(r.content)
                    if Config.verbose >= 1:  print(planetName, "- Image saved successfully")
                    rtnVal = True
            else:
                if Config.verbose >= 1:  print("Image not found for planet", planetName)
        except:
            print("{} - failed to save the image\nUrl: [{}]\nLocal path [{}]\n\n".format(planetName, url, filepath))
            raise

    return rtnVal


def DownloadMissingImagesForTheWikiByPlanetList(planetList):
    rtnVal = 0
    for planetName in planetList:
        wikiImage = GetPlanetWikiImage(planetName)
        if not wikiImage:
            if DownloadImageForPlanet(planetName):
                rtnVal += 1

    return rtnVal


def DownloadImagesForPlanetList(planetList):
    rtnVal = 0
    for planetName in planetList:
        if DownloadImageForPlanet(planetName):
            rtnVal += 1

    return rtnVal


def GetPlanetWikiImage(planetName):
    planetName = planetName.strip()
    planetNameList = [ "Planet {}".format(planetName), planetName ]
    if "'" in planetName:
        planetNameList.append("Planet {}".format(planetName.replace("'", "")))
        planetNameList.append(planetName.replace("'", ""))

    return WikiUtils.GetWikiImageForNameList(planetNameList)



def GetImageUploadDownloadInfoForPlanet(planetName):
    filepath = os.path.join('public', 'images', 'Planet', "{}.png".format(planetName))
    rtnVal = {
        'description': 'Planet - {}'.format(planetName),
        'exists': os.path.exists(filepath),
        'filepath': filepath,
        'filename': "{}.png".format(planetName),
        'name': "Planet_{}.png".format(planetName.replace(' ', '_')),
        'url': GetPlanetImageUrl(planetName),
        'subDir': "Planet",
    }

    return rtnVal


def UploadImagesToWikiForPlanetList(planetList):
    planetImageInfoList = [ GetImageUploadDownloadInfoForPlanet(p) for p in planetList ]
    return WikiUtils.UploadImageListToWiki(planetImageInfoList)



def GetMineralInfoById(id):
    id = id.lower()
    for mineralInfo in mineralData.values():
        if mineralInfo['id'].lower() == id:
            return mineralInfo





def Initialize():
    LoadGalaxyInformation()


def LoadGalaxyInformation():
    global galaxyData, gatesAndWormHoles, mineralData
    galaxyData = DataLoader.LoadSystemDataFromBenOldingWebsite()
    gatesAndWormHoles = DataLoader.LoadGateDataFromBenOldingWebsite()
    mineralData = DataLoader.LoadMineralDataFromBenOldingWebsite()

    return True


Initialize()
