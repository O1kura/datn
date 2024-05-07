from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from api.views import rbac_views, user_views, upload_view, submission_views, question_view, admin_view


router = DefaultRouter()
router.register(r'users', admin_view.AdminUserView, basename='user')
router.register(r'files', admin_view.AdminFileView, basename='file')
router.register(r'datas', admin_view.AdminDataView, basename='data')
router.register(r'questions', admin_view.AdminQuestionView, basename='question')
router.register(r'question_datas', admin_view.AdminQuestionDataView, basename='question_data')

urlpatterns = [
    path('manage/', include(router.urls)),
    path('login', rbac_views.LoginView.as_view()),
    path('logout', rbac_views.LogoutView.as_view()),
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me', user_views.CurrentUserView.as_view()),
    path('me/change_password', user_views.ChangePassword.as_view()),
    path('password-reset', rbac_views.ResetPasswordRequestToken.as_view()),
    path('password-reset-confirm', rbac_views.ResetPasswordConfirm.as_view()),
    path('register', rbac_views.RegisterView.as_view()),

    path('extract', upload_view.UnauthorizedUploadView.as_view()),
    path('submissions', submission_views.ListSubmissionView.as_view()),

    # File and file data
    path('file', submission_views.ListFilesView.as_view()),
    path('file/<int:file_id>', submission_views.FileDetailView.as_view()),
    path('file/<int:file_id>/image', submission_views.FileImageView.as_view()),
    path('file/<int:file_id>/generate', submission_views.GenerateQuestionView.as_view()),
    path('file/<int:file_id>/<int:data_id>', submission_views.DataDetailView.as_view()),
    path('file/<int:file_id>/<int:data_id>/restore', submission_views.RestoreDataDetailView.as_view()),
    # Question and question data
    path('question', question_view.QuestionView.as_view()),
    path('question/<int:question_id>', question_view.QuestionDetailView.as_view()),
    path('question/<int:question_id>/image', question_view.QuestionImageView.as_view()),
    path('question_image/<int:question_id>', question_view.QuestionWithImageDetailView.as_view()),
    path('question/<int:question_id>/<int:question_data_id>', question_view.QuestionDataView.as_view()),
    path('question/<int:question_id>/add', question_view.AddQuestionDataView.as_view()),
]