.PHONY: build-dws-base publish-dws-base tag-dws-base-latest \
	build-dynamic-service publish-dynamic-service tag-dynamic-service-latest \
	build-did-webs-resolver-service publish-did-webs-resolver-service tag-did-webs-resolver-latest \
	run-agent build-all publish-latest warn tag fmt check tag-latest-all
VERSION=0.3.1  # also change in pyproject.toml and src/dws/__init__.py

RED="\033[0;31m"
NO_COLOUR="\033[0m"

define DOCKER_WARNING
In order to use the multi-platform build enable the containerd image store
The containerd image store is not enabled by default.
To enable the feature for Docker Desktop:
	Navigate to Settings in Docker Desktop.
	In the General tab, check Use containerd for pulling and storing images.
	Select Apply and Restart."
endef
export DOCKER_WARNING

.warn:
	@echo -e ${RED}"$$DOCKER_WARNING"${NO_COLOUR}

# Base Image for all other did:webs  images
BASE_IMAGE=gleif/dws-base
build-dws-base: .warn
	@docker build \
		--platform=linux/amd64,linux/arm64 \
		-f images/dws-base.dockerfile \
		-t $(BASE_IMAGE):$(VERSION) .

publish-dws-base:
	@docker push $(BASE_IMAGE):$(VERSION)

tag-dws-base-latest:
	@$(MAKE) tag IMAGE_NAME=$(BASE_IMAGE) VERSION=$(VERSION)

tag-latest-all: tag-dws-base-latest tag-dynamic-service-latest tag-did-webs-resolver-latest

# Build did:webs service that dynamically generates did:webs  assets
DYN_IMAGE=gleif/did-webs-service
build-dynamic-service: .warn
	@docker build \
		--platform=linux/amd64,linux/arm64 \
		-f images/dws-dynamic-service.dockerfile \
		-t $(DYN_IMAGE):$(VERSION) .

publish-dynamic-service:
	@docker push $(DYN_IMAGE):$(VERSION)

tag-dynamic-service-latest:
	@$(MAKE) tag IMAGE_NAME=$(DYN_IMAGE) VERSION=$(VERSION)

# build did:webs resolver service
RSLV_IMAGE=gleif/did-webs-resolver-service
build-did-webs-resolver-service: .warn
	@docker build \
		--platform=linux/amd64,linux/arm64 \
		-f images/dws-resolver-service.dockerfile \
		-t $(RSLV_IMAGE):$(VERSION) .

publish-did-webs-resolver-service:
	@docker push $(RSLV_IMAGE):$(VERSION)

tag-did-webs-resolver-latest:
	@$(MAKE) tag IMAGE_NAME=$(RSLV_IMAGE) VERSION=$(VERSION)

# Other targets
build-all:
	# Base image
	@$(MAKE) build-dws-base
	@$(MAKE) tag-dws-base-latest
	# Dynamic service
	@$(MAKE) build-dynamic-service
	@$(MAKE) tag-dynamic-service-latest
	# Resolver service
	@$(MAKE) build-did-webs-resolver-service
	@$(MAKE) tag-did-webs-resolver-latest

publish-latest:
	@docker push $(BASE_IMAGE):latest
	@docker push $(DYN_IMAGE):latest
	@docker push $(RSLV_IMAGE):latest

tag:
	@IMAGE_ID=$$(docker images --format "{{.ID}}" $(IMAGE_NAME):$(VERSION) | head -n 1); \
	if [ -z "$$IMAGE_ID" ]; then \
		echo "Error: No local image found for '$(IMAGE_NAME)'"; \
		exit 1; \
	fi; \
	docker tag $$IMAGE_ID $(IMAGE_NAME):latest; \
	echo "Successfully tagged $(IMAGE_NAME) ($$IMAGE_ID) as $(IMAGE_NAME):latest"

# Formatting targets
fmt:
	@uv tool run ruff check --select I --fix
	@uv tool run ruff format

# used by ci
check:
	uv tool run ruff check --select I
	uv tool run ruff format --check

