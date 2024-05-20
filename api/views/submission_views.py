import datetime
import json
import os
import random
import string
import uuid
from io import BytesIO
from itertools import chain
from os import path

import cv2
from PIL import Image
from django.core.files.storage import default_storage
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.middlewares.custome_middleware import CustomException
from api.models.submission import Submission, File, Question, QuestionData, Category, Data
from api.models.tag import Tag
from api.serializers.data_serializer import DataSerializer
from api.serializers.file_serializer import ListSubmissionSerializer, QuestionSerializer, FileSerializer, \
    FileDetailSerializer
from api.utils.add_watermark import add_watermark
from api.utils.text_extract2 import convertOpenCVImagetoPIL, convertPILtoOpenCVImage
from api.utils.text_extraction import text_line_extraction
from api.utils.upload_utils import upload_files
from api.utils.utils import save_file, generate_question, update_tags, try_parse_datetime, replace_vietnamese
from config import watermark_img_path
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
        success_ids, error_file_names, submission_id = upload_files(self.request)

        return Response({'submission_ids': submission_id, 'error_file_name': error_file_names, 'file_ids': success_ids})


class GenerateQuestionView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, file_id):
        file = File.objects.filter(id=file_id).first()
        if not file:
            raise CustomException('file_does_not_exist', 'File not found')
        if file.submission.user != request.user:
            raise CustomException('permission_denied', 'Not your file')
        img = cv2.imread(file.path)
        question = Question(file=file, display_name=file.display_name, user=file.submission.user)
        question.save()
        question.tags.set(file.tags.all())

        # Get random 4 data from its data_set
        data = file.data_set.filter(deleted_at__isnull=True).all()
        random_data = random.sample(list(data), 4)

        list_value = []
        duplicate_idx = []

        # Get the unique when format value
        for idx, item in enumerate(random_data):
            if item.normalized_value not in list_value:
                list_value.append(replace_vietnamese(item.normalized_value))
            else:
                duplicate_idx.append(idx)

        # Change the duplicate value data from index to another one
        for data_index in duplicate_idx:
            unique_data_set = [x for x in data if replace_vietnamese(x.normalized_value) not in list_value]
            if len(unique_data_set) == 0:
                random_data.pop(data_index)
                continue
            random_index = random.randint(0, len(unique_data_set) - 1)
            random_data[data_index] = unique_data_set[random_index]
            list_value.append(random_data[data_index].normalized_value)

        ran = random.randint(0, 3)
        ans = random_data[ran]
        question_a = QuestionData(value=ans.normalized_value, category=Category.dap_an.value, question=question)
        question_a.save()

        uppercase_letters = list(string.ascii_uppercase)
        for data in random_data:
            symbol = uppercase_letters.pop(0)
            symbol_box = data.symbol_box
            box = data.box

            cv2.rectangle(img, (box['x'], box['y']),
                          (box['rect_x'], box['rect_y']),
                          box['filled_color'], -1)
            cv2.rectangle(img, (box['x'], box['y']),
                          (box['rect_x'], box['rect_y']),
                          box['border_color'], box['border_thickness'])

            cv2.putText(img, symbol, (symbol_box['text_x'], symbol_box['text_y']),
                        symbol_box['text_font'], symbol_box['text_scale'], symbol_box['color'],
                        symbol_box['text_thickness'])

            if data == ans:
                q = generate_question(symbol)
                question_q = QuestionData(value=q, category=Category.cau_hoi.value, question=question)
                question_q.save()
            else:
                question_c = QuestionData(value=data.normalized_value, category=Category.cau_tra_loi.value,
                                          question=question)
                question_c.save()

        img = convertOpenCVImagetoPIL(img)
        watermark_img = Image.open(watermark_img_path)
        img = add_watermark(img, watermark_img)

        is_success, buffer = cv2.imencode("." + file.extension, convertPILtoOpenCVImage(img))
        io_buf = BytesIO(buffer)
        io_buf.name = 'temp.' + file.extension
        img_path = save_file('question', io_buf)

        question.path = img_path
        question.save(update_fields={'path'})

        return Response(QuestionSerializer(instance=question).data)


class ListFilesView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        files = File.objects.filter(submission__user=request.user)

        params = request.query_params
        display_name = params.get('display_name', None)
        tags = params.getlist('tags', None)
        start = params.get('from', None)
        end = params.get('to', None)

        start = try_parse_datetime(start)
        end = try_parse_datetime(end)

        if display_name:
            files = files.filter(Q(display_name__contains=display_name)|Q( name__contains=display_name))
        if start:
            files = files.filter(created_at__gte=start)
        if end:
            files = files.filter(created_at__lte=end)
        if tags:
            if not isinstance(tags, list):
                tags = [tags]
            files = files.filter(tags__tag_name__in=tags)
        data = FileSerializer(instance=files, many=True).data
        return Response(data)


class FileDetailView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, file_id):
        file = File.objects.filter(id=file_id).first()
        if not file:
            raise CustomException('file_does_not_exist', 'File not found')
        if file.submission.user != request.user:
            raise CustomException('permission_denied', 'Not your file')

        res = FileDetailSerializer(instance=file).data
        return Response(res)

    def delete(self, request, file_id):
        file = File.objects.filter(id=file_id).first()
        if not file:
            raise CustomException('file_does_not_exist', 'File not found')
        if file.submission.user != request.user:
            raise CustomException('permission_denied', 'Not your file')

        file.delete()
        return Response({'status': "ok"})

    def put(self, request, file_id):
        file = File.objects.filter(id=file_id).first()
        if not file:
            raise CustomException('file_does_not_exist', 'File not found')
        if file.submission.user != request.user:
            raise CustomException('permission_denied', 'Not your file')

        data = json.loads(request.body)
        display_name = data.get('display_name', None)
        tags = data.get('tags', [])
        if isinstance(tags, list):
            tags_model = update_tags(tags)
            file.tags.set(tags_model)

        if display_name:
            file.display_name = display_name
            file.save()

        res = FileDetailSerializer(instance=file).data
        return Response(res)


class FileImageView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, file_id):
        file = File.objects.filter(id=file_id).first()
        if not file:
            raise CustomException('file_does_not_exist', 'File not found')
        if file.submission.user != request.user:
            raise CustomException('permission_denied', 'Not your file')

        image = file.get_content_image()
        return HttpResponse(image, content_type='image/JPEG')


class DataDetailView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, file_id, data_id):
        file = File.objects.filter(id=file_id).first()
        if not file:
            raise CustomException('file_does_not_exist', 'File not found')
        if file.submission.user != request.user:
            raise CustomException('permission_denied', 'Not your file')
        data = file.data_set.filter(id=data_id, deleted_at__isnull=True).first()
        if not data:
            raise CustomException('data_does_not_exits', 'Data not found')
        body = json.loads(request.body)
        value = body.get('value', None)
        if value:
            data.normalized_value = value
            data.save()

            return Response(DataSerializer(instance=data).data)

        return Response({'status': 'ok'})

    def delete(self, request, file_id, data_id):
        file = File.objects.filter(id=file_id).first()
        if not file:
            raise CustomException('file_does_not_exist', 'File not found')
        if file.submission.user != request.user:
            raise CustomException('permission_denied', 'Not your file')
        data = file.data_set.filter(id=data_id).first()
        if not data:
            raise CustomException('data_does_not_exits', 'Data not found')

        data.deleted_at = timezone.now()
        data.save()

        return Response({'status': 'ok'})


class RestoreDataDetailView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, file_id, data_id):
        file = File.objects.filter(id=file_id).first()
        if not file:
            raise CustomException('file_does_not_exist', 'File not found')
        if file.submission.user != request.user:
            raise CustomException('permission_denied', 'Not your file')
        data = file.data_set.filter(id=data_id).first()
        if not data:
            raise CustomException('data_does_not_exits', 'Data not found')

        data.normalized_value = data.last_ocr_value
        data.deleted_at = None
        data.save()

        return Response(DataSerializer(instance=data).data)
