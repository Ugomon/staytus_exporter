"""
Application exporter example
based on https://trstringer.com/quick-and-easy-prometheus-exporter/
"""

import os
import time
import logging
from prometheus_client import start_http_server, CollectorRegistry, Enum
import requests


class StaytusExporter:
    """
    Loop to fetch and transform
    application metrics into Prometheus metrics.
    """

    def __init__(self):
        self.polling_interval_seconds = int(os.getenv("POLLING_INTERVAL_SECONDS", "2"))
        self.exporter_port = int(os.getenv("EXPORTER_PORT", "9877"))
        self.staytus_api_url = os.getenv("STAYTUS_API_URL", "http://localhost:8787/")
        self.staytus_api_token = os.environ["STAYTUS_API_TOKEN"].strip()
        self.staytus_api_secret = os.environ["STAYTUS_API_SECRET"].strip()

        self.registry = CollectorRegistry()
        self.service_statuses_metric = Enum(
            name="service_status",
            documentation="Service Status",
            labelnames=["service_permalink"],
            states=["ok", "minor", "major", "maintenance"],
            registry=self.registry,
        )

    def run(self):
        logging.info("Run exporter.")
        start_http_server(self.exporter_port, registry=self.registry)
        self.run_metrics_loop()

    def run_metrics_loop(self):
        "Metrics fetching loop"
        while True:
            self.fetch()
            time.sleep(self.polling_interval_seconds)

    def fetch(self):
        "Metrics fetching method"
        logging.debug("Try to update metrics.")
        response = requests.get(
            url=f"{self.staytus_api_url}api/v1/services/all",
            headers={
                "X-Auth-Token": self.staytus_api_token,
                "X-Auth-Secret": self.staytus_api_secret,
            },
        )
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


def main():
    "Main entry point"
    logging.basicConfig(
        level=logging.DEBUG if os.getenv("DEBUG") else logging.INFO,
        format="%(asctime)s [%(levelname)s] <%(name)s> %(message)s",
    )
    StaytusExporter().run()


if __name__ == "__main__":
    main()
