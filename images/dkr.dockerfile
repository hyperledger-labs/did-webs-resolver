FROM gleif/keri:latest



WORKDIR /usr/local/var

RUN mkdir did-keri-resolver
COPY . /usr/local/var/did-keri-resolver

WORKDIR /usr/local/var/did-keri-resolver

RUN pip install -r requirements.txt
