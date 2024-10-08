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
ARG java_image_tag=11-jre-slim

FROM openjdk:${java_image_tag}

ARG spark_uid=185

# Before building the docker image, first build and make a Spark distribution following
# the instructions in https://spark.apache.org/docs/latest/building-spark.html.
# If this docker file is being used in the context of building your images from a Spark
# distribution, the docker build command should be invoked from the top level directory
# of the Spark distribution. E.g.:
# docker build -t spark:latest -f kubernetes/dockerfiles/spark/Dockerfile .

ARG DEBIAN_FRONTEND=noninteractive

RUN set -ex && \
  sed -i 's/http:\/\/deb.\(.*\)/https:\/\/deb.\1/g' /etc/apt/sources.list && \
  apt-get update && \
  ln -s /lib /lib64 && \
  apt install -y bash tini libc6 libpam-modules krb5-user libnss3 \
  procps net-tools curl python3 python3-pip && \
  pip3 install --upgrade pip setuptools && \
  rm /bin/sh && \
  ln -sv /bin/bash /bin/sh && \
  echo "auth required pam_wheel.so use_uid" >> /etc/pam.d/su && \
  chgrp root /etc/passwd && chmod ug+rw /etc/passwd && \
  rm -rf /root/.cache && rm -rf /var/cache/apt/*

# SPARK
ENV SPARK_VERSION 3.5.3
ENV HADOOP_VERSION 3.3.4
ENV SPARK_PACKAGE spark-${SPARK_VERSION}-bin-hadoop3
ENV SPARK_HOME /opt/spark

ENV PATH $PATH:${SPARK_HOME}/bin

RUN curl -sL --retry 3 \
  "https://dlcdn.apache.org/spark/spark-${SPARK_VERSION}/${SPARK_PACKAGE}.tgz" \
  | gunzip \
  | tar x -C /opt/ && \
  mv /opt/${SPARK_PACKAGE}/ ${SPARK_HOME} && \
  chown -R root:root $SPARK_HOME

COPY decom.sh /opt/

WORKDIR $SPARK_HOME/work-dir
RUN chmod g+w $SPARK_HOME/work-dir
RUN chmod a+x /opt/decom.sh
RUN mkdir -pv $SPARK_HOME/.ivy2 && chown ${spark_uid}:${spark_uid} $SPARK_HOME/.ivy2

# Specify the User that the actual main process will run as
USER ${spark_uid}
