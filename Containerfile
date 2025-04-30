# Copyright 2025 Thales
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#==============================================================================#
# This container image is based on the GoLang Debian officical image and
# and embarks Goreleaser "github.com/goreleaser/goreleaser" and GCC for both
# linux/amd64 (x86_64) and linux/arm64 (aarch64).
#==============================================================================#

# Set Go & tools versions. Be carreful when upgrading these versions, make sure
# to keep them in sync with the version golang
ARG PYTHON_VERSION=3.9
ARG IMAGE_REGISTRY=docker.io/library
ARG IMAGE_NAME=python

# Builder image's registry
ARG BUILDER_IMAGE_TAG=${PYTHON_VERSION}-bookworm

# Run image's registry
ARG RUN_IMAGE_TAG=${PYTHON_VERSION}-slim-bookworm

# For OCI labels
# DO NOT REMOVE
ARG BASE_REGISTRY=${IMAGE_REGISTRY}
ARG BASE_IMAGE=${IMAGE_NAME}
ARG BASE_IMAGE_TAG=${RUN_IMAGE_TAG}

#==============================================================================#
# Python image with support for both linux/amd64 and linux/arm64
#==============================================================================#
FROM ${IMAGE_REGISTRY}/${IMAGE_NAME}:${BUILDER_IMAGE_TAG} AS builder-base

WORKDIR /build

COPY ./sslamanagerrest/ ./sslamanagerrest/
COPY build.sh poetry.lock pyproject.toml README.md ./

RUN curl -sSL https://install.python-poetry.org | python3 -
RUN /root/.local/bin/poetry run python -m pip install --upgrade pip

#RUN /root/.local/bin/poetry config repositories.sslamanager https://github.com/ThalesGroup/ssla-manager
RUN /root/.local/bin/poetry update
RUN /root/.local/bin/poetry build

#==============================================================================#
# Final image
#==============================================================================#
FROM ${IMAGE_REGISTRY}/${IMAGE_NAME}:${RUN_IMAGE_TAG}

ARG SSLA_MANAGER_VERSION=0.1.0
ARG SSLA_MANAGER_NAME=sslamanagerrest
ARG SSLA_MANAGER_PACKAGE=${SSLA_MANAGER_NAME}-${SSLA_MANAGER_VERSION}-py3-none-any.whl

WORKDIR /app

# git is necessary to install ssla-manager sub-module
RUN apt update
RUN apt install git -y

COPY --from=builder-base /build/dist/${SSLA_MANAGER_PACKAGE} /app/
RUN pip install --no-cache-dir /app/${SSLA_MANAGER_PACKAGE}

COPY ./deployments/container/config.yaml /app/
RUN mkdir -p /data/

CMD ["python", "-m", "sslamanagerrest", "-c", "/app/config.yaml"]

# See https://github.com/opencontainers/image-spec/blob/main/annotations.md
ARG LABEL_CREATED=""
ARG LABEL_AUTHOR="Thales Open Source <oss@thalesgroup.com>"
ARG LABEL_URL="https://github.com/ThalesGroup/ssla-manager-rest"
ARG LABEL_DOCUMENTATION="https://github.com/ThalesGroup/ssla-manager-rest"
ARG LABEL_SOURCE="https://github.com/ThalesGroup/ssla-manager-rest"
ARG LABEL_VERSION="0.1.0"
ARG LABEL_REVISION=""
ARG LABEL_VENDOR="Thales"
ARG LABEL_LICENSES="Apache 2.0"
ARG LABEL_TITLE="thales-ssla-manager-rest"
ARG LABEL_REF_NAME=""
ARG LABEL_DESCRIPTION="Container base image for the rest API of the SSLA manager"
ARG LABEL_BASE_DIGEST=""
ARG BASE_REGISTRY
ARG BASE_IMAGE
ARG BASE_IMAGE_TAG
ARG LABEL_BASE_NAME="${IMAGE_REGISTRY}/${IMAGE_NAME}:${RUN_IMAGE_TAG}"
LABEL org.opencontainers.image.created="${LABEL_CREATED}"
LABEL org.opencontainers.image.authors="${LABEL_AUTHOR}"
LABEL org.opencontainers.image.url="${LABEL_URL}"
LABEL org.opencontainers.image.documentation="${LABEL_DOCUMENTATION}"
LABEL org.opencontainers.image.source="${LABEL_SOURCE}"
LABEL org.opencontainers.image.version="${LABEL_VERSION}"
LABEL org.opencontainers.image.revision="${LABEL_REVISION}"
LABEL org.opencontainers.image.vendor="${LABEL_VENDOR}"
LABEL org.opencontainers.image.licenses="${LABEL_LICENSES}"
LABEL org.opencontainers.image.title="${LABEL_TITLE}"
LABEL org.opencontainers.image.ref.name="${LABEL_REF_NAME}"
LABEL org.opencontainers.image.description="${LABEL_DESCRIPTION}"
LABEL org.opencontainers.image.base.digest="${LABEL_BASE_DIGEST}"
LABEL org.opencontainers.image.base.name="${LABEL_BASE_NAME}"