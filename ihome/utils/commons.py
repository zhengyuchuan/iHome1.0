from werkzeug.routing import BaseConverter


# 定义正则转换器
class ReConverter(BaseConverter):
    """"""
    def __init__(self, url_map, regex):
        super().__init__(url_map)
        # 保存正则表达式
        self.regex = regex