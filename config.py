import redis
class Config(object):
    """配置信息"""
    SECRET_KEY = ''
    SQLALCHEMY_DATABASE_URI = 'mysql://你的用户名:你的密码@localhost:3306/ihome'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # redis
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    # 使用flask_session将session保存在redis中
    SESSION_TYPE = 'redis'
    # 指定redis实例，即连接好的对象。注意：如果不指定decode，取出来的值都为Byte类型
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 对cookie中session_id进行隐藏
    SESSION_USER_SIGNER = True
    # session保存时限，单位：秒
    PERMANENT_SESSION_LIFETIME = 86400



class DevelopConfig(Config):
    """开发模式的配置信息"""
    DEBUG = True


class ProduceConfig(Config):
    """生产环境下的配置信息"""
    pass

config_map = {
    "develop":DevelopConfig,
    "produce":ProduceConfig
}
