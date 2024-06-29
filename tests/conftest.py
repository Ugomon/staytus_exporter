import os
import sys

import environ
import pytest
import requests
import requests_mock

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(root, "src")
sys.path.insert(0, src)

from config import StaytusExporterConfig
from exporter import StaytusExporter


@pytest.fixture(scope="function")
def exporter():
    envs_config = {
        "STAYTUS_API_URL": "http://staytus:8787/",
        "STAYTUS_API_TOKEN": "test",
        "STAYTUS_API_SECRET": "test",
        "DEBUG": "False",
    }
    config: StaytusExporterConfig = environ.to_config(StaytusExporterConfig, environ=envs_config)
    exporter = StaytusExporter(config=config)
    yield exporter
    exporter.stop()


@pytest.fixture(scope="function")
def mock_adapter(exporter):
    session: requests.Session = exporter.session
    mock_adapter = requests_mock.Adapter()
    session.mount("http://", mock_adapter)
    yield mock_adapter
    mock_adapter.close()
