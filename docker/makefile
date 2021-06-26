SRC_DIR=/Users/culbertj/Development/python/s3-response-time
DOCKER_REPO=mghpcc
TAG=latest
TARGET=s3_response_time

build: 
	docker build \
		--pull \
		--file $(SRC_DIR)/docker/Dockerfile \
		--tag $(DOCKER_REPO)/$(TARGET):$(TAG) \
		$(SRC_DIR)

push:
	docker push $(DOCKER_REPO)/$(TARGET):$(TAG)