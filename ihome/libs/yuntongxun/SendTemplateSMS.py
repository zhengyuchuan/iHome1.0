# coding=utf-8
from .CCPRestSDK import REST
# import ConfigParser         #官网sdk带的，没有使用
import logging

# 账号id
accountSid = '8aaf07087051bcec01708a6d21fd212b'
# 账号Token
accountToken = 'af95fbbdd1f2483cad35b4af323bf1f0'
# 应用Id
appId = '8aaf07087051bcec01708a6d22572131'  # token请自行去官网申请
# 服务地址
serverIP = 'app.cloopen.com'
# 服务端口
serverPort = '8883'
# REST版本
softVersion = '2013-12-26'


# def sendTemplateSMS(to,datas,tempId):
#
#
#     #REST SDK
#     rest = REST(serverIP,serverPort,softVersion)
#     rest.setAccount(accountSid,accountToken)
#     rest.setAppId(appId)
#
#     result = rest.sendTemplateSMS(to,datas,tempId)
#     for k,v in result.iteritems():
#
#         if k=='templateSMS' :
#                 for k,s in v.iteritems():
#                     print '%s:%s' % (k, s)
#         else:
#             print '%s:%s' % (k, v)


class CCP(object):
    instance = None
    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            obj = super().__new__(cls)
            cls.instance = obj
            obj.rest = REST(serverIP, serverPort, softVersion)
            obj.rest.setAccount(accountSid, accountToken)
            obj.rest.setAppId(appId)
        return cls.instance

    def sendTemplateSMS(self, to, datas, tempId):
        try:
            result = self.rest.sendTemplateSMS(to, datas, tempId)
        except Exception as e:
            logging.error(e)
            raise e
        # print result
        # for k, v in result.iteritems():
        #     if k == 'templateSMS':
        #         for k, s in v.iteritems():
        #             print '%s:%s' % (k, s)
        #     else:
        #         print '%s:%s' % (k, v)
        success = "<statusCode>000000</statusCode>"
        if success in result:
            return True
        else:
            return False


if __name__ == "__main__":
    ccp = CCP()
    res = ccp.sendTemplateSMS("注册容联云使用的手机号", ["1234", "5"], 1)
    print(res)
