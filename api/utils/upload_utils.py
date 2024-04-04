import base64
import json
import uuid
from io import BytesIO

from PIL.Image import Image


def upload_files(request):
    data_type = request.headers.get('content_type')
    print(data_type)
    success_ids = []
    error_file_names = []
    # if data_type in ['application/json', 'text/plain']:
    # data = json.loads(request.body)
    # print(data)
    # claim_form_id = data.get('claim_form_id', None)
    uploaded_files = request.FILES.getlist('files', [])
    print(uploaded_files)
    files = []
    for file_data in uploaded_files:
        # print(file_data.name)
        data_bytes = file_data.read()
        # open_cv_image = convertPILtoOpenCVImage(image)
        # data_bytes = base64.b64decode(file_data)
        file = BytesIO(data_bytes)
        # file_name = data.get('filename', str(uuid.uuid4()) + '.pdf')
        file.name = file_data.name
        file.size = len(file.read())
        # print(file.name)
        files.append(file)



    file_instances = []

    # if isinstance(request.user, User):
    #     user = request.user
    # else:
    #     user = None

    for file in files:
        # create_submission(file, folder, data, file_instances,
                          # error_file_names, integration=integration, user=user)
        print(file.name)
    for f in file_instances:
        success_ids.append(f.submission_id)

    return success_ids, error_file_names
