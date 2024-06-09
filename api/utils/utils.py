import pathlib
import random
from datetime import datetime
import os
import uuid
import re

from PIL import Image
from django.core.files.storage import default_storage

from api.models.tag import Tag
from api.models.token import SlidingToken
from config import thumb_size, thumbs_dir
from datn.settings import MEDIA_ROOT


def str_to_bool(_str):
    _str = _str.strip().lower()
    if _str == 'true':
        return True
    else:
        return False


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
    list_question = [
        f'What is {str(symbol)}?',
        f'What to fill in {str(symbol)}?',
        f'The value of {str(symbol)}:'
    ]
    return list_question.pop(random.randint(0, len(list_question)-1))


def update_tags(tags):
    existed_tags = Tag.objects.filter(tag_name__in=tags)
    existed_tags_values = existed_tags.values_list('tag_name', flat=True)
    _tags = list(set(tags) - set(existed_tags_values))
    tag_objects = [Tag(tag_name=tag) for tag in _tags]
    Tag.objects.bulk_create(tag_objects, unique_fields=['tag_name'], ignore_conflicts=True)

    return Tag.objects.filter(tag_name__in=tags)


def try_parse_datetime(inp: str):
    if not inp:
        return None
    try:
        inp = datetime.strptime(inp, "%Y-%m-%d %H:%M:%S")
        return inp
    except ValueError:
        pass

    try:
        inp = datetime.strptime(inp, "%Y-%m-%d")
    except ValueError:
        inp = None

    return inp


def no_accent_vietnamese(s):
    s = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
    s = re.sub(r'[ÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪ]', 'A', s)
    s = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', s)
    s = re.sub(r'[ÈÉẸẺẼÊỀẾỆỂỄ]', 'E', s)
    s = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
    s = re.sub(r'[ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ]', 'O', s)
    s = re.sub(r'[ìíịỉĩ]', 'i', s)
    s = re.sub(r'[ÌÍỊỈĨ]', 'I', s)
    s = re.sub(r'[ùúụủũưừứựửữ]', 'u', s)
    s = re.sub(r'[ƯỪỨỰỬỮÙÚỤỦŨ]', 'U', s)
    s = re.sub(r'[ỳýỵỷỹ]', 'y', s)
    s = re.sub(r'[ỲÝỴỶỸ]', 'Y', s)
    s = re.sub(r'[Đ]', 'D', s)
    s = re.sub(r'[đ]', 'd', s)
    s = re.sub(r'[&]', 'and', s)
    return s


def replace_vietnamese(value: str):
    if not value:
        return None
    new_value = no_accent_vietnamese(
        re.sub(r"[-()\"#/@;:<>{}`+=~|.!?,]", "",
               value.replace('\n', '').replace('\t', '').replace(' ', '').strip().lower()))

    return new_value


def save_profile_image(profile_img_dir, file, user=None, org=None):
    path = save_file(profile_img_dir, file)
    image = Image.open(path)
    image.thumbnail((thumb_size, thumb_size))
    ext = file.content_type.split('/')[-1]

    thumb_dir = os.path.join(MEDIA_ROOT, profile_img_dir, thumbs_dir)
    if not os.path.exists(thumb_dir):
        os.makedirs(thumb_dir)

    thumb_path = os.path.join(thumb_dir, 'thumb_' + str(uuid.uuid4()) + '.' + ext)
    image.save(thumb_path)

    if user is not None:
        user.profile_path = path
        user.thumb_profile_path = thumb_path
        user.save()


def get_path(path):
    if path is not None:
        if MEDIA_ROOT not in path:
            parts = pathlib.Path(path).parts
            path_split = [MEDIA_ROOT]
            path_split.extend(parts[1:])
            path = '/'.join(path_split)

    return path
