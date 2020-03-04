from celery import Celery
from ihome.libs.yuntongxun.SendTemplateSMS import CCP


# 定义celery对象
celery_app = Celery("ihome", broker="redis://localhost:6379/1")

# 定义发送短信的异步任务
@celery_app.task
def send_sms_async(to, data, temp_id):
    ccp = CCP()
    ccp.sendTemplateSMS(to, data, temp_id)



# 开启worker：
# 1。cd到爱家租房路径
# 2。celery -A ihome.tasks.task_sms worker