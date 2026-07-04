# ------------------------------------------------------------
# Smart Energy Analytics - PySpark Docker Image
# Java 11 + Spark 3.5.0 + Python 3
# ------------------------------------------------------------

FROM eclipse-temurin:11-jre

# Environment Variables
ENV SPARK_VERSION=3.5.0 \
    HADOOP_VERSION=3 \
    SPARK_HOME=/spark \
    PYTHONUNBUFFERED=1 \
    PATH=$PATH:/spark/bin

# Install dependencies
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    wget \
    curl \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install Apache Spark
RUN cd /opt && \
    wget -q https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    tar -xzf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /spark && \
    rm spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz

# Create required directories
RUN mkdir -p /app \
             /data \
             /output/results

# Copy requirements
COPY requirements.txt /app/

# Install Python packages
RUN pip3 install --break-system-packages --no-cache-dir \
    -r /app/requirements.txt

# Copy Spark application
COPY spark_app.py /app/

# Copy dataset into image
COPY data/powerconsumption.csv /data/

# Set working directory
WORKDIR /app

# Spark UI
EXPOSE 4040

# Run application
ENTRYPOINT ["python3","spark_app.py"]