from . import api
from ihome.utils.commons import login_required
from ihome.models import Order
from flask import g, current_app, jsonify, request
from ihome.utils.response_code import RET
from ihome import constants, db
from alipay import AliPay
import os


@api.route("/orders/<int:order_id>/payment", methods=["POST"])
@login_required
def order_pay(order_id):
    """发起支付宝支付"""
    user_id = g.user_id
    # 判断订单状态
    try:
        order = Order.query.filter(Order.id==order_id, Order.user_id==user_id, Order.status=="WAIT_PAYMENT").first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    if not order:
        return jsonify(errno=RET.NODATA, errmsg="订单数据有误")

    # 创建支付宝sdk的工具对象

    app_private_key_string = open(os.path.join(os.path.dirname(__file__), "Alipay_keys/app_private_key.pem")).read()
    alipay_public_key_string = open(os.path.join(os.path.dirname(__file__), "Alipay_keys/alipay_public_key.pem")).read()
    alipay_client = AliPay(
        appid="2016101400686425",
        app_notify_url=None,  # 默认回调url
        app_private_key_string=app_private_key_string,
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2" , # RSA 或者 RSA2
        debug = True  # 默认False
    )
    order_string = alipay_client.api_alipay_trade_wap_pay(
        out_trade_no=order.id,  # 订单编号
        total_amount=str(order.amount/100.0),  # 总金额
        subject="爱家租房订单",
        return_url="http://127.0.0.1:5000/orders.html",
        notify_url=None # 可选, 不填则使用默认notify url
    )
    # 构建让用户跳转的支付链接地址
    pay_url = constants.ALIPAY_URL_PREFIX + order_string
    return jsonify(errno=RET.OK, errmsg="OK", data={"pay_url":pay_url})


@api.route("/order/payment", methods=['PUT'])
@login_required
def save_order_payment_result():
    """
    save the result of payment,and redirect to payComplete.html page. meanwhile returm the
    formType data from alipay, such as:
     /orders.html?charset=utf-8
     &out_trade_no=1
     &method=alipay.trade.wap.pay.return
     &total_amount=798.00
     &sign=aONlDGPkHCgvpF7JlzT......QW0PqhP2jMKA%3D%3D
     &trade_no=2019090322001403331000089566
     &auth_app_id=2016101300679257
     &version=1.0
     &app_id=2016101300679257
     &sign_type=RSA2
     &seller_id=2088102179436454
     &timestamp=2019-09-03+17%3A38%3A46
    当在payComplete.html点击“Go back to My Order”时, 向后端发起请求,将数据保存,订单的状态改为“待评价”
    """
    # get parameters and convert to dict
    alipay_dict = request.form.to_dict()

    # 对支付宝的数据进行分离  提取出支付宝的签名参数sign 和剩下的其他数据
    alipay_sign = alipay_dict.pop("sign") # pop(): get and pop(delete)

    app_private_key_string = open(os.path.join(os.path.dirname(__file__), "Alipay_keys/app_private_key.pem")).read()
    alipay_public_key_string = open(os.path.join(os.path.dirname(__file__), "Alipay_keys/alipay_public_key.pem")).read()

    # create alipay sdk tools object
    alipay_client = AliPay(
        appid="2016101400686425",
        app_notify_url=None,  # 默认回调url
        app_private_key_string=app_private_key_string,
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True  # 默认False
    )

    # verify the correctness of parameters with the help of tools
    # 如果确定参数是支付宝的，返回True，否则返回false
    result = alipay_client.verify(alipay_dict, alipay_sign)

    if result:
        # change the order status in database
        order_id = alipay_dict.get("out_trade_no")
        trade_no = alipay_dict.get("trade_no") # 支付宝交易的流水号

        try:
            Order.query.filter_by(id=order_id).update({"status":"WAIT_COMMENT", "trade_no":trade_no})
            db.session.commit()
        except Exception as e:
            current_app.logger.errer(e)
            db.session.rollback()

    return jsonify(errno = RET.OK, errmsg='OK')




