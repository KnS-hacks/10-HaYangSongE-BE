# pull official base image
FROM python:3.8.0-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1


RUN apk update
RUN apt-get update
RUN  apk add postgresql-dev gcc python3-dev musl-dev zlib-dev jpeg-dev #--(5.2)
RUN  apk add --no-cache python3-dev libffi-dev gcc && pip3 install --upgrade pip
RUN  apk add gcc musl-dev python3-dev libffi-dev openssl-dev

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/goodle.list'
RUN apt-get update
RUN apt-get install -y google-chrome-stable

# install chromedriver
RUN apt-get install -yqq unzip
RUN apt-get install -y curl
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
ENV DISPLAY=:99

COPY . /usr/src/app/
# install dependencies
RUN pip install --upgrade pip
RUN python3 -m pip install --upgrade pip setuptools wheel
RUN pip install cryptography
RUN pip install -r requirements.txt
