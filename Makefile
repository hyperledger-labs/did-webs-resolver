.PHONY: build-did-keri-resolver
build-did-keri-resolver:
	@docker buildx build --platform=linux/amd64 --no-cache -f images/did-keri-resolver.dockerfile --tag weboftrust/did-keri-resolver:latest --tag weboftrust/did-keri-resolver:0.1.0 .

.PHONY: build-did-web
build-did-web:
	@docker build --platform=linux/amd64 -f images/did-web.dockerfile --tag weboftrust/did-web:latest --tag weboftrust/did-web:0.1.0 .

.PHONY: run-did-keri-resolver
run-agent:
	@docker run -p 5921:5921 -p 5923:5923 --name agent weboftrust/did-keri-resolver:0.1.0

.PHONY: push-all
push-all:
	@docker push weboftrust/did-web --all-tags
