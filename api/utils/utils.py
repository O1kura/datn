import os
import uuid
from django.core.files.storage import default_storage
from api.models.token import SlidingToken
from datn.settings import MEDIA_ROOT


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Use the first item in X-Forwarded-For (or customize as needed)
        ip = x_forwarded_for.split(',')[0]
    else:
        # If X-Forwarded-For is not present, use REMOTE_ADDR
        ip = request.META.get('REMOTE_ADDR')
    return ip


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


def generate_question(symbol):
    return str(symbol) + ' là gì?'
