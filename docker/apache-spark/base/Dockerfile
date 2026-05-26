#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ARG java_image_tag=11-jre-slim

FROM ubuntu:26.04

# Install Python
COPY --from=python:3.11-slim /usr/local /usr/local

ARG spark_uid=185

# Before building the docker image, first build and make a Spark distribution following
# the instructions in https://spark.apache.org/docs/latest/building-spark.html.
# If this docker file is being used in the context of building your images from a Spark
# distribution, the docker build command should be invoked from the top level directory
# of the Spark distribution. E.g.:
# docker build -t spark:latest -f kubernetes/dockerfiles/spark/Dockerfile .

ARG DEBIAN_FRONTEND=noninteractive

# # SPARK
ENV SPARK_VERSION=4.1.2
ENV HADOOP_VERSION=3.4.2
ENV SPARK_PACKAGE=spark-${SPARK_VERSION}-bin-hadoop3
ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:${SPARK_HOME}/bin

RUN set -ex && \
    apt-get update && \
    ln -s /lib /lib64 && \
    apt install -y curl bash tini libc6 libpam-modules krb5-user libnss3 procps net-tools logrotate libssl-dev \
    openjdk-21-jdk \
    && \
    rm /bin/sh && \
    ln -sv /bin/bash /bin/sh && \
    echo "auth required pam_wheel.so use_uid" >> /etc/pam.d/su && \
    chgrp root /etc/passwd && chmod ug+rw /etc/passwd && \
    rm -rf /var/cache/apt/* && rm -rf /var/lib/apt/lists/*

RUN curl -sL --retry 3 \
  "https://dlcdn.apache.org/spark/spark-${SPARK_VERSION}/${SPARK_PACKAGE}.tgz" \
  | gunzip \
  | tar x -C /opt/ && \
  mv /opt/${SPARK_PACKAGE} ${SPARK_HOME} && \
  chown -R root:root $SPARK_HOME

RUN mkdir -pv $SPARK_HOME/work-dir
WORKDIR $SPARK_HOME/work-dir
RUN chmod g+w $SPARK_HOME/work-dir
COPY decom.sh /opt/decom.sh
RUN chmod a+x /opt/decom.sh

COPY entrypoint.sh /opt/entrypoint.sh
RUN chmod a+x /opt/entrypoint.sh

RUN useradd -d /home/spark -ms /bin/bash -u ${spark_uid} -g root spark && \
    mkdir -p /home/spark && \
    chown -R spark:root /home/spark && \
    chmod -R g+w /home/spark

USER ${spark_uid}

ENTRYPOINT [ "/opt/entrypoint.sh" ]
