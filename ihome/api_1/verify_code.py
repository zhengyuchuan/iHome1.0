from . import api
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store, constants
from flask import current_app,jsonify, make_response, request
from ihome.utils.response_code import RET
from ihome.models import User
import random
from ihome.libs.yuntongxun.SendTemplateSMS import CCP


# GET 127.0.0.1/api/v1/image_codes/<image_code_id>
@api.route("/image_codes/<image_code_id>")
def get_image_code(image_code_id):
    """
    获取图片验证码
    :param image_code_id: 图片验证码编号
    :return: 验证码图片 or 错误信息
    """
    # 业务逻辑处理
    # 生成验证码图片,返回名字、真实文本、图片数据
    name, text, image_data = captcha.generate_captcha()
    # 将真实值与编号保存在redis中,选用str类型,并设置有效期
    try:
        redis_store.setex("image_code_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as E:
        # 记录日志
        current_app.logger.error(E)
        return jsonify(error=RET.DBERR, errmsg="image saving is error")

    # 返回图片
    resp = make_response(image_data)
    resp.headers["Content-Type"] = "image/jpg"
    return resp


# GET /api/v1/sms_codes/<mobile>?image_code=xxxx&image_code_id=xxx
@api.route("/sms_codes/<re(r'1[34578]\d{9}'):mobile>")
def get_sms_code(mobile):
    """获取短信验证码"""
    image_code = request.args.get("image_code")
    image_code_id = request.args.get("image_code_id")
    # 校验参数
    if not all([image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')
    # 从redis中取出真实的图片验证码，进行对比
    try:
        real_image_code = redis_store.get("image_code_%s" % image_code_id)
        real_image_code = real_image_code.decode("utf-8")
    except Exception as E:
        current_app.logger.error(E)
        return jsonify(errno=RET.DBERR, errmsg="redis数据库异常")
    # 判断图片验证码是否过期
    if not real_image_code:
        # 表示图片验证码没有或者过期
        return jsonify(errno=RET.NODATA, errmsg="图片验证码失效")
    # 删除redis中图片验证码，防止用户使用同一个图片验证码验证多次
    try:
        redis_store.delete("image_code_%s" % image_code_id)
    except Exception as E:
        current_app.logger.error(E)

    if real_image_code.lower() != image_code.lower():
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码错误")
    # 判断这个手机号有没有发送短信的记录，有则认为发送频繁
    try:
        send_flag = redis_store.get("sms_code_%s" % mobile)
    except Exception as E:
        current_app.logger.error(E)
    else:
        if send_flag is not None:
            return jsonify(errno=RET.REQERR, errmsg="请求过于频繁，请60s后重试")

    # 判断手机号是否注册过，如果否则发送短信，并保存真实的短信验证码
    try:
        user = User.query.filter_by(phone_num=mobile).first()
    except Exception as E:
        current_app.logger.error(E)
    else:
        if user is not None:
            return jsonify(errno=RET.DATAEXIST, errmsg="手机号已存在")
    # 生成短信验证码
    sms_code = "%6d" % random.randint(0,999999)
    # 将短信验证码保存在redis中
    try:
        redis_store.setex("sms_code_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 保存发送给这个手机号的记录，防止用户在60s内再次发送短信(value值随便设置)
        redis_store.setex("send_sms_code_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
    except Exception as E:
        current_app.logger.error(E)
        return jsonify(errno=RET.DBERR, errmsg="保存短信验证码异常")
    # 发送短信
    try:
        ccp = CCP()
        result = ccp.sendTemplateSMS(mobile, [sms_code, int(constants.SMS_CODE_REDIS_EXPIRES)/69], 1)
    except Exception as E:
        current_app.logger.error(E)
        return jsonify(errno=RET.THIRDERR, errmsg="发送异常")
    if result:
        # 发送成功
        return jsonify(errno=RET.OK, errmsg="发送成功")
    else:
        return jsonify(errno=RET.THIRDERR, errmsg="发送失败")








