import json
from datetime import timedelta

from django.contrib.auth.password_validation import validate_password, get_password_validators
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django_rest_passwordreset.models import get_password_reset_token_expiry_time, clear_expired, \
    get_password_reset_lookup_field, ResetPasswordToken
from django_rest_passwordreset.serializers import PasswordTokenSerializer
from django_rest_passwordreset.signals import reset_password_token_created, pre_password_reset, post_password_reset

from rest_framework import status
from rest_framework.exceptions import ValidationError
# from postmarker.models import status
# from requests import Response
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from api.middlewares.custome_middleware import CustomException
from api.models import User
from api.serializers.user_serializer import UserSerializer, EmailSerializer
from api.utils.utils import get_tokens_for_user
from datn import settings


class LoginView(GenericAPIView):
    authentication_classes = ()

    def post(self, request):
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)

        if not username:
            raise CustomException('No username')
        if not password:
            raise CustomException('No username')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)

            status_code = status.HTTP_200_OK

            access = get_tokens_for_user(user)
            user_dict = {'auth_token': access}
            res = user_dict

        else:
            raise CustomException('invalid_email_or_pass')
        return Response(res, status=status_code)


class LogoutView(GenericAPIView):
    permission_classes = []

    def get(self, request):
        logout(request)
        token = request.auth
        token.blacklist()
        return Response({'status': 'OK'})


class RegisterView(GenericAPIView):
    authentication_classes = ()

    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email', None)
        username = data.get('username', None)
        password = data.get('password', None)
        if email is None:
            raise CustomException('missing_fields', 'Missing email field')
        if User.objects.filter(email=email).first():
            raise CustomException('email_existed', 'Email already exists')
        user = User.objects.create_user(username=username, password=password, email=email)
        user_serializer = UserSerializer(instance=user, data=data, partial=True)
        if user_serializer.is_valid(raise_exception=False):
            user_serializer.save()

        return Response(user_serializer.data)


HTTP_USER_AGENT_HEADER = getattr(settings, 'DJANGO_REST_PASSWORDRESET_HTTP_USER_AGENT_HEADER', 'HTTP_USER_AGENT')
HTTP_IP_ADDRESS_HEADER = getattr(settings, 'DJANGO_REST_PASSWORDRESET_IP_ADDRESS_HEADER', 'REMOTE_ADDR')


class ResetPasswordRequestToken(GenericAPIView):
    """
    An Api View which provides a method to request a password reset token based on an e-mail address

    Sends a signal reset_password_token_created when a reset token was created
    """
    serializer_class = EmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        # before we continue, delete all existing expired tokens
        password_reset_token_validation_time = get_password_reset_token_expiry_time()

        # datetime.now minus expiry hours
        now_minus_expiry_time = timezone.now() - timedelta(hours=password_reset_token_validation_time)

        # delete all tokens where created_at < now - 24 hours
        clear_expired(now_minus_expiry_time)

        # find a user by email address (case insensitive search)
        users = User.objects.filter(**{'{}__iexact'.format(get_password_reset_lookup_field()): email})

        active_user_found = False

        # iterate over all users and check if there is any user that is active
        # also check whether the password can be changed (is useable), as there could be users that are not allowed
        # to change their password (e.g., LDAP user)
        for user in users:
            if user.eligible_for_reset():
                active_user_found = True

        # No active user found, raise a validation error
        # but not if DJANGO_REST_PASSWORDRESET_NO_INFORMATION_LEAKAGE == True
        if not active_user_found and not getattr(settings, 'DJANGO_REST_PASSWORDRESET_NO_INFORMATION_LEAKAGE', False):
            raise CustomException('does_not_exists')

        # last but not least: iterate over all users that are active and can change their password
        # and create a Reset Password Token and send a signal with the created token
        for user in users:
            if user.eligible_for_reset():
                # define the token as none for now
                token = None

                # check if the user already has a token
                if user.password_reset_tokens.all().count() > 0:
                    # yes, already has a token, re-use this token
                    token = user.password_reset_tokens.all()[0]
                else:
                    # no token exists, generate a new token
                    token = ResetPasswordToken.objects.create(
                        user=user,
                        user_agent=request.META.get(HTTP_USER_AGENT_HEADER, ''),
                        ip_address=request.META.get(HTTP_IP_ADDRESS_HEADER, ''),
                    )
                # send a signal that the password token was created
                # let whoever receives this signal handle sending the email for the password reset
                reset_password_token_created.send(sender=self.__class__, instance=self, reset_password_token=token)
        # done
        return Response({'status': 'OK'})


class ResetPasswordConfirm(GenericAPIView):
    """
    An Api View which provides a method to reset a password based on a unique token
    """
    throttle_classes = ()
    authentication_classes = ()
    serializer_class = PasswordTokenSerializer

    def post(self, request, *args, **kwargs):
        request_data = json.loads(request.body)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data['password']
        token = serializer.validated_data['token']

        # get token validation time
        password_reset_token_validation_time = get_password_reset_token_expiry_time()

        # find token
        reset_password_token = ResetPasswordToken.objects.filter(key=token).first()

        if reset_password_token is None:
            raise CustomException('password_changed')

        # check expiry date
        expiry_date = reset_password_token.created_at + timedelta(hours=password_reset_token_validation_time)

        if timezone.now() > expiry_date:
            # delete expired token
            reset_password_token.delete()
            return Response({'status': 'Failed', 'message': 'Link expired'}, status=status.HTTP_400_BAD_REQUEST)

        # change users password (if we got to this code it means that the user is_active)
        if reset_password_token.user.eligible_for_reset():
            pre_password_reset.send(sender=self.__class__, user=reset_password_token.user)
            try:
                # validate the password against existing validators
                validate_password(
                    password,
                    user=reset_password_token.user,
                    password_validators=get_password_validators(settings.AUTH_PASSWORD_VALIDATORS)
                )
            except ValidationError as e:
                # raise a validation error for the serializer
                raise CustomException('validation_error', e.messages)

            reset_password_token.user.set_password(password)

            name = request_data.get('name', None)
            if name is not None:
                reset_password_token.user.name = name
            phone = request_data.get('phone', None)
            if phone is not None:
                reset_password_token.user.phone = phone
            reset_password_token.user.save()
            post_password_reset.send(sender=self.__class__, user=reset_password_token.user)

        # Delete all password reset tokens for this user
        ResetPasswordToken.objects.filter(user=reset_password_token.user).delete()

        return Response(UserSerializer(reset_password_token.user).data)
