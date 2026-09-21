# syntax=docker/dockerfile:1
# ==================== 构建阶段：Maven reactor ====================
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /build

# 先复制全部 POM 再拉依赖，充分利用层缓存
COPY pom.xml ./
COPY shared/pom.xml shared/
COPY identity/pom.xml identity/
COPY recipe/pom.xml recipe/
COPY novel/pom.xml novel/
COPY api-bootstrap/pom.xml api-bootstrap/
RUN mvn -B -q -pl api-bootstrap -am dependency:go-offline

COPY shared/src shared/src
COPY identity/src identity/src
COPY recipe/src recipe/src
COPY novel/src novel/src
COPY api-bootstrap/src api-bootstrap/src
# 测试依赖本地 MySQL/Redis，容器内只做打包；验证由 CI 与 compose 环境承担
RUN mvn -B -pl api-bootstrap -am -DskipTests package

# ==================== 运行阶段：JRE ====================
FROM eclipse-temurin:17-jre AS runtime
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --system --create-home appuser \
    && mkdir -p /app/uploads /app/logs \
    && chown -R appuser:appuser /app

COPY --from=build /build/api-bootstrap/target/po-api-bootstrap-0.0.1-SNAPSHOT.jar app.jar

USER appuser
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
