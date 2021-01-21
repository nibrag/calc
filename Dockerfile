FROM python:3.8

ADD requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt
RUN rm /tmp/requirements.txt

RUN mkdir /sources
WORKDIR /sources
