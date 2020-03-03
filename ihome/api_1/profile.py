from . import api
from ihome.utils.commons import login_required
from ihome.utils.response_code import RET
from flask import g, current_app, jsonify, request, session
from ihome.utils import image_storage
from ihome.models import User
from ihome import db,constants


@api.route("/users/avatar", methods=["POST"])
@login_required
def set_user_avatar():
    """
    设置用户头像
    :param:图片（多媒体表单）、用户id(g.user_id)
    :return:
    """
    user_id = g.user_id
    image_file = request.files.get("avatar")
    if image_file is None:
        return jsonify(errno=RET.PARAMERR, errmsg="未上传图片")
    image_data = image_file.read()

    # 调用七牛上传图片
    try:
        file_name = image_storage.storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传图片失败")

    # 保存文件名到数据库中
    try:
        User.query.filter_by(id=user_id).update({"avatar_url": file_name})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="保存图片失败")
    avatar_url = constants.QINIU_URL_DOMAIN + file_name
    return jsonify(errno=RET.OK, errmsg="保存成功", data={"avatar_url":avatar_url})


@api.route("/users/name", methods=["PUT"])
@login_required
def set_user_name():
    """
    设置用户名
    :return:
    """
    data_dict = request.get_json()
    user_name = data_dict.get("user_name")
    if not user_name:
        return jsonify(errno=RET.PARAMERR, errmsg="用户名不能为空")
    if len(user_name) >= 32:
        return jsonify(errno=RET.PARAMERR, errmsg="用户名过长")
    user_id = g.user_id
    # 利用数据库的唯一索引
    try:
        User.query.filter_by(id=user_id).update({"name":user_name})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="设置用户名失败")
    session["name"] = user_name
    return jsonify(errno=RET.OK, errmsg="保存成功")


@api.route("/users", methods=["GET"])
@login_required
def get_user_profile():
    """进入信息页，自动获取个人信息"""
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户信息失败")

    if user is None:
        return jsonify(errno=RET.NODATA, errmsg="无效操作")

    return jsonify(errno=RET.OK, errmsg="OK", data=user.to_dict())


@api.route("/users/auth", methods=["GET"])
@login_required
def get_user_auth():
    """获取用户的实名认证信息"""
    user_id = g.user_id

    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户实名信息失败")

    if user is None:
        return jsonify(errno=RET.NODATA, errmsg="无效操作")

    return jsonify(errno=RET.OK, errmsg="OK", data=user.to_auth_dict())


@api.route("/users/auth", methods=["POST"])
@login_required
def set_user_auth():
    """保存实名认证信息"""
    user_id = g.user_id
    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    real_name = req_data.get("real_name")
    id_card = req_data.get("id_card")

    # 参数校验
    if not all([real_name, id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 保存用户的姓名与身份证号
    try:
        # 身份信息只能保存一次
        User.query.filter_by(id=user_id, real_name=None, id_card=None).update({"real_name":real_name, "id_card":id_card})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="mysql数据库错误")
    return jsonify(errno=RET.OK, errmsg="OK")


