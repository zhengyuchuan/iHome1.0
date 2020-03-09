from . import api
from flask import request,jsonify,current_app,session
from ihome.utils.response_code import RET
from ihome import redis_store, constants
import re
from ihome.models import User,db
from sqlalchemy.exc import IntegrityError


@api.route("/users", methods=["POST"])
def register():
    """
    用户注册
    :parameter:手机号、短信验证码、密码、确认密码
    :return:
    """
    req_dict = request.get_json()
    mobile = req_dict.get("mobile")
    sms_code = req_dict.get("sms_code")
    password = req_dict.get("password")
    password2 = req_dict.get("password2")

    # 判断参数是否完整
    if not all([mobile, sms_code, password, password2]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 判断手机号格式
    if not re.match(r'1[34578]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")
    if password != password2:
        return jsonify(errno=RET.PARAMERR, errmsg="两次密码不一致")

    # 从redis中取出短信验证码
    try:
        real_sms_code = redis_store.get("sms_code_%s" % mobile)
        real_sms_code = real_sms_code.decode("utf-8")
    except Exception as E:
        current_app.logger.error(E)
        return jsonify(errno=RET.DBERR, errmsg="redis数据库异常")

    # 判断短信验证码是否过期
    if real_sms_code is None:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码失效")

    # 比对短信验证码
    if real_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码错误")

    # 删除redis中短信验证码
    try:
        redis_store.delete("sms_code_%s" % mobile)
    except Exception as E:
        current_app.logger.error(E)

    # 判断用户手机号是否注册过(利用保存重复数据时，数据库会抛异常)
    user = User(name=mobile, phone_num=mobile)
    user.password_hash = password
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        # 表示手机号出现重复值，已注册过
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg="手机号已存在")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="mysql数据库异常")

    # 创建session，保存登录状态
    session["name"] = mobile
    session["mobile"] = mobile
    session["user_id"] = user.id

    return jsonify(errno=RET.OK, errmsg="注册成功！")


@api.route("/sessions", methods=["POST"])
def login():
    """
    用户登录
    :param : 手机号，密码
    :return: json
    """
    # 获取参数
    req_dict = request.get_json()
    mobile = req_dict.get("mobile")
    password = req_dict.get("password")

    # 参数完整校验
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 手机号的格式
    if not re.match(r'1[34578]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")

    # 判断错误次数是否超过限制，如果超过限制，则5分钟内不能在此尝试
    user_ip = request.remote_addr  # 用户ip
    try:
        access_num = redis_store.get("access_num_%s" % user_ip)
        if access_num:
            access_num = access_num.decode("utf-8")
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_num is not None and int(access_num)>=constants.LOGIN_ERROR_MAX_TIMES:
            return jsonify(errno=RET.REQERR, errmsg="错误次数过多，请稍后尝试")
    try:
        user = User.query.filter_by(phone_num=mobile).first()
    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg="mysql数据库错误")
    if user is None or not user.check_password(password):
        # 如果验证失败，保存验证次数，返回信息
        try:
            redis_store.incr("access_num_%s" % user_ip)
            redis_store.expire("access_num_%s" % user_ip, constants.LOGIN_ERROR_TIME)
        except Exception as e:
            current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="用户名或密码错误")

    # 如果验证成功，保存登录状态
    session["name"] = user.name
    session["mobile"] = user.phone_num
    session["user_id"] = user.id

    return jsonify(errno=RET.OK, errmsg="登录成功")


@api.route("/session", methods=["GET"])
def check_login():
    """检查登录状态"""
    name = session.get("name")
    if name is not None:
        return jsonify(errno=RET.OK, errmsg="true", data={"name":name})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg="false")


@api.route("/session", methods=["DELETE"])
def logout():
    """登出"""
    csrf_token = session.get("csrf_token")
    session.clear()
    session["csrf_token"] = csrf_token
    return jsonify(errno=RET.OK, errmsg="OK")






