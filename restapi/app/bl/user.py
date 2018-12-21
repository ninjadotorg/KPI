
from __future__ import division
from flask import g
from openpyxl import load_workbook
from app.models import User

import os
import hashlib

dir_path = os.path.dirname(os.path.realpath(__file__))

def read_data():
    arr = []
    try:
        wb = load_workbook(filename = dir_path + '/staff.xlsx')
        sheet_ranges = wb['staff']
        for row in sheet_ranges.iter_rows('D2:E125'):
            name = None
            email = None
            for cell in row:    
                if cell.column == 'D':
                    name = cell.value.strip()
                if cell.column == 'E':
                    email = cell.value.strip()

            password = hashlib.md5('123456').hexdigest()
            user = User(
                name=name,
                email=email,
                password=password
            )
            arr.append(user)
    except Exception as ex:
        print(str(ex))

    return arr
    