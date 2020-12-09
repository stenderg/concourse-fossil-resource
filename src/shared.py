#!/usr/bin/env python3

import os
import subprocess
import sys
import requests
from requests.auth import HTTPBasicAuth 
import json
from urllib.parse import urljoin

AUTH_TOKEN_FILE = "token"
AUTH_TOKEN_FILE_COOKIE = "cookie"

def eprint(*args, **kwargs):
    #print(*args, file=sys.stderr, **kwargs)
    pass

def validate_schema(target, schema, prefix=""):
    for (key, value) in schema.items():
        if not key in target:
            raise ValueError("Expected to find '%s%s' value in config" % (prefix, key))

        if not type(value) == type(target[key]):
            raise ValueError("Expected '%s%s' to be %s, found %s" % (prefix, key, type(value).__name__, type(target[key]).__name__))

        if isinstance(value, dict):
            validate_schema(target[key], schema[key], "%s." % key)


def login(url, postData):
    if checkLogin(url):
        return getAuthToken()

    url_login = url + "/json/login"
    #pload = {"payload":{"name":user, "password":password}}
    #pload = {"payload":{"name":"anonymous", "anonymousSeed":str(user)+password, "password":password}}
    #eprint(pload)
    headers = {'content-type': 'application/json'}

    token = None

    r = requests.post(url_login, data=json.dumps(postData), headers=headers)
    #print(r.text)
    #print(r.status_code)

    if r.status_code == 200:
        resp_dict = r.json()
        eprint(resp_dict)
        if 'payload' in resp_dict:
            token = resp_dict['payload']['authToken']
            toFile(AUTH_TOKEN_FILE, token)

            cookie = {resp_dict['payload']['loginCookieName']:resp_dict['payload']['authToken']}
            toFile(AUTH_TOKEN_FILE_COOKIE, json.dumps(cookie))
        else:
            delAuthTokens()

    else:
        delAuthTokens()
        print("Login return HTTP-Status: " + r.status_code)

    return token

def loginAnonym(url):
    if checkLogin(url):
        return getAuthToken()

    url_login = url + "/json/anonymousPassword"
    headers = {'content-type': 'application/json'}

    token = None

    r = requests.post(url_login, headers=headers)
    eprint(r.text)
    #print(r.status_code)

    if r.status_code == 200:
        resp_dict = r.json()
        seed = resp_dict['payload']['seed']
        password = resp_dict['payload']['password']
        pload = {"payload":{"name":"anonymous", "anonymousSeed":str(seed)+password, "password":password}}
        token = login(url, pload)

        # second try...
        if token is None:
            token = login(url, pload)
    else:
        print("Login return HTTP-Status: " + r.status_code)

    return token

def checkLogin(url):
    url_whoami = url + "/json/whoami"
    headers = {'content-type': 'application/json'}
    pload = {"payload":{"name":"nobody", "capabilities":"o", "authToken":getAuthToken()}}

    r = requests.post(url_whoami, data=json.dumps(pload), headers=headers)
    eprint(r.text)

    if r.status_code == 200:
        resp_dict = r.json()
        if 'payload' in resp_dict:
            eprint(resp_dict['payload']['authToken'])
            if resp_dict['payload']['authToken'] != None and resp_dict['payload']['authToken'] != 'null':
                return True
    
    delAuthTokens()
    return False


def getTimeline(url, tag, token):
    url_timeline = url + '/json/timeline/checkin'
    url_params = {'tag': tag}
    uuid = None

    #token = getAuthToken()
    if token is not None:
        #pload = {"payload":{"authToken":token}}
        url_params['authToken'] = token 

    r = requests.get(url_timeline, params=url_params)

    if r.status_code == 200:
        resp_dict = r.json()

        #eprint(resp_dict.keys())
        if 'payload' in resp_dict:
            #eprint(resp_dict['payload']['timeline'][0]['uuid'])
            uuid = resp_dict['payload']['timeline'][0]['uuid']
        
    if uuid is None:
        delAuthTokens()

    return uuid


def getTarball(path, url, uuid, cookies=None):
    url_tarball = url + '/tarball/' + uuid
    file_to_write = None
    url_params = {}
    auth_params = {}

    eprint(cookies)

    r = requests.get(url_tarball, params=url_params, auth=auth_params, cookies=cookies)
    #print(r.headers['Content-Type'])
    eprint(r.headers)

    if r.status_code == 200 and 'application' in r.headers['Content-Type'] :
        file_to_write = os.path.join(path, 'fossil.tar.gz')
        toFileBinary(file_to_write, r.content)

    return file_to_write


def getAuthToken():
    token = None
    try:
        with open(AUTH_TOKEN_FILE, 'r') as f:
            token = f.read()
            f.close()
    except IOError:
        pass
    return token

def getCookieToken():
    jsonData = None
    try:
        with open(AUTH_TOKEN_FILE_COOKIE, 'r') as f:
            jsonData = json.load(f)
            f.close()
    except IOError:
        pass
    return jsonData

def delAuthTokens():
    ## If file exists, delete it ##
    if os.path.isfile(AUTH_TOKEN_FILE):
        os.remove(AUTH_TOKEN_FILE)
    if os.path.isfile(AUTH_TOKEN_FILE_COOKIE):
        os.remove(AUTH_TOKEN_FILE_COOKIE)

def toFile(filename, content):
    with open(filename, 'w') as f:
        f.write(content)
        f.close()

def toFileBinary(filename, content):
    with open(filename, 'wb') as f:
        f.write(content)
        f.close()
