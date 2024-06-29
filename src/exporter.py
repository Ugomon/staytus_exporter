"""StaytusExporter class."""

import logging
import time
from threading import Thread
from urllib.parse import urljoin
from wsgiref.simple_server import WSGIServer

import requests
from prometheus_client import CollectorRegistry, Enum, start_http_server

from config import StaytusExporterConfig


class StaytusExporter:  # pylint: disable=R0902
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
        self._session: requests.Session = requests.Session()
        self._registry = CollectorRegistry()
        self._last_update: float = 0.0
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
    def registry(self) -> CollectorRegistry:
        """Used CollectorRegistry"""
        return self._registry

    @property
    def session(self) -> requests.Session:
        """Used requests.Session"""
        return self._session

    @property
    def stopped(self) -> bool:
        """Is the Exporter stopped"""
        return self._stopped

    def stop(self):
        """Stop the Exporter correctly."""
        self._stopped = True
        if self.session is not None:
            self.session.close()
        if self._server is not None:
            self._server.server_close()

    def run(self):
        """Run the Exporter."""
        logging.info("Run exporter.")
        self._server_thread, self._server_thread = start_http_server(
            self.config.exporter_port, registry=self.registry
        )
        self.session.headers.update(
            {
                "X-Auth-Token": self.config.staytus_api_token,
                "X-Auth-Secret": self.config.staytus_api_secret,
                "User-Agent": self._USER_AGENT,
            }
        )
        self.run_metrics_loop()

    def run_metrics_loop(self):
        "Metrics fetching loop"
        while not self.stopped:
            if time.time() > self._last_update + self.config.polling_interval_seconds:
                self.fetch()
            time.sleep(self._CHECK_INTERVAL_SECONDS)
        logging.info("Stopped.")

    def fetch(self):
        "Metrics fetching method"
        logging.debug("Try to update metrics.")
        try:
            self._fetch()
        except (ValueError, TypeError, requests.RequestException) as err:
            self.staytus_health.state("unhealthy")
            logging.error("Error when requesting the status :: %s", err)
        else:
            self.staytus_health.state("healthy")
            self._last_update = time.time()
        logging.debug("Success updated metrics.")

    def _fetch(self):
        response = self.session.get(
            url=urljoin(self.config.staytus_api_url, "/api/v1/services/all")
        )
        response.raise_for_status()
        staytus_data = response.json()
        if staytus_data.get("status") != "success":
            raise ValueError("invalid staytus_data.status")
        logging.debug("Success got staytus data.")
        for service_data in staytus_data["data"]:
            service_permalink = service_data["permalink"]
            service_status = service_data["status"]["status_type"]
            current_label = self.service_statuses_metric.labels(
                service_permalink=service_permalink
            )
            current_label.state(service_status)
