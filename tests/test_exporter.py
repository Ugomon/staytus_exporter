from http import HTTPMethod, HTTPStatus
import pytest
from prometheus_client import CollectorRegistry


@pytest.mark.usefixtures("exporter")
@pytest.mark.usefixtures("mock_adapter")
def test_success(exporter, mock_adapter):
    mock_adapter.register_uri(
        method=HTTPMethod.GET,
        url="http://staytus:8787/api/v1/services/all",
        status_code=HTTPStatus.OK,
        json={
            "status": "success",
            "data": [
                {
                    "permalink": "test-1",
                    "status": {
                        "status_type": "ok",
                    },
                },
                {
                    "permalink": "test-2",
                    "status": {
                        "status_type": "maintenance",
                    },
                },
            ],
        },
    )
    exporter.fetch()
    registry: CollectorRegistry = exporter.registry
    assert (
        registry.get_sample_value(
            name="service_status",
            labels={"service_permalink": "test-1", "service_status": "ok"},
        )
        == 1
    )
    assert (
        registry.get_sample_value(
            name="service_status",
            labels={"service_permalink": "test-1", "service_status": "minor"},
        )
        == 0
    )
    assert (
        registry.get_sample_value(
            name="service_status",
            labels={"service_permalink": "test-1", "service_status": "major"},
        )
        == 0
    )
    assert (
        registry.get_sample_value(
            name="service_status",
            labels={"service_permalink": "test-1", "service_status": "maintenance"},
        )
        == 0
    )

    assert (
        registry.get_sample_value(
            name="service_status",
            labels={"service_permalink": "test-2", "service_status": "ok"},
        )
        == 0
    )
    assert (
        registry.get_sample_value(
            name="service_status",
            labels={"service_permalink": "test-2", "service_status": "minor"},
        )
        == 0
    )
    assert (
        registry.get_sample_value(
            name="service_status",
            labels={"service_permalink": "test-2", "service_status": "major"},
        )
        == 0
    )
    assert (
        registry.get_sample_value(
            name="service_status",
            labels={"service_permalink": "test-2", "service_status": "maintenance"},
        )
        == 1
    )
    assert (
        registry.get_sample_value(
            name="staytus_health",
            labels={"staytus_health": "healthy"},
        )
        == 1
    )
    assert (
        registry.get_sample_value(
            name="staytus_health",
            labels={"staytus_health": "unhealthy"},
        )
        == 0
    )


@pytest.mark.usefixtures("exporter")
@pytest.mark.usefixtures("mock_adapter")
def test_404(exporter, mock_adapter):
    mock_adapter.register_uri(
        method=HTTPMethod.GET,
        url="http://staytus:8787/api/v1/services/all",
        status_code=HTTPStatus.NOT_FOUND,
    )
    exporter.fetch()
    registry: CollectorRegistry = exporter.registry
    assert (
        registry.get_sample_value(
            name="staytus_health",
            labels={"staytus_health": "healthy"},
        )
        == 0
    )
    assert (
        registry.get_sample_value(
            name="staytus_health",
            labels={"staytus_health": "unhealthy"},
        )
        == 1
    )


@pytest.mark.usefixtures("exporter")
@pytest.mark.usefixtures("mock_adapter")
def test_unsuccess(exporter, mock_adapter):
    mock_adapter.register_uri(
        method=HTTPMethod.GET,
        url="http://staytus:8787/api/v1/services/all",
        status_code=HTTPStatus.OK,
        json={"status": "error"},
    )
    exporter.fetch()
    registry: CollectorRegistry = exporter.registry
    assert (
        registry.get_sample_value(
            name="staytus_health",
            labels={"staytus_health": "healthy"},
        )
        == 0
    )
    assert (
        registry.get_sample_value(
            name="staytus_health",
            labels={"staytus_health": "unhealthy"},
        )
        == 1
    )
