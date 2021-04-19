#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import uuid
import sqlite3
from SFIWikiBotLib import Config


DEFAULT_PATH = os.path.join(Config.cacheDir, 'UrlShortener')
if not os.path.exists(DEFAULT_PATH):
    os.makedirs(DEFAULT_PATH, exist_ok=True)
DEFAULT_PATH = os.path.join(DEFAULT_PATH, 'db.sqlite3')

con = sqlite3.connect(DEFAULT_PATH)
con.row_factory = sqlite3.Row



def CreateToken():
    return uuid.uuid4().hex[:20]


def UpdateJsonTokenDate(token):
    cur = con.cursor()
    sql = "UPDATE jsonList SET dateAddedTs = ? WHERE jsonToken = ?;"
    cur.execute(sql, (int(time.time()), token))
    con.commit()


def GetTokenForJson(json):
    cur = con.cursor()
    token = None

    sql = "SELECT jsonToken FROM jsonList WHERE fullJson = ?;"
    cur.execute(sql, (json,))
    result = cur.fetchone()
    try:
        token = result['jsonToken']
        UpdateJsonTokenDate(token)
        return token
    except:
        pass

    while token is None:
        token = CreateToken()
        testUrl = GetJsonForToken(token)
        if testUrl:
            token = None

    sql = "INSERT INTO jsonList (jsonToken, fullJson, dateAddedTs) VALUES (?, ?, ?);"
    cur.execute(sql, (token, json, int(time.time())))
    con.commit()

    return token


def GetJsonForToken(token):
    cur = con.cursor()
    sql = "SELECT fullJson FROM jsonList WHERE jsonToken = ?;"
    cur.execute(sql, (token,))
    result = cur.fetchone()
    try:
        rtnVal = result['fullJson']
        UpdateUrlTokenDate(token)
        return rtnVal
    except:
        pass


def UpdateUrlTokenDate(token):
    cur = con.cursor()
    sql = "UPDATE urlList SET dateAddedTs = ? WHERE urlToken = ?;"
    cur.execute(sql, (int(time.time()), token))
    con.commit()


def GetTokenForUrl(url):
    cur = con.cursor()
    token = None

    sql = "SELECT urlToken FROM urlList WHERE fullUrl = ?;"
    cur.execute(sql, (url,))
    result = cur.fetchone()
    try:
        token = result['urlToken']
        UpdateUrlTokenDate(token)
        return token
    except:
        pass

    while token is None:
        token = CreateToken()
        testUrl = GetUrlForToken(token)
        if testUrl:
            token = None

    sql = "INSERT INTO urlList (urlToken, fullUrl, dateAddedTs) VALUES (?, ?, ?);"
    cur.execute(sql, (token, url, int(time.time())))
    con.commit()

    return token


def GetUrlForToken(token):
    cur = con.cursor()
    sql = "SELECT fullUrl FROM urlList WHERE urlToken = ?;"
    cur.execute(sql, (token,))
    result = cur.fetchone()
    try:
        rtnVal = result['fullUrl']
        UpdateUrlTokenDate(token)
        return rtnVal
    except:
        pass


def InitializeTables():
    cur = con.cursor()

    sql = '''
    CREATE TABLE IF NOT EXISTS urlList (
        urlToken text NOT NULL PRIMARY KEY,
        fullUrl text NOT NULL UNIQUE,
        dateAddedTs integer
    );
    '''
    cur.execute(sql)
    con.commit()

    sql = '''
    CREATE INDEX urlListDateAdded ON urlList(dateAddedTs);
    '''
    try:
        cur.execute(sql)
        con.commit()
    except:
        pass

    sql = '''
    CREATE TABLE IF NOT EXISTS jsonList (
        jsonToken text NOT NULL PRIMARY KEY,
        fullJson text NOT NULL UNIQUE,
        dateAddedTs integer
    );
    '''
    cur.execute(sql)
    con.commit()

    sql = '''
    CREATE INDEX jsonListDateAdded ON jsonList(dateAddedTs);
    '''
    try:
        cur.execute(sql)
        con.commit()
    except:
        pass


InitializeTables()
