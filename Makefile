.PHONY: help
help: ## ❓ Show help menu
	@grep -E '^[a-z.A-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: build-spark
build-spark: ## 🐳 Build Spark image
	@docker build --progress=plain -f docker/base/Dockerfile docker/base -t ignitz/apache-spark-base:latest
	@docker build --progress=plain -f docker/custom/Dockerfile docker/custom -t ignitz/apache-spark-custom:latest --build-arg SPARK_IMAGE=ignitz/apache-spark-base:latest

.PHONY: build-operator
build-operator: build-spark ## 🐳 Build Spark Operator image
	@docker build --progress=plain -f docker/spark-operator/Dockerfile docker/spark-operator -t ignitz/apache-spark-operator:latest --build-arg SPARK_IMAGE=ignitz/apache-spark-custom:latest

.PHONY: buildx
buildx: ## 🐳 Build Multi-Arch and publish to registry
	@docker buildx build --progress=plain -f docker/base/Dockerfile docker/base --platform linux/amd64,linux/arm64 -t ignitz/apache-spark-base:latest --push
	@docker buildx build --progress=plain -f docker/custom/Dockerfile docker/custom --platform linux/amd64,linux/arm64 -t ignitz/apache-spark-custom:latest --build-arg SPARK_IMAGE=ignitz/apache-spark-base:latest --push
	@docker buildx build --progress=plain -f docker/spark-operator/Dockerfile docker/spark-operator --platform linux/amd64,linux/arm64 -t ignitz/apache-spark-operator:latest  --build-arg SPARK_IMAGE=ignitz/apache-spark-custom:latest --push
