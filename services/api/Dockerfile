# 基础镜像默认走国内加速镜像（Docker Hub 本地直连不通）；
# 云端构建可 --build-arg BUILD_IMAGE=maven:3.9-eclipse-temurin-17 --build-arg RUNTIME_IMAGE=eclipse-temurin:17-jre 覆盖回官方
ARG BUILD_IMAGE=docker.m.daocloud.io/library/maven:3.9-eclipse-temurin-17
ARG RUNTIME_IMAGE=docker.m.daocloud.io/library/eclipse-temurin:17-jre
# ==================== 构建阶段：Maven reactor ====================
FROM ${BUILD_IMAGE} AS build
WORKDIR /build

# 走阿里云 Maven 镜像加速依赖下载（Maven Central 国内直连极慢/超时）
COPY maven-settings.xml /root/.m2/settings.xml
# 先复制全部 POM 再拉依赖，充分利用层缓存
COPY pom.xml ./
COPY shared/pom.xml shared/
COPY identity/pom.xml identity/
COPY recipe/pom.xml recipe/
COPY api-bootstrap/pom.xml api-bootstrap/
RUN mvn -B -q -pl api-bootstrap -am dependency:go-offline

COPY shared/src shared/src
COPY identity/src identity/src
COPY recipe/src recipe/src
COPY api-bootstrap/src api-bootstrap/src
# 测试依赖本地 MySQL/Redis，容器内只做打包；验证由 CI 与 compose 环境承担
RUN mvn -B -pl api-bootstrap -am -DskipTests package

# ==================== 运行阶段：JRE ====================
FROM ${RUNTIME_IMAGE} AS runtime
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
