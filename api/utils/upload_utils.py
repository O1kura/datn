import uuid
from io import BytesIO

from PIL import Image

from api.models.submission import Submission, File
from api.utils.utils import save_file


def upload_files(request):
    # data_type = request.headers.get('content_type')
    success_ids = []
    error_file_names = []
    uploaded_files = request.FILES.getlist('files', [])
    files = []
    for file_data in uploaded_files:
        data_bytes = file_data.read()
        file = BytesIO(data_bytes)
        file.name = file_data.name
        file.size = len(file.read())
        files.append(file)

    submission = Submission(user=request.user)
    submission.save()
    for file in files:
        file_names = file.name.split('.')
        ext = file_names[-1].lower()

        if ext not in ('jpg', 'png'):
            error_file_names.append(file.name)
        else:
            path = save_file('origin', file)[1:]
            f = File(name=file.name, extension=ext, path=path, size=file.size, submission=submission )
            f.save()
            success_ids.append(f.submission_id)

    return success_ids, error_file_names
