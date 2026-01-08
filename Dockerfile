# build: docker buildx build --platform linux/amd64 -f Dockerfile -t wzdnzd/aggregator:tag --build-arg PIP_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple" .

FROM python:3.12.3-slim

LABEL maintainer="wzdnzd"

# github personal access token
ENV GIST_PAT=""

# github gist info, format: username/gist_id
ENV GIST_LINK=""

# customize airport listing url address
ENV CUSTOMIZE_LINK=""

# pip default index url
ARG PIP_INDEX_URL="https://pypi.org/simple"

WORKDIR /aggregator

# copy files, only linux related files are needed
COPY requirements.txt /aggregator
COPY subscribe /aggregator/subscribe 
COPY clash/clash-linux-amd /aggregator/clash
COPY clash/Country.mmdb /aggregator/clash

COPY subconverter /aggregator/subconverter
RUN rm -rf subconverter/subconverter-darwin-amd \
    && rm -rf subconverter/subconverter-darwin-arm \
    && rm -rf subconverter/subconverter-linux-arm \
    && rm -rf subconverter/subconverter-windows.exe

# copy additional files for plugin system
COPY plugin_manager /aggregator/plugin_manager
COPY plugins /aggregator/plugins
COPY config /aggregator/config
COPY plugin_control.py /aggregator/plugin_control.py
COPY main_executor.py /aggregator/main_executor.py

# install dependencies
RUN pip install -i ${PIP_INDEX_URL} --no-cache-dir -r requirements.txt

# start and run
# Default to run the main executor for plugin system
CMD ["python", "-u", "main_executor.py"]
