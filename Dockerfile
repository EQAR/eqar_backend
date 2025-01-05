FROM python:3.8

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN mkdir /deqar
WORKDIR /deqar

ADD requirements.txt /deqar/
RUN pip install --no-cache-dir gunicorn \
	&& pip install --no-cache-dir -r requirements.txt

ADD . /deqar

