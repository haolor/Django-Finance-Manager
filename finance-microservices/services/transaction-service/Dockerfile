# syntax=docker/dockerfile:1
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /workspace
COPY pom.xml ../../pom.xml
COPY services/transaction-service/pom.xml services/transaction-service/pom.xml
COPY services/transaction-service/src services/transaction-service/src
RUN --mount=type=cache,target=/root/.m2 \
    mvn -f services/transaction-service/pom.xml -DskipTests package

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=build /workspace/services/transaction-service/target/*.jar app.jar
EXPOSE 8082
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
