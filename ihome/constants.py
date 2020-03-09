# 图片验证码的有效期
IMAGE_CODE_REDIS_EXPIRES = 180

# 短信验证码的有效期
SMS_CODE_REDIS_EXPIRES = 300

# 发送短信验证码的间隔
SEND_SMS_CODE_INTERVAL = 60

# 登录验证尝试次数上限
LOGIN_ERROR_MAX_TIMES = 5

# 尝试次数的过期时间
LOGIN_ERROR_TIME = 600

# 七牛域名
QINIU_URL_DOMAIN = "http://q6gtzltin.bkt.clouddn.com/"

# 城区信息的缓存时间
AREA_INFO_REDIS_CACHE_EXPIRES = 7200

# 主页显示最大房源数量
HOME_PAGE_MAX_HOUSES = 5

# 主页房源缓存时间
INDEX_PAGE_DATA_REDIS_EXPIRES = 7200

# 房源详细信息页缓存时间
DETAIL_PAGE_DATA_REDIS_EXPIRES = 7200

# 房屋详情页展示最大评论数
HOUSE_DETAIL_COMMENT_COUNTS = 30

# 房屋列表页每页数据量
HOUSE_LIST_PAGE_CAPACITY = 2

# 房屋列表页数缓存时间
HOUSES_LIST_PAGE_REDIS_CACHE_EXPIRES = 7200

# 支付宝域名
ALIPAY_URL_PREFIX = "https://openapi.alipaydev.com/gateway.do?"