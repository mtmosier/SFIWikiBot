#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import os
import decouple

Csv = decouple.Csv

# Determine default settings path - start with current director then fall back to /etc/sfiWikiBot
configDir = os.getenv("botSettingsDir", None)

if configDir is None:
    configDir = '.'
    testPath = os.path.join(configDir, 'settings.ini')
    if not os.path.isfile(testPath):
        testPath = os.path.join(configDir, '.env')
        if not os.path.isfile(testPath):
            configDir = '/etc/sfiWikiBot'

config = decouple.AutoConfig(configDir)



# Visit https://starfighter-infinity.fandom.com/wiki/Special:BotPasswords to set up your password
botUsername = config("botUsername", default=None)
botPassword = config("botPassword", default=None)

debug = config("debug", default=False, cast=bool)
verbose = config("verbose", default=0, cast=int)

craftingPageName = config("botCraftingPageName", default="Crafting")
cacheDir = config("botCacheDir", default="/tmp")

maxWordsInArticleTitleSearch = config("botMaxWordsInArticleTitleSearch", default=4, cast=int)
defaultDpsTimeframeInSec = config("botDefaultDpsTimeframeInSec", default=10, cast=float)
shipMassForDamageCalculation = config("botShipMassForDamageCalculation", default=2, cast=float)
turnMultiplier = config("botTurnMultiplier", default=30, cast=float)

pauseBetweenContentUpdateStepsInSec = config("botPauseBetweenContentUpdateStepsInSec", default=2, cast=float)
pauseAfterSuccessfullyUpdatingWikiPageInSec = config("botPauseAfterSuccessfullyUpdatingWikiPageInSec", default=1.5, cast=float)
pauseAfterFailingToUpdateWikiPageInSec = config("botPauseAfterFailingToUpdateWikiPageInSec", default=2, cast=float)
pauseAfterSkippingWikiPageUpdateInSec = config("botPauseAfterSkippingWikiPageUpdateInSec", default=1, cast=float)


damageTypeIconClassMappingDefault = 'Projectile=fa fa-ellipsis-h, Explosive=fa fa-bomb, Laser=fa fa-asterisk, Heat=fa fa-fire, Repair=fa fa-heartbeat, Electrostatic=fa fa-bolt, Tractor=fa fa-link, Photonic=fa fa-star, RedMist=fa fa-cloud, Cold=fa fa-snowflake'
damageTypeIconClassMapping = dict(config('botDamageTypeIconClassMapping', cast=Csv(cast=lambda s: tuple(s.split('='))), default=damageTypeIconClassMappingDefault))

effectIconClassMapping = dict(config('botEffectIconClassMapping', cast=Csv(cast=lambda s: tuple(s.split('='))), default=''))

unreleasedRaceList = config('botUnreleasedRaceList', cast=Csv(), default='')
unreleasedShipList = config('botUnreleasedShipList', cast=Csv(), default='')
unreleasedSystemList = config('botUnreleasedSystemList', cast=Csv(), default='TBZ')
wikiLinkReplacementExclusionList = config('botWikiLinkReplacementExclusionList', cast=Csv(), default='Black, Damage, Energy, Ships')

bpLocationOverride = dict(config('botBpLocationOverride', cast=Csv(cast=lambda s: tuple(s.split('='))), default=''))

projectileCountOverrideDefault = 'Sheenite Orbital Ultra Ring=30, Sheenite Orbital Chevron Ring=8, Church Savior Cloud=15'
projectileCountOverride = dict(config('botProjectileCountOverride', cast=Csv(cast=lambda s: tuple(s.split('='))), default=projectileCountOverrideDefault))
projectileCountOverride = { k:int(v) for k, v in projectileCountOverride.items() }

weaponRangeOverrideDefault = 'Sheenite Orbital Ultra Ring=17, Sheenite Orbital Chevron Ring=17, Ascendant Gun Turret=125'
weaponRangeOverride = dict(config('botWeaponRangeOverride', cast=Csv(cast=lambda s: tuple(s.split('='))), default=weaponRangeOverrideDefault))
weaponRangeOverride = { k:float(v) for k, v in weaponRangeOverride.items() }

subWeaponIDOverrideDefault = 'Cake Bomb=cks, Stinger Cloud=st_1, Sheenite Orbital Ultra Ring=soc, Sheenite Orbital Chevron Ring=soc'
subWeaponIDOverride = dict(config('botSubWeaponIDOverride', cast=Csv(cast=lambda s: tuple(s.split('='))), default=subWeaponIDOverrideDefault))

wikiImageAndPageListTtl = config("botWikiImageAndPageListTtlSec", default=900, cast=int)  # Default 15 minutes
publicDatabaseContentTtl = config("botPublicDatabaseContentTtlSec", default=25200, cast=int)  # Default 7 hours
privateDatabaseContentTtl = config("botPrivateDatabaseContentTtlSec", default=25200, cast=int)  # Default 7 hours

publicDatabaseUrl = config("botPublicDatabaseUrl", default='http://www.starfighterinfinity.com/Database.htm')
privateDataUrlTemplate = config("botPrivateDataUrlTemplate", default='https://www.benoldinggames.co.uk/sfi/gamedata/files/{}.jsonp')
privateObjectListUrl = config("botPrivateObjectListUrl", default='https://benoldinggames.co.uk/sfi/files/planets/planets.htm')
