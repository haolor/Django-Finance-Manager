# syntax=docker/dockerfile:1
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /workspace
COPY pom.xml ../../pom.xml
COPY services/discovery-server/pom.xml services/discovery-server/pom.xml
COPY services/discovery-server/src services/discovery-server/src
RUN --mount=type=cache,target=/root/.m2 \
    mvn -f services/discovery-server/pom.xml -DskipTests package

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=build /workspace/services/discovery-server/target/*.jar app.jar
EXPOSE 8761
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
