"""
Application exporter example
based on https://trstringer.com/quick-and-easy-prometheus-exporter/
"""

import os
import time
from prometheus_client import start_http_server, CollectorRegistry, Gauge, Enum


class StaytusExporter:
    """
    Loop to fetch and transform
    application metrics into Prometheus metrics.
    """

    def __init__(self):
        self.polling_interval_seconds = int(os.getenv("POLLING_INTERVAL_SECONDS", "2"))
        self.exporter_port = int(os.getenv("EXPORTER_PORT", "9877"))
        self.start_time = 0

        self.registry = CollectorRegistry()
        self.total_uptime = Gauge("app_uptime", "Uptime", registry=self.registry)
        self.health = Enum("app_health", "Health", states=["healthy", "unhealthy"], registry=self.registry)

    def run(self):
        self.start_time = int(time.time())
        start_http_server(self.exporter_port, registry=self.registry)
        self.run_metrics_loop()

    def run_metrics_loop(self):
        "Metrics fetching loop"
        while True:
            self.fetch()
            time.sleep(self.polling_interval_seconds)

    def fetch(self):
        """
        Get metrics from application and refresh Prometheus metrics with
        new values.
        """
        self.total_uptime.set(int(time.time()) - self.start_time)
        self.health.state("healthy")


def main():
    "Main entry point"
    StaytusExporter().run()


if __name__ == "__main__":
    main()
