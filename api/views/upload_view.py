import base64
import json
import uuid
from io import BytesIO

from PIL import Image
from django.http import HttpResponse
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from api.middlewares.custome_middleware import CustomException
from api.serializers.image_serializer import ImageSerializer
from api.utils.text_extract2 import text_extraction, convertPILtoOpenCVImage, convertOpenCVImagetoPIL
from api.utils.text_extraction import text_line_extraction, get_file_content


class UploadView(GenericAPIView):
    def post(self, request):
        images = request.FILES.getlist('images', [])
        list = []
        for image in images:
            # data_bytes = base64.b64decode(image)
            # file = BytesIO(data_bytes)
            image = Image.open(image)

            open_cv_image = convertPILtoOpenCVImage(image)

            # res = text_extraction(open_cv_image)
            res, res2 = text_line_extraction(open_cv_image)
            print(res)
            img = convertOpenCVImagetoPIL(res2)
            image = get_file_content(img)
            list.append(image)
            # ser = ImageSerializer(res2)
        return HttpResponse(list, content_type='image/JPEG')

