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

RUN apt update && apt install -y git

RUN cd /tmp && git clone https://github.com/edenhill/librdkafka.git && \
    cd librdkafka && git checkout tags/v2.3.0 && \
    ./configure && make && make install && \
    cd ../ && rm -rf librdkafka


# Build main Spark Image
FROM ${SPARK_IMAGE}
ARG spark_uid=185

# Switch to user root so we can add additional jars and configuration files.
USER root

# Install maven packages
COPY nop.py /root/nop.py

ENV DELTA_LAKE_VERSION 3.2.1
ENV SCALA_VERSION 2.12
ENV SPARK_BIGQUERY 0.30.0
ENV AWS_BUNDLE_VERSION 1.12.638
ENV AWS_MSK_IAM_AUTH_VERSION 2.0.3

# Use org.apache.hadoop:hadoop-cloud:${HADOOP_VERSION} with others cloud providers
RUN spark-submit --packages \
    org.apache.hadoop:hadoop-aws:${HADOOP_VERSION},org.apache.spark:spark-sql-kafka-0-10_${SCALA_VERSION}:${SPARK_VERSION},io.delta:delta-spark_${SCALA_VERSION}:${DELTA_LAKE_VERSION},com.google.cloud.spark:spark-bigquery_${SCALA_VERSION}:${SPARK_BIGQUERY},org.apache.spark:spark-avro_${SCALA_VERSION}:${SPARK_VERSION},org.apache.spark:spark-protobuf_${SCALA_VERSION}:${SPARK_VERSION},com.google.cloud.bigdataoss:gcs-connector:hadoop3-2.2.18 \
    /root/nop.py && \
    rm /root/.ivy2/jars/com.amazonaws_aws-java-sdk-bundle*.jar && \
    mv /root/.ivy2/jars/* $SPARK_HOME/jars/ && \
    spark-submit --packages com.amazonaws:aws-java-sdk-bundle:${AWS_BUNDLE_VERSION} /root/nop.py && \
    mv /root/.ivy2/jars/* $SPARK_HOME/jars/ && \
    rm -rf /root/.ivy2
RUN curl --output $SPARK_HOME/jars/aws-msk-iam-auth-${AWS_MSK_IAM_AUTH_VERSION}-all.jar \
    -L https://github.com/aws/aws-msk-iam-auth/releases/download/v${AWS_MSK_IAM_AUTH_VERSION}/aws-msk-iam-auth-${AWS_MSK_IAM_AUTH_VERSION}-all.jar || exit 1

RUN chmod 644 $SPARK_HOME/jars/*

# Install delta libraries
RUN pip install --upgrade pip
RUN pip install delta-spark==${DELTA_LAKE_VERSION} --no-dependencies

# Setup for the Prometheus JMX exporter.
# Add the Prometheus JMX exporter Java agent jar for exposing metrics sent to the JmxSink to Prometheus.
ADD https://repo1.maven.org/maven2/io/prometheus/jmx/jmx_prometheus_javaagent/0.18.0/jmx_prometheus_javaagent-0.18.0.jar /prometheus/
RUN chmod 644 /prometheus/jmx_prometheus_javaagent-0.18.0.jar

RUN mkdir -p /etc/metrics/conf
COPY conf/metrics.properties /etc/metrics/conf
COPY conf/prometheus.yaml /etc/metrics/conf

ENV HADOOP_HOME /opt/hadoop
ENV HADOOP_CONF_DIR $HADOOP_HOME/conf
RUN mkdir -p $HADOOP_HOME/conf

ENV HADOOP_HOME /opt/hadoop
COPY conf/hive-site.xml $HADOOP_HOME/conf/
COPY conf/spark-env.sh $HADOOP_HOME/conf/
COPY conf/spark-defaults.conf $HADOOP_HOME/conf/
# Just to test
ENV SPARK_CONF_DIR $HADOOP_HOME/conf

ENV PATH $PATH:/opt/spark/bin

# Copy LIBRDKAFKA_LIBRARY_PATH to this image
# This shit is needed for librdkafka to work on Apple Silicon (M1)
COPY --from=0 /usr/local/lib /usr/local/lib
COPY --from=0 /usr/local/include /usr/local/include
COPY --from=0 /usr/local/share/doc/librdkafka /usr/local/share/doc/librdkafka

# PIP requirements
COPY ./requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Support Jupyter Notebook
# RUN pip install jupyter
# ENV PYSPARK_DRIVER_PYTHON "jupyter"
# ENV PYSPARK_DRIVER_PYTHON_OPTS "notebook --properties-file /opt/spark/conf/spark.properties"
# ENV PYSPARK_PYTHON python3

COPY ./entrypoint.sh /opt/entrypoint.sh
ENTRYPOINT [ "/opt/entrypoint.sh" ]

USER ${spark_uid}