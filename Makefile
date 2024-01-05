.PHONY: build-did-webs-resolver
build-did-webs-resolver:
	@docker buildx build --platform=linux/amd64 --no-cache -f images/did-webs-resolver.dockerfile --tag weboftrust/did-webs-resolver:latest --tag weboftrust/did-webs-resolver:0.1.0 .

.PHONY: build-did-web
build-did-web:
	@docker build --platform=linux/amd64 -f images/did-web.dockerfile --tag weboftrust/did-web:latest --tag weboftrust/did-web:0.1.0 .

.PHONY: run-did-webs-resolver
run-agent:
	@docker run -p 5921:5921 -p 5923:5923 --name agent weboftrust/did-webs-resolver:0.1.0

.PHONY: push-all
push-all:
	@docker push weboftrust/did-web --all-tags
