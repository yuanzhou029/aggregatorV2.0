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

# copy additional files for UI
COPY api /aggregator/api
COPY web /aggregator/web
COPY start_ui.py /aggregator/start_ui.py
COPY plugin_manager /aggregator/plugin_manager

# install dependencies
RUN pip install -i ${PIP_INDEX_URL} --no-cache-dir -r requirements.txt

# install Node.js and npm
RUN apt-get update && apt-get install -y curl python3-dev gcc && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# install python packages for api
RUN pip install flask flask-cors

# build frontend
WORKDIR /aggregator/web
RUN npm install && npm run build

WORKDIR /aggregator

# start and run
# Default to run the UI service
EXPOSE 5000
EXPOSE 3000
EXPOSE 14047

# Copy built frontend to static directory
RUN mkdir -p /aggregator/frontend_static && cp -r /aggregator/frontend_dist/* /aggregator/frontend_static/ 2>/dev/null || echo "Frontend build not found, skipping"

CMD ["python", "-u", "start_ui.py", "--mode", "prod"]
