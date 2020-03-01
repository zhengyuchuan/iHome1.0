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
        return jsonify(errno=RET.PARAMERR, errmag="未上传图片")
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


@api.route("/users/name", methods=["POST"])
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
    try:
        user = User.query.filter_by(name=user_name).first()
        if user:
            return jsonify(errno=RET.DATAEXIST, errmsg="用户名已存在")
        else:
            User.query.filter_by(id=user_id).update({"name":user_name})
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="保存图片失败")
    session["name"] = user_name
    return jsonify(errno=RET.OK, errmsg="保存成功")

