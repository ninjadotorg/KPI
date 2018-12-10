
from __future__ import division
import os
import re
import app.constants as CONST

from flask import g
from PIL import Image
from app.helpers.utils import current_milli


def delete_file(path_file):
    try:
        os.remove(path_file)    
    except Exception as ex:
        print(str(ex))


def handle_upload_file(file, file_name=None):
    if file_name is None:
        file_name = formalize_filename(file.filename)
    saved_path = os.path.join(g.UPLOAD_DIR, file_name)
    file.save(saved_path)
    return file_name, saved_path


def handle_crop_image(image_name, saved_path):
    try:
        im = Image.open(saved_path)
        width, heigth = im.size
        ratio = CONST.IMAGE_CROP_WIDTH / width
        resize_img = im.resize((int(width * ratio), int(heigth * ratio)), Image.ANTIALIAS)

        width, height = resize_img.size

        crop_x = (width - CONST.IMAGE_CROP_WIDTH)/2
        crop_y = (height - CONST.IMAGE_CROP_HEIGHT)/2
        crop_w = (width + CONST.IMAGE_CROP_WIDTH)/2
        crop_h = (height + CONST.IMAGE_CROP_HEIGHT)/2

        crop_img = resize_img.crop((crop_x, crop_y, crop_w, crop_h))

        crop_saved_path = saved_path.replace(image_name, "crop_{}".format(image_name))
        crop_img.save(crop_saved_path)
        return saved_path, crop_saved_path
        
    except Exception as ex:
        print(str(ex))
        return ex


def formalize_filename(filename):
    # '/[^a-z0-9\_\-\.]/'
    file_name = re.sub(r'[^A-Za-z0-9\_\-\.]+', '_', filename)
    file_name = file_name.replace('.', '-' + str(current_milli()) + '.')
    return file_name


def validate_extension(filename, arr_ext):
    if filename is not None:
        d = os.path.splitext(filename)
        if len(d) > 0:
            ext = d[len(d) - 1]
            return ext in arr_ext
    return False
