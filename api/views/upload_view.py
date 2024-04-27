import base64
import json
import os
import uuid
from io import BytesIO

from PIL import Image
from django.http import HttpResponse
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from api.middlewares.custome_middleware import CustomException
from api.serializers.image_serializer import ImageSerializer
from api.utils.add_watermark import add_watermark
from api.utils.text_extract2 import text_extraction, convertPILtoOpenCVImage, convertOpenCVImagetoPIL, text_extract_3
from api.utils.text_extraction import text_line_extraction, get_file_content, text_line_extraction_2
from config import watermark_img_path
from datn.settings import BASE_DIR


class UnauthorizedUploadView(GenericAPIView):
    def post(self, request):
        image = request.FILES.get('image', None)
        if image:
            image = Image.open(image)

            open_cv_image = convertPILtoOpenCVImage(image)

            res, res2 = text_line_extraction_2(open_cv_image, get_image=True)
            # res2 = text_extraction(open_cv_image)
            img = convertOpenCVImagetoPIL(res2)

            watermark_img = Image.open(watermark_img_path)
            img = add_watermark(img, watermark_img)
            image = get_file_content(img)
            return HttpResponse(image, content_type='image/jpeg')

        raise CustomException('no image')
# class