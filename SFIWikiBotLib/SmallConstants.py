#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import json
import os
import re
from contextlib import suppress
from SFIWikiBotLib import GeneralUtils
from SFIWikiBotLib import DataLoader


raceData = None
skillsData = None
effectsData = None
effectLookup = None
guidanceLookup = None
fireSideLookup = None
typeLookup = None
damageTypeLookup = None
augTypeLookup = None
weaponTypeLookup = None
spawnTypeLookup = None
sectorTypeLookup = None
extraTypeLookup = None
effectDamagesData = None
effectHealsData = None
effectRechargeData = None
shieldEffectMultipliersData = None
shieldEffectMultipliersNegativeData = None
humanTree = None
aralienTree = None

# Additional lookups we define ourself

equipCategoryLookup = {
    0: 'Normal',
    1: 'Micro Gate / Igni Harden, Wall',
    2: 'Nebula Bomb',
    3: 'Stealth / Damage Bubble',
    4: '[Inverse] Gravity Field',
    5: '',
    6: '',
    7: 'Ultra Rare',
}

effectDamagesData = {
    "Heat Damage":7,
    "Photonic Damage":400,
    "Anti Stealth":5,
    "Cold Fusion Damage":6,
    "Hellfire":12,
# 	"Shield Repair": -7.5,
# 	"Fast Shield Repair": -20,
# 	"Energy Recharge": 10,
}


def GetNprInfoById(id):
    for race in raceData:
        if race['race'] == id:
            return race


def GetNprNameFromId(id):
    race = GetNprInfoById(id)
    with suppress(KeyError, TypeError):
        return race['name']


def GetNprIdFromName(name):
    nprName = name
    match = re.search(r'\[?npr([\]\s:\-]+)(.*)$', name, re.I)
    if match:
        nprName = match.group(2);
    nprName = GeneralUtils.NormalizeString(nprName)

    for race in raceData:
        if GeneralUtils.NormalizeString(race['name']) == nprName:
            return race['race']

    if name.find("ghost") >= 0:
        return "ghost"


def GetFullEffectNameList():
    from SFIWikiBotLib import ItemUtils
    damageTypesToIncludePostfix = ['Electrostatic', 'Explosive', 'Ghostly', 'Heat', 'Laser', 'Photonic', 'Projectile']

    rtnList = set()

    for effect in effectsData:
        rtnList.add(effect['name'])
    for effectName in effectLookup:
        if effectName != 'NONE':
            rtnList.add(effectName.replace('_', ' ').title())
    for dname in damageTypeLookup:
        dname = GeneralUtils.CamelCaseToTitleCase(dname)
        rtnList.add(dname)
        if dname in damageTypesToIncludePostfix:
            rtnList.add('{} Damage'.format(dname))

    l = [ v['resistExtraEffect'] for v in ItemUtils.itemData if v['type'] == 5 and 'resistExtraEffect' in v and v['resistExtraEffect'] >= 0 ]
    s = set(l)
    for resistId in s:
        n = effectsData[resistId]['name'] + ' Resist'
        rtnList.add(n)

    rtnList.add("Ultra Rare")
    rtnList.add("Collectible")
    rtnList.add("Collectable")  # For removal / correction purposes only
    rtnList.add("Seasonal Items")
    rtnList.add("Andromedan Stealth")
    rtnList.add("Cold Fusion Resist")
    rtnList.add("Electrostatic Weakness")
    rtnList.add("Explosive Resist")
    rtnList.add("Explosive Weakness")
    rtnList.add("Freezing Weakness")
    rtnList.add('Fire Suppression')
    rtnList.add("Heat Weakness")
    rtnList.add('Hyperspace Recharge')
    rtnList.add("Laser Resist")
    rtnList.add("Laser Weakness")
    rtnList.add("Photonic Resist")
    rtnList.add("Photonic Weakness")
    rtnList.add("Projectile Resist")
    rtnList.add("Projectile Weakness")
    rtnList.add('Shield Recharge')
    rtnList.add('Stealth')
    rtnList.add('Energy Extaction')

    for catName in rtnList.copy():
        if 'Damage:' not in rtnList:
            rtnList.add('Damage:{}'.format(catName))
        if 'Effect:' not in rtnList:
            rtnList.add('Effect:{}'.format(catName))
        rtnList.add(catName.replace(' Damage', '').replace(' Resist', '').replace(' Weakness', ''))

    return sorted(list(rtnList))


def LoadConstantInformation():
    global raceData, effectsData, skillsData
    global effectLookup, guidanceLookup, fireSideLookup
    global typeLookup, damageTypeLookup, augTypeLookup
    global weaponTypeLookup, spawnTypeLookup, sectorTypeLookup
    global extraTypeLookup, effectDamagesData

    # Load constants` data
    rtnInfo = DataLoader.LoadConstantsData()

    augTypeLookup = rtnInfo["augTypeLookup"] if 'augTypeLookup' in rtnInfo else None
    damageTypeLookup = rtnInfo["damageTypeLookup"] if 'damageTypeLookup' in rtnInfo else None
    effectLookup = rtnInfo["effectLookup"] if 'effectLookup' in rtnInfo else None
    effectsData = rtnInfo["effectsData"] if 'effectsData' in rtnInfo else None
    extraTypeLookup = rtnInfo["extraTypeLookup"] if 'extraTypeLookup' in rtnInfo else None
    fireSideLookup = rtnInfo["fireSideLookup"] if 'fireSideLookup' in rtnInfo else None
    guidanceLookup = rtnInfo["guidanceLookup"] if 'guidanceLookup' in rtnInfo else None
    raceData = rtnInfo["raceData"] if 'raceData' in rtnInfo else None
    sectorTypeLookup = rtnInfo["sectorTypeLookup"] if 'sectorTypeLookup' in rtnInfo else None
    skillsData = rtnInfo["skillsData"] if 'skillsData' in rtnInfo else None
    spawnTypeLookup = rtnInfo["spawnTypeLookup"] if 'spawnTypeLookup' in rtnInfo else None
    typeLookup = rtnInfo["typeLookup"] if 'typeLookup' in rtnInfo else None
    weaponTypeLookup = rtnInfo["weaponTypeLookup"] if 'weaponTypeLookup' in rtnInfo else None

    if typeLookup:
        typeLookup = [ v if v != 'COLLECTABLE' else 'COLLECTIBLE' for v in typeLookup ]

    return True


LoadConstantInformation()
