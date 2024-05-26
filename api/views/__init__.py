from django.http import Http404
from rest_framework.response import Response
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework.exceptions import ValidationError as ErrorValid, AuthenticationFailed, NotFound
from rest_framework.exceptions import PermissionDenied, NotAuthenticated, ValidationError
from binascii import Error as ImageError

from rest_framework_simplejwt.exceptions import InvalidToken
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django_rest_passwordreset.serializers import EmailSerializer
import traceback

from api.middlewares.custome_middleware import CustomException

error_messages = {
    'bad_request': "Bad request",
    'unique': "Duplicate entry",  # send with object_name field: email, company, building
    'read_img_failed': "Read image failed",
    'foreign_key_constraint_fails': "Foreign key constraint fails",
    'permission_denied': "Permission denied",
    'not_authenticated': "Not authenticated",
    'invalid_email_or_pass': "Invalid email or password",
    'change_pass_required': "You must change your password",
    'payment_required': "Payment required",
    'too_common_pass': "This password is too common",
    'invalid_pass': "Invalid password",
    'delete_yourself': "Can not delete yourself",
    'can_not_delete_last_admin': "Can not delete last admin",
    'incorrect_pass': "Incorrect password",
    'email_existed': 'Email already exists',
    'password_changed': "You've changed password",  # only 1 time for reset password
    'does_not_exists': "Object does not exist",
    'file_not_found': "File not found",
    'image_not_found': "Image not found",
    'required': "This field is required",
    'missing_fields': "Missing fields",
    '404_not_found': "404 not found",
    'archived': 'Object is archived',
    'invalid_validation_data': 'Invalid validation data',
    'invalid_token': 'Invalid token',
    'expired_token': 'Token is expired',
    'not_ready_to_retry': 'File is not ready to retry',
    'file_ext_not_allowed': 'This file extension is not allowed',
    'invalid_files_length': 'Invalid files length',
    'contain_unsupported_file_type': "Contain unsupported file type",
    'can_not_open_file': 'Can not open file',
    'invalid_auth_token': 'Invalid auth token',
    'authentication_failed': 'Authentication failed',
    'unsupported_file_format': 'Unsupported file format',
    'missing_required_field': 'Missing required field'
}


def custom_exception_handler(exc, context):
    message = None
    label = getattr(exc, 'label', None)
    status_code = 400

    if isinstance(exc, IntegrityError):
        code = exc.args[0]
        if code == 1452:
            error_code = 'foreign_key_constraint_fails'
        else:
            error_code = 'bad_request'
    elif isinstance(exc, ObjectDoesNotExist):
        error_code = 'does_not_exists'
    elif isinstance(exc, PermissionDenied):
        error_code = 'permission_denied'
        status_code = 403
    elif isinstance(exc, ImageError):
        error_code = 'read_img_failed'
    elif isinstance(exc, CustomException):
        error_code = exc.error_code
        message = exc.message
    elif isinstance(exc, NotAuthenticated) or isinstance(exc, InvalidToken) \
           or isinstance(exc, AuthenticationFailed):
        error_code = 'not_authenticated'
        status_code = 401
    elif isinstance(exc, NotFound):
        error_code = '404_not_found'
    elif isinstance(exc, Http404):
        error_code = 'expired_token'
    elif isinstance(exc, ValidationError):
        if 'serializer' in exc.args[0] and isinstance(exc.args[0].serializer, EmailSerializer):
            error_code = 'does_not_exists'
        else:
            error_code = 'bad_request'
            error_mgs = []
            for key, val in exc.detail.items():
                if key == 'password':
                    error_code = 'invalid_password'
                label = key
                if isinstance(val, list):
                    error_code = val[0].code
                    mgs = ', '.join([str(i) for i in val])
                    error_mgs.append(mgs)
                elif isinstance(val, dict):
                    for k, v in val.items():
                        if isinstance(v, list):
                            mes = str(k) + ': ' + ', '.join([str(i) for i in v])
                        else:
                            mes = str(v)
                        error_mgs.append(mes)

                else:
                    mgs = str(val)
                    error_mgs.append(mgs)

            message = '\n'.join(error_mgs)
        error_list = getattr(exc, 'ValidationError', None)
        if error_list is not None:
            message = ''
            for v in exc.error_list:
                message += " ".join([str(i) for i in v])
    elif isinstance(exc, ErrorValid):
        error_code = 15
        message = exc.detail['password'][0]
    elif isinstance(exc, FileNotFoundError):
        error_code = 'file_not_found'
    else:
        error_code = 'bad_request'

    if error_code == 'invalid' and label == 'password':
        error_code = 'too_common_pass'
    if error_code == 'permission_denied' or error_code == 'not_authenticated':
        status_code = 403
    if error_code == 'does_not_exists' or error_code == 'expired_token':
        status_code = 404
    if message is None:
        message = error_messages.get(error_code)
    data = {'Context': str(context), 'Exception': str(exc), 'message': message, 'code': error_code,
            'label': label}

    return Response(data, status_code)
