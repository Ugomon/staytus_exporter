#!/usr/bin/env python3
"""Entrypoint"""
import logging
import os
import signal

from config import get_config
from exporter import StaytusExporter


def main():
    "Main entry point"
    logging.basicConfig(
        level=logging.DEBUG if os.getenv("DEBUG") else logging.INFO,
        format="%(asctime)s [%(levelname)s] <%(name)s> %(message)s",
    )
    config = get_config()
    app = StaytusExporter(config)
    signal.signal(signal.SIGINT, lambda *args: app.stop())
    signal.signal(signal.SIGTERM, lambda *args: app.stop())
    app.run()


if __name__ == "__main__":
    main()
