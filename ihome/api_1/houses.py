from . import api
from ihome.utils.commons import login_required
from ihome.utils.response_code import RET
from flask import g, current_app, jsonify, request, session
from ihome.models import Area, House, Facility, HouseImage
from ihome import db, constants, redis_store
from ihome.utils.image_storage import storage
import json


@api.route("/areas")
def get_area_info():
    """获取城区信息"""
    # 先从redis中取数据，如果没有，再去mysql中取数据

    try:
        resp_json = redis_store.get("area_info")
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json:
            current_app.logger.info("hit redis area_info")
            return  resp_json, 200, {"Content-Type":"application/json"}

    try:
        area_li = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="mysql数据库错误")
    area_dict = []
    for area in area_li:
        area_dict.append(area.to_dict())

    resp_dict = dict(errno=RET.OK, errmsg="OK", data=area_dict)
    resp_json = json.dumps(resp_dict)

    # 将城区信息存入到redis中
    try:
        redis_store.setex("area_info", constants.AREA_INFO_REDIS_CACHE_EXPIRES, resp_json)
    except Exception as e:
        current_app.logger.error(e)

    return resp_json, 200, {"Content-Type":"application/json"}


@api.route("/houses/info", methods=["POST"])
@login_required
def save_house_info():
    """
    保存要发布的房源的信息
    :param:{
        title
        price
        area_id
        address
        room_count
        acreage
        unit
        capacity
        beds
        deposit
        min_days
        max_days
        facility
    }
    :return:
    """
    house_dict = request.get_json()
    title = house_dict.get("title")  # 名称标题
    price = house_dict.get("price")  # 单价
    area_id = house_dict.get("area_id")  # 所属城区
    address = house_dict.get("address")  # 详细地址
    room_count = house_dict.get("room_count")  # 房间数
    acreage = house_dict.get("acreage")  # 总面积
    unit = house_dict.get("unit")  # 布局
    capacity = house_dict.get("capacity")  # 容纳人数
    beds = house_dict.get("beds")  # 床数量
    deposit = house_dict.get("deposit")  # 押金
    min_days = house_dict.get("min_days")  # 最小入住天数
    max_days = house_dict.get("max_days")  # 最大入住天数
    # facility = house_dict.get("facility")  # 房屋名称标题

    # 校验参数
    if not all([title,price,area_id,address,room_count,acreage,unit,capacity,beds,deposit,min_days,max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    try:
        price = int(float(price) * 100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 判断城区id是否存在
    try:
        area = Area.query.get(area_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")
    if not area:
        return jsonify(errno=RET.NODATA, errmsg="城区信息有误")

    # 保存房屋信息
    house = House(
        user_id=g.user_id,
        area_id=area_id,
        title=title,
        price=price,
        address=address,
        room_count=room_count,
        acreage=acreage,
        unit=unit,
        capacity=capacity,
        beds=beds,
        deposit=deposit,
        min_days=min_days,
        max_days=max_days,
    )

    # 处理房屋设施信息
    facilities = house_dict.get("facility")
    if facilities:
        try:
            facilities_list = Facility.query.filter(Facility.id.in_(facilities)).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询数据库异常")
        if facilities_list:
            # 保存设施信息
            house.facilities = facilities_list
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据库异常")

    return jsonify(errno=RET.OK, errmsg="保存成功", data={"house_id":house.id})



@api.route("/houses/image", methods=["POST"])
@login_required
def save_house_image():
    """
    保存房屋的图片
    :return:
    """
    image_file = request.files.get("house_image")
    house_id = request.form.get("house_id")

    # 判断参数完整性
    if not all([image_file, house_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 判断house_id正确性
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if not house:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")

    # 上传图片至七牛云
    image_data = image_file.read()
    try:
        file_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="保存图片失败")

    # 保存图片url至数据库中
    house_image = HouseImage(house_id=house_id, url=file_name)
    db.session.add(house_image)

    if not house.index_image_url:
        house.index_image_url = file_name
        db.session.add(house)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存图片数据异常")

    image_url = constants.QINIU_URL_DOMAIN + file_name
    return jsonify(errno=RET.OK, errmsg="OK", data={"image_url":image_url})






