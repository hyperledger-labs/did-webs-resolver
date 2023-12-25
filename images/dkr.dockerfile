FROM gleif/keri:latest

WORKDIR /usr/local/var

RUN mkdir webs
COPY . /usr/local/var/webs

WORKDIR /usr/local/var/webs/

RUN pip install -r requirements.txt
# RUN cd /usr/local/var/webs/volume/dkr/examples
# RUN ./get_started_create_id.sh "controller" "./my-scripts" "config-docker" "incept-wits.json"
# RUN ./get_started_webs_gen.sh "controller" "did-webs-service%3a7676" "EKYGGh-FtAphGmSZbsuBs_t4qpsjYJ2ZqvMKluq9OxmP"
