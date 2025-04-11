FROM public.ecr.aws/emr-on-eks/spark/emr-7.8.0:20250228 as emr_base

USER root

COPY certs/*.crt /etc/pki/ca-trust/source/anchors/
RUN for cert_file in /etc/pki/ca-trust/source/anchors/*; do mv "${cert_file}" "${cert_file}.pem"; done
RUN update-ca-trust
RUN for cert_file in /etc/pki/ca-trust/source/anchors/*; do keytool -importcert -file "${cert_file}" -alias "${cert_file}" -keystore $JAVA_HOME/lib/security/cacerts --storepass changeit --noprompt; done

# Install maven packages
COPY nop.py /root/nop.py
RUN echo "" > /usr/lib/spark/conf/spark-defaults.conf 

ENV SPARK_VERSION=3.5.3
ENV DELTA_LAKE_VERSION=3.3.0
ENV SCALA_VERSION=2.12
ENV AWS_MSK_IAM_AUTH_VERSION=2.0.3
ENV AWS_SDK_BUNDLE_VERSION=1.12.780
ENV AWS_JAVA_BUNDLE_VERSION=2.29.52
ENV AWS_GLUE_CATALOG_VERSION=4.5.0

# Use org.apache.hadoop:hadoop-cloud:${HADOOP_VERSION} with others cloud providers
RUN spark-submit --packages \
    org.apache.spark:spark-sql-kafka-0-10_${SCALA_VERSION}:${SPARK_VERSION},io.delta:delta-spark_${SCALA_VERSION}:${DELTA_LAKE_VERSION},org.apache.spark:spark-avro_${SCALA_VERSION}:${SPARK_VERSION},org.apache.spark:spark-protobuf_${SCALA_VERSION}:${SPARK_VERSION} \
    /root/nop.py && \
    mv /root/.ivy2/jars/* ${SPARK_HOME}/jars/ && \
    rm -rf /root/.ivy2

RUN cp /usr/lib/hadoop/hadoop-aws-* ${SPARK_HOME}/jars/
RUN cp /usr/share/aws/aws-java-sdk/aws-java-sdk-bundle-${AWS_SDK_BUNDLE_VERSION}.jar ${SPARK_HOME}/jars/
RUN cp /usr/share/aws/aws-java-sdk-v2/aws-sdk-java-bundle-${AWS_JAVA_BUNDLE_VERSION}.jar ${SPARK_HOME}/jars/
RUN cp /usr/share/aws/hmclient/lib/aws-glue-datacatalog-spark-client-${AWS_GLUE_CATALOG_VERSION}.jar \
    ${SPARK_HOME}/jars/

RUN unlink /usr/lib/spark/work && unlink /usr/lib/spark/conf && mkdir -pv /usr/lib/spark/conf && cp -r /etc/spark/conf/* /usr/lib/spark/conf/
RUN rm -rf /usr/lib/spark/connector/ && rm -rf /usr/lib/spark/examples/ && rm -rf /usr/lib/spark/yarn/
RUN unlink /usr/lib/spark/jars/mariadb-connector-java.jar && \
    unlink /usr/lib/spark/jars/emr-spark-goodies.jar && \
    unlink /usr/lib/spark/jars/spark-fgac.jar && \
    unlink /usr/lib/spark/jars/spark-kubernetes.jar && \
    unlink /usr/lib/spark/python/lib/py4j-src.zip

# RUN cd /tmp && git clone https://github.com/edenhill/librdkafka.git && \
#     cd librdkafka && git checkout tags/v2.2.0 && \
#     ./configure && make && make install && \
#     cd ../ && rm -rf librdkafka

# Build main Spark Ima
FROM openjdk:11-jre-slim

# Create spark user
ARG spark_uid=185
RUN groupadd --system --gid=${spark_uid} spark && \
    useradd --system --uid=${spark_uid} --gid=spark spark && \
    mkdir -pv /home/spark && \
    chown -R spark:spark /home/spark

ENV PATH=$PATH:/home/spark/.local/bin

USER root

ARG DEBIAN_FRONTEND=noninteractive

ENV SPARK_VERSION=3.5.3
ENV DELTA_LAKE_VERSION=3.3.0
ENV SCALA_VERSION=2.12
ENV AWS_MSK_IAM_AUTH_VERSION=2.0.3
ENV AWS_SDK_BUNDLE_VERSION=1.12.780
ENV AWS_JAVA_BUNDLE_VERSION=2.29.52
ENV AWS_GLUE_CATALOG_VERSION=4.5.0
ENV SPARK_HOME=/opt/spark

COPY certs/*.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates
RUN for cert_file in /usr/local/share/ca-certificates/*; do keytool -importcert -file "${cert_file}" -alias "${cert_file}" -keystore $JAVA_HOME/lib/security/cacerts --storepass changeit --noprompt; done

COPY --from=emr_base --chown=spark:spark /usr/lib/spark /opt/spark

RUN set -ex && \
    sed -i 's/http:\/\/deb.\(.*\)/https:\/\/deb.\1/g' /etc/apt/sources.list && \
    apt-get update && \
    ln -s /lib /lib64 && \
    apt install -y bash tini libc6 libpam-modules krb5-user libnss3 \
                   procps net-tools curl python3 python3-pip \
                   jq unzip && \
    pip3 install --upgrade pip setuptools && \
    rm /bin/sh && \
    ln -sv /bin/bash /bin/sh && \
    echo "auth required pam_wheel.so use_uid" >> /etc/pam.d/su && \
    chgrp root /etc/passwd && chmod ug+rw /etc/passwd && \
    rm -rf /root/.cache && rm -rf /var/cache/apt/*

RUN curl --output $SPARK_HOME/jars/aws-msk-iam-auth-${AWS_MSK_IAM_AUTH_VERSION}-all.jar \
    -L https://github.com/aws/aws-msk-iam-auth/releases/download/v${AWS_MSK_IAM_AUTH_VERSION}/aws-msk-iam-auth-${AWS_MSK_IAM_AUTH_VERSION}-all.jar || exit 1
RUN chmod 644 $SPARK_HOME/jars/*

# Install delta libraries
RUN pip install --upgrade pip
RUN pip install delta-spark==${DELTA_LAKE_VERSION} --no-dependencies

# Spark conf setup
COPY conf/spark-defaults.conf ${SPARK_HOME}/conf/
ENV PATH=$PATH:/opt/spark/bin

RUN mkdir -pv /etc/kafka/secrets/certs/
# Unset if you are not using root user
RUN chown -R spark:spark /etc/kafka/secrets/certs/

# Copy LIBRDKAFKA_LIBRARY_PATH to this image
# This steps are needed for librdkafka to work on Apple Silicon (M1)
# COPY --from=0 /usr/local/lib /usr/local/lib
# COPY --from=0 /usr/local/include /usr/local/include
# COPY --from=0 /usr/local/share/doc/librdkafka /usr/local/share/doc/librdkafka

# PIP requirements
COPY ./requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Install AWSCLI v1
RUN pip install awscli

# Support Jupyter Notebook
# RUN pip install jupyter
# ENV PYSPARK_DRIVER_PYTHON "jupyter"
# ENV PYSPARK_DRIVER_PYTHON_OPTS "notebook --properties-file /opt/spark/conf/spark.properties"
# ENV PYSPARK_PYTHON python3

RUN mkdir -pv /opt/spark/work-dir
WORKDIR /opt/spark/work-dir

RUN chown -R spark:spark /opt/spark
RUN chown -R root:root /tmp
RUN chmod -R 777 /tmp

COPY entrypoint.sh /opt/
RUN chmod +x /opt/entrypoint.sh
ENTRYPOINT [ "/opt/entrypoint.sh" ]

USER spark

