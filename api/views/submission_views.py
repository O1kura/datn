import os
import uuid
from io import BytesIO
from os import path

import cv2
from PIL import Image
from django.core.files.storage import default_storage
from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.middlewares.custome_middleware import CustomException
from api.models.submission import Submission, File, Question
from api.serializers.image_serializer import ListSubmissionSerializer
from api.utils.text_extraction import text_line_extraction
from api.utils.upload_utils import upload_files
from api.utils.utils import save_file
from datn.settings import MEDIA_ROOT


class ListSubmissionView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer(self, *args, **kwargs):
        return ListSubmissionSerializer(*args, **kwargs)
    #
    def get_queryset(self):
        # return list_submissions(self)
        return Submission.objects.filter(user=self.request.user)

    def post(self, *args, **kwargs):
        success_ids, error_file_names = upload_files(self.request)

        return Response({'success_submission_ids': success_ids, 'error_file_name': error_file_names})


class GenerateQuestionView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, file_id):
        file = File.objects.filter(id=file_id).first()
        if not file:
            raise CustomException('file_does_not_exist', 'File not found')
        img = cv2.imread(file.path)
        res, res2 = text_line_extraction(img)

        is_success, buffer = cv2.imencode("."+file.extension, res2)
        io_buf = BytesIO(buffer)
        io_buf.name = 'temp.' + file.extension
        path = save_file('question', io_buf)

        for data in res:
            pass
        question = Question(file=file, path=path)
        question.save()
        return Response({'res': res})
