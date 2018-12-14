#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import json

from sqlalchemy import func
from flask_jwt_extended import get_jwt_identity
from functools import wraps
from flask import request, g
from app import db
from app.helpers.response import response_error
from app.models import User
from app.constants import Role


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


def hr_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        current_user = get_jwt_identity() 
        user = db.session.query(User).filter(User.email==func.binary(current_user)).first()

        if user is None or \
            user.role is None or \
            user.role.name != Role['HR']:
			return response_error("Access deny!")

        return f(*args, **kwargs)
    return wrap


def both_hr_and_amdin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        current_user = get_jwt_identity() 
        user = db.session.query(User).filter(User.email==func.binary(current_user)).first()
        
        if user is None or \
            user.role is None or \
            user.role.name is None:
            return response_error("Access deny!")

        if user.role.name != Role['HR'] and \
            user.role.name != Role['Administrator']:
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