from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from api.views import rbac_views, user_views, upload_view, submission_views

urlpatterns = [
    path('login', rbac_views.LoginView.as_view()),
    path('login', rbac_views.LogoutView.as_view()),
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user', user_views.UserView.as_view()),
    path('extract', upload_view.UnauthorizedUploadView.as_view()),
    path('submissions', submission_views.ListSubmissionView.as_view()),
    path('register', rbac_views.RegisterView.as_view()),
    path('file/<int:file_id>/generate',submission_views.GenerateQuestionView.as_view())
]