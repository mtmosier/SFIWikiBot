shipPresetList = {
    'Human Ships': {'name': 'Human Ships', 'targetPage': 'Category:Human Ships', 'tableHeader': '', 'ruleSet': {'condition': 'AND', 'rules': [{'operator': 'equal', 'value': False, 'type': 'boolean', 'id': 'ShipUtils.IsShipHidden', 'input': 'radio', 'field': 'ShipUtils.IsShipHidden'}, {'operator': 'equal', 'value': True, 'type': 'boolean', 'id': 'ShipUtils.ShipCanBeBoughtByPlayers', 'input': 'radio', 'field': 'ShipUtils.ShipCanBeBoughtByPlayers'}, {'operator': 'equal', 'value': 'Humans', 'type': 'string', 'id': 'ShipUtils.GetRaceForShip', 'input': 'select', 'field': 'ShipUtils.GetRaceForShip'}], 'valid': True}, 'tableClassNames': '', 'tableCaption': '', 'useCustomTableOptions': 0, 'tableColumnList': []},
    'Aralien Ships': {'name': 'Aralien Ships', 'targetPage': 'Category:Aralien Ships', 'tableHeader': '', 'ruleSet': {'condition': 'AND', 'rules': [{'operator': 'equal', 'value': False, 'type': 'boolean', 'id': 'ShipUtils.IsShipHidden', 'input': 'radio', 'field': 'ShipUtils.IsShipHidden'}, {'operator': 'equal', 'value': True, 'type': 'boolean', 'id': 'ShipUtils.ShipCanBeBoughtByPlayers', 'input': 'radio', 'field': 'ShipUtils.ShipCanBeBoughtByPlayers'}, {'operator': 'equal', 'value': 'Aralien', 'type': 'string', 'id': 'ShipUtils.GetRaceForShip', 'input': 'select', 'field': 'ShipUtils.GetRaceForShip'}], 'valid': True}, 'tableClassNames': '', 'tableCaption': '', 'useCustomTableOptions': 0, 'tableColumnList': []},
    'Restricted Ships': {'name': 'Restricted Ships', 'targetPage': 'Restricted Ships', 'tableHeader': '', 'ruleSet': {'condition': 'AND', 'rules': [{'operator': 'equal', 'value': False, 'type': 'boolean', 'id': 'ShipUtils.IsShipHidden', 'input': 'radio', 'field': 'ShipUtils.IsShipHidden'}, {'operator': 'equal', 'value': False, 'type': 'boolean', 'id': 'ShipUtils.ShipCanBeBoughtByPlayers', 'input': 'radio', 'field': 'ShipUtils.ShipCanBeBoughtByPlayers'}, {'condition': 'OR', 'rules': [{'operator': 'equal', 'value': 'Aralien', 'type': 'string', 'id': 'ShipUtils.GetRaceForShip', 'input': 'select', 'field': 'ShipUtils.GetRaceForShip'}, {'operator': 'equal', 'value': 'Humans', 'type': 'string', 'id': 'ShipUtils.GetRaceForShip', 'input': 'select', 'field': 'ShipUtils.GetRaceForShip'}]}], 'valid': True}, 'tableClassNames': '', 'tableCaption': '', 'useCustomTableOptions': 0, 'tableColumnList': []},
    'NPR Ships': {'name': 'NPR Ships', 'targetPage': 'NPR Ships', 'ruleSet': {'condition': 'AND', 'rules': [{'id': 'ShipUtils.IsShipHidden', 'field': 'ShipUtils.IsShipHidden', 'type': 'boolean', 'input': 'radio', 'operator': 'equal', 'value': False}, {'id': 'ShipUtils.ShipCanBeBoughtByPlayers', 'field': 'ShipUtils.ShipCanBeBoughtByPlayers', 'type': 'boolean', 'input': 'radio', 'operator': 'equal', 'value': False}, {'condition': 'AND', 'rules': [{'id': 'ShipUtils.GetRaceForShip', 'field': 'ShipUtils.GetRaceForShip', 'type': 'string', 'input': 'select', 'operator': 'not_equal', 'value': 'Aralien'}, {'id': 'ShipUtils.GetRaceForShip', 'field': 'ShipUtils.GetRaceForShip', 'type': 'string', 'input': 'select', 'operator': 'not_equal', 'value': 'Humans'}]}], 'valid': True}, 'useCustomTableOptions': 0, 'tableHeader': '', 'tableCaption': '', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': []},
    'Category:Ships': {'name': 'Ships Available To Players', 'targetPage': 'Category:Ships', 'ruleSet': {'condition': 'AND', 'rules': [{'id': 'ShipUtils.IsShipHidden', 'field': 'ShipUtils.IsShipHidden', 'type': 'boolean', 'input': 'radio', 'operator': 'equal', 'value': False}, {'id': 'ShipUtils.ShipCanBeBoughtByPlayers', 'field': 'ShipUtils.ShipCanBeBoughtByPlayers', 'type': 'boolean', 'input': 'radio', 'operator': 'equal', 'value': True}], 'valid': True}, 'useCustomTableOptions': 1, 'sortBy': 'unlockLevel', 'tableHeader': '', 'tableCaption': '', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Ship', 'Sh', 'Sp', 'T', 'Ac', 'La', 'Ma', 'C', 'Tu', 'Ra', 'Le', 'S', 'U', 'M', 'P', 'L', 'A']},
}

itemPresetList = [
{'name': 'Primary Weapons', 'id': 'sf-62a799a69fbecfc98c46ea7a953db6b1', 'targetPage': 'Primary Weapons', 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsItemHidden', 'id': 'ItemUtils.IsItemHidden', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}, {'field': 'weaponType', 'id': 'weaponType', 'input': 'select', 'operator': 'equal', 'type': 'integer', 'value': 0}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}], 'valid': True}, 'tableCaption': '', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Item','Dmg','TD','DPS','ROF','EU','DPE','Rng','Lt','IS','MS','Ac','Effect','Sk'], 'tableHeader': '', 'useCustomTableOptions': 1},
{'name': 'Standard Secondary - Guided ammo based weapons', 'id': 'sf-e249a448050027a146b543286a2d3569', 'targetPage': 'Standard Secondary Weapons', 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsItemHidden', 'id': 'ItemUtils.IsItemHidden', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}, {'field': 'guidance', 'id': 'guidance', 'input': 'select', 'operator': 'equal', 'type': 'integer', 'value': 1}, {'field': 'weaponType', 'id': 'weaponType', 'input': 'select', 'operator': 'equal', 'type': 'integer', 'value': 1}, {'field': 'energyBased', 'id': 'energyBased', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}], 'valid': True}, 'tableCaption': 'Ammo Based', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Item','Dmg','TD','DPS','ROF','Am','MRng','LRng','IS','MS','Trn','Effect','Sk'], 'tableHeader': '', 'useCustomTableOptions': 1},
{'name': 'Standard Secondary - Guided energy based weapons', 'id': 'sf-1347be5e3fdcecf434c87155b2a21f90', 'targetPage': 'Standard Secondary Weapons', 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsItemHidden', 'id': 'ItemUtils.IsItemHidden', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}, {'field': 'guidance', 'id': 'guidance', 'input': 'select', 'operator': 'equal', 'type': 'integer', 'value': 1}, {'field': 'weaponType', 'id': 'weaponType', 'input': 'select', 'operator': 'equal', 'type': 'integer', 'value': 1}, {'field': 'energyBased', 'id': 'energyBased', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': True}, {'field': 'ItemUtils.IsBeamWeapon', 'id': 'ItemUtils.IsBeamWeapon', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}], 'valid': True}, 'tableCaption': 'Energy Based', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Item','Dmg','TD','DPS','ROF','EU','DPE','LRng','IS','MS','Trn','Effect','Sk'], 'tableHeader': '', 'useCustomTableOptions': 1},
{'name': 'Standard Secondary - Beam weapons', 'id': 'sf-e7c9cde16c207f0c10c986dfa933bdbe', 'targetPage': 'Standard Secondary Weapons', 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsBeamWeapon', 'id': 'ItemUtils.IsBeamWeapon', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': True}, {'field': 'ItemUtils.IsItemHidden', 'id': 'ItemUtils.IsItemHidden', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}, {'field': 'weaponType', 'id': 'weaponType', 'input': 'select', 'operator': 'equal', 'type': 'integer', 'value': 1}], 'valid': True}, 'tableCaption': '', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Item','Dmg','TD','DPS','EU','DPE','LRng','Effect','Sk'], 'tableHeader': '', 'useCustomTableOptions': 1},
{'name': 'Standard Secondary - Unguided ammo based weapons', 'id': 'sf-db4e2d3e5b812748a6a4a4164f1c51e5', 'targetPage': 'Standard Secondary Weapons', 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsItemHidden', 'id': 'ItemUtils.IsItemHidden', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}, {'field': 'guidance', 'id': 'guidance', 'input': 'select', 'operator': 'not_equal', 'type': 'integer', 'value': 1}, {'field': 'weaponType', 'id': 'weaponType', 'input': 'select', 'operator': 'equal', 'type': 'integer', 'value': 1}, {'field': 'energyBased', 'id': 'energyBased', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}], 'valid': True}, 'tableCaption': 'Ammo Based', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Item','Dmg','TD','DPS','ROF','Am','MRng','Rng','MS','Trn','Effect','Sk'], 'tableHeader': '', 'useCustomTableOptions': 1},
{'name': 'Standard Secondary - Unguided energy based weapons', 'id': 'sf-7dfa3fdff32b98e4af564fc0b153df5d', 'targetPage': 'Standard Secondary Weapons', 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsItemHidden', 'id': 'ItemUtils.IsItemHidden', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}, {'field': 'guidance', 'id': 'guidance', 'input': 'select', 'operator': 'not_equal', 'type': 'integer', 'value': 1}, {'field': 'weaponType', 'id': 'weaponType', 'input': 'select', 'operator': 'equal', 'type': 'integer', 'value': 1}, {'field': 'energyBased', 'id': 'energyBased', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': True}, {'field': 'ItemUtils.IsBeamWeapon', 'id': 'ItemUtils.IsBeamWeapon', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}], 'valid': True}, 'tableCaption': 'Energy Based', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Item','Dmg','TD','DPS','ROF','EU','DPE','MRng','Rng','MS','Trn','Effect','Sk'], 'tableHeader': '', 'useCustomTableOptions': 1},
{'name': 'Utilities', 'id': 'sf-43cf49c5062d86c140bda66ed6c7bb8c', 'targetPage': 'Utilities', 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'weaponType', 'id': 'weaponType', 'input': 'select', 'operator': 'equal', 'type': 'integer', 'value': 2}, {'field': 'ItemUtils.IsItemHidden', 'id': 'ItemUtils.IsItemHidden', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}], 'valid': True}, 'tableCaption': '', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Item','Ammo','EU','Rng','Turn','Effect','Notes','Sk'], 'tableHeader': '', 'useCustomTableOptions': 1},
{'name': 'Mines - Ammo based', 'id': 'sf-6eb6708e644c196c21f7c450a0850dcb', 'targetPage': 'Mines', 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsItemHidden', 'id': 'ItemUtils.IsItemHidden', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}, {'field': 'weaponType', 'id': 'weaponType', 'input': 'select', 'operator': 'equal', 'type': 'integer', 'value': 3}, {'field': 'energyBased', 'id': 'energyBased', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}], 'valid': True}, 'tableCaption': '', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Item','Dmg','TD','ROF','Ammo','Arm','Lt','Effect','Skill'], 'tableHeader': '', 'useCustomTableOptions': 1},
{'name': 'Mines - Energy based', 'id': 'sf-e1242d4f97918aea034615fcb4d97233', 'targetPage': 'Mines', 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsItemHidden', 'id': 'ItemUtils.IsItemHidden', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}, {'field': 'weaponType', 'id': 'weaponType', 'input': 'select', 'operator': 'equal', 'type': 'integer', 'value': 3}, {'field': 'energyBased', 'id': 'energyBased', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': True}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}], 'valid': True}, 'tableCaption': '', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Item','Dmg','TD','ROF','Energy','DPE','Arm','Lt','Effect','Skill'], 'tableHeader': '', 'useCustomTableOptions': 1},
{'name': 'Proximity Weapons - Ammo', 'id': 'sf-8fbd7d0d7e78fdc7b803204621c73f1a', 'targetPage': 'Proximity Weapons', 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsItemHidden', 'id': 'ItemUtils.IsItemHidden', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}, {'field': 'weaponType', 'id': 'weaponType', 'input': 'select', 'operator': 'equal', 'type': 'integer', 'value': 4}, {'field': 'energyBased', 'id': 'energyBased', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}, {'field': 'name', 'id': 'name', 'input': 'text', 'operator': 'not_contains', 'type': 'string', 'value': 'Bubble'}, {'field': 'life', 'id': 'life', 'input': 'number', 'operator': 'less_or_equal', 'type': 'double', 'value': 5}], 'valid': True}, 'tableCaption': '', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Item','Dmg','TD','ROF','Am','Lt','Rng','Effect','Notes','Sk'], 'tableHeader': '', 'useCustomTableOptions': 1},
{'name': 'Proximity Weapons - Energy', 'id': 'sf-ea0a3b9e1fe39eeb95381b6ed891fd31', 'targetPage': 'Proximity Weapons', 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsItemHidden', 'id': 'ItemUtils.IsItemHidden', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}, {'field': 'weaponType', 'id': 'weaponType', 'input': 'select', 'operator': 'equal', 'type': 'integer', 'value': 4}, {'field': 'energyBased', 'id': 'energyBased', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': True}, {'field': 'name', 'id': 'name', 'input': 'text', 'operator': 'not_contains', 'type': 'string', 'value': 'Bubble'}, {'field': 'life', 'id': 'life', 'input': 'number', 'operator': 'less_or_equal', 'type': 'double', 'value': 5}], 'valid': True}, 'tableCaption': '', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Item','Dmg','ROF','EU','Lt','Rng','Effect','Notes','Sk'], 'tableHeader': '', 'useCustomTableOptions': 1},
{'name': 'Proximity Weapons - Passive', 'id': 'sf-41df5f5be4309afd02f2981280987993', 'targetPage': 'Proximity Weapons', 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsItemHidden', 'id': 'ItemUtils.IsItemHidden', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}, {'field': 'weaponType', 'id': 'weaponType', 'input': 'select', 'operator': 'equal', 'type': 'integer', 'value': 4}, {'condition': 'OR', 'rules': [{'field': 'name', 'id': 'name', 'input': 'text', 'operator': 'contains', 'type': 'string', 'value': 'bubble'}, {'field': 'life', 'id': 'life', 'input': 'number', 'operator': 'greater', 'type': 'double', 'value': 5}]}], 'valid': True}, 'tableCaption': '', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Item','Dmg','ROF','Am','EU','Lt','Rng','Effect','Notes','Sk'], 'tableHeader': '', 'useCustomTableOptions': 1},
{'name': 'Large Weapons - Traditional Bombs', 'id': 'sf-20544f01009c3b7021592ac37af4b034', 'targetPage': 'Large Weapons', 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsItemHidden', 'id': 'ItemUtils.IsItemHidden', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}, {'field': 'weaponType', 'id': 'weaponType', 'input': 'select', 'operator': 'equal', 'type': 'integer', 'value': 5}, {'condition': 'OR', 'rules': [{'field': 'name', 'id': 'name', 'input': 'text', 'operator': 'contains', 'type': 'string', 'value': 'bomb'}, {'field': 'name', 'id': 'name', 'input': 'text', 'operator': 'equal', 'type': 'string', 'value': 'Mr Frosty'}]}, {'field': 'damage', 'id': 'damage', 'input': 'number', 'operator': 'equal', 'type': 'double', 'value': 0}, {'field': 'ItemUtils.GetWeaponEffectName', 'id': 'ItemUtils.GetWeaponEffectName', 'input': 'select', 'operator': 'not_equal', 'type': 'string', 'value': 'None'}], 'valid': True}, 'tableCaption': '', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Item','TD','Arm','Rng','Effect','Am','Cost','Ammo Cost','Notes','Sk'], 'tableHeader': '', 'useCustomTableOptions': 1},
{'name': 'Large Weapons - Unconventional Bombs', 'id': 'sf-ce53d11b575613ca24ae18f5ee120712', 'targetPage': 'Large Weapons', 'ruleSet': {'condition': 'AND', 'rules': [{'id': 'ItemUtils.IsItemHidden', 'value': False, 'type': 'boolean', 'operator': 'equal', 'field': 'ItemUtils.IsItemHidden', 'input': 'radio'}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}, {'id': 'weaponType', 'value': 5, 'type': 'integer', 'operator': 'equal', 'field': 'weaponType', 'input': 'select'}, {'id': 'name', 'value': 'bomb', 'type': 'string', 'operator': 'contains', 'field': 'name', 'input': 'text'}, {'condition': 'OR', 'rules': [{'id': 'damage', 'value': 0, 'type': 'double', 'operator': 'greater', 'field': 'damage', 'input': 'number'}, {'id': 'ItemUtils.GetWeaponEffectName', 'value': 'None', 'type': 'string', 'operator': 'equal', 'field': 'ItemUtils.GetWeaponEffectName', 'input': 'select'}]}, {'id': 'name', 'value': 'bombard', 'type': 'string', 'operator': 'not_contains', 'field': 'name', 'input': 'text'}], 'valid': True}, 'tableCaption': '', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Item','TD','Lt','Rng','Effect','Am','Cost','Ammo Cost','Notes','Sk'], 'tableHeader': '', 'useCustomTableOptions': 1},
{'name': 'Large Weapons - Clouds', 'id': 'sf-5ab72843e794921e972ec96c98836606', 'targetPage': 'Large Weapons', 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsItemHidden', 'id': 'ItemUtils.IsItemHidden', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}, {'field': 'weaponType', 'id': 'weaponType', 'input': 'select', 'operator': 'equal', 'type': 'integer', 'value': 5}, {'field': 'name', 'id': 'name', 'input': 'text', 'operator': 'contains', 'type': 'string', 'value': 'Cloud'}], 'valid': True}, 'tableCaption': '', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Item','Dmg','TD','Rng','Am','Cost','Ammo Cost','Notes','Sk'], 'tableHeader': '', 'useCustomTableOptions': 1},
{'name': 'Large Weapons - Droids', 'id': 'sf-30aab9016ff1f68d1b9ad698c6015ea9', 'targetPage': 'Large Weapons', 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsItemHidden', 'id': 'ItemUtils.IsItemHidden', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}, {'field': 'weaponType', 'id': 'weaponType', 'input': 'select', 'operator': 'equal', 'type': 'integer', 'value': 5}, {'field': 'name', 'id': 'name', 'input': 'text', 'operator': 'contains', 'type': 'string', 'value': 'Droid'}], 'valid': True}, 'tableCaption': '', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Item','Lt','Ammo','Cost','Ammo Cost','Notes','Sk'], 'tableHeader': '', 'useCustomTableOptions': 1},
{'name': 'Large Weapons - Beacons', 'id': 'sf-0b9d04f449e50fcfd5bd0ca64eef405d', 'targetPage': 'Large Weapons', 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsItemHidden', 'id': 'ItemUtils.IsItemHidden', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}, {'field': 'weaponType', 'id': 'weaponType', 'input': 'select', 'operator': 'equal', 'type': 'integer', 'value': 5}, {'condition': 'OR', 'rules': [{'field': 'name', 'id': 'name', 'input': 'text', 'operator': 'contains', 'type': 'string', 'value': 'Beacon'}, {'field': 'name', 'id': 'name', 'input': 'text', 'operator': 'contains', 'type': 'string', 'value': 'Launcher'}, {'field': 'name', 'id': 'name', 'input': 'text', 'operator': 'contains', 'type': 'string', 'value': 'Portal'}]}], 'valid': True}, 'tableCaption': '', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Item','Lt','Ammo','Cost','Ammo Cost','Notes','Sk'], 'tableHeader': '', 'useCustomTableOptions': 1},
{'name': 'Large Weapons - Micro Gates', 'id': 'sf-d40dae3783a42fae281a3a7258c2c270', 'targetPage': 'Large Weapons', 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsItemHidden', 'id': 'ItemUtils.IsItemHidden', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}, {'field': 'weaponType', 'id': 'weaponType', 'input': 'select', 'operator': 'equal', 'type': 'integer', 'value': 5}, {'field': 'name', 'id': 'name', 'input': 'text', 'operator': 'contains', 'type': 'string', 'value': 'micro gate'}], 'valid': True}, 'tableCaption': '', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Item','Ammo','Ammo Cost','Destination','Sk'], 'tableHeader': '', 'useCustomTableOptions': 1},
{'name': 'Large Weapons - Other', 'id': 'sf-d535f92608356e7cebe668c129d497c5', 'targetPage': 'Large Weapons', 'ruleSet': {'condition': 'AND', 'rules': [{'id': 'ItemUtils.IsItemHidden', 'value': False, 'type': 'boolean', 'operator': 'equal', 'field': 'ItemUtils.IsItemHidden', 'input': 'radio'}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}, {'id': 'weaponType', 'value': 5, 'type': 'integer', 'operator': 'equal', 'field': 'weaponType', 'input': 'select'}, {'id': 'name', 'value': 'Droid', 'type': 'string', 'operator': 'not_contains', 'field': 'name', 'input': 'text'}, {'id': 'name', 'value': 'Launcher', 'type': 'string', 'operator': 'not_contains', 'field': 'name', 'input': 'text'}, {'id': 'name', 'value': 'Beacon', 'type': 'string', 'operator': 'not_contains', 'field': 'name', 'input': 'text'}, {'id': 'name', 'value': 'Cloud', 'type': 'string', 'operator': 'not_contains', 'field': 'name', 'input': 'text'}, {'id': 'name', 'value': 'Micro Gate', 'type': 'string', 'operator': 'not_contains', 'field': 'name', 'input': 'text'}, {'id': 'name', 'value': 'Portal', 'type': 'string', 'operator': 'not_contains', 'field': 'name', 'input': 'text'}, {'id': 'name', 'value': 'Mr Frosty', 'type': 'string', 'operator': 'not_equal', 'field': 'name', 'input': 'text'}, {'condition': 'OR', 'rules': [{'id': 'name', 'value': 'Bombard', 'type': 'string', 'operator': 'contains', 'field': 'name', 'input': 'text'}, {'id': 'name', 'value': 'Bomb', 'type': 'string', 'operator': 'not_contains', 'field': 'name', 'input': 'text'}]}], 'valid': True}, 'tableCaption': '', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Item','Dmg','TD','Range','Lt','Ammo','Cost','Ammo Cost','Notes','Sk'], 'tableHeader': '', 'useCustomTableOptions': 1},
{'name': 'Engines', 'id': 'sf-dd12c631d6854fdc082390191b92df86', 'targetPage': 'Engines', 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsItemHidden', 'id': 'ItemUtils.IsItemHidden', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}, {'field': 'type', 'id': 'type', 'input': 'select', 'operator': 'equal', 'type': 'integer', 'value': 4}], 'valid': True}, 'tableCaption': '', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Item','Speed','Reverse','Accel','Turning','Prop','Prop Time','Sk'], 'tableHeader': '', 'useCustomTableOptions': 1},
{'name': 'Shields', 'id': 'sf-d8aa0dc101f732f91985fa8f22895281', 'targetPage': 'Shields', 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsItemHidden', 'id': 'ItemUtils.IsItemHidden', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}, {'field': 'type', 'id': 'type', 'input': 'select', 'operator': 'equal', 'type': 'integer', 'value': 5}], 'valid': True}, 'tableCaption': '', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Item','Maximum Charge Multiplier','Charge Rate','Charge Delay','Secondary Effects','Skill'], 'tableHeader': '', 'useCustomTableOptions': 1},
{'name': 'Augmentations - Active', 'id': 'sf-edaeabc84c6fa393803fe743ac13b095', 'targetPage': 'Augmentations', 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsItemHidden', 'id': 'ItemUtils.IsItemHidden', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}, {'field': 'type', 'id': 'type', 'input': 'select', 'operator': 'equal', 'type': 'integer', 'value': 6}, {'field': 'passive', 'id': 'passive', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}], 'valid': True}, 'tableCaption': '', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Item','Notes','Cost','Skill'], 'tableHeader': '', 'useCustomTableOptions': 1},
{'name': 'Augmentations - Passive', 'id': 'sf-bb527ab901e042e9cde6a4506c2d9b9d', 'targetPage': 'Augmentations', 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsItemHidden', 'id': 'ItemUtils.IsItemHidden', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}, {'field': 'type', 'id': 'type', 'input': 'select', 'operator': 'equal', 'type': 'integer', 'value': 6}, {'field': 'passive', 'id': 'passive', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': True}, {'field': 'ItemUtils.GetItemAugType', 'id': 'ItemUtils.GetItemAugType', 'input': 'select', 'operator': 'not_equal', 'type': 'string', 'value': 'Turret'}, {'field': 'ItemUtils.GetItemAugType', 'id': 'ItemUtils.GetItemAugType', 'input': 'select', 'operator': 'not_equal', 'type': 'string', 'value': 'Deathtrap'}, {'field': 'ItemUtils.GetItemAugType', 'id': 'ItemUtils.GetItemAugType', 'input': 'select', 'operator': 'not_equal', 'type': 'string', 'value': 'Death Trap Spawn'}, {'field': 'ItemUtils.GetItemAugType', 'id': 'ItemUtils.GetItemAugType', 'input': 'select', 'operator': 'not_equal', 'type': 'string', 'value': 'Andromedan Power Source'}, {'field': 'ItemUtils.GetItemAugType', 'id': 'ItemUtils.GetItemAugType', 'input': 'select', 'operator': 'not_equal', 'type': 'string', 'value': 'Dark Energy Charging'}, {'field': 'ItemUtils.GetItemAugType', 'id': 'ItemUtils.GetItemAugType', 'input': 'select', 'operator': 'not_equal', 'type': 'string', 'value': 'Solar Panel Upgrade'}], 'valid': True}, 'tableCaption': '', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Item','Notes','Cost','Skill'], 'tableHeader': '', 'useCustomTableOptions': 1},
{'name': 'Augmentations - Energy Charging', 'id': 'sf-c068772723069fe8bd3c3a7446c2fde2', 'targetPage': 'Augmentations', 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsItemHidden', 'id': 'ItemUtils.IsItemHidden', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}, {'field': 'type', 'id': 'type', 'input': 'select', 'operator': 'equal', 'type': 'integer', 'value': 6}, {'field': 'passive', 'id': 'passive', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': True}, {'condition': 'OR', 'rules': [{'field': 'ItemUtils.GetItemAugType', 'id': 'ItemUtils.GetItemAugType', 'input': 'select', 'operator': 'equal', 'type': 'string', 'value': 'Andromedan Power Source'}, {'field': 'ItemUtils.GetItemAugType', 'id': 'ItemUtils.GetItemAugType', 'input': 'select', 'operator': 'equal', 'type': 'string', 'value': 'Dark Energy Charging'}, {'field': 'ItemUtils.GetItemAugType', 'id': 'ItemUtils.GetItemAugType', 'input': 'select', 'operator': 'equal', 'type': 'string', 'value': 'Solar Panel Upgrade'}]}], 'valid': True}, 'tableCaption': '', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Item','Aug Type','Notes','Cost','Skill'], 'tableHeader': '', 'useCustomTableOptions': 1},
{'name': 'Augmentations - Deathtraps', 'id': 'sf-7ede64dddf353a3e3d135792dbe2c7e4', 'targetPage': 'Augmentations', 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsItemHidden', 'id': 'ItemUtils.IsItemHidden', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}, {'field': 'type', 'id': 'type', 'input': 'select', 'operator': 'equal', 'type': 'integer', 'value': 6}, {'field': 'passive', 'id': 'passive', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': True}, {'condition': 'OR', 'rules': [{'field': 'ItemUtils.GetItemAugType', 'id': 'ItemUtils.GetItemAugType', 'input': 'select', 'operator': 'equal', 'type': 'string', 'value': 'Deathtrap'}, {'field': 'ItemUtils.GetItemAugType', 'id': 'ItemUtils.GetItemAugType', 'input': 'select', 'operator': 'equal', 'type': 'string', 'value': 'Death Trap Spawn'}]}], 'valid': True}, 'tableCaption': '', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Item','Notes','Cost','Skill'], 'tableHeader': '', 'useCustomTableOptions': 1},
{'name': 'Augmentations - Turrets', 'id': 'sf-0bb4e660ba9a8becd387df20b9ab1430', 'targetPage': 'Augmentations', 'ruleSet': {'condition': 'AND', 'rules': [{'field': 'ItemUtils.IsItemHidden', 'id': 'ItemUtils.IsItemHidden', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': False}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}, {'field': 'type', 'id': 'type', 'input': 'select', 'operator': 'equal', 'type': 'integer', 'value': 6}, {'field': 'passive', 'id': 'passive', 'input': 'radio', 'operator': 'equal', 'type': 'boolean', 'value': True}, {'field': 'ItemUtils.GetItemAugType', 'id': 'ItemUtils.GetItemAugType', 'input': 'select', 'operator': 'equal', 'type': 'string', 'value': 'Turret'}], 'valid': True}, 'tableCaption': '', 'tableClassNames': 'wikitable sortable floatheader', 'tableColumnList': ['Item','Dmg','DPS','Rng','Notes','Cost','Skill'], 'tableHeader': '', 'useCustomTableOptions': 1},
{'name': 'Crafted Items', 'targetPage': 'Crafting', 'ruleSet': {'condition': 'AND', 'rules': [{'id': 'ItemUtils.IsItemHidden', 'field': 'ItemUtils.IsItemHidden', 'type': 'boolean', 'input': 'radio', 'operator': 'equal', 'value': False}, {'id':'ItemUtils.IsItemNprExclusive','field':'ItemUtils.IsItemNprExclusive','type':'boolean','input':'radio','operator':'equal','value':False}, {'id': 'ItemUtils.ItemDisplayStatBPLocation', 'field': 'ItemUtils.ItemDisplayStatBPLocation', 'type': 'string', 'input': 'text', 'operator': 'is_not_empty', 'value': None}], 'valid': True}, 'useCustomTableOptions': 0, 'tableHeader': '', 'tableCaption': '', 'tableClassNames': '', 'tableColumnList': [], 'pageType': 'crafting'},
]
