from datetime import datetime
import os
import uuid
import re
from django.core.files.storage import default_storage

from api.models.tag import Tag
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
