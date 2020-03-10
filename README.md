# iHome1.0
基于Flask实现的租房项目

## 基于flask实现的c2c租房项目



> 引言：这个原是黑马培训的爱家租房项目，本人仅用于个人学习使用，不作他用。

---



### 1.需要安装的python package

- [requirements.txt](https://github.com/zhengyuchuan/iHome1.0/blob/master/requirements.txt)





### 2.第三方SDK支持

- 容联云通讯：用于注册短信通知，项目中使用的是测试版，上线使用需购买。项目启动前需要自行去容联云通讯注册账号，然后到[SendTemplateSMS](https://github.com/zhengyuchuan/iHome1.0/blob/master/ihome/libs/yuntongxun/SendTemplateSMS.py)文件中用自己的账号id、token、应用id替换下图中标红的部分[SendTemplateSMS](http://q6gtmshh2.bkt.clouddn.com/uPic/截屏2020-03-09下午10.14.55.png)
- 七牛云：项目启动后，用户上传的图片不是保存在本地，而是保存在七牛云中，所以需要自行注册七牛云账号。然后到[image_storage](https://github.com/zhengyuchuan/iHome1.0/blob/master/ihome/utils/image_storage.py)文件中替换成自己的access key、secret key。[image_storage](http://q6gtmshh2.bkt.clouddn.com/uPic/截屏2020-03-09下午10.28.16.png)
- 支付宝：这里使用的是支付宝的沙箱环境，仅用于测试，用户可以随意设置金额，用起来很爽。使用之前，需要先使用openSSL工具生成密钥对，将自己生成的公钥填入支付宝沙箱中的应用公钥。然后将生成的私钥和支付宝的公钥，放到[app_private_key](https://github.com/zhengyuchuan/iHome1.0/blob/master/ihome/api_1/Alipay_keys/app_private_key.pem)与[alipay_public_key](https://github.com/zhengyuchuan/iHome1.0/blob/master/ihome/api_1/Alipay_keys/alipay_public_key.pem)两个文件中。





### 3.数据库支持

本项目中使用mysql作为数据库，使用redis作为缓存。配置都是使用的默认配置，绑定端口不变。其中使用了Flask-Migrate作为mysql数据库迁移扩展，十分方便。

#### 3.1 启动前mysql准备

- ```sql
  create database ihome charset="utf8";
  ```

- 在项目目录中，终端执行一下命令（python3），来生成对应数据表

  ```shell
  python manage.py db init
  python manage.py db migrate
  ```

- 最后进入ihome数据库，导入城区信息和房屋设施信息

  ```sql
  use ihome;
  INSERT INTO ih_area_info (name) VALUES ('东城区'),('西城区'),('朝阳区'),('海淀区'),('昌平区'),('丰台区'),('房山区'),('通州区'),('顺义区'),('大兴区'),('怀柔区'),('平谷区'),('密云区'),('延庆区'),('石景山区'),('门头沟区');
  INSERT INTO ih_facility_info (name) VALUES ('无线网络'),('热水淋浴'),('空调'),('暖气'),('允许吸烟'),('饮水设备'),('牙具'),('香皂'),('拖鞋'),('手纸'),('毛巾'),('沐浴露、洗发露'),('冰箱'),('洗衣机'),('电梯'),('允许做饭'),('允许带宠物'),('允许聚会'),('门禁系统'),('停车位'),('有线网络'),('电视'),('浴缸');
  ```

#### 3.2 启动前redis准备

- 开启redis-server服务。配置中我只配置了一项，就是 让redis守护进程启动。

  ```shell
  sudo redis-server /usr/local/etc/redis.conf
  ```

#### 3.3 项目中数据库配置

- 需要到[config.py](https://github.com/zhengyuchuan/iHome1.0/blob/master/config.py)中配置自己的数据库连接信息。

  [config.py中配置信息](http://q6gtmshh2.bkt.clouddn.com/uPic/截屏2020-03-09下午11.03.58.png)





### 4.constants参数

在[constants.py](https://github.com/zhengyuchuan/iHome1.0/blob/master/ihome/constants.py)中配置了一些参数，这些参数可根据需要自行修改。

[constants](http://q6gtmshh2.bkt.clouddn.com/uPic/截屏2020-03-10上午8.33.18.png)





### 5.celery worker开启

短信验证业务使用了celery异步队列，启动前要先开启celery worker。

- cd到该项目目录下

- ```shell
  celery -A ihome.tasks.task_sms worker
  ```







### 6.项目启动

- 项目测试时：

  ```
  python manage.py runserver
  ```

- 项目部署时，可以使用gunicorn作为wsgi服务程序

  ```shell
  gunicorn -w 4 -b 192.168.1.4:8001 manage:app
  ```

  

---

### 参考文档

- [flask中文文档](https://dormousehole.readthedocs.io/en/latest/)
- [flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/)
- [flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/)
- [flask-script](https://flask-script.readthedocs.io/en/latest/)现在好多项目都迁移到flask-CLI了，后续本人会研究一下
- [gunicorn](https://docs.gunicorn.org/en/stable/)
- [容联云通讯](https://www.yuntongxun.com/?ly=baidu-pz-p&qd=cpc&cp=ppc&xl=null&kw=10360228)
- [七牛云](https://www.qiniu.com/)
- [支付宝开发者中心](https://developers.alipay.com/developmentAccess/developmentAccess.htm)

