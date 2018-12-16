# -*- coding: utf-8 -*-
from decimal import *

# ReviewType
Type = {
	'People': 'people',
	'Team': 'team',
	'Company': 'company'
}


# RoleType
Role = {
	'Administrator': 'administrator',
	'HR': 'hr'
}


UPLOAD_MAX_FILE_SIZE = 2 * 1024 * 1024
UPLOAD_ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png']
BASE_IMAGE_URL = 'https://storage.googleapis.com/cryptosign/images/performance_review/'

ROLES = ['administrator', 'hr']