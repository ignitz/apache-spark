#
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# ARG SPARK_IMAGE=gcr.io/spark-operator/spark-py:v3.1.1-hadoop3
ARG SPARK_IMAGE
FROM ${SPARK_IMAGE}
USER root

RUN apt update && apt install -y build-essential git

RUN cd /tmp && git clone https://github.com/edenhill/librdkafka.git && \
    cd librdkafka && git checkout tags/v2.14.1 && \
    ./configure && make && make install && \
    cd ../ && rm -rf librdkafka

# Build main Spark Image
FROM ${SPARK_IMAGE}
ARG spark_uid=185

# Switch to user root so we can add additional jars and configuration files.
USER root

# Install maven packages
COPY nop.py /root/nop.py

ENV DELTA_LAKE_VERSION=4.2.0
ENV SCALA_VERSION=2.13
ENV HADOOP_VERSION=3.4.2
ENV AWS_MSK_IAM_AUTH_VERSION=2.36.3
ENV SCALA_VERSION=2.13
ENV POSTGRES_JDBC_VERSION=42.7.4
ENV MYSQL_JDBC_VERSION=9.1.0
ENV UNITY_CATALOG_VERSION=0.4.1

RUN spark-submit --packages \
    org.apache.hadoop:hadoop-aws:${HADOOP_VERSION},org.apache.spark:spark-sql-kafka-0-10_${SCALA_VERSION}:${SPARK_VERSION},io.delta:delta-spark_${SCALA_VERSION}:${DELTA_LAKE_VERSION},org.apache.spark:spark-avro_${SCALA_VERSION}:${SPARK_VERSION},org.apache.spark:spark-protobuf_${SCALA_VERSION}:${SPARK_VERSION},io.unitycatalog:unitycatalog-spark_${SCALA_VERSION}:${UNITY_CATALOG_VERSION} \
    /root/nop.py && \
    mv /root/.ivy2.5.2/jars/* $SPARK_HOME/jars/ && \
    rm -rf /root/.ivy2.5.2
# RUN spark-submit --packages \
#     org.apache.hadoop:hadoop-aws:${HADOOP_VERSION},org.apache.spark:spark-sql-kafka-0-10_${SCALA_VERSION}:${SPARK_VERSION},io.delta:delta-spark_${SCALA_VERSION}:${DELTA_LAKE_VERSION},org.apache.spark:spark-avro_${SCALA_VERSION}:${SPARK_VERSION},org.apache.spark:spark-protobuf_${SCALA_VERSION}:${SPARK_VERSION} \
#     /root/nop.py && \
#     rm /root/.ivy2/jars/com.amazonaws_aws-java-sdk-bundle*.jar && \
#     mv /root/.ivy2/jars/* $SPARK_HOME/jars/ && \
#     spark-submit --packages com.amazonaws:aws-java-sdk-bundle:${AWS_BUNDLE_VERSION} /root/nop.py && \
#     mv /root/.ivy2/jars/* $SPARK_HOME/jars/ && \
#     rm -rf /root/.ivy2
RUN curl --output $SPARK_HOME/jars/aws-msk-iam-auth-${AWS_MSK_IAM_AUTH_VERSION}-all.jar \
    -L https://github.com/aws/aws-msk-iam-auth/releases/download/v${AWS_MSK_IAM_AUTH_VERSION}/aws-msk-iam-auth-${AWS_MSK_IAM_AUTH_VERSION}-all.jar || exit 1

# PostgreSQL and MySQL JDBC drivers
RUN curl --output $SPARK_HOME/jars/postgresql-${POSTGRES_JDBC_VERSION}.jar \
    -L https://repo1.maven.org/maven2/org/postgresql/postgresql/${POSTGRES_JDBC_VERSION}/postgresql-${POSTGRES_JDBC_VERSION}.jar || exit 1
RUN curl --output $SPARK_HOME/jars/mysql-connector-j-${MYSQL_JDBC_VERSION}.jar \
    -L https://repo1.maven.org/maven2/com/mysql/mysql-connector-j/${MYSQL_JDBC_VERSION}/mysql-connector-j-${MYSQL_JDBC_VERSION}.jar || exit 1

RUN chmod 644 $SPARK_HOME/jars/*

# Install delta libraries
# RUN pip3 install --upgrade pip
RUN pip3 install delta-spark==${DELTA_LAKE_VERSION} --no-dependencies --break-system-packages

# Setup for the Prometheus JMX exporter.
# Add the Prometheus JMX exporter Java agent jar for exposing metrics sent to the JmxSink to Prometheus.
ADD https://repo1.maven.org/maven2/io/prometheus/jmx/jmx_prometheus_javaagent/0.18.0/jmx_prometheus_javaagent-0.18.0.jar /prometheus/
RUN chmod 644 /prometheus/jmx_prometheus_javaagent-0.18.0.jar

RUN mkdir -p /etc/metrics/conf
COPY conf/metrics.properties /etc/metrics/conf
COPY conf/prometheus.yaml /etc/metrics/conf

ENV PATH=$PATH:/opt/spark/bin

# Copy LIBRDKAFKA_LIBRARY_PATH to this image
# This shit is needed for librdkafka to work on Apple Silicon (M1)
COPY --from=0 /usr/local/lib /usr/local/lib
COPY --from=0 /usr/local/include /usr/local/include
COPY --from=0 /usr/local/share/doc/librdkafka /usr/local/share/doc/librdkafka

# PIP requirements
COPY ./requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt --break-system-packages && rm /tmp/requirements.txt

# Spark Connect client deps (used by marimo, which imports the bundled pyspark
# from $SPARK_HOME/python rather than a pip-installed one). zstandard is new in
# the 4.1 client; protobuf already ships in the image.
RUN pip3 install --no-cache-dir --break-system-packages \
    pandas pyarrow grpcio grpcio-status numpy "zstandard>=0.25.0"
RUN pip3 install --no-cache-dir --break-system-packages \
    "jupyterhub>=5.5.0,<6.0.0"

# Point Python at the bundled pyspark so `import pyspark` works for the Connect client.
ENV PYTHONPATH=/opt/spark/python:/opt/spark/python/lib/py4j-0.10.9.9-src.zip

# uv: required by the marimo-operator (it runs `marimo edit --sandbox`, which
# provisions the notebook env with uv). marimo resolves uv at /usr/bin/uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/bin/uv
RUN ln -sf /usr/bin/uv /usr/local/bin/uv && /usr/bin/uv --version

# Support Jupyter Notebook
# RUN pip install jupyter
# ENV PYSPARK_DRIVER_PYTHON "jupyter"
# ENV PYSPARK_DRIVER_PYTHON_OPTS "notebook --properties-file /opt/spark/conf/spark.properties"
# ENV PYSPARK_PYTHON python3

# COPY ./entrypoint.sh /opt/entrypoint.sh
# ENTRYPOINT [ "/opt/entrypoint.sh" ]

USER ${spark_uid}
