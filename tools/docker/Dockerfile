# tt-support-tools on Python 3.11 with the EDA tools and LibreLane from the
# pinned LibreLane image (its /nix tree, unchanged).
# klayout 0.29.12 and gdstk 0.9.60 publish no linux-aarch64 wheels, so they
# are compiled from source on arm64 hosts.
ARG LIBRELANE_IMAGE=ghcr.io/librelane/librelane:3.1.0.dev3
FROM ${LIBRELANE_IMAGE} AS librelane

FROM ubuntu:24.04
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates git libcairo2 \
      build-essential cmake zlib1g-dev libexpat1-dev libpng-dev libqhull-dev libcurl4-openssl-dev \
 && apt-get clean \
 && rm -r /var/lib/apt/lists
COPY --from=ghcr.io/astral-sh/uv:0.12.10 /uv /usr/local/bin/uv
COPY --from=librelane /nix /nix
COPY requirements.txt /tmp/tt-requirements.txt
ENV UV_PYTHON_INSTALL_DIR=/opt/python
# Each klayout compile job needs over 1 GB; fit Docker Desktop's default VM memory.
ENV KLAYOUT_SETUP_MULTICORE=3
RUN uv venv --python 3.11 /opt/tt \
 && uv pip install --python /opt/tt/bin/python -r /tmp/tt-requirements.txt
