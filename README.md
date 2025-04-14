# Custom Apache Spark

> Version 3.5.3

My custom image to use Spark in Kubernetes and GCS/S3 and Delta Lake.

## Usage

Check options with `make` command

```
$ make
help                           ❓ Show help menu
build-spark                    🐳 Build Spark image
build-operator                 🐳 Build Spark Operator image
build-emr                      🐳 Build EMR on EKS image
build-emr-operator             🐳 Build EMR on EKS Operator image
buildx                         🐳 Build Multi-Arch and publish to registry
```
