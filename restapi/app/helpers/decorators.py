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


def dev_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if g.ENV != 'DEV':
            return response_error("Access deny!") 
        return f(*args, **kwargs)
    return wrap
