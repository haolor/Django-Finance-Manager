# syntax=docker/dockerfile:1
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /workspace
COPY pom.xml ../../pom.xml
COPY services/ai-service/pom.xml services/ai-service/pom.xml
COPY services/ai-service/src services/ai-service/src
RUN --mount=type=cache,target=/root/.m2 \
    mvn -f services/ai-service/pom.xml -DskipTests package

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=build /workspace/services/ai-service/target/*.jar app.jar
EXPOSE 8085
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
