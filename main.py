import subprocess, os, sys
from config import run_port, workers, log_file
if not os.path.exists(os.path.dirname(log_file)):
    os.makedirs(os.path.dirname(log_file))

python_path = sys.executable
dir_path = os.path.dirname(python_path)
gunicorn_path = os.path.join(dir_path, 'gunicorn')
# celery_path = os.path.join(dir_path, 'celery')

main_process = subprocess.run(
    gunicorn_path + ' django_fastdoc.wsgi -w %s --access-logfile - -b 0.0.0.0:%s -t 3000' % (workers, run_port),
    shell=True)