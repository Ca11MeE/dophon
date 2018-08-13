
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


> dophon.properties.__init__.py
>
> """<div/>
> 配置集合<div/>
> author:CallMeE<div/>
> date:2018-06-01<div/>
> """

```python
# 定义工程根目录(必须)
project_root=os.getcwd()

# 此处为服务器配置(必须,默认开启ssl)
host = '127.0.0.1'  # 服务器监听地址(全ip监听为0.0.0.0),默认监听本地
port = 443 # 服务器监听端口
ssl_context = 'adhoc' # ssl证书路径(默认本地证书)

# 此处为蓝图文件夹配置
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
    name='demo',  # 此处为蓝图代号(必须,不能重复)
    import_name=__name__  # 此处为蓝图初始化名称(必须,无特定需求填写__name__)
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

1. 方式二为直接使用flask的Blueprint定义蓝图路由

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

> 1. 通过初始化模型管理器获取数据库表映射骨架
> 2. 通过实例化映射骨架获取表操作缓存实例(操作实例)
> 3. 通过对操作实例赋值进行对对应表模拟操作
> 4. 通过对操作实例结构化操作对数据库对应表结构进行数据落地操作

## 10.容器启动