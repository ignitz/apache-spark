ARG SPARK_IMAGE

FROM golang:1.23.1 AS builder

WORKDIR /workspace

RUN git clone https://github.com/kubeflow/spark-operator.git && \
    cd spark-operator && \
    git checkout tags/v2.1.1

WORKDIR /workspace/spark-operator

RUN go mod download

ENV GOCACHE=/root/.cache/go-build

ARG TARGETARCH

RUN --mount=type=cache,target=/go/pkg/mod/ \
    --mount=type=cache,target="/root/.cache/go-build" \
    CGO_ENABLED=0 GOOS=linux GOARCH=${TARGETARCH} GO111MODULE=on make build-operator

FROM ${SPARK_IMAGE}

ARG SPARK_UID=185

ARG SPARK_GID=185

USER root

RUN apt-get update \
    && apt-get install -y tini \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /etc/k8s-webhook-server/serving-certs /home/spark && \
    chmod -R g+rw /etc/k8s-webhook-server/serving-certs && \
    chown -R spark /etc/k8s-webhook-server/serving-certs /home/spark

COPY --from=builder /workspace/spark-operator/bin/spark-operator /usr/bin/spark-operator
COPY --from=builder /workspace/spark-operator/entrypoint.sh /usr/bin/entrypoint.sh
RUN chmod +x /usr/bin/entrypoint.sh

USER ${SPARK_UID}:${SPARK_GID}
ENTRYPOINT ["/usr/bin/entrypoint.sh"]
