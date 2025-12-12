# Spring Boot Backend Dockerfile
FROM eclipse-temurin:17-jdk-alpine AS build

WORKDIR /app

# Copy Maven wrapper and pom.xml
COPY mvnw .
COPY .mvn .mvn
COPY pom.xml .

# Download dependencies (cached layer)
RUN chmod +x mvnw && ./mvnw dependency:go-offline -B

# Copy source code and build
COPY src src
RUN ./mvnw package -DskipTests -B

# Runtime stage - use Python 3.9 on Debian Bookworm for TensorFlow 2.11 compatibility
FROM python:3.9-slim-bookworm

# Install Java 17 runtime from Adoptium (Eclipse Temurin)
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    && wget -qO - https://packages.adoptium.net/artifactory/api/gpg/key/public | gpg --dearmor -o /usr/share/keyrings/adoptium.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/adoptium.gpg] https://packages.adoptium.net/artifactory/deb bookworm main" > /etc/apt/sources.list.d/adoptium.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends temurin-17-jre \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies for heatmap generation
RUN pip3 install --no-cache-dir \
    numpy==1.23.5 \
    tensorflow==2.11.0 \
    pillow \
    tf-keras-vis \
    matplotlib \
    h5py

# Copy the built jar
COPY --from=build /app/target/*.jar app.jar

# Expose port
EXPOSE 8080

# Run the application
ENTRYPOINT ["java", "-jar", "app.jar"]
