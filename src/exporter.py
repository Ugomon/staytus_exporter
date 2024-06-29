import os
import time
import logging
from urllib.parse import urljoin
from threading import Thread
from wsgiref.simple_server import WSGIServer

from prometheus_client import start_http_server, CollectorRegistry, Enum
import requests

from config import StaytusExporterConfig


class StaytusExporter:
    """
    Loop to fetch and transform
    application metrics into Prometheus metrics.
    """

    _CHECK_INTERVAL_SECONDS: float = 0.05
    _USER_AGENT: str = "staytus_exporter"

    def __init__(self, config: StaytusExporterConfig):
        self.config = config
        self._stopped = False
        self._server_thread: Thread | None = None
        self._server: WSGIServer | None = None
        self._session: requests.Session | None = None

        self.registry = CollectorRegistry()
        self.service_statuses_metric = Enum(
            name="service_status",
            documentation="Service Status",
            labelnames=["service_permalink"],
            states=["ok", "minor", "major", "maintenance"],
            registry=self.registry,
        )
        self.staytus_health = Enum(
            name="staytus_health",
            documentation="Staytus Health",
            states=["healthy", "unhealthy"],
            registry=self.registry,
        )

    @property
    def stopped(self) -> bool:
        return self._stopped

    def stop(self):
        self._stopped = True
        if self._session is not None:
            self._session.close()
        if self._server is not None:
            self._server.server_close()

    def run(self):
        logging.info("Run exporter.")
        self._server_thread, self._server_thread = start_http_server(self.config.exporter_port, registry=self.registry)
        self._session: requests.Session = requests.Session()
        self._session.headers.update(
            {
                "X-Auth-Token": self.config.staytus_api_token,
                "X-Auth-Secret": self.config.staytus_api_secret,
                "User-Agent": self._USER_AGENT,
            }
        )
        self.run_metrics_loop()

    def run_metrics_loop(self):
        "Metrics fetching loop"
        last_update: float = 0.0
        while not self.stopped:
            now = time.time()
            if time.time() > last_update + self.config.polling_interval_seconds:
                try:
                    self.fetch()
                except (ValueError, TypeError, requests.RequestException) as err:
                    self.staytus_health.state("unhealthy")
                    logging.error("Error when requesting the status :: %s", err)
                else:
                    self.staytus_health.state("healthy")
                    last_update = now
            time.sleep(self._CHECK_INTERVAL_SECONDS)
        logging.info("Stopped.")

    def fetch(self):
        "Metrics fetching method"
        logging.debug("Try to update metrics.")
        response = self._session.get(url=urljoin(self.config.staytus_api_url, "/api/v1/services/all"))
        response.raise_for_status()
        staytus_data = response.json()
        if staytus_data.get("status") != "success":
            raise ValueError("invalid staytus_data.status")
        logging.debug("Success got staytus data.")
        for service_data in staytus_data["data"]:
            service_permalink = service_data["permalink"]
            service_status = service_data["status"]["status_type"]
            current_label = self.service_statuses_metric.labels(service_permalink=service_permalink)
            current_label.state(service_status)
        logging.debug("Success updated metrics.")
