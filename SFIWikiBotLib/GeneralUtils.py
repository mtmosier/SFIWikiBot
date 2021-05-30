#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import io
import re
import json
import decimal
import math
import hashlib
from html.parser import HTMLParser
from collections import OrderedDict
from nltk.stem import PorterStemmer



# levelUpBase = 246


def RoundToMeaningful(input, smallValue=False, allowDec=False):
    if input >= 1000000:
        return NumDisplay(NormalRound(input / 50000) * 50000, 0)
    if input >= 10000:
        return NumDisplay(NormalRound(input / 1000) * 1000, 0)
    if input >= 500:
        return NumDisplay(NormalRound(input / 100) * 100, 0)
    return NumDisplay(NormalRound(input / 50) * 50, 0)


levelUpBase = 246.2
levelMultInc = 0.0514
def LevelStart(level, debug=False):
    num = 0
    num2 = 1
    for i in range(level+1):
        num += int(RoundToMeaningful(i * levelUpBase * num2))
        num2 += levelMultInc
        if debug:
            print(i, RoundToMeaningful(num), '::', num, num + (i * levelUpBase * num2))

    # return num
    return RoundToMeaningful(num)


# from deepdiff import DeepDiff
# ddiff = DeepDiff(t1, t2, ignore_order=True)
# print (DeepDiff(t1, t2, exclude_paths={"root['ingredients']"}))
# ddiff.to_dict()
# ddiff.to_json()



# https://stackoverflow.com/questions/27265939/comparing-python-dictionaries-and-nested-dictionaries
def DictCompare(d1, d2, path=""):
    #  Consider using DeepDiff instead!  https://github.com/seperman/deepdiff
    for k in d1:
        if (k not in d2):
            print (path, ":")
            print (k + " as key not in d2", "\n")
        else:
            if type(d1[k]) is dict:
                if path == "":
                    path = k
                else:
                    path = path + "->" + k
                findDiff(d1[k],d2[k], path)
            else:
                if d1[k] != d2[k]:
                    print (path, ":")
                    print (" - ", k," : ", d1[k])
                    print (" + ", k," : ", d2[k])


def mkdirr(path):
    os.makedirs(path, exist_ok=True)


def CleanupImportedText(input):
    return input.replace("\u00e2\u20ac\u0153", '"') \
                .replace("\u00e2\u20ac?", '"') \
                .replace('â€™', "'") \
                .replace('\r\n', '\n') \
                .strip()


def floatCmp(v1, c, v2, dec=None):
    if v1 is None or v2 is None:
        if c == '!=' or c == '<>' or c == '><':
            return v1 is not v2
        elif c == '==':
            return v1 is v2
        return False
    if c == '==':
        return math.isclose(v1, v2, rel_tol=1e-04)
    if c == '!=' or c == '<>' or c == '><':
        return not math.isclose(v1, v2, rel_tol=1e-04)
    if c == '>=' or c == '=>':
        return math.isclose(v1, v2, rel_tol=1e-04) or v1 > v2
    if c == '<=' or c == '=<':
        return math.isclose(v1, v2, rel_tol=1e-04) or v1 < v2
    if c == '>':
        return not math.isclose(v1, v2, rel_tol=1e-04) and v1 > v2
    if c == '<':
        return not math.isclose(v1, v2, rel_tol=1e-04) and v1 < v2

    raise NotImplementedError


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = io.StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def StripTags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def GenerateDataSignature(data):
    try:
        input = data.copy()
    except:
        input = data

    if type(input) == OrderedDict or type(input) == dict:
        input = NormalizeDict(input)

    if type(input) == str:
        input = input.replace('\r', '').replace('\n', '').strip()

    jsonStr = json.dumps(input, sort_keys=True)
    return hashlib.md5(jsonStr.encode("utf-8")).hexdigest()


def NormalizeDict(data):
    if type(data) == OrderedDict or type(data) == dict:
        fixedList = OrderedDict()
        for k, v in sorted(data.items()):
            if type(v) == OrderedDict or type(v) == dict:
                v = NormalizeDict(v)
            elif type(v) == list:
                v = NormalizeList(v)
            else:
                v = str(v).replace('\r', '').strip()
            fixedList[k] = v
        data = fixedList

    return data


def NormalizeList(data):
    if type(data) == list:
        fixedList = []
        for v in data:
            if type(v) == OrderedDict or type(v) == dict:
                v = NormalizeDict(v)
            elif type(v) == list:
                v = NormalizeList(v)
            else:
                v = str(v).replace('\r', '').strip()
            fixedList.append(v)
        data = fixedList

    return data



# https://stackoverflow.com/a/45424214
def NormalRound(num):
    return ((num > 0) - (num < 0)) * int(abs(num) + 0.5)


# https://stackoverflow.com/questions/5807952/removing-trailing-zeros-in-python
def NumDisplay(num, decPlaces=..., insertCommas=False):
    try:
        dec = decimal.Decimal(num)
        if decPlaces is not ...:
            dec = round(dec, decPlaces)
    except:
        return ''

    tup = dec.as_tuple()
    delta = len(tup.digits) + tup.exponent
    digits = ''.join(str(d) for d in tup.digits)
    if delta <= 0:
        zeros = abs(tup.exponent) - len(tup.digits)
        val = '0.' + ('0'*zeros) + digits
    else:
        val = digits[:delta] + ('0'*tup.exponent) + '.' + digits[delta:]
    val = val.rstrip('0')
    if val[-1] == '.':
        val = val[:-1]
    if tup.sign:
        val = '-' + val
    if insertCommas:
        val = '{:,}'.format(decimal.Decimal(val))
    return stripTrailingZerosFromNumStr(val)


def stripTrailingZerosFromNumStr(input):
    if '.' in input:
        input = input.rstrip('0').rstrip('.')
    return input


def RoundToSignificantAmount(input, smallValue=False, allowDec=False):
    if input >= 500:
        return NumDisplay(NormalRound(input / 100) * 100, 0)
    if smallValue and input >= 100:  # Used for ammo cost
        return NumDisplay(NormalRound(input / 50) * 50, 0)
    if input >= 50:
        return NumDisplay(NormalRound(input / 10) * 10, 0)
    if input >= 10:
        return NumDisplay(NormalRound(input / 5) * 5, 0)
    if allowDec:
        return NumDisplay(input, 1)
    return NumDisplay(input, 0)


# https://www.geeksforgeeks.org/python-program-to-convert-camel-case-string-to-snake-case/
def CamelCaseToTitleCase(input):
    rtnVal = ''.join([ ' ' + i if i.isupper() else i for i in input ])
    return rtnVal.strip().title()


def GetPluralForm(word):
    if word[-1] == 'y':
        return "{}ies".format(word[:-1])
    if word[-2:] == 'es':
        return word
    if word[-1] == 's':
        return "{}es".format(word)
    return "{}s".format(word)


def PrettyPrint(input):
    print(json.dumps(input, indent=4))


def SecondsDisplay(sec):
    rtnVal = str(sec) + " second"
    if sec != 1:
        rtnVal += "s"
    return rtnVal


def FixJson(input):
    input = re.sub(r',\s*}$', '}', input)
    input = re.sub(r',\s*\]', ']', input)
    return input


def NormalizeString(str, includeStemming=False):
    try:
        str = str.lower()
    except:
        pass
    return str


def ConvertListToHtmlTable(tableData, tableHeader = None, tableTitle = None, tableClass = None, tableId = None, tableColumnTitleList = None):
    rtnVal = ""
    if len(tableData) > 0:
        if tableHeader:
            rtnVal += '<h3>{}</h3>\n'.format(tableHeader)
        if tableTitle:
            rtnVal += '<div style="display: inline-block;"><h4><span class="mw-headline" id="{0}"><div class="tableCaption">{0}</div></span></h4>'.format(tableTitle)

        rtnVal += "<table"
        if tableId:
            rtnVal += ' id="sf-{}"'.format(tableId)
        if tableClass:
            rtnVal += ' class="{}"'.format(tableClass)
        rtnVal += ">\n"
        rtnVal += "<thead>\n"

        first = True
        for row in tableData:
            values = "<tr>\n"
            headings = ""
            if first:
                headings += "<tr>\n"


            idx = 0
            for key, val in row.items():
                if first:
                    if tableColumnTitleList and len(tableColumnTitleList) > idx and tableColumnTitleList[idx]:
                        headings += '<th scope="col"><span title="{}">{}</span></th>\n'.format(tableColumnTitleList[idx], key)
                    else:
                        headings += "<th>{}</th>\n".format(key)
                values += "<td>{}</td>\n".format(val)
                idx += 1

            rtnVal += headings
            if first:
                rtnVal += "</thead>\n"
                rtnVal += "<tbody>\n"
            rtnVal += values
            first = False

        rtnVal += "</tbody>\n"
        rtnVal += "</table>\n\n"
        if tableTitle:
            rtnVal += '</div>'

    return rtnVal





# def stemSentence(sentence):
#     token_words=word_tokenize(sentence)
#     token_words
#     stem_sentence=[]
#     for word in token_words:
#         stem_sentence.append(porter.stem(word))
#         stem_sentence.append(" ")
#     return "".join(stem_sentence)
#
# tokens = nltk.word_tokenize(sentence)

# def ReplaceWikiLinksWithPlaceholders(content):
# def ReplacePlaceholdersWithWikiLinks(content, placeholderMap):
# def GetWikiLink(input):
# def GetWikiArticlePageForNameList(nameList, finalRedirect=False):
# def GetWikiArticlePageList():


def SplitTextIntoPhrases(input, maxPhrase):
    input = re.sub(r'[^a-zA-Z0-9\(\):-]', " ", input)
    inputWordList = re.split(r'\s+', input)
    phraseList = [];
    for plen in range(maxPhrase, 0, -1):
        for sIdx in range(0, len(inputWordList) - plen):
            phrase = ' '.join(inputWordList[sIdx:sIdx+plen]).strip()
            phraseList.append(phrase)
    return phraseList


# SplitNameIntoBaseNameAndItemLevel(input)
    # return { 'name': name, 'fullNameMinusLevel': fullNameMinusLevel, 'levelDisplay': levelDisplayOrig, 'levelIdx': levelIdx, 'namePostfix': postfix }

def AddWikiLinksToText(input, useHtml=False, allowExtraWeaponCheck=True, additionalReplacementOverrides=None):
    from SFIWikiBotLib import WikiUtils
    from SFIWikiBotLib import Config
    from SFIWikiBotLib import ItemUtils

    includeStemming = True
    normalizedReplacementExclusionList = [ NormalizeString(v, includeStemming) for v in Config.wikiLinkReplacementExclusionList ]
    normalizedReplacementOverrideList = { NormalizeString(k, includeStemming):NormalizeString(v, includeStemming) for k, v in Config.wikiLinkReplacementOverrideList.items() }
    if type(additionalReplacementOverrides) == dict:
        for k, v in additionalReplacementOverrides.items():
            normalizedReplacementOverrideList[NormalizeString(k, includeStemming)] = NormalizeString(v, includeStemming)

    phraseList = SplitTextIntoPhrases(input, Config.maxWordsInArticleTitleSearch)
    replacementList = []
    replacementInfo = {}
    placeholderCount = 0

    for origPhrase in phraseList:
        normalizedPhrase = NormalizeString(origPhrase, includeStemming)
        if normalizedPhrase in normalizedReplacementExclusionList:
            continue
        if normalizedPhrase in normalizedReplacementOverrideList:
            normalizedPhrase = normalizedReplacementOverrideList[normalizedPhrase]

        nameList = [ normalizedPhrase ]
        if allowExtraWeaponCheck:
            altNameInfo = ItemUtils.SplitNameIntoBaseNameAndItemLevel(origPhrase)
            if altNameInfo['fullNameMinusLevel'].lower() != normalizedPhrase.lower():
                altName = NormalizeString(altNameInfo['fullNameMinusLevel'], includeStemming)
                if altName not in normalizedReplacementExclusionList:
                    nameList.append(altName)

        wikiPage = WikiUtils.GetWikiArticlePageForNameList(nameList)
        if wikiPage:
            replacementInfo = {};
            replacementInfo["originalText"] = origPhrase;
            if useHtml:
                replacementInfo["replacementText"] = '<a href="{}" target="_blank">{}</a>'.format(WikiUtils.GetWikiLink(wikiPage), origPhrase)
            else:
                replacementInfo["replacementText"] = WikiUtils.GetWikiTextLink(wikiPage, origPhrase)
            replacementInfo["placeholder"] = "~~placeholder:{}:~~".format(placeholderCount)
            replacementList.append(replacementInfo)

            placeholderCount += 1
            input = re.sub(r'\b{}\b'.format(re.escape(replacementInfo["originalText"])), replacementInfo["placeholder"], input, 0, re.I)

    for replacementInfo in replacementList:
        input = re.sub(re.escape(replacementInfo["placeholder"]), replacementInfo["replacementText"], input, 0, re.I)

    return input



# statUpdateUtils.addWikiLinksToText = function(input) {
#     var phraseList = statUpdateUtils.splitTextIntoPhrases(input, Config.maxWordsInArticleTitleSearch);
#     var replacementList = [];
#     var replacementInfo = {};
#     var placeholderCount = 0;
#
#     for (var pIdx in phraseList) {
#         var origPhrase = phraseList[pIdx];
#         var normalizedPhrase = statUpdateUtils.getStemmedAndNormalizedString(origPhrase);
#         var wIdx = statUpdateUtils.normalizedWikiPageList.indexOf(normalizedPhrase);
#         if (wIdx >= 0) {
#             var url = mw.util.wikiGetlink(statUpdateUtils.wikiPageList[wIdx]);
#             replacementInfo = {};
#             replacementInfo["originalHtml"] = origPhrase;
#             replacementInfo["replacementHtml"] = "<a href=\"" + url + "\" title=\"" + statUpdateUtils.escapeHtml(statUpdateUtils.wikiPageList[wIdx]) + "\">" + statUpdateUtils.escapeHtml(origPhrase) + "</a>";
#             replacementInfo["placeholder"] = "~~placeholder:" + placeholderCount + ":~~";
#             replacementList.push(replacementInfo);
#             placeholderCount++;
#
#             var regExp = new RegExp(statUpdateUtils.escapeRegExp(replacementInfo["originalHtml"]), 'g');
#             input = input.replace(regExp, replacementInfo["placeholder"]);
#         }
#     }
#
#     for (var idx in replacementList) {
#         replacementInfo = replacementList[idx];
#         var regExp = new RegExp(statUpdateUtils.escapeRegExp(replacementInfo["placeholder"]), 'g');
#         input = input.replace(regExp, replacementInfo["replacementHtml"]);
#     }
#
#     return input;
# };
#
#
# statUpdateUtils.getStemmedAndNormalizedString = function(input) {
#     var stringMapping = statUpdateUtils.getStemmedAndNormalizedStringMapping(input);
#     return stringMapping.map(function(i){return i.normalizedWord;}).join(" ");
# };
#
#
# statUpdateUtils.getStemmedAndNormalizedStringMapping = function(input) {
#     var inputWordList = input.split(/\b/);
#
#     var wordMapping = [];
#     var count = 0;
#     var start = false;
#     var curWord = "";
#     var first = true;
#     var wordInfo = {};
#
#     for (var idx in inputWordList) {
#         var word = inputWordList[idx];
#         if (word.search(/^[^a-zA-Z0-9'\-]+$/) === 0) {
#             if (count > 0) {
#                 wordInfo = {};
#                 wordInfo.origWord = inputWordList.slice(start, start + count).join("");
#                 wordInfo.normalizedWord = curWord.toLowerCase();
#                 if (statUpdateUtils.normalizedExactMatchWordList.indexOf(wordInfo.normalizedWord) == -1)
#                     wordInfo.normalizedWord = statUpdateUtils.stemWord(wordInfo.normalizedWord);
#                 wordMapping.push(wordInfo);
#             }
#
#             start = false;
#             count = 0;
#             curWord = "";
#             continue;
#         }
#         if (word.search(/^['\-]+$/) === 0) {
#             if (start === false)  start = parseInt(idx);
#             count++;
#             continue;
#         }
#
#         if (start === false)  start = parseInt(idx);
#         curWord += word;
#         count++;
#     }
#
#     if (count > 0) {
#         wordInfo = {};
#         wordInfo.origWord = inputWordList.slice(start, start + count + 1).join("");
#         wordInfo.normalizedWord = curWord.toLowerCase();
#         if (statUpdateUtils.normalizedExactMatchWordList.indexOf(wordInfo.normalizedWord) == -1)
#             wordInfo.normalizedWord = statUpdateUtils.stemWord(wordInfo.normalizedWord);
#         wordMapping.push(wordInfo);
#     }
#
#     return wordMapping;
# };












# Example Rule List
# ruleList = [
#     { 'id': 'name', 'op': 'contains', 'val': 'Tornadian', },
#     { 'id': 'weaponType', 'op': '==', 'val': 4, },
# ]

def SearchObjectListUsingSimpleRules(dataList, ruleList):
    rtnList = [ obj for obj in dataList if TestObjectAgainstRuleList(obj, ruleList) ]
    return rtnList

def TestObjectAgainstRuleList(object, ruleList):
    rtnVal = True
    try:
        for rule in ruleList:
            if 'operator' not in rule:  rule['operator'] = rule['op']
            if 'value' not in rule:  rule['value'] = rule['val']
            rtnVal = rtnVal and ResolveRuleForObject(object, rule)
    except:
        return False

    return rtnVal



# Example RuleSet
# ruleSet = {
#     'condition': 'AND',
#     'rules': [
#         { 'id': 'name', 'operator': 'contains', 'value': 'orbital' },
#         { 'condition': 'OR', 'rules': [
#             { 'id': 'weaponType', 'operator': 'equal', 'value': 0, },
#             { 'id': 'weaponType', 'operator': 'equal', 'value': 4, },
#         ] }
#     ]
# }

def SearchObjectListUsingRuleset(dataList, ruleSet):
    rtnList = [ obj for obj in dataList if TestObjectAgainstRuleset(obj, ruleSet) ]
    return rtnList


def TestObjectAgainstRuleset(object, ruleSet):
    rtnVal = False
    if ruleSet['condition'] == 'AND':
        rtnVal = True

    for rule in ruleSet['rules']:
        if 'rules' in rule:
            ruleVal = TestObjectAgainstRuleset(object, rule)
        else:
            ruleVal = ResolveRuleForObject(object, rule)

        if ruleSet['condition'] == 'AND':
            rtnVal = rtnVal and ruleVal
        else:
            rtnVal = rtnVal or ruleVal
    return rtnVal


switcher = {
    '=': (lambda v1, v2: v1 == v2),
    '==': (lambda v1, v2: v1 == v2),
    '!=': (lambda v1, v2: v1 != v2),
    '=!': (lambda v1, v2: v1 != v2),
    '<': (lambda v1, v2: v1 < v2),
    '<=': (lambda v1, v2: v1 <= v2),
    '=<': (lambda v1, v2: v1 <= v2),
    '>': (lambda v1, v2: v1 > v2),
    '>=': (lambda v1, v2: v1 >= v2),
    '=>': (lambda v1, v2: v1 >= v2),
    'equal': (lambda v1, v2: v1 == v2),
    'not_equal': (lambda v1, v2: v1 != v2),
    'in': (lambda v1, v2: v2.find(v1) >= 0 if v2 else False),
    'in_list': (lambda v1, v2: v2 in v1 if v1 else False),
    'not_in_list': (lambda v1, v2: v2 not in v1 if v1 else True),
    'not_in': (lambda v1, v2: v2.find(v1) == -1 if v2 else True),
    'begins_with': (lambda v1, v2: v1.find(v2) == 0 if v1 else False),
    'not_begins_with': (lambda v1, v2: v1.find(v2) != 0 if v1 else True),
    'contains': (lambda v1, v2: v1.find(v2) >= 0 if v1 else False),
    'not_contains': (lambda v1, v2: v1.find(v2) == -1 if v1 else True),
    'ends_with': (lambda v1, v2: v1.find(v2) == len(v1) - len(v2) if v1 else False),
    'not_ends_with': (lambda v1, v2: v1.find(v2) != len(v1) - len(v2) if v1 else True),
    'is_empty': (lambda v1, v2: False if v1 else True),
    'is_not_empty': (lambda v1, v2: True if v1 else False),
    'is_null': (lambda v1, v2: v1 is None),
    'is_not_null': (lambda v1, v2: v1 is not None),
    'less': (lambda v1, v2: v1 < v2),
    'less_or_equal': (lambda v1, v2: v1 <= v2),
    'greater': (lambda v1, v2: v1 > v2),
    'greater_or_equal': (lambda v1, v2: v1 >= v2),
    'between': (lambda v1, v2: v1 >= v2[0] and v1 <= v2[1]),
    'not_between': (lambda v1, v2: v1 < v2[0] or v1 > v2[1]),
}


def ResolveRuleForObject(object, rule):
    from SFIWikiBotLib import ItemUtils
    from SFIWikiBotLib import ShipUtils

    value1 = None
    if rule['id'] in object:
        value1 = NormalizeString(object[rule['id']])
    elif rule['id'] == 'ItemUtils.IsBeamWeapon':
        value1 = ItemUtils.IsBeamWeapon(object)
    elif rule['id'] == 'ItemUtils.IsItemHidden':
        value1 = ItemUtils.IsItemHidden(object)
    elif rule['id'] == 'ItemUtils.IsItemNprExclusive':
        value1 = ItemUtils.IsItemNprExclusive(object)
    elif rule['id'] == 'ItemUtils.GetItemRange':
        value1 = ItemUtils.GetItemRange(object)
    elif rule['id'] == 'ItemUtils.GetItemDps':
        value1 = ItemUtils.GetItemDps(object)
    elif rule['id'] == 'ItemUtils.GetItemDpsIncludingEffectDamage':
        value1 = ItemUtils.GetItemDpsIncludingEffectDamage(object)
    elif rule['id'] == 'ItemUtils.GetItemDpe':
        value1 = ItemUtils.GetItemDpe(object)
    elif rule['id'] == 'ItemUtils.GetItemDpeIncludingEffectDamage':
        value1 = ItemUtils.GetItemDpeIncludingEffectDamage(object)
    elif rule['id'] == 'ItemUtils.GetWeaponEffectName':
        v = ItemUtils.GetWeaponEffectName(object)
        value1 = NormalizeString(v if v else "None")
    elif rule['id'] == 'ItemUtils.GetShieldEffectName':
        v = ItemUtils.GetShieldEffectName(object)
        value1 = NormalizeString(v if v else "None")
    elif rule['id'] == 'ItemUtils.GetItemEffectTime':
        value1 = ItemUtils.GetItemEffectTime(object)
    elif rule['id'] == 'ItemUtils.GetItemSource':
        value1 = NormalizeString(ItemUtils.GetItemSource(object))
    elif rule['id'] == 'ItemUtils.GetItemSkillName':
        value1 = NormalizeString(ItemUtils.GetItemSkillName(object))
    elif rule['id'] == 'ItemUtils.GetItemAugType':
        value1 = NormalizeString(ItemUtils.GetItemAugType(object))
    elif rule['id'] == 'ItemUtils.GetItemSkillLevel':
        value1 = ItemUtils.GetItemSkillLevel(object)
    elif rule['id'] == 'ItemUtils.GetItemDamageType':
        value1 = NormalizeString(ItemUtils.GetItemDamageType(object) or '')
    elif rule['id'] == 'ItemUtils.GetItemDescription':
        value1 = NormalizeString(ItemUtils.GetItemDescription(object))
    elif rule['id'] == 'ItemUtils.ItemDisplayStatBPLocation':
        value1 = NormalizeString(ItemUtils.ItemDisplayStatBPLocation(object))
    elif rule['id'] == 'ItemUtils.GetItemPurchasePrice':
        value1 = ItemUtils.GetItemPurchasePrice(object)
    elif rule['id'] == 'ShipUtils.GetShipPurchasePrice':
        value1 = ShipUtils.GetShipPurchasePrice(object)
    elif rule['id'] == 'ShipUtils.GetMaxSpeedForShip':
        value1 = ShipUtils.GetMaxSpeedForShip(object)
    elif rule['id'] == 'ShipUtils.ShipCanBeBoughtByPlayers':
        value1 = ShipUtils.ShipCanBeBoughtByPlayers(object)
    elif rule['id'] == 'ShipUtils.GetTypeForShip':
        value1 = NormalizeString(ShipUtils.GetTypeForShip(object))
    elif rule['id'] == 'ShipUtils.IsShipHidden':
        value1 = ShipUtils.IsShipHidden(object)
    elif rule['id'] == 'ShipUtils.GetRaceForShip':
        value1 = NormalizeString(ShipUtils.GetRaceForShip(object))
    elif rule['id'] == 'ItemUtils.GetRaceForItem':
        value1 = NormalizeString(ItemUtils.GetRaceForItem(object))
    elif rule['id'] == 'ItemUtils.GetItemTotalDamagePerVolley':
        value1 = ItemUtils.GetItemTotalDamagePerVolley(object)

    if 'degrees.' in rule['id'].lower() and value1 is None:
        prop = rule['id'].split('.', 1)[1]
        if prop in object:
            value1 = object[prop] * 30

    if 'percent.' in rule['id'].lower() and value1 is None:
        prop = rule['id'].split('.', 1)[1]
        if prop in object:
            value1 = object[prop] * 100

    value2 = NormalizeString(rule['value'])

    func = switcher.get(rule['operator'], (lambda v1, v2: None))
    try:
        rtnVal = func(value1, value2)
    except:
        rtnVal = False

    return rtnVal
