#!/usr/bin/env python3

import os
import subprocess
import sys
import requests
from requests.auth import HTTPBasicAuth 
import json
from urllib.parse import urljoin

AUTH_TOKEN_FILE = "token"

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def validate_schema(target, schema, prefix=""):
    for (key, value) in schema.items():
        if not key in target:
            raise ValueError("Expected to find '%s%s' value in config" % (prefix, key))

        if not type(value) == type(target[key]):
            raise ValueError("Expected '%s%s' to be %s, found %s" % (prefix, key, type(value).__name__, type(target[key]).__name__))

        if isinstance(value, dict):
            validate_schema(target[key], schema[key], "%s." % key)


def login(url, user, password):
    url_login = url + "/json/login"
    pload = {"payload":{"name":user, "password":password}}
    headers = {'content-type': 'application/json'}

    ret_value = None

    r = requests.post(url_login, data=json.dumps(pload), headers=headers)
    #print(r.text)
    #print(r.status_code)

    if r.status_code == 200:
        resp_dict = r.json()
        toFile(AUTH_TOKEN_FILE, resp_dict['payload']['authToken'])
        ret_value = resp_dict['payload']
    else:
        print("Login return HHTP-Status: " + r.status_code)

    return ret_value


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
        
    return uuid


def getTarball(path, url, uuid, cookies=None):
    url_tarball = url + '/tarball/' + uuid
    url_params = {}
    auth_params = {}

    r = requests.get(url_tarball, params=url_params, auth=auth_params, cookies=cookies)
    #print(r.text)
    #print(r.status_code)

    if r.status_code == 200:
        file_to_write = os.path.join(path, uuid[0:10] + '.tar.gz')
        toFileBinary(file_to_write, r.content)


def getAuthToken():
    token = None
    try:
        with open(AUTH_TOKEN_FILE, 'r') as f:
            token = f.read()
            f.close()
            return token
    except IOError:
        pass
    return token


def toFile(filename, content):
    with open(filename, 'w') as f:
        f.write(content)
        f.close()

def toFileBinary(filename, content):
    with open(filename, 'wb') as f:
        f.write(content)
        f.close()
