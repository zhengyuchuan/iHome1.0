from . import api
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store, constants
from flask import current_app,jsonify, make_response
from ihome.utils.response_code import RET



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