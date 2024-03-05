FROM gleif/keri:1.0.1

WORKDIR /usr/local/var

RUN mkdir webs
COPY . /usr/local/var/webs

WORKDIR /usr/local/var/webs/

RUN pip install -r requirements.txt

WORKDIR /usr/local/var/webs/volume/dkr/examples