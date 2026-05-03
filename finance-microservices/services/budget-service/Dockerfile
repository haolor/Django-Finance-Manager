# syntax=docker/dockerfile:1
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /workspace
COPY pom.xml ../../pom.xml
COPY services/budget-service/pom.xml services/budget-service/pom.xml
COPY services/budget-service/src services/budget-service/src
RUN --mount=type=cache,target=/root/.m2 \
    mvn -f services/budget-service/pom.xml -DskipTests package

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=build /workspace/services/budget-service/target/*.jar app.jar
EXPOSE 8083
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
