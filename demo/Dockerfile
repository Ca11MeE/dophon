FROM python:3.6.5
ADD . ./demo
ADD . ./demo/demo
WORKDIR ./demo
RUN pip install -r requirements.txt
CMD ["python","./Bootstrap.py"]
