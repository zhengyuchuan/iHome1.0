from . import api
from ihome.utils.commons import login_required
from ihome.utils.response_code import RET
from flask import g, current_app, jsonify, request, session
from ihome.models import Area, House, Facility, HouseImage, User
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


@api.route("/houses", methods=["GET"])
@login_required
def get_passcard():
    """判断用户是否进行过实名认证，是否可以发布新房源"""
    user_id = g.user_id
    try:
        user = User.query.filter_by(id=user_id).first()
        real_name = user.real_name
        id_card = user.id_card
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="mysql数据库错误")
    if real_name and id_card:
        return jsonify(errno=RET.OK, errmsg="OK")


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

    # 将第一次上传的图片设置为index主图
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



@api.route("/user/houses", methods=["GET"])
@login_required
def get_user_house():
    """获取信息页用户发布过的房源信息"""
    user_id = g.user_id

    try:
        # 这样可以同时判断用户id是否存在
        user = User.query.get(user_id)
        houses  =user.houses
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取数据失败")
    houses_list = []
    if houses:
        for house in houses:
            houses_list.append(house.to_basic_dict())
    return jsonify(errno=RET.OK, errmsg="OK", data={"houses":houses_list})


@api.route("/houses/index")
def get_house_index():
    """主页幻灯片获取房源基本信息，不需要登录也可以访问"""
    # 首先从缓存中获取房源数据，如果没有，再去数据库中查询，然后保存至缓存中
    try:
        ret = redis_store.get("home_page_data")
    except Exception as e:
        current_app.logger.error(e)
        ret = None
    if ret:
        ret = ret.decode("utf-8")
        current_app.logger.info("hit house index info redis")
        return '{"errno":"0", "errmsg":"OK", "data":%s}' % ret, 200, {"Content-Type": "application/json"}
    else:
        try:
            # 查询数据库，返回订单量最大的最多5条数据
            houses = House.query.order_by(House.order_count.desc()).limit(constants.HOME_PAGE_MAX_HOUSES)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="获取数据失败")
        if not houses:
            return jsonify(errno=RET.NODATA, errmsg="查询无数据")

        houses_list  =[]
        for house in houses:
            # 如果房源主图还没有设置，那么就跳过，不予展示
            if not house.index_image_url:
                continue
            houses_list.append(house.to_basic_dict())

        json_houses = json.dumps(houses_list)
        try:
            redis_store.setex("home_page_data", constants.INDEX_PAGE_DATA_REDIS_EXPIRES, json_houses)
        except Exception as e:
            current_app.logger.error(e)
        return '{"errno":"0", "errmsg":"OK", "data":%s}' % json_houses, 200, {"Content-Type": "application/json"}


@api.route("/houses/<int:house_id>", methods=["GET"])
def get_house_detail(house_id):
    """显示房源详细信息"""
    # 如果查看的是房主本人，那么不予显示预定按钮。将user_id与房主id查询结果发给前端，让前端判断
    user_id = session.get("user_id", "-1")

    if not house_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        ret = redis_store.get("house_info_%s" % house_id)
    except Exception as e:
        current_app.logger.error(e)
        ret = None
    if ret:
        current_app.logger.info("hit house info redis")
        ret = ret.decode("utf-8")
        return '{"errno":"0", "errmsg":"OK", "data":{"user_id":%s, "house":%s}}' % (user_id, ret), 200, {"Content-Type": "application/json"}

    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

    if not house:
        return jsonify(errno=RET.NODATA, errmsg="房源不存在")

    try:
        house_data = house.to_full_dict()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

    json_house = json.dumps(house_data)
    try:
        redis_store.setex("house_info_%s" %house_id, constants.DETAIL_PAGE_DATA_REDIS_EXPIRES, json_house)
    except Exception as e:
        current_app.logger.error(e)
    resp = '{"errno":"0", "errmsg":"OK", "data":{"user_id":%s, "house":%s}}' % (user_id, json_house), 200, {"Content-Type":"application/json"}
    return resp