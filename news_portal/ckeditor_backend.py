from django.core.files.storage import default_storage
from django.core.files import File
import os
from PIL import Image

from ckeditor_uploader import utils
from ckeditor_uploader.backends import get_backend
import ckeditor_uploader.utils

def create_thumbnail(file_path):
    thumbnail_size = (75, 75)
    try:
        image = Image.open(default_storage.open(file_path))
        size = image.size
        image.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
        thumbnail_filename = utils.get_thumb_filename(file_path)
        image_file = File(utils.create_tmp())
        image.save(image_file, format='JPEG', quality=90)
        return default_storage.save(thumbnail_filename, image_file)
    except IOError:
        return None
