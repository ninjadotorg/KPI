#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import json
import time
import calendar
import hashlib

from fractions import Fraction
from datetime import datetime
from flask import g

def is_valid_email(email):
	if email is not None:
		email = email.lower()
		if re.match("^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$", email) != None:
			return True
	return False


def is_valid_password(password):
	if len(password) >= 3:
		return True
	return False


def is_valid_name(name):
	if len(name.strip()) == 0:
		return False
	return True


def is_valid_event(data):
	if 'txId' in data and 'txStatus' in data and 'events' in data:
		return True
	return False


def parse_date_to_int(input):
	delta = input - datetime.now()
	return delta.seconds


def isnumber(s):
   try:
	 float(s)
	 return True
   except ValueError:
	 try: 
	   Fraction(s)
	   return True
	 except ValueError: 
	   return False


def formalize_description(desc):
	if desc is None or len(desc.strip()) == 0:
		return desc
		
	desc = desc.strip()
	if desc[len(desc)-1] != '.':
		desc = "{}.".format(desc)

	return desc


def parse_str_to_array(shake_user_ids):
	if shake_user_ids is None:
		return []
	try:
		data = json.loads(shake_user_ids)
		if isinstance(data, list):
			return data
		return []
	except Exception as ex:
		print str(ex)
		return []


def parse_shakers_array(shakers):
	if shakers is None:
		return []
	try:
		shaker_ids = []
		for shaker in shakers:
			shaker_ids.append(shaker.shaker_id)	
		return shaker_ids
	except Exception as ex:
		print(str(ex))
		return []

	
def parse_date_string_to_timestamp(date_str):
	dt_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ').strftime('%s')
	return int(dt_obj)


def local_to_utc(t):
	secs = time.mktime(t)
	return calendar.timegm(time.gmtime(secs))


def utc_to_local(t):
	secs = calendar.timegm(t)
	return time.localtime(secs)


def current_milli():
	return int(round(time.time() * 1000))


def second_to_strftime(seconds, format = '%b %d %Y %I:%M:%S %p'):
    # '%Y-%m-%d %H:%M:%S'
	return datetime.fromtimestamp(seconds).strftime(format)


def now_to_strftime(format = '%b %d %Y %I:%M:%S %p'):
	return datetime.now().strftime(format)


def is_equal(a, b):
	if a is None or b is None:
		return False

	delta = 0.00003 # 1 cent
	if abs(a - b) <= delta:
		return True

	return False


def render_unsubscribe_url(user_id, passphase):
	code = hashlib.md5('{}{}'.format(user_id, passphase)).hexdigest()
	return "ninja.org/unsubscribe?token={}&id={}".format(code, user_id)


def render_generate_link(match_id, uid):
	return "?match={}&ref={}".format(match_id, uid)