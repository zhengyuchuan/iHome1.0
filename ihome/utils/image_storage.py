from qiniu import Auth, put_data, etag
import qiniu.config

#需要填写你的 Access Key 和 Secret Key
access_key = 'cZUkbjmSLynr8jcQbCur3EnG8ZyEkYXsTkeEnjmJ'
secret_key = 'x-v9UJVb3EfRATWoKVljHeDCamczZ7FiR_Kv-_DB'


def storage(file_data):
    """上传文件到七牛
    :param:file_data:文件数据
    :return:
    """
    #构建鉴权对象
    q = Auth(access_key, secret_key)

    #要上传的空间
    bucket_name = 'ihomepythonflask'

    #生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)

    ret, info = put_data(token, None, file_data)
    if info.status_code == 200:
        # 表示上传成功
        return ret.get("key")
    else:
        raise Exception("上传七牛云失败")
