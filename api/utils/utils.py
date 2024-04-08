import os
import uuid
from django.core.files.storage import default_storage
from api.models.token import SlidingToken
from datn.settings import MEDIA_ROOT


def get_tokens_for_user(user, lifetime=None):
    token = SlidingToken.for_user(user, lifetime)
    return str(token)


def save_file(dir_path, file):
    ext = file.name.split('.')[-1]
    dir_path_with_media_root = os.path.join(MEDIA_ROOT, dir_path)

    if not os.path.exists(dir_path_with_media_root):
        os.makedirs(dir_path_with_media_root)

    filename = str(uuid.uuid4()) + '.' + ext

    path = os.path.join(dir_path, filename)
    file_name = default_storage.save(path, file)
    return MEDIA_ROOT + '/' + file_name


def generate_question(ans):
    return str(ans.symbol) + 'la gi?'
