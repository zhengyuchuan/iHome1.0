from config import config_map
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect
import redis
import logging
from logging.handlers import RotatingFileHandler
from ihome.utils.commons import ReConverter


db = SQLAlchemy()
# 工厂模式
redis_store = None

# 配置日志信息
# 设置日志记录等级
logging.basicConfig(level=logging.INFO)
# 创建日志记录器，指明日志保存路径，每个日志大小，保存日志文件个数上限
file_log_handler = RotatingFileHandler('logs/log', maxBytes=1024*1024*100, backupCount=10)
# 创建日志的记录格式，                 日志等级     日志信息的文件名  行数      日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局日志对象添加日志记录器
logging.getLogger().addHandler(file_log_handler)
# 设置日志记录等级
logging.basicConfig(level=logging.DEBUG)



def create_app(config_name):
    """
    创建flask应用对象
    :param config_name:str 配置模式的名字（"develop"，"produce"）
    :return:app
    """
    app = Flask(__name__)
    config_class = config_map.get(config_name)
    app.config.from_object(config_class)
    db.init_app(app)

    # 创建redis连接对象
    global redis_store
    redis_store = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT)

    # 用flask——session将数据保存到redis中
    Session(app)
    # 为flask添充csrf防护
    CSRFProtect(app)
    # 为flask添加自定义的转换器
    app.url_map.converters["re"] = ReConverter

    # 注册蓝图
    from ihome import api_1
    app.register_blueprint(api_1.api, url_prefix='/api/v1')

    # 注册提供静态文件的蓝图
    from ihome import web_html
    app.register_blueprint(web_html.html)

    return app

