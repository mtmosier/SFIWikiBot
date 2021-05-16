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


shieldEffectIconClassMappingDefault = 'Andromedan Stealth=fas fa-low-vision, Gravity=fab fa-grav, Nuclear=fas fa-radiation, NPR Damage=fab fa-android, Beam Refracting=fas fa-slash, Cold Fusion=fas fa-snowflake, Deflector=, Effect Reduce=fas fa-angle-double-down, Electrostatic=fas fa-bolt, Energy Absorb=fas fa-charging-station, Explosive=fas fa-bomb, Frozen=fas fa-icicles, Heat Resist=fas fa-burn, Heat Weakness=fas fa-burn, Ghostly=fas fa-ghost, Laser=fas fa-asterisk, Overdose Resist=fas fa-wind, Photonic=fas fa-sun, Projectile=fas fa-ellipsis-h, Selective Effect Reduce=fas fa-angle-down, Stabiliser Fail=fas fa-fighter-jet fa-rotate-135, Mine Claimer=fas fa-hands, Mine Sweeper=fas fa-snowplow'
shieldEffectIconClassMapping = dict(config('botShieldEffectIconClassMapping', cast=Csv(cast=lambda s: tuple(s.split('='))), default=shieldEffectIconClassMappingDefault))


damageTypeIconClassMappingDefault = 'Projectile=fas fa-ellipsis-h, Explosive=fas fa-bomb, Laser=fas fa-asterisk, Heat=fas fa-fire, Repair=fas fa-heartbeat, Electrostatic=fas fa-bolt, Tractor=fas fa-link, Photonic=fas fa-sun, RedMist=fas fa-wind, Cold=fas fa-snowflake, Ghostly=fas fa-ghost, EnergyExtraction=fas fa-sign-out-alt, ShieldExtraction=fas fa-sign-out-alt, Combo=fas fa-sign-out-alt, Undefined=fas fa-question-circle, Other=fas fa-question-circle, AmmoHarvest=fas fa-sign-out-alt fa-rotate-270, ShieldHarvest=fas fa-sign-out-alt fa-rotate-270, EnergyHarvest=fas fa-sign-out-alt fa-rotate-270, DartianMining=fas fa-sign-out-alt fa-rotate-270, Null=[html]&\\#8709;'
damageTypeIconClassMapping = dict(config('botDamageTypeIconClassMapping', cast=Csv(cast=lambda s: tuple(s.split('='))), default=damageTypeIconClassMappingDefault))

effectIconClassMapping = dict(config('botEffectIconClassMapping', cast=Csv(cast=lambda s: tuple(s.split('='))), default=''))

unreleasedRaceList = config('botUnreleasedRaceList', cast=Csv(), default='')
unreleasedShipList = config('botUnreleasedShipList', cast=Csv(), default='')
unreleasedSystemList = config('botUnreleasedSystemList', cast=Csv(), default='TBZ')
wikiLinkReplacementExclusionList = config('botWikiLinkReplacementExclusionList', cast=Csv(), default='Black, Damage, Energy, Ships')

wikiLinkReplacementOverrideListDefault = 'Black Ships=Ascendants'
wikiLinkReplacementOverrideList = dict(config('botWikiLinkReplacementOverrideList', cast=Csv(cast=lambda s: tuple(s.split('='))), default=wikiLinkReplacementOverrideListDefault))

bpLocationOverride = dict(config('botBpLocationOverride', cast=Csv(cast=lambda s: tuple(s.split('='))), default=''))

projectileCountOverrideDefault = 'Sheenite Orbital Ultra Ring=30, Sheenite Orbital Chevron Ring=8, Church Savior Cloud=15'
projectileCountOverride = dict(config('botProjectileCountOverride', cast=Csv(cast=lambda s: tuple(s.split('='))), default=projectileCountOverrideDefault))
projectileCountOverride = { k:int(v) for k, v in projectileCountOverride.items() }

weaponRangeOverrideDefault = 'Sheenite Orbital Ultra Ring=17, Sheenite Orbital Chevron Ring=17, Ascendant Gun Turret=125'
weaponRangeOverride = dict(config('botWeaponRangeOverride', cast=Csv(cast=lambda s: tuple(s.split('='))), default=weaponRangeOverrideDefault))
weaponRangeOverride = { k:float(v) for k, v in weaponRangeOverride.items() }

mainFactionListDefault = 'Human Alliance=, Alliance Science Corps=Human Alliance\#Alliance Science Corps, Aralien Empire=, Empire Intelligence=Aralien Empire\#Empire Intelligence, Freedom Initiative='
mainFactionList = dict(config('botMainFactionList', cast=Csv(cast=lambda s: tuple(s.split('='))), default=mainFactionListDefault))

nprPageNameMappingDefault = 'Ascendants=Ascendant, Andromedans=Andromedan, Dartians=Dartian, Devimon=Devimon, Forkworms=Forkworm, Ghosts=Ghost, Igni=Igni, Null Dwellers=Null Dweller, Prongworms=Prongworm, Radii=Radii, Red Mist=Red Mist, Relisk=Relisk, Resonites=Resonite, Rodions=Rodion, Sheenites=Sheenite, Solarions=Solarion, Splicers=Splicer, The Church of Megmos=Church of Megmos, The Gao=The Gao, Tobor=Tobor, Tornadians=Tornadian, Tyraan=Tyraan, Vacuum Flies=Vacuum Fly'
nprPageNameMapping = dict(config('botNprPageNameMapping', cast=Csv(cast=lambda s: tuple(s.split('='))), default=nprPageNameMappingDefault))

subWeaponIDOverrideDefault = 'Cake Bomb=cks, Stinger Cloud=st_1, Sheenite Orbital Ultra Ring=soc, Sheenite Orbital Chevron Ring=soc'
subWeaponIDOverride = dict(config('botSubWeaponIDOverride', cast=Csv(cast=lambda s: tuple(s.split('='))), default=subWeaponIDOverrideDefault))

wikiImageAndPageListTtl = config("botWikiImageAndPageListTtlSec", default=900, cast=int)  # Default 15 minutes
publicDatabaseContentTtl = config("botPublicDatabaseContentTtlSec", default=25200, cast=int)  # Default 7 hours
privateDatabaseContentTtl = config("botPrivateDatabaseContentTtlSec", default=25200, cast=int)  # Default 7 hours

publicDatabaseUrl = config("botPublicDatabaseUrl", default='http://www.starfighterinfinity.com/Database.htm')
privateDataUrlTemplate = config("botPrivateDataUrlTemplate", default='https://www.benoldinggames.co.uk/sfi/gamedata/files/{}.jsonp')
privateObjectListUrl = config("botPrivateObjectListUrl", default='https://benoldinggames.co.uk/sfi/files/planets/planets.htm')
