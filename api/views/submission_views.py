from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models.submission import Submission
from api.serializers.image_serializer import ListSubmissionSerializer
from api.utils.upload_utils import upload_files


class ListSubmissionView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer(self, *args, **kwargs):
        return ListSubmissionSerializer(*args, **kwargs)
    #
    def get_queryset(self):
        # return list_submissions(self)
        return Submission.objects.all()

    def post(self, request):
        success_ids, error_file_names = upload_files(request)

        return Response({'success_submission_ids': success_ids, 'error_file_name': error_file_names})
