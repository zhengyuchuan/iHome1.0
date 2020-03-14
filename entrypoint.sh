python manage.py db init
python manage.py db migrate
celery -A ihome.tasks.task_sms worker
gunicorn -w 4 manage:app