#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import json

from functools import wraps
from flask import request, g
from app import db
from app.helpers.response import response_error
from app.models import User


trusted_proxies = ('127.0.0.1')
white_ips = ( '127.0.0.1' )

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        remote = request.remote_addr
        route = list(request.access_route)
        while remote not in trusted_proxies:
            remote = route.pop()

        if remote not in white_ips:
            return response_error("Access deny!")       

        return f(*args, **kwargs)
    return wrap

def whitelist(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        blacklist_path = os.path.abspath(os.path.dirname(__file__)) + '/blacklist.json'
        try:
            with open(blacklist_path) as data_file:    
                data = json.load(data_file)
            ip = request.headers['X-Real-Ip']
            print '--IP: {}'.format(ip)
            if ip is not None:
                ips = ip.split(',')
                if ips[0] in data:
                    return response_error("Access deny!")
        except Exception as ex:
            print str(ex)
        
        return f(*args, **kwargs)
    return wrap

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs): 
        if not request.headers["Uid"]:
            return response_error("Please login first!")
        else:
            try:
                uid = int(request.headers["Uid"])
                token = request.headers['Fcm-Token'] if 'Fcm-Token' in request.headers else ''
                payload = request.headers['Payload'] if 'Payload' in request.headers else ''
                user = User.find_user_with_id(uid)
                if user is None:
                    user = User(
                        id=uid,
                        fcm_token=token,
                        payload=payload
                    )
                    db.session.add(user)
                    db.session.commit()
                elif user.fcm_token != token or user.payload != payload:
                    user.payload = payload
                    user.fcm_token = token
                    db.session.commit()
            except Exception as ex:
                db.session.rollback()
                print(str(ex))

        return f(*args, **kwargs)
    return wrap

def dev_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if g.ENV != 'DEV':
            return response_error("Access deny!") 
        return f(*args, **kwargs)
    return wrap

def service_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        remote = request.remote_addr
        if "10." not in remote and remote not in white_ips:
            return response_error("Access deny!")

        return f(*args, **kwargs)
    return wrap
