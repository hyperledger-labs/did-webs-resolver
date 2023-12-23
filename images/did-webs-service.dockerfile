FROM gleif/dkr:latest

EXPOSE 7676

RUN cd /pages
RUN get_started_webs_serve.sh "controller" "${ORIG_CUR_DIR}/volume/dkr/examples/my-scripts" "config-local"
