FROM python:3.11-alpine AS blueprint
WORKDIR /opt/exporter
COPY src/requirements.txt ./requirements.txt
RUN python3 -m pip install \
    --no-cache-dir \
    -r ./requirements.txt
COPY src ./src
USER nobody

FROM blueprint as app
EXPOSE 9877/tcp
ENV EXPORTER_PORT="9877" \
    STAYTUS_API_URL="http://staytus:8787/" \
    POLLING_INTERVAL_SECONDS="2"
CMD ["python3", "src/main.py"]

FROM blueprint as ci
COPY tests ./tests
RUN python3 -m pip install \
    --no-cache-dir \
    -r ./tests/requirements.txt
CMD ["python3", "-m", "pytest", "tests"]
