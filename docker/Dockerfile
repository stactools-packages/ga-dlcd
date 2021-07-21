ARG STACTOOLS_VERSION=latest
FROM ghcr.io/stac-utils/stactools:$STACTOOLS_VERSION

WORKDIR /opt/stactools-ga-dlcd

# For caching purposes, install dependencies but remove the actual package
COPY pyproject.toml setup.cfg ./
COPY src/stactools/ga_dlcd/__init__.py src/stactools/ga_dlcd/
RUN pip install . \
    && rm -r /opt/conda/lib/python3.8/site-packages/stactools/ga_dlcd

COPY src ./src
RUN pip install .
