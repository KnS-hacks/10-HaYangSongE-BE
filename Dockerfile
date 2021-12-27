# pull official base image
FROM python:3.8.0-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1


RUN apk update
RUN  apk add postgresql-dev gcc python3-dev musl-dev zlib-dev jpeg-dev #--(5.2)
RUN  apk add --no-cache python3-dev libffi-dev gcc && pip3 install --upgrade pip
RUN  apk add gcc musl-dev python3-dev libffi-dev openssl-dev
RUN mv chomeDriver/chromeProd/chromedriver /usr/local/bin

COPY . /usr/src/app/
# install dependencies
RUN pip install --upgrade pip
RUN python3 -m pip install --upgrade pip setuptools wheel
RUN pip install cryptography
RUN pip install -r requirements.txt
