import json
import html
from urllib.parse import parse_qs
from datetime import date
from SFIWikiBotLib import ItemUtils
from SFIWikiBotLib import ShipUtils
from SFIWikiBotLib import WikiUtils
from SFIWikiBotLib import GalaxyUtils
from SFIWikiBotLib import SmallConstants
from SFIWikiBotLib import GeneralUtils
from SFIWikiBotLib import PresetList
from SFIWikiBotLib import UrlShortener



def application(environ, start_response):
    response = '404 Not Found'
    responseBody = ""
    responseContentType = 'text/html'
    result = None
    headerList = []

    path = environ['PATH_INFO']
    queryString = parse_qs(environ['QUERY_STRING'])
    bodyData = ''
    if environ['REQUEST_METHOD'] == 'POST':
        bodyData = environ['wsgi.input'].read().decode("utf-8")

    if path == '/ajax/getItemList':
        result = GetItemList(queryString, bodyData)
        if result:
            response = '200 OK'
            responseContentType = 'application/javascript'
            headerList.append(('Content-Type', responseContentType))
            responseBody = result

    elif path == '/ajax/getItemPresetList':
        result = GetItemListFromPreset(queryString, bodyData)
        if result:
            response = '200 OK'
            responseContentType = 'application/javascript'
            headerList.append(('Content-Type', responseContentType))
            responseBody = result

    elif path == '/ajax/getShipList':
        result = GetShipList(queryString, bodyData)
        if result:
            response = '200 OK'
            responseContentType = 'application/javascript'
            headerList.append(('Content-Type', responseContentType))
            responseBody = result

    elif path == '/ajax/getShipPresetList':
        result = GetShipListFromPreset(queryString, bodyData)
        if result:
            response = '200 OK'
            responseContentType = 'application/javascript'
            headerList.append(('Content-Type', responseContentType))
            responseBody = result

    elif path == '/ajax/getShortenedUrl':
        result = GetShortenedUrl(queryString)
        if result:
            response = '200 OK'
            responseContentType = 'application/json'
            headerList.append(('Content-Type', responseContentType))
            responseBody = json.dumps(result)
        else:
            response = '400 Bad Request'
            responseContentType = 'text/html'
            headerList.append(('Content-Type', responseContentType))

    elif path == '/s':
        result = GetFullPathForToken(queryString)
        if result:
            response = '301 Moved Permanently'
            headerList.append(('Location', result))

    elif path == '/js/getPresetListForItemFinder':
        result = GetPresetListForItemFinder(queryString)
        if result:
            response = '200 OK'
            responseContentType = 'application/javascript'
            headerList.append(('Content-Type', responseContentType))
            responseBody = "var presetList = {};".format(result)

    elif path == '/js/getPresetListForShipFinder':
        result = GetPresetListForShipFinder(queryString)
        if result:
            response = '200 OK'
            responseContentType = 'application/javascript'
            headerList.append(('Content-Type', responseContentType))
            responseBody = "var presetList = {};".format(result)

    elif path == '/js/getFilterListForItemFinder':
        result = GetFilterListForItemFinder(queryString)
        if result:
            response = '200 OK'
            responseContentType = 'application/javascript'
            headerList.append(('Content-Type', responseContentType))
            responseBody = "var filterList = {};".format(result)

    elif path == '/js/getFilterListForShipFinder':
        result = GetFilterListForShipFinder(queryString)
        if result:
            response = '200 OK'
            responseContentType = 'application/javascript'
            headerList.append(('Content-Type', responseContentType))
            responseBody = "var filterList = {};".format(result)

    elif path == '/js/getUnreleasedRaceList':
        from SFIWikiBotLib import Config
        response = '200 OK'
        responseContentType = 'application/javascript'
        headerList.append(('Content-Type', responseContentType))
        responseBody = "var unreleasedRaceList = {};".format(json.dumps(Config.unreleasedRaceList))

    elif path == '/js/getUnreleasedShipList':
        from SFIWikiBotLib import Config
        response = '200 OK'
        responseContentType = 'application/javascript'
        headerList.append(('Content-Type', responseContentType))
        responseBody = "var unreleasedShipList = {};".format(json.dumps(Config.unreleasedShipList))

    elif path == '/RefreshData':
        ItemUtils.Initialize()
        ShipUtils.Initialize()
        GalaxyUtils.Initialize()
        SmallConstants.Initialize()

        response = '200 OK'
        responseContentType = 'text/html'
        headerList.append(('Content-Type', responseContentType))
        responseBody = "Success"

    elif path == '/Debug':
        from SFIWikiBotLib import Config
        response = '200 OK'
        responseContentType = 'text/html'
        headerList.append(('Content-Type', responseContentType))
        responseBody = "User: " + Config.botUsername

    start_response(response, headerList)
    return [ responseBody ]


def GetShortenedUrl(params):
    try:
        url = params['url'][0]
        if url.find('https://sf-i.mtmosier.com/') == 0 or url.find('https://starfighter-infinity.mtmosier.com/') == 0:
            token = UrlShortener.GetTokenForUrl(url)
            return "https://sf-i.mtmosier.com/s?t={}".format(token)
    except:
        pass


def GetPresetListForItemFinder(params):
    try:
        return json.dumps(PresetList.itemPresetList)
    except:
        pass


def GetPresetListForShipFinder(params):
    try:
        return json.dumps(list(PresetList.shipPresetList.values()))
    except:
        pass


def GetFullPathForToken(params):
    try:
        url = UrlShortener.GetUrlForToken(params['t'][0])
    except:
        pass
    if not url:
        url = 'https://starfighter-infinity.mtmosier.com/itemFinder.html'
    return url


def GetItemListFromPreset(params, bodyData):
    preset = json.loads(bodyData)
    res = WikiUtils.RenderItemPreset(preset, True, True)

    js = '$("#resultDisplayHtmlTable").html({});\n'.format(json.dumps(res['htmlContent']))
    js += '$("#resultDisplayWiki").html({});\n'.format(json.dumps(html.escape(res['content'])))
    js += '$("#resultDisplayJson").html(\'{}\');\n'.format(html.escape(json.dumps(res['objList'], indent=2, sort_keys=True)).replace('\n', '\\n').replace("'", "\\'"))
    js += '$("#resultCount").html(\'{}\');\n'.format(res['resultCount'])
    js += 'finderLastResult = {};\n'.format(json.dumps(res['objList'], sort_keys=True))
    js += 'console.log("finderLastResult:", finderLastResult);\n'
    return js


def GetShipListFromPreset(params, bodyData):
    preset = json.loads(bodyData)
    res = WikiUtils.RenderShipPreset(preset, True, True)

    js = '$("#resultDisplayHtmlTable").html({});\n'.format(json.dumps(res['htmlContent']))
    js += '$("#resultDisplayWiki").html({});\n'.format(json.dumps(html.escape(res['content'])))
    js += '$("#resultDisplayJson").html(\'{}\');\n'.format(html.escape(json.dumps(res['objList'], indent=2, sort_keys=True)).replace('\n', '\\n').replace("'", "\\'"))
    js += '$("#resultCount").html(\'{}\');\n'.format(res['resultCount'])
    js += 'finderLastResult = {};\n'.format(json.dumps(res['objList'], sort_keys=True))
    js += 'console.log("finderLastResult:", finderLastResult);\n'
    return js



def GetItemList(params, bodyData):
    wikiTableOutput = ""
    htmlTableOutput = ""
    filteredItemList = []

    tableHeader = ""
    tableCaption = ""
    tableClassNames = ""
    tableColumnList = []

    ruleSet = json.loads(bodyData)
    filteredItemList = GeneralUtils.SearchObjectListUsingRuleset(ItemUtils.itemData, ruleSet)
    filteredItemList = sorted(filteredItemList, key=lambda v: v['name'])

    tableId = GeneralUtils.GenerateDataSignature(ruleSet)

    if 'useCustomTableOptions' in params and params['useCustomTableOptions'][0] == '1':
        if 'tableHeader' in params:
            tableHeader = params["tableHeader"][0]
        if 'tableCaption' in params:
            tableCaption = params["tableCaption"][0]
        if 'tableClassNames' in params:
            tableClassNames = params["tableClassNames"][0]
        if 'tableColumnList[]' in params:
            tableColumnList = params["tableColumnList[]"]
        elif 'tableColumnList' in params:
            tableColumnList = params["tableColumnList"][0]

        if tableColumnList:
            tableData = ItemUtils.GetWikiDisplayDataForItemList(filteredItemList, tableColumnList)
            dataSignature = GeneralUtils.GenerateDataSignature(tableData)
            tableClassNames += " data-{} generated-{}".format(dataSignature, date.today().isoformat())
            tableClassNames = tableClassNames.strip()
            wikiTableOutput = WikiUtils.ConvertListToWikiTable(tableData, tableHeader, tableCaption, tableClassNames, tableId)

            tableData = ItemUtils.GetDisplayDataForItemList(filteredItemList, tableColumnList)
            htmlTableOutput = GeneralUtils.ConvertListToHtmlTable(tableData, tableHeader, tableCaption, tableClassNames, tableId)
        else:
            htmlTableOutput = "No table columns specified - Unable to display data"
            wikiTableOutput = "No table columns specified - Unable to display data"

    else:
        itemTypeList = [ 2, 3, 4, 5, 6, 14, 1 ]
        weaponTypeList = [ 1, 2, 3, 4, 5 ]

        for itemType in itemTypeList:
            if itemType == 3:
                for weaponType in weaponTypeList:
                    itemList = []
                    try:
                        itemList = [ item for item in filteredItemList if 'type' in item and item['type'] == itemType and 'weaponType' in item and item['weaponType'] == weaponType ]
                    except:
                        pass

                    if itemList:
                        tableInfo = ItemUtils.GetDefaultTableInfoByItemType(itemType, weaponType)
                        tableHeader = tableInfo['tableHeader']
                        tableCaption = tableInfo['tableCaption']
                        tableColumnList = tableInfo['tableColumnList']
                        tableColumnTitleList = tableInfo['tableColumnTitleList']
                        tableClassNames = tableInfo['tableClassNames']
                        if len(itemList) > 7:
                            tableClassNames += " floatheader"
                            tableClassNames = tableClassNames.strip()

                        tableData = ItemUtils.GetWikiDisplayDataForItemList(itemList, tableColumnList)
                        dataSignature = GeneralUtils.GenerateDataSignature(tableData)
                        tableClassNames += " data-{} generated-{}".format(dataSignature, date.today().isoformat())
                        tableClassNames = tableClassNames.strip()
                        wikiTableOutput += WikiUtils.ConvertListToWikiTable(tableData, tableHeader, tableCaption, tableClassNames, tableId, tableColumnTitleList)

                        tableData = ItemUtils.GetDisplayDataForItemList(itemList, tableColumnList)
                        htmlTableOutput += GeneralUtils.ConvertListToHtmlTable(tableData, tableHeader, tableCaption, tableClassNames, tableId, tableColumnTitleList)
            else:
                itemList = []
                try:
                    itemList = [ item for item in filteredItemList if 'type' in item and item['type'] == itemType ]
                except:
                    pass

                if itemList:
                    tableInfo = ItemUtils.GetDefaultTableInfoByItemType(itemType)
                    tableHeader = tableInfo['tableHeader']
                    tableCaption = tableInfo['tableCaption']
                    tableColumnList = tableInfo['tableColumnList']
                    tableColumnTitleList = tableInfo['tableColumnTitleList']
                    tableClassNames = tableInfo['tableClassNames']
                    if len(itemList) > 7:
                        tableClassNames += " floatheader"
                        tableClassNames = tableClassNames.strip()

                    tableData = ItemUtils.GetWikiDisplayDataForItemList(itemList, tableColumnList)
                    dataSignature = GeneralUtils.GenerateDataSignature(tableData)
                    tableClassNames += " data-{} generated-{}".format(dataSignature, date.today().isoformat())
                    tableClassNames = tableClassNames.strip()
                    wikiTableOutput += WikiUtils.ConvertListToWikiTable(tableData, tableHeader, tableCaption, tableClassNames, tableId, tableColumnTitleList)

                    tableData = ItemUtils.GetDisplayDataForItemList(itemList, tableColumnList)
                    htmlTableOutput += GeneralUtils.ConvertListToHtmlTable(tableData, tableHeader, tableCaption, tableClassNames, tableId, tableColumnTitleList)


    js = '$("#resultDisplayHtmlTable").html({});\n'.format(json.dumps(htmlTableOutput))
    js += '$("#resultDisplayWiki").html({});\n'.format(json.dumps(html.escape(wikiTableOutput)))
    js += '$("#resultDisplayJson").html(\'{}\');\n'.format(html.escape(json.dumps(filteredItemList, indent=2, sort_keys=True)).replace('\n', '\\n').replace("'", "\\'"))
    js += '$("#resultCount").html(\'{}\');\n'.format(len(filteredItemList))
    js += 'finderLastResult = {};\n'.format(json.dumps(filteredItemList, sort_keys=True))
    js += 'console.log("finderLastResult:", finderLastResult);\n'
    return js


def GetShipList(params, bodyData):
    wikiTableOutput = ""
    htmlTableOutput = ""

    tableHeader = ""
    tableCaption = ""
    tableClassNames = ""
    tableColumnList = []

    ruleSet = json.loads(bodyData)
    filteredShipList = GeneralUtils.SearchObjectListUsingRuleset(ShipUtils.shipData, ruleSet)
    # Sort Human / Arlien ships by unlock level, then add NPR ships after sorted by their drop chance
    # lm = lambda v : float(v['specialDropLikelihood']) * 100000 if v['race'] > 1 and 'specialDropLikelihood' in v else int(v['unlockLevel'])
    filteredShipList = sorted(filteredShipList, key=ShipUtils.GetShipSortFunc())

    tableId = GeneralUtils.GenerateDataSignature(ruleSet)

    if 'useCustomTableOptions' in params and params['useCustomTableOptions'][0] == '1':
        if 'tableHeader' in params:
            tableHeader = params["tableHeader"][0]
        if 'tableCaption' in params:
            tableCaption = params["tableCaption"][0]
        if 'tableClassNames' in params:
            tableClassNames = params["tableClassNames"][0]
        if 'tableColumnList[]' in params:
            tableColumnList = params["tableColumnList[]"]
        elif 'tableColumnList' in params:
            tableColumnList = params["tableColumnList"][0]

        if tableColumnList:
            tableData = ShipUtils.GetWikiDisplayDataForShipList(filteredShipList, tableColumnList)
            dataSignature = GeneralUtils.GenerateDataSignature(tableData)
            tableClassNames += " data-{} generated-{}".format(dataSignature, date.today().isoformat())
            tableClassNames = tableClassNames.strip()
            wikiTableOutput = WikiUtils.ConvertListToWikiTable(tableData, tableHeader, tableCaption, tableClassNames, tableId)

            tableData = ShipUtils.GetDisplayDataForShipList(filteredShipList, tableColumnList)
            htmlTableOutput = GeneralUtils.ConvertListToHtmlTable(tableData, tableHeader, tableCaption, tableClassNames, tableId)
        else:
            htmlTableOutput = "No table columns specified - Unable to display data"
            wikiTableOutput = "No table columns specified - Unable to display data"

    else:
        tableInfo = ShipUtils.GetDefaultTableInfo()
        tableHeader = tableInfo['tableHeader']
        tableCaption = tableInfo['tableCaption']
        tableColumnList = tableInfo['tableColumnList']
        tableColumnTitleList = tableInfo['tableColumnTitleList']
        tableClassNames = tableInfo['tableClassNames']
        if len(filteredShipList) > 7:
            tableClassNames += " floatheader"
            tableClassNames = tableClassNames.strip()

        tableData = ShipUtils.GetWikiDisplayDataForShipList(filteredShipList, tableColumnList)
        dataSignature = GeneralUtils.GenerateDataSignature(tableData)
        tableClassNames += " data-{} generated-{}".format(dataSignature, date.today().isoformat())
        tableClassNames = tableClassNames.strip()
        wikiTableOutput = WikiUtils.ConvertListToWikiTable(tableData, tableHeader, tableCaption, tableClassNames, tableId, tableColumnTitleList)

        tableData = ShipUtils.GetDisplayDataForShipList(filteredShipList, tableColumnList)
        htmlTableOutput = GeneralUtils.ConvertListToHtmlTable(tableData, tableHeader, tableCaption, tableClassNames, tableId, tableColumnTitleList)


    js = '$("#resultDisplayHtmlTable").html({});\n'.format(json.dumps(htmlTableOutput))
    js += '$("#resultDisplayWiki").html({});\n'.format(json.dumps(html.escape(wikiTableOutput)))
    js += '$("#resultDisplayJson").html(\'{}\');\n'.format(html.escape(json.dumps(filteredShipList, indent=2, sort_keys=True)).replace('\n', '\\n').replace("'", "\\'"))
    js += '$("#resultCount").html(\'{}\');\n'.format(len(filteredShipList))
    js += 'finderLastResult = {};\n'.format(json.dumps(filteredShipList, sort_keys=True))
    js += 'console.log("finderLastResult:", finderLastResult);\n'
    return js


def GetFilterListForItemFinder(params):
    filterList = []
    filterList.append({
        'id': 'acceleration',
        'label': 'Acceleration',
        'type': 'double',
        'validation': { 'min': 0, 'step': 0.1 },
    })
    filterList.append({
        'id': 'accuracy',
        'label': 'Accuracy',
        'type': 'double',
        'validation': { 'min': -1, 'step': 0.1 },
        'default_operator': 'less_or_equal',
    })
    filterList.append({
        'id': 'armingTime',
        'label': 'Arming Time',
        'type': 'double',
        'validation': { 'min': 0, 'step': 0.1 },
    })
    filterList.append({
        'id': 'uniqueToShipID',
        'label': 'Associated Ship',
        'type': 'string',
        'input': 'select',
        'values': dict({(v['id'],v['name']) for v in ItemUtils.GetShipInfoListAssociatedWithItems() if v}),
        'operators': [ 'equal', 'not_equal', 'is_not_empty', 'is_empty' ],
    })
    filterList.append({
        'id': 'ItemUtils.GetItemAugType',
        'label': 'Augmentation Type',
        'type': 'string',
        'input': 'select',
        'values':  ["Andromedan Power Source", "Aralien Spectral Locking", "Auto Switcher", "Barrage Line", "Barrage V", "Cargo Extender", "Crate Attractor", "Crate Magnet", "Dark Energy Charging", "Dartian Converter", "Dartian Hyperspace", "Death Trap Spawn", "Deathtrap", "Deep Ship Scan", "Devimon Energize", "Devimon Vigor", "Dodge", "Drift", "Dynamo", "Early Warning", "Effect Dampener", "Enemy Player Warning", "Energy Overcharge", "Energy To Shield", "Explorer Autopilot", "Field Hop", "Field Hop Quick Turn", "Fire Extinguisher", "Fling", "Glare Filter", "Hacking Accellerate", "Hacking Range Booster", "Handbrake", "Human Spectral Locking", "Hyperspace Integrity", "Hyperspace Recharge Booster", "Intelligent Autopilot", "Laser Sight", "Life Extender", "Locking Widener", "Metal Sacrifice", "Mine Arming Time Shortener", "Mine Grid", "Mine Hoop", "Mine V", "Mine Wall", "Prospector", "Quick Getaway", "Radiation Charging", "Radii Reloader", "Red Mist", "Reload Accelerator", "Rock Interference", "Roid Avoid", "S/E Balancer", "Sacrifice", "Selective Effect Dampen", "Self Torture", "Sheenite Signal Pulse", "Shield To Energy", "Ship Constructor", "Short Range Hyper Space", "Short Range Teleport", "Signal Booster", "Solar Panel Upgrade", "Solarion Sight", "Sticky Mine Launcher", "Sticky Mine Launcher Rear", "Turret", "Weapon Constructor", "Weapon Scan"],
        'operators': [ 'equal', 'not_equal' ],
    })
    filterList.append({
        'id': 'autoPilotSpeedInc',
        'label': 'Auto-pilot Speed Increase',
        'type': 'double',
        'validation': { 'min': 0, 'step': 0.1 },
    })
    filterList.append({
        'id': 'ItemUtils.ItemDisplayStatBPLocation',
        'label': 'Blueprint Location',
        'type': 'string',
    })
    filterList.append({
        'id': 'damage',
        'label': 'Damage',
        'type': 'double',
        'validation': { 'min': 0, 'step': 1 },
    })
    filterList.append({
        'id': 'ItemUtils.GetItemDamageType',
        'label': 'Damage Type',
        'type': 'string',
        'input': 'select',
        'values':  [ 'Ammo Harvest', 'Combo', 'Dartian Mining', 'Electrostatic', 'Energy Extraction', 'Energy Harvest', 'Explosive', 'Ghostly', 'Heat', 'Hyperspace Harvest', 'Laser', 'None', 'Other', 'Photonic', 'Projectile', 'Red Mist', 'Repair', 'Shield Extraction', 'Shield Harvest', 'Tractor', 'Undefined' ],
        'operators': [ 'equal', 'not_equal' ],
    })
    filterList.append({
        'id': 'ItemUtils.GetItemDpeIncludingEffectDamage',
        'label': 'Damage / Energy',
        'type': 'double',
        'validation': { 'min': 0, 'step': 1 },
    })
    filterList.append({
        'id': 'ItemUtils.GetItemDpsIncludingEffectDamage',
        'label': 'Damage / Second',
        'type': 'double',
        'validation': { 'min': 0, 'step': 5 },
    })
    filterList.append({
        'id': 'ItemUtils.GetItemDescription',
        'label': 'Description',
        'type': 'string',
    })
    filterList.append({
        'id': 'ItemUtils.GetShieldEffectName',
        'label': 'Effect (Shield)',
        'type': 'string',
        'input': 'select',
        'values':  [ 'None', 'Energy Absorb', 'Anti Gravity', 'Deflector', 'Heat Resist', 'Shock Absorbing', 'Flange', 'Mine Sweeper', 'Front Facing', 'Back Facing', 'Beam Refracting', 'Anti Nuclear', 'Effect Reduce', 'Tank', 'Human Ghostly', 'Dark', 'Andromedan', 'Refractive', 'Aralien Ghostly', 'Insulator', 'Rock', 'Selective Effect Reduce', 'Overdose Resist', 'Devimon', 'Vampire', 'Mine Claimer', 'Enlightened', 'Tornadian', 'Solarion' ],
        'operators': [ 'equal', 'not_equal' ],
    })
    filterList.append({
        'id': 'ItemUtils.GetWeaponEffectName',
        'label': 'Effect (Weapon)',
        'type': 'string',
        'input': 'select',
        'values':  ['None', 'Absorbing Stealth', 'Anti Gravity', 'Anti Stealth', 'Augmentation Impaired', 'Backward Camouflage', 'Ben\'s Blessing', 'Ben\'s Curse', 'Black Light Saw', 'Blessing of Megmos', 'Blinded', 'Cold Fusion Damage', 'Concussion', 'Corrosion', 'Curse', 'Damage Bubble', 'Dark Bubble', 'Dephase', 'Disruption', 'Drift', 'Effect Dampen', 'Effect Nourish', 'Electrostatic Bubble', 'Energy Drain', 'Energy Recharge', 'Engine Overdrive', 'Escape Teleport', 'Evaporate', 'Fast Shield Repair', 'Fire Suppression', 'Forward Camouflage', 'Frozen', 'Gravity Field', 'Hallucination', 'Hard Light Decay', 'Hard Light Saw', 'Harden', 'Heat Bubble', 'Heat Damage', 'Hellfire', 'Hidden by Smoke', 'Highlighted', 'Holographic Disguise', 'Inverse Gravity Field', 'Invulnerable', 'Light Bending Stealth', 'Locking Jammed', 'Magnetic Disruption', 'Mass Field', 'Mass Warp', 'Mine Magnet', 'Obnoxious Effect', 'Passive Stealth', 'Photonic Damage', 'Pixellation', 'Power Failure', 'Propulsion Dehance', 'Radiation Damage', 'Recharging Blocked', 'Red Mist Haze', 'Red Mist Horn Circle', 'Red Mist Horns', 'Red Mist Overdose', 'Reflecting Bubble', 'Reflecting Stealth', 'Resonance', 'Reveal', 'Rodion Engine Overdrive', 'Scanner Jammed', 'Secondary Weapons Disabled', 'Selective Effect Dampen', 'Sheenite Locking Boost', 'Shield Bubble', 'Shield Repair', 'Slow Down', 'Solarion Sight', 'Stabiliser Fail', 'Targetting Enhance', 'Teleport Jammed', 'Thunderbolt', 'Transparent Stealth', 'Vendetta Bonus', 'Weapon Attract', 'Weapon Repel'],
        'operators': [ 'equal', 'not_equal' ],
    })
    filterList.append({
        'id': 'ItemUtils.GetItemEffectTime',
        'label': 'Effect Time',
        'type': 'double',
        'validation': { 'min': 0, 'step': 0.5 },
    })
    filterList.append({
        'id': 'accelMod',
        'label': 'Engine Acceleration Mult',
        'type': 'double',
        'validation': { 'min': 0, 'step': 0.1 },
    })
    filterList.append({
        'id': 'reverseSpeedMod',
        'label': 'Engine Reverse Mult',
        'type': 'double',
        'validation': { 'min': 0, 'step': 0.1 },
    })
    filterList.append({
        'id': 'maxSpeedMod',
        'label': 'Engine Speed Mult',
        'type': 'double',
        'validation': { 'min': 0, 'step': 0.1 },
    })
    filterList.append({
        'id': 'turning',
        'label': 'Engine Turning Mult',
        'type': 'double',
        'validation': { 'min': 0, 'step': 0.1 },
    })
    filterList.append({
        'id': 'equipCategory',
        'label': 'Equip Category',
        'type': 'integer',
        'input': 'select',
        'values': dict({(k,v) for k,v in SmallConstants.equipCategoryLookup.items() if v}),
        'operators': [ 'equal', 'not_equal' ],
    })
    filterList.append({
        'id': 'fireRate',
        'label': 'Fire Rate',
        'type': 'double',
        'validation': { 'min': 0, 'step': 0.01 },
    })
    filterList.append({
        'id': 'guidance',
        'label': 'Guidance',
        'type': 'integer',
        'input': 'select',
        'values': {0: 'Unguided', 1: 'Homing', 2: 'Attached', 3: 'No Collision', 4: 'Radial Fire', 5: 'Attached To Target'},
        'operators': [ 'equal', 'not_equal' ],
    })
    filterList.append({
        'id': 'initSpeed',
        'label': 'Initial Speed',
        'type': 'integer',
        'validation': { 'min': 0, 'step': 0.1 },
    })
    filterList.append({
        'id': 'passive',
        'label': 'Is Augmentation Passive',
        'type': 'boolean',
        'input': 'radio',
        'values': {True: 'Yes', False: 'No'},
    })
    filterList.append({
        'id': 'ItemUtils.IsBeamWeapon',
        'label': 'Is Beam',
        'type': 'boolean',
        'input': 'radio',
        'values': {True: 'Yes', False: 'No'},
    })
    filterList.append({
        'id': 'energyBased',
        'label': 'Is Energy Based',
        'type': 'boolean',
        'input': 'radio',
        'values': {True: 'Yes', False: 'No'},
        'operators': [ 'equal' ],
    })
    filterList.append({
        'id': 'ItemUtils.IsItemHidden',
        'label': 'Is Item Hidden',
        'type': 'boolean',
        'input': 'radio',
        'values': {True: 'Yes', False: 'No'},
        'operators': [ 'equal' ],
    })
    filterList.append({
        'id': 'ItemUtils.IsItemShipExclusive',
        'label': 'Is Item Ship Exclusive',
        'type': 'boolean',
        'input': 'radio',
        'values': {True: 'Yes', False: 'No'},
    })
    filterList.append({
        'id': 'ItemUtils.IsItemNprExclusive',
        'label': 'Is Item NPR Exclusive',
        'type': 'boolean',
        'input': 'radio',
        'values': {True: 'Yes', False: 'No'},
    })
    filterList.append({
        'id': 'ItemUtils.GetItemPurchasePrice',
        'label': 'Item Cost',
        'type': 'integer',
        'validation': { 'min': 0, 'step': 10 },
    })
    filterList.append({
        'id': 'id',
        'label': 'Item Id',
        'type': 'string',
    })
    filterList.append({
        'id': 'type',
        'label': 'Item Type',
        'type': 'integer',
        'input': 'select',
        'values': {1: 'Mineral', 2: 'Primary Weapon', 3: 'Secondary Weapon', 4: 'Engine', 5: 'Shield', 6: 'Augmentation', 14: 'Collectible'},
        'operators': [ 'equal', 'not_equal' ],
    })
    filterList.append({
        'id': 'life',
        'label': 'Lifetime',
        'type': 'double',
        'validation': { 'min': 0, 'step': 1 },
    })
    filterList.append({
        'id': 'name',
        'label': 'Name',
        'type': 'string',
        'default_operator': 'contains',
    })
    filterList.append({
        'id': 'ItemUtils.GetItemSource',
        'label': 'Obtained',
        'type': 'string',
        'input': 'select',
        'values':  [ 'Purchased', 'Purchased (Seasonal)', 'Crafted', 'Rare Drop', 'Unknown' ],
        'operators': [ 'equal', 'not_equal' ],
    })
    filterList.append({
        'id': 'amount',
        'label': 'Proj Count',
        'type': 'integer',
        'validation': { 'min': 0, 'step': 1 },
    })
    filterList.append({
        'id': 'maxSpeed',
        'label': 'Proj Speed',
        'type': 'integer',
        'validation': { 'min': 0, 'step': 5 },
    })
    filterList.append({
        'id': 'propulsionEnhance',
        'label': 'Propulsion Enhance',
        'type': 'double',
        'validation': { 'min': 0, 'step': 0.1 },
    })
    filterList.append({
        'id': 'propulsionEnhanceTime',
        'label': 'Propulsion Enhance Time',
        'type': 'double',
        'validation': { 'min': 0, 'step': 0.1 },
    })
    filterList.append({
        'id': 'ItemUtils.GetRaceForItem',
        'label': 'Race',
        'type': 'string',
        'input': 'select',
        'values': ['Humans', 'Aralien', 'The Abyss', 'Andromedan', 'Aralien Ghost', 'Ascendant', 'Chronoduke', 'Church of Megmos', 'Dartian', 'Devimon', 'Enlightened', 'Face of Space', 'Forkworm', 'The Gao', 'Human Ghost', 'Igni', 'Meteor Burger', 'Null Dweller', 'Prongworm', 'Radii', 'Red Mist', 'Relisk', 'Resonite', 'Robosphere', 'Rodion', 'Sheenite', 'Solarion', 'Splicer', 'Tobor', 'Tornadian', 'Tyraan', 'Vacuum Fly'],
        'operators': [ 'equal', 'not_equal' ],
    })
    filterList.append({
        'id': 'ItemUtils.GetItemRange',
        'label': 'Range',
        'type': 'double',
        'validation': { 'min': 0, 'step': 5 },
    })
    filterList.append({
        'id': 'ItemUtils.GetItemSkillLevel',
        'label': 'Skill Level',
        'type': 'integer',
        'validation': { 'min': 0, 'max': 12, 'step': 1 },
    })
    filterList.append({
        'id': 'ItemUtils.GetItemSkillName',
        'label': 'Skill Tree',
        'type': 'string',
        'input': 'select',
        'values':  [ 'Chemistry', 'Energy', 'Explosives', 'Gravity', 'Lasers', 'Light', 'Programming', 'Propulsion', 'Shields', 'Support' ],
        'operators': [ 'equal', 'not_equal' ],
    })
    filterList.append({
        'id': 'chargeDelay',
        'label': 'Shield Charge Delay',
        'type': 'double',
        'validation': { 'min': 0, 'step': 0.1 },
    })
    filterList.append({
        'id': 'chargeModifier',
        'label': 'Shield Charge Rate',
        'type': 'double',
        'validation': { 'min': 0, 'step': 0.1 },
    })
    filterList.append({
        'id': 'maxModifier',
        'label': 'Shield Max Mult',
        'type': 'double',
        'validation': { 'min': 0, 'step': 0.1 },
    })
    filterList.append({
        'id': 'ItemUtils.GetItemTotalDamagePerVolley',
        'label': 'Total Damage/Volley',
        'type': 'double',
        'validation': { 'min': 0, 'step': 0.5 },
    })
    filterList.append({
        'id': 'Degrees.turning',
        'label': 'Turning',
        'type': 'double',
        'validation': { 'min': 0, 'step': 0.5 },
    })
    filterList.append({
        'id': 'weaponType',
        'label': 'Weapon Type',
        'type': 'integer',
        'input': 'select',
        'values': {0: 'Primary', 1: 'Standard', 2: 'Utility', 3: 'Mine', 4: 'Proximity', 5: 'Large'},
        'operators': [ 'equal', 'not_equal' ],
    })

    return json.dumps(sorted(filterList, key=lambda x: x['label']))


def GetFilterListForShipFinder(params):
    filterList = []
    filterList.append({
        'id': 'Percent.accel',
        'label': 'Acceleration',
        'type': 'double',
        'validation': { 'min': 0, 'max': 50, 'step': 2.5 },
        'default_operator': 'greater_or_equal',
    })
    filterList.append({
        'id': 'augmentations',
        'label': 'Augmentations',
        'type': 'integer',
        'validation': { 'min': 0, 'max': 6, 'step': 1 },
        'default_operator': 'greater_or_equal',
    })
    filterList.append({
        'id': 'ShipUtils.ShipCanBeBoughtByPlayers',
        'label': 'Available for Purchase',
        'type': 'boolean',
        'input': 'radio',
        'values': {True: 'Yes', False: 'No'},
        'operators': [ 'equal' ],
    })
    filterList.append({
        'id': 'cargoAmount',
        'label': 'Cargo',
        'type': 'integer',
        'validation': { 'min': 0, 'max': 60, 'step': 1 },
        'default_operator': 'greater_or_equal',
    })
    filterList.append({
        'id': 'cockpit',
        'label': 'Cockpit Type',
        'type': 'boolean',
        'input': 'radio',
        'values': {0: 'Normal', 1: 'Captial'},
        'operators': [ 'equal' ],
    })
    filterList.append({
        'id': 'description',
        'label': 'Description',
        'type': 'string',
        'default_operator': 'contains',
    })
    filterList.append({
        'id': 'isHighMass',
        'label': 'High Mass',
        'type': 'boolean',
        'input': 'radio',
        'values': {True: 'Yes', False: 'No'},
        'operators': [ 'equal' ],
    })
    filterList.append({
        'id': 'ShipUtils.IsShipHidden',
        'label': 'Is Ship Hidden',
        'type': 'boolean',
        'input': 'radio',
        'values': {True: 'Yes', False: 'No'},
        'operators': [ 'equal' ],
    })
    filterList.append({
        'id': 'id',
        'label': 'Item Id',
        'type': 'string',
    })
    filterList.append({
        'id': 'largeSecondary',
        'label': 'Large Slots',
        'type': 'integer',
        'validation': { 'min': 0, 'max': 10, 'step': 1 },
        'default_operator': 'greater_or_equal',
    })
    filterList.append({
        'id': 'lifePrice',
        'label': 'Life Cost',
        'type': 'integer',
        'validation': { 'min': 0, 'step': 10 },
        'default_operator': 'less_or_equal',
    })
    filterList.append({
        'id': 'lockingAngle',
        'label': 'Locking Angle',
        'type': 'integer',
        'validation': { 'min': 0, 'max': 360, 'step': 5 },
        'default_operator': 'greater_or_equal',
    })
    filterList.append({
        'id': 'isLowMass',
        'label': 'Low Mass',
        'type': 'boolean',
        'input': 'radio',
        'values': {True: 'Yes', False: 'No'},
        'operators': [ 'equal' ],
    })
    filterList.append({
        'id': 'mass',
        'label': 'Mass',
        'type': 'double',
        'validation': { 'min': 0, 'max': 20, 'step': 0.1 },
        'default_operator': 'less_or_equal',
    })
    filterList.append({
        'id': 'mineSecondary',
        'label': 'Mine Slots',
        'type': 'integer',
        'validation': { 'min': 0, 'max': 10, 'step': 1 },
        'default_operator': 'greater_or_equal',
    })
    filterList.append({
        'id': 'name',
        'label': 'Name',
        'type': 'string',
        'default_operator': 'contains',
    })
    filterList.append({
        'id': 'proximitySecondary',
        'label': 'Proximity Slots',
        'type': 'integer',
        'validation': { 'min': 0, 'max': 10, 'step': 1 },
        'default_operator': 'greater_or_equal',
    })
    filterList.append({
        'id': 'ShipUtils.GetRaceForShip',
        'label': 'Race',
        'type': 'string',
        'input': 'select',
        'values': ['Humans', 'Aralien', 'The Abyss', 'Andromedan', 'Aralien Ghost', 'Ascendant', 'Chronoduke', 'Church of Megmos', 'Dartian', 'Devimon', 'Enlightened', 'Face of Space', 'Forkworm', 'The Gao', 'Human Ghost', 'Igni', 'Meteor Burger', 'Null Dweller', 'Prongworm', 'Radii', 'Red Mist', 'Relisk', 'Resonite', 'Robosphere', 'Rodion', 'Sheenite', 'Solarion', 'Splicer', 'Tobor', 'Tornadian', 'Tyraan', 'Vacuum Fly'],
        'operators': [ 'equal', 'not_equal' ],
    })
    filterList.append({
        'id': 'maxShield',
        'label': 'Shield',
        'type': 'integer',
        'validation': { 'min': 0, 'step': 10 },
        'default_operator': 'greater_or_equal',
    })
    filterList.append({
        'id': 'shieldSize',
        'label': 'Shield Size',
        'type': 'double',
        'validation': { 'min': 0, 'max': 35, 'step': 0.1 },
        'default_operator': 'less_or_equal',
    })
    filterList.append({
        'id': 'ShipUtils.GetShipPurchasePrice',
        'label': 'Ship Cost',
        'type': 'integer',
        'validation': { 'min': 0, 'step': 50 },
        'default_operator': 'less_or_equal',
    })
    filterList.append({
        'id': 'ShipUtils.GetTypeForShip',
        'label': 'Ship Type',
        'type': 'string',
        'input': 'select',
        'values': [
            'Drone',
            'Converted Drone',
            'Escape Pod',
            'Small Ship',
            'Dogfighter',
            'Mining Ship',
            'Warship',
            'Capital Ship',
            'CC / Elite Ship',
            'Boss Ship',
            'Turret',
            'Special Non-Player Ship',
            'Megaboss',
        ],
        'operators': [ 'equal', 'not_equal' ],
    })
    filterList.append({
        'id': 'Percent.specialDropLikelihood',
        'label': 'Special Drop Likelihood',
        'type': 'integer',
        'validation': { 'min': 0, 'max': 100, 'step': 1 },
        'default_operator': 'greater_or_equal',
    })
    filterList.append({
        'id': 'ShipUtils.GetMaxSpeedForShip',
        'label': 'Speed',
        'type': 'double',
        'validation': { 'min': 0, 'max': 20, 'step': 0.5 },
        'default_operator': 'greater_or_equal',
    })
    filterList.append({
        'id': 'standardSecondary',
        'label': 'Standard Secondary Slots',
        'type': 'integer',
        'validation': { 'min': 0, 'max': 10, 'step': 1 },
        'default_operator': 'greater_or_equal',
    })
    filterList.append({
        'id': 'Degrees.turning',
        'label': 'Turning (degrees/s)',
        'type': 'integer',
        'validation': { 'min': 0, 'max': 360, 'step': 5 },
        'default_operator': 'greater_or_equal',
    })
    filterList.append({
        'id': 'turretSlot',
        'label': 'Turret Available',
        'type': 'boolean',
        'input': 'radio',
        'values': {True: 'Yes', False: 'No'},
        'operators': [ 'equal' ],
    })
    filterList.append({
        'id': 'turrets',
        'label': 'Turret Count',
        'type': 'integer',
        'validation': { 'min': 0, 'max': 10, 'step': 1 },
        'default_operator': 'greater_or_equal',
    })
    filterList.append({
        'id': 'unlockLevel',
        'label': 'Unlock Level',
        'type': 'integer',
        'validation': { 'min': 0, 'max': 200, 'step': 1 },
        'default_operator': 'less_or_equal',
    })
    filterList.append({
        'id': 'utilitySecondary',
        'label': 'Utility Slots',
        'type': 'integer',
        'validation': { 'min': 0, 'max': 10, 'step': 1 },
        'default_operator': 'greater_or_equal',
    })

    return json.dumps(sorted(filterList, key=lambda x: x['label']))




# To clear passenger cache:
#     sudo passenger-config restart-app /var/www/sf-wiki-bot
#
# To fix file permissions:
#     sudo chown -R sf-wiki-bot:mtmosier /var/www/sf-wiki-bot
#     sudo chmod -R ug+rw,o-w,o+r /var/www/sf-wiki-bot
#
# To restart nginx after config update:
#     sudo service nginx restart
#
#
# Useful environ entries:
#     'wsgi.input': <_io.BufferedReader name=5>,
#     'REQUEST_METHOD': 'GET',
#     'QUERY_STRING': 'input=testing',
#     'REQUEST_URI': '/queryBuilder/test.py?input=testing',
#     'PATH_INFO': '/queryBuilder/test.py',
#     'SERVER_NAME': 'starfighter-infinity.mtmosier.com',
#     'HTTP_USER_AGENT': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0',
#     'wsgi.url_scheme': 'http',
#     'passenger.hijack': <function RequestHandler.process_request.<locals>.hijack at 0x7f8bea35c378>,
#
