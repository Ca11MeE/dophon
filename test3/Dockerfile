FROM python:3.6.2
ADD . ./test3
ADD . ./test3/test3
WORKDIR ./test3
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
CMD ["python","./TestRoute.py"]
