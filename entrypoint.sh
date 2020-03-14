cd 爱家租房
python manage.py db init
python manage.py db migrate
celery -A ihome.tasks.task_sms worker
gunicorn -w $worker manage:app