import subprocess, os, sys
from config import run_port, log_file
if not os.path.exists(os.path.dirname(log_file)):
    os.makedirs(os.path.dirname(log_file))

python_path = sys.executable
dir_path = os.path.dirname(python_path)
gunicorn_path = os.path.join(dir_path, 'gunicorn')
# celery_path = os.path.join(dir_path, 'celery')

main_process = subprocess.run(
    gunicorn_path + ' datn.wsgi -w 3 --access-logfile - -b 0.0.0.0:%s -t 3000' %  run_port,
    shell=True)
