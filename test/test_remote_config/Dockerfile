FROM python:3.6.2
ADD . ./test_remote_config
ADD . ./test_remote_config/test_remote_config
WORKDIR ./test_remote_config
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python","./test_server.py"]
