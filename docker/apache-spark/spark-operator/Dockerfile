ARG SPARK_IMAGE

FROM golang:1.24.10 AS builder

WORKDIR /workspace

RUN git config --global url."https://github.com/".insteadOf "git@github.com:" && \
    git clone --depth 1 --branch v2.5.0 git@github.com:kubeflow/spark-operator.git .

RUN --mount=type=cache,target=/go/pkg/mod/ \
    go mod download


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

USER ${SPARK_UID}:${SPARK_GID}

COPY --from=builder /workspace/bin/spark-operator /usr/bin/spark-operator

COPY --from=builder /workspace/entrypoint.sh /usr/bin/

ENTRYPOINT ["/usr/bin/entrypoint.sh"]
