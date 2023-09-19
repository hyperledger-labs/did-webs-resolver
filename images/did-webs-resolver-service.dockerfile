FROM gleif/dkr:latest

EXPOSE 7677

CMD ["/usr/local/var/did-keri-resolver/scripts/did-webs-resolver-service.sh"]
