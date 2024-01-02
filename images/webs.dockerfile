FROM gleif/keri:latest

WORKDIR /usr/local/var

RUN mkdir webs
COPY . /usr/local/var/webs

WORKDIR /usr/local/var/webs/

RUN pip install -r requirements.txt
