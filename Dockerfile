FROM python:3.11-alpine AS app
WORKDIR /opt/exporter
COPY src/requirements.txt ./requirements.txt
RUN python3 -m pip install \
    --no-cache-dir \
    -r ./requirements.txt
COPY src/* ./
EXPOSE 9877/tcp
ENV EXPORTER_PORT="9877" \
    STAYTUS_API_URL="http://staytus:8787/" \
    POLLING_INTERVAL_SECONDS="2"
USER nobody
CMD ["python3", "main.py"]
