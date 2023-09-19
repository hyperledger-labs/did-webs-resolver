FROM gleif/dkr:latest

EXPOSE 7676

CMD ["/usr/local/var/did-keri-resolver/scripts/did-webs-service.sh"]
