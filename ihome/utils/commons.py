from werkzeug.routing import BaseConverter
from flask import session, jsonify, g
from ihome.utils.response_code import RET
import functools


# 定义正则转换器
class ReConverter(BaseConverter):
    """"""
    def __init__(self, url_map, regex):
        super().__init__(url_map)
        # 保存正则表达式
        self.regex = regex


# 定义验证登录状态的装饰器
def login_required(view_func):

    @functools.wraps(view_func)  # 不改变被装饰函数的属性，比如__name__、__doc__
    def wrapper(*args, **kwargs):
        # 判断用户登录状态
        # 如果已登录，执行视图函数
        user_id = session.get("user_id")
        if user_id:
            # g对象来传递参数
            g.user_id = user_id
            return view_func(*args, **kwargs)
        # 如果未登录，返回未登录的信息
        else:
            return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    return wrapper
