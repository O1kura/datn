import os
import random
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
from api.models.submission import Submission, File, Question, QuestionData, Category, Data
from api.serializers.image_serializer import ListSubmissionSerializer, QuestionSerializer, FileSerializer
from api.utils.text_extraction import text_line_extraction
from api.utils.upload_utils import upload_files
from api.utils.utils import save_file, generate_question
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
        question = Question(file=file)
        question.save()
        ran = random.randint(0, len(file.data_set.all()) - 1)
        ans = file.data_set.all()[ran]
        q = generate_question(ans)
        question_q = QuestionData(value=q, category=Category.cau_hoi.value, question=question, data=ans)
        question_q.save()
        question_a = QuestionData(value=ans.normalized_value, category=Category.dap_an.value, question=question,
                                  data=ans)
        question_a.save()
        for data in file.data_set.all():
            symbol_box = data.symbol_box
            box = data.box

            cv2.rectangle(img, (box['x'], box['y']),
                          (box['rect_x'], box['rect_y']),
                          box['filled_color'], -1)
            cv2.rectangle(img, (box['x'], box['y']),
                          (box['rect_x'], box['rect_y']),
                          box['border_color'], box['border_thickness'])

            cv2.putText(img, data.symbol, (symbol_box['text_x'], symbol_box['text_y']),
                        symbol_box['text_font'], symbol_box['text_scale'], symbol_box['color'],
                        symbol_box['text_thickness'])

            if data == ans:
                continue

            question_c = QuestionData(value=data.normalized_value, category=Category.cau_tra_loi.value,
                                      question=question,
                                      data=ans)
            question_c.save()

        is_success, buffer = cv2.imencode("." + file.extension, img)
        io_buf = BytesIO(buffer)
        io_buf.name = 'temp.' + file.extension
        img_path = save_file('question', io_buf)

        question.path = img_path
        question.save(update_fields={'path'})

        return Response(QuestionSerializer(intance=question).data)


class ListFilesView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        files = File.objects.filter(submission__user=request.user)
        data = FileSerializer(instance=files, many=True).data
        return Response(data)
