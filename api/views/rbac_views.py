from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework import status
# from postmarker.models import status
# from requests import Response
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from api.middlewares.custome_middleware import CustomException
from api.utils.utils import get_tokens_for_user


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