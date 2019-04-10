FROM python:3.6.2
ADD . ./test_deceration_description
WORKDIR ./test_deceration_description
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
CMD ["python","./Bootstrap.py"]
