FROM python:3.6.2
ADD . ./test
ADD . ./test/test
WORKDIR ./test
RUN pip install --no-cache-dir -r requirements.txt
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
CMD ["python","./test_server.py"]
