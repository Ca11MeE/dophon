
# dophon
[CookBook](dophon.blog):[框架文档(点击跳转)](dophon.blog)


---
# 快速开始

## 1.引入dophon

```
pip install dophon
```

## 2.启动服务器

```python
from dophon import boot

...

if '__main__' == __name__:

    boot.run_app()
```

## 3.配置文件参数


```python
# dophon.properties.__init__.py

"""<div/>
配置集合<div/>
author:CallMeE<div/>
date:2018-06-01<div/>
"""

# 定义工程根目录(必须)
project_root=os.getcwd()

# 此处为服务器配置(必须,默认开启ssl)
host = '127.0.0.1'  # 服务器监听地址(全ip监听为0.0.0.0),默认监听本地
port = 443 # 服务器监听端口
ssl_context = 'adhoc' # ssl证书路径(默认本地证书)

# 此处为路由文件夹配置
blueprint_path = ['/routes'] # route model dir path(路由文件夹名称)

# 此处为数据库配置
pool_conn_num = 5 # size of db connect pool() # 数据库连接池连接数(默认5个)
pydc_host = 'localhost' # 数据库连接地址
pydc_port = 3306 # 数据库连接端口
pydc_user = 'username' # 数据库连接用户名
pydc_password = 'password' # 数据库连接密码
pydc_database = 'database' # 连接数据库名(可在后面跟连接参数)
```

## 4.路由

快速定义:

```python
from dophon import boot

app = boot.get_app()
```

<span id="to4routeOne">方式一:</span>

```python
import dophon
import DemoClass

_DemoRou=None

app=dophon.blue_print(
    inject_config={
        'inj_obj_list': {
            '_DemoRou': DemoClass
        },
        'global_obj': globals()
    },  # 此处为自动注入参数配置(非必须,不需要请填入空字典)
    name='demo',  # 此处为路由代号(必须,不能重复)
    import_name=__name__  # 此处为路由初始化名称(必须,无特定需求填写__name__)
) 
```

1. 方式一所定义的app为flask的Blueprint类型路由,同时自带了实例注入功能(inject_config参数)
2. inject_config参数默认空,即不调用实例注入
3. inject_config中的inj_obj_list的key必须在上文显式定义(主要为了读写方便)
4. 其余参数同flask中的Blueprint

方式二:
```python
from flask import Blueprint

app=Blueprint('demo',__name__) # 具体参数参照flask.Blueprint
```

1. 方式二为直接使用flask的Blueprint定义路由

## <span id = "to5Autowired">5.对象注入</span>

### 5.1 配置方式注入

方式一: 参考<a href="#to4routeOne"><4.路由.方式一></a>

方式二:

```python
from dophon import annotation
import class_1
import class_2

inject_prop={
    'obj_1':class_1.obj1,
    'obj_2':class_2.obj1
}

obj_1=None
obj_2=None

@Autowired.OuterWired(inject_prop,globals())
def inject_method():
    pass

inject_method()
```

方式三(不推荐):

```python
from dophon import annotation

import class_1
import class_2

obj_1=None
obj_2=None

@Autowired.InnerWired([class_1.obj1,class_2.obj1],['obj_1','obj_2'],globals())
def inject_method():
 pass

inject_method()
```
> ps:上列注入配置可通过引入外部对象进行管理,即创建一个文件通过引入文件中变量实现配置的统一管理

### 5.2 函数装饰器方式注入

#### 5.2.1 实例管理器的定义
注入前必须定义一个实例管理器

```python
from dophon.annotation import *

class OwnBeanConfig(BeanConfig):
    """
    实例管理器必须继承BeanConfig)
    
    注意!!!
        实例定义关键字必须唯一
    """
        
    # 方式一
    @bean()
    def demo_obj_1(self):
        """
        此处返回管理关键字为demo_obj_1的DemoObj()实例
        """
        return DemoObj()
        
    # 方式二
    @bean(name='Demo')
    def demo_obj_2(self):
        """
        此处返回管理关键字为Demo的DemoObj()实例
        """
        return DemoObj()

```

* 实例管理器支持with语法

```python
with OwnBeanConfig() as config:
    pass
```

* 也可以使用普通实例化的实例启动方式来启动实例管理器

```python
OwnBeanConfig()()  # 注意是两个括号
```

> ps:推荐使用BeanConfig子类作为实例批量管理

#### 5.2.2 实例的获取

```python
from dophon.annotation import *

bean=Bean('demo_obj_1')  # 此处获取管理关键字为demo_obj_1对应的实例

# 或者使用类来定位实例
bean=Bean(DemoObj)  # 多个同类实例会抛出语义错误

```

## 6.其他注解

首先引入注解模块
```python
from dophon import annotation
```

或者

```python
from dophon.annotation import *
```

### 6.1 @ResponseBody

返回json格式数据
```python
from dophon.annotation import *

@ResponseBody()
def fun():
    return 'result'
    
# response -> result

@ResponseBody()
def fun():
    return {
    'message':'result'
    }
    
# response -> { 'message' : 'result' }

@ResponseBody()
def fun():
    result={
        'message':'result'
        }
    return result
    
# response -> { 'message' : 'result' }

```
### 6.2 @ResponseTemplate

返回对应页面(默认路由目录下html文件)
```python

from dophon.annotation import *

@ResponseTemplate('index.html')
def ...
```
ps:额外管理页面路径请在路由定义(dophon.blue_print())中配置template_folder,遵从linux系统cd路径语法

### 6.3 @AutoParam

自动配置请求中的参数(分离形式)
推荐指定装饰器中的kwarg_list参数的列表(也就是说形参的列表形式),否则会出现参数混乱(严重)

```python
from dophon.annotation import *

@AutoParam(kwarg_list=['param_1','param_2','param_3'])
def fun(param_1,param_2,param_3):
    print(param_1)
    print(param_2)
    print(param_3)

# request -> (params){ 'param_1' : '1' , 'param_2' : '2' , 'param_3' : '3' }
# console -> 1
#            2
#            3

```

由于本装饰器存在参数混乱,推荐使用FullParam参数装饰器(下文)

### 6.4 @FullParam

自动配置请求中的参数(集中形式),表现形式为dict
赋值参数无名称要求,其中默认赋值参数列表中的第一个参数
```python
from dophon.annotation import *

@FullParam()
def fun(args):
    print(args)

# request -> (params){ 'param_1' : '1' , 'param_2' : '2' , 'param_3' : '3' }
# console -> { 'param_1' : '1' , 'param_2' : '2' , 'param_3' : '3' }
```

### 6.5 @RequestMapping

简化版路由(同app.route())
```python
from dophon.annotation import *
from dophon import boot

app=boot.get_app()

@RequestMapping(app=app,'/test',['get'])
def fun():
    pass

```

### 6.5 @Autowired

参考<a href="#to5Autowired"><5.对象注入></a>
```python
from dophon.annotation import *

@AutoWired()
def fun():
    pass

```

## 7.日志模块(基于python中的logging模块)

### 7.1 日志模块引用

```python
from dophon import logger

logger.inject_logger(globals())

```
其中:
    globals()为注入日志记录功能的变量域,可以为本地变量域,局部变量域,也可以为自定义变量管理域
    
### 7.2 日志模块的使用

控制台带颜色输出(略丑)

日志输出格式如下(暂不可自定义):

```
'%(levelname)s : (%(asctime)s) ==> ::: %(message)s'
```

例如:

```
INFO : (2018-08-02 15:34:11) ==> ::: 执行批量实例管理初始化
```

#### 7.2.1 debug:
       
#### 7.2.2 info:

#### 7.2.3 warning:

#### 7.2.4 error:

#### 7.2.5 critical:


## 8.消息队列

1. 只是一个轻量级消息队列,承载能力中等
2. 即使使用线程池处理消息,极为消耗cpu资源
3. 该队列基于io作为消息持久化,高频消息容易导致io阻塞
4. 消息消费默认有1-3秒延迟(本地)

### 8.1 配置

消息队列承载上限为30个话题(tag)
可通过自定义配置配置上限


<application.py>
```python
msg_queue_max_num = 30   # 消息队列线程池承载上限
```

### 8.2 生产者配置

推荐使用json格式传递数据(便于消费者转义数据)

```python
from dophon.msg_queue import *

@producer(tag='DEMO_TAG')
def producer():
    return 'aaa'

```

### 8.3 消费者配置

方式一:

```python
from dophon.msg_queue import *

@consumer(tag='DEMO_TAG')
def consumer(args):
    print(args)
    
consumer()

# ERROR : (2018-08-02 21:29:15) ==> ::: 2018080221291454499310002: consume() argument after ** must be a mapping, not str

```

> 非json会报错,需在装饰器上打开as_arg

```python
from dophon.msg_queue import *

@consumer(tag='DEMO_TAG',as_args=True)
def consumer(args):
    print(args)
    
consumer()

# aaa

```

### 8.4 统一管理消费者

```python
from dophon.msg_queue import *

class TestConsumer(Consumer):

    @consumer(tag='test_msg_tag|test_msg_tag2', as_args=False, delay=1)
    def consume_msg(msg, timestamp, tag):
        print(msg)
        print(timestamp)
        print(tag)

# 实例化衍生类启动消费者
TestConsumer()

```

## 9.数据库交互

### 9.0 配置相关

### 9.1 结果集映射方式

结果集:sql执行脚本的一个集合,由于在实际开发中查询居多,简称结果集

> 通过xml文件规范若干结果集组成
```xml
<!--test.xml-->
<select id="findAll">
    SELECT
    *
    FROM
    table
</select>
```

> 通过代码关联xml文件,初始化结果集
```python
from dophon.mysql import *

_cursor=db_obj('/test.xml',auto_fix=True)

# 根路径为配置文件路径
# 文件路径必须以/开头

```

> 通过代码获取xml文件其中某一个结果集(以id区分)
```python
result= _cursor.exe_sql(methodName='findAll')
```
> 支持动态参数传入(#{}形式)以及骨架参数传入(${形式})

动态参数传入:
```xml
<select id="findAllById">
    SELECT
    *
    FROM
    table
    WHERE
    id=#{id}
</select>
```

```python
result= _cursor.exe_sql(methodName='findAll',args={'id':'12345678'})
```

骨架参数传入:
```xml
<select id="findAllByTableName">
    SELECT
    *
    FROM
    ${table_name}
</select>
```

```python
result= _cursor.exe_sql(methodName='findAll',args={'id':'12345678'})
```

> 支持单条查询,列表查询,队列查询(结果集id与参数列表的列表形式和字典形式)

单条查询:
```python
result= _cursor.exe_sql_single(methodName='findAll',args={'id':'12345678'})


# result<dict>

```

列表查询:
```python
result= _cursor.exe_sql(methodName='findAll',args={'id':'12345678'})

# result<list>

```

队列查询(不稳定):

1.列表形式:
```python
result= _cursor.exe_sql_queue(
    method_queue=['test1','test2'],
    args_queue=[
        {'id':'123456','name':'tom'},
        {}
    ]
)

# result<dict>
# {
#   method_name:exec_result
# }

```
2.字典形式:
```python
result= _cursor.exe_sql_obj_queue(
    queue_obj={
        'test1':{
            'id':'123456'
        },
        'test2':{}
    }
)

# result<dict>
# {
#   method_name:exec_result
# }

```

> 支持结果集文件热更新

```python
update_round(_cursor,1)

# update_round(<cursor>,second:int)

```

> 支持远程维护结果集文件

```python
remote_cell = remote.getCell('test.xml', remote_path='http://127.0.0.1:8400/member/export/xml/test.xml')
_cursor = db_obj(remote_cell.getPath(), debug=True)
或者
_cursor = db_obj(remote_cell, debug=True)
```

### 9.2 表模型映射方式

暂时支持单条事务操作

> 通过初始化模型管理器获取数据库表映射骨架

```python
from dophon import orm
manager = orm.init_orm_manager(['user'])
```
> 通过实例化映射骨架获取表操作缓存实例(操作实例)
```python
user = manager.user()
```
> 通过对操作实例赋值进行对对应表模拟操作
```python
print('打印对象变量域')
for attr in dir(user):
    print(attr, ":", eval("user." + attr))
print('开始对对象赋值')
user.user_id = 'id'
user.info_id = 'info_id'
user.user_name = 'user_name'
user.user_pwd = 'user_pwd'
user.user_status = 123
user.create_time = datetime.datetime.now().strftime('%y-%m-%d')
user.update_time = datetime.datetime.now().strftime('%y-%m-%d')
print('对象赋值完毕')
print('打印对象变量域')
for attr in dir(user):
    print(attr, ":", eval("user." + attr))
print('打印对象参数表')
print(user([]))

print('user([]):', user([]))
print("user(['user_id','info_id']):", user(['user_id', 'info_id']))
print("user.get_field_list():", user.get_field_list())
print("user.alias('user_table').get_field_list():", user.alias('user_table').get_field_list())



```
> 通过对操作实例结构化操作对数据库对应表结构进行数据落地操作
```python
print(user.where())
print(user.values())

user.select()
user.user_name = '111'
user.select_one()
user.select_all()

user = manager.user()
user.alias('u').select()
user.user_name = '111'
user.alias('us').select_one()
user.alias('userr').select_all()


user.user_id='test_id'
user.info_id='test_info_id'
user.user_name='test_user_name'
user.user_pwd='test_user_pwd'
user.user_status=1
user.create_time = datetime.datetime.now().strftime('%y-%m-%d')
user.update_time = datetime.datetime.now().strftime('%y-%m-%d')

print(user.insert())
#
user.user_id = 'test_id'
user.info_id = 'info_id'
user.user_name = '柯李艺'
user.user_pwd = '333'
user.user_status = 123
print(user.update(update=['user_name','user_pwd'],where=['user_id']))
#
user.user_id = 'test_id'
user.info_id = 'info_id'
user.user_name = 'user_name'
user.user_pwd = 'user_pwd'
user.user_status = 123
print(user.delete(where=['user_id']))

user1=manager.user()
user2=manager.user()
print(user1.select())
user1.user_name='early'
user1.left_join(user2,['user_id'],['user_id'])
user1.alias('u1').left_join(user2.alias('u2'),['user_id'],['user_id'])
# print(user1.exe_join())
print(user1.select())

user1 = manager.user()
print('user1', '---', id(user1))
user2 = user1.copy_to_obj(manager.user)
print('user2', '---', id(user2))
print(user1('user_id'))
user3 = user1.read_from_dict({
    'user_id': '111'
})
print('user3', '---', id(user3))
print(user1('user_id'))
print(user3('user_id'))
```

## 10.容器启动

> 框架容器启动功能:<br/>
> 1. 实现自动生成部署容器
> 2. 自动安装项目相关依赖
> 3. 开发ide控制台调试

> 框架依赖容器: [docker(点击前往官网)](http://www.docker.com)

代码:
```python
# coding: utf-8"
from dophon import docker_boot

docker_boot.run_as_docker()
```

> - 运行结果:
```
INFO : (2018-08-14 12:10:14) ==> ::: 容器前期准备
INFO : (2018-08-14 12:10:14) ==> ::: 生成依赖文件
INFO : (2018-08-14 12:10:17) ==> ::: 生成Dockerfile
INFO : (2018-08-14 12:10:17) ==> ::: 暂停已运行的实例
demo
INFO : (2018-08-14 12:10:28) ==> ::: 移除已运行的实例
demo
INFO : (2018-08-14 12:10:29) ==> ::: 移除旧镜像
Untagged: demo:latest
Deleted: sha256:eb9ace16ac18eea033b87a4bcab0925dc0139664193e480796b00bff72ac132c
Deleted: sha256:2a1af90ac889f36ce7b2861cd8a0f9efa3a98c31915e965cb0bfd7887c32cb05
Deleted: sha256:42bf2fedac374e453deaf06c62643679e8b71de52835a71b228966330b2e90ab
INFO : (2018-08-14 12:10:30) ==> ::: 检测配置合法性
INFO : (2018-08-14 12:10:31) ==> ::: 建立镜像
Sending build context to Docker daemon  26.62kB
Step 1/6 : FROM python:3.6.5
 ---> 9a58cce9b09f
Step 2/6 : ADD . ./demo
 ---> 2b30f0d25df8
Step 3/6 : ADD . ./demo/demo
 ---> 61c751581940
Step 4/6 : WORKDIR ./demo
Removing intermediate container f9439713ab6f
 ---> 8ac1423c208b
Step 5/6 : RUN pip install -r requirements.txt
 ---> Running in 60b5364841ee
Collecting click==6.7 (from -r requirements.txt (line 1))
  Downloading https://files.pythonhosted.org/packages/34/c1/8806f99713ddb993c5366c362b2f908f18269f8d792aff1abfd700775a77/click-6.7-py2.py3-none-any.whl (71kB)
Collecting dophon==1.1.7 (from -r requirements.txt (line 2))
  Downloading https://files.pythonhosted.org/packages/98/81/33d06b15b37ef0715308a764c1cbf7a53ab69000d2bf7f029365b1c760cd/dophon-1.1.7-py3-none-any.whl (59kB)
Collecting Flask==1.0.2 (from -r requirements.txt (line 3))
  Downloading https://files.pythonhosted.org/packages/7f/e7/08578774ed4536d3242b14dacb4696386634607af824ea997202cd0edb4b/Flask-1.0.2-py2.py3-none-any.whl (91kB)
Collecting itsdangerous==0.24 (from -r requirements.txt (line 4))
  Downloading https://files.pythonhosted.org/packages/dc/b4/a60bcdba945c00f6d608d8975131ab3f25b22f2bcfe1dab221165194b2d4/itsdangerous-0.24.tar.gz (46kB)
Collecting Jinja2==2.10 (from -r requirements.txt (line 5))
  Downloading https://files.pythonhosted.org/packages/7f/ff/ae64bacdfc95f27a016a7bed8e8686763ba4d277a78ca76f32659220a731/Jinja2-2.10-py2.py3-none-any.whl (126kB)
Collecting MarkupSafe==1.0 (from -r requirements.txt (line 6))
  Downloading https://files.pythonhosted.org/packages/4d/de/32d741db316d8fdb7680822dd37001ef7a448255de9699ab4bfcbdf4172b/MarkupSafe-1.0.tar.gz
Collecting six==1.11.0 (from -r requirements.txt (line 7))
  Downloading https://files.pythonhosted.org/packages/67/4b/141a581104b1f6397bfa78ac9d43d8ad29a7ca43ea90a2d863fe3056e86a/six-1.11.0-py2.py3-none-any.whl
Collecting Werkzeug==0.14.1 (from -r requirements.txt (line 8))
  Downloading https://files.pythonhosted.org/packages/20/c4/12e3e56473e52375aa29c4764e70d1b8f3efa6682bef8d0aae04fe335243/Werkzeug-0.14.1-py2.py3-none-any.whl (322kB)
Collecting PyMySQL>=0.9.0 (from dophon==1.1.7->-r requirements.txt (line 2))
  Downloading https://files.pythonhosted.org/packages/a7/7d/682c4a7da195a678047c8f1c51bb7682aaedee1dca7547883c3993ca9282/PyMySQL-0.9.2-py2.py3-none-any.whl (47kB)
Collecting urllib3>=1.23 (from dophon==1.1.7->-r requirements.txt (line 2))
  Downloading https://files.pythonhosted.org/packages/bd/c9/6fdd990019071a4a32a5e7cb78a1d92c53851ef4f56f62a3486e6a7d8ffb/urllib3-1.23-py2.py3-none-any.whl (133kB)
Collecting Flask-Bootstrap>=3.3.7.1 (from dophon==1.1.7->-r requirements.txt (line 2))
  Downloading https://files.pythonhosted.org/packages/88/53/958ce7c2aa26280b7fd7f3eecbf13053f1302ee2acb1db58ef32e1c23c2a/Flask-Bootstrap-3.3.7.1.tar.gz (456kB)
Collecting schedule>=0.5.0 (from dophon==1.1.7->-r requirements.txt (line 2))
  Downloading https://files.pythonhosted.org/packages/df/2c/3a94d846682a4fb94966e65bca19a1acb6f7dd85977f4e4cece6e677b757/schedule-0.5.0-py2.py3-none-any.whl
Collecting pyOpenSSL>=18.0.0 (from dophon==1.1.7->-r requirements.txt (line 2))
  Downloading https://files.pythonhosted.org/packages/96/af/9d29e6bd40823061aea2e0574ccb2fcf72bfd6130ce53d32773ec375458c/pyOpenSSL-18.0.0-py2.py3-none-any.whl (53kB)
Collecting gevent>=1.3.5 (from dophon==1.1.7->-r requirements.txt (line 2))
  Downloading https://files.pythonhosted.org/packages/b6/2b/6be042be1023df54889d9e2a90b167f6fea65445384fccfdfd988cc16239/gevent-1.3.5-cp36-cp36m-manylinux1_x86_64.whl (4.6MB)
Collecting cryptography (from PyMySQL>=0.9.0->dophon==1.1.7->-r requirements.txt (line 2))
  Downloading https://files.pythonhosted.org/packages/c2/fa/fa9a8933c285895935d1392922fe721e9cb1b2c1881d14f149213a227ee3/cryptography-2.3-cp34-abi3-manylinux1_x86_64.whl (2.1MB)
Collecting dominate (from Flask-Bootstrap>=3.3.7.1->dophon==1.1.7->-r requirements.txt (line 2))
  Downloading https://files.pythonhosted.org/packages/43/b2/3b7d67dd59dab93ae08569384b254323516e8868b453eea5614a53835baf/dominate-2.3.1.tar.gz
Collecting visitor (from Flask-Bootstrap>=3.3.7.1->dophon==1.1.7->-r requirements.txt (line 2))
  Downloading https://files.pythonhosted.org/packages/d7/58/785fcd6de4210049da5fafe62301b197f044f3835393594be368547142b0/visitor-0.1.3.tar.gz
Collecting greenlet>=0.4.13; platform_python_implementation == "CPython" (from gevent>=1.3.5->dophon==1.1.7->-r requirements.txt (line 2))
  Downloading https://files.pythonhosted.org/packages/de/7b/cb662640540725deb0627264f6b890ee2b7725848b8cbca49e27bf3273c6/greenlet-0.4.14-cp36-cp36m-manylinux1_x86_64.whl (41kB)
Collecting asn1crypto>=0.21.0 (from cryptography->PyMySQL>=0.9.0->dophon==1.1.7->-r requirements.txt (line 2))
  Downloading https://files.pythonhosted.org/packages/ea/cd/35485615f45f30a510576f1a56d1e0a7ad7bd8ab5ed7cdc600ef7cd06222/asn1crypto-0.24.0-py2.py3-none-any.whl (101kB)
Collecting idna>=2.1 (from cryptography->PyMySQL>=0.9.0->dophon==1.1.7->-r requirements.txt (line 2))
  Downloading https://files.pythonhosted.org/packages/4b/2a/0276479a4b3caeb8a8c1af2f8e4355746a97fab05a372e4a2c6a6b876165/idna-2.7-py2.py3-none-any.whl (58kB)
Collecting cffi!=1.11.3,>=1.7 (from cryptography->PyMySQL>=0.9.0->dophon==1.1.7->-r requirements.txt (line 2))
  Downloading https://files.pythonhosted.org/packages/6d/c0/47db8f624f3e4e2f3f27be03a93379d1ba16a1450a7b1aacfa0366e2c0dd/cffi-1.11.5-cp36-cp36m-manylinux1_x86_64.whl (421kB)
Collecting pycparser (from cffi!=1.11.3,>=1.7->cryptography->PyMySQL>=0.9.0->dophon==1.1.7->-r requirements.txt (line 2))
  Downloading https://files.pythonhosted.org/packages/8c/2d/aad7f16146f4197a11f8e91fb81df177adcc2073d36a17b1491fd09df6ed/pycparser-2.18.tar.gz (245kB)
Building wheels for collected packages: itsdangerous, MarkupSafe, Flask-Bootstrap, dominate, visitor, pycparser
  Running setup.py bdist_wheel for itsdangerous: started
  Running setup.py bdist_wheel for itsdangerous: finished with status 'done'
  Stored in directory: /root/.cache/pip/wheels/2c/4a/61/5599631c1554768c6290b08c02c72d7317910374ca602ff1e5
  Running setup.py bdist_wheel for MarkupSafe: started
  Running setup.py bdist_wheel for MarkupSafe: finished with status 'done'
  Stored in directory: /root/.cache/pip/wheels/33/56/20/ebe49a5c612fffe1c5a632146b16596f9e64676768661e4e46
  Running setup.py bdist_wheel for Flask-Bootstrap: started
  Running setup.py bdist_wheel for Flask-Bootstrap: finished with status 'done'
  Stored in directory: /root/.cache/pip/wheels/e8/b9/93/ef6ac3b8ead2d72cbcc042b9d58b613aaf47e533b9dc5b5999
  Running setup.py bdist_wheel for dominate: started
  Running setup.py bdist_wheel for dominate: finished with status 'done'
  Stored in directory: /root/.cache/pip/wheels/86/7c/76/a514f343c9e4f85f4c98fe13138ab9c8f756647155c4c1f25e
  Running setup.py bdist_wheel for visitor: started
  Running setup.py bdist_wheel for visitor: finished with status 'done'
  Stored in directory: /root/.cache/pip/wheels/68/b0/a2/cc8c7cf94ca3d1088a7d2e27936c1e0da170e05f560973e8dd
  Running setup.py bdist_wheel for pycparser: started
  Running setup.py bdist_wheel for pycparser: finished with status 'done'
  Stored in directory: /root/.cache/pip/wheels/c0/a1/27/5ba234bd77ea5a290cbf6d675259ec52293193467a12ef1f46
Successfully built itsdangerous MarkupSafe Flask-Bootstrap dominate visitor pycparser
Installing collected packages: click, MarkupSafe, Jinja2, itsdangerous, Werkzeug, Flask, six, asn1crypto, idna, pycparser, cffi, cryptography, PyMySQL, urllib3, dominate, visitor, Flask-Bootstrap, schedule, pyOpenSSL, greenlet, gevent, dophon
Successfully installed Flask-1.0.2 Flask-Bootstrap-3.3.7.1 Jinja2-2.10 MarkupSafe-1.0 PyMySQL-0.9.2 Werkzeug-0.14.1 asn1crypto-0.24.0 cffi-1.11.5 click-6.7 cryptography-2.3 dominate-2.3.1 dophon-1.1.7 gevent-1.3.5 greenlet-0.4.14 idna-2.7 itsdangerous-0.24 pyOpenSSL-18.0.0 pycparser-2.18 schedule-0.5.0 six-1.11.0 urllib3-1.23 visitor-0.1.3
You are using pip version 10.0.1, however version 18.0 is available.
You should consider upgrading via the 'pip install --upgrade pip' command.
Removing intermediate container 60b5364841ee
 ---> 4f7f51326068
Step 6/6 : CMD ["python","./Bootstrap.py"]
 ---> Running in a01240a5675c
Removing intermediate container a01240a5675c
 ---> 7fe9614a4948
Successfully built 7fe9614a4948
Successfully tagged demo:latest
SECURITY WARNING: You are building a Docker image from Windows against a non-Windows Docker host. All files and directories added to build context will have '-rwxr-xr-x' permissions. It is recommended to double check and reset permissions for sensitive files and directories.
INFO : (2018-08-14 12:11:04) ==> ::: 运行镜像
6686125b7b5ccef21240181bc08da3aabbf0765b72d4ae404d2cc15aabbd0999
INFO : (2018-08-14 12:11:06) ==> ::: 打印容器内部地址(空地址代表启动失败)
'172.17.0.2'
INFO : (2018-08-14 12:11:07) ==> ::: 打印容器载体地址
10.10.75.1
INFO : (2018-08-14 12:11:07) ==> ::: 启动检测容器端口
INFO : (2018-08-14 12:11:07) ==> ::: 容器启动完毕
INFO : (2018-08-14 12:12:17) ==> ::: 容器存活性检查:http://10.10.75.1:80
INFO : (2018-08-14 12:12:27) ==> ::: 容器存活性检查:http://10.10.75.1:80
INFO : (2018-08-14 12:12:38) ==> ::: 容器存活性检查:http://10.10.75.1:80
```