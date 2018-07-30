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

<span id="to4routeOne">方式一:</span>

```python
import dophon


_DemoRou=None
app=dophon.blue_print(inject_config={
    'inj_obj_list': {
        '_DemoRou': 'test'
    },
    'global_obj': globals()
},  # 此处为自动注入参数配置(非必须,不需要请填入空字典)
name='demo', # 此处为蓝图代号(必须,不能重复)
import_name=__name__) # 此处为蓝图初始化名称(必须,无特定需求填写__name__)
```

方式二:
```python
from flask import Blueprint

app=Blueprint('demo',__name__) # 具体参数参照flask.Blueprint
```

## <span id = "to5Autowired">5.对象注入</span>

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
> ps:上列注入配置可通过引入外部对象进行管理

## 6.其他注解

首先引入注解模块
```python
from dophon import annotation
```

或者

```python
from dophon.annotation import *
```

### 6.1? ? ResponseBody

返回json格式数据
```python
@ResponseBody()
def ...
```
### 6.2? ? ResponseTemplate

返回对应页面(默认路由目录下html文件)
```python
@ResponseTemplate('index.html')
def ...
```
ps:额外管理页面路径请在路由定义(dophon.blue_print())中配置template_folder,遵从linux系统cd路径语法

### 6.3? ? AutoParam

自动配置请求中的参数(分离形式)
```python
@AutoParam()
def ...
```

### 6.4? ? FullParam

自动配置请求中的参数(集中形式)
```python
@FullParam()
def ...
```

### 6.5? ? RequestMapping

简化版路由(同app.route())
```python
@RequestMapping()
def ...
```

### 6.5? ? Autowired

参考<a href="#to5Autowired"><5.对象注入></a>
```python
@Autowired()
def ...
```