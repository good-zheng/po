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
COPY talk/pom.xml talk/
COPY novel/pom.xml novel/
COPY api-bootstrap/pom.xml api-bootstrap/
# 缓存挂载只能挂 /root/.m2/repository：挂整个 /root/.m2 会遮住上面的 settings.xml，
# 阿里云镜像失效、退化成直连 Maven Central。go-offline 冷跑要下载 200MB+，持久化后重跑近乎秒过。
RUN --mount=type=cache,target=/root/.m2/repository mvn -B -pl api-bootstrap -am dependency:go-offline

COPY shared/src shared/src
COPY identity/src identity/src
COPY recipe/src recipe/src
COPY talk/src talk/src
COPY novel/src novel/src
COPY api-bootstrap/src api-bootstrap/src
# 测试依赖本地 MySQL/Redis，容器内只做打包；验证由 CI 与 compose 环境承担
RUN --mount=type=cache,target=/root/.m2/repository mvn -B -pl api-bootstrap -am -DskipTests package

# ==================== 运行阶段：JRE ====================
FROM ${RUNTIME_IMAGE} AS runtime
WORKDIR /app

# curl 是运行期必需的：docker-compose.yml 的 api 健康检查（`curl -fsS .../actuator/health`）依赖它。
# Ubuntu 自带源指向 archive.ubuntu.com，本机网络下会在 universe 索引上反复断连（实测重试 6 次全失败，
# exit 100），所以默认把源整体换到国内镜像；APT_MIRROR 传空串则保留镜像自带源（云端/梯子构建）。
# 两个候选文件名都要改：24.04 起是 deb822 格式的 ubuntu.sources（URIs 带结尾斜杠），老镜像才是 sources.list。
ARG APT_MIRROR=mirrors.tuna.tsinghua.edu.cn
RUN set -eux; \
    if [ -n "$APT_MIRROR" ]; then \
      for f in /etc/apt/sources.list /etc/apt/sources.list.d/ubuntu.sources; do \
        [ -f "$f" ] || continue; \
        sed -i -E "s#https?://(archive|security)[.]ubuntu[.]com/ubuntu/?#http://${APT_MIRROR}/ubuntu#g" "$f"; \
      done; \
    fi; \
    apt-get -o Acquire::Retries=5 update \
    && apt-get -o Acquire::Retries=5 install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --system --create-home appuser \
    && mkdir -p /app/uploads /app/logs \
    && chown -R appuser:appuser /app \
    && curl --version | head -1

COPY --from=build /build/api-bootstrap/target/po-api-bootstrap-0.0.1-SNAPSHOT.jar app.jar

USER appuser
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
