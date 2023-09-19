FROM gleif/dkr:latest

EXPOSE 7678

CMD ["/usr/local/var/did-keri-resolver/scripts/did-keri-resolver-service.sh"]
