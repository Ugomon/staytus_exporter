"""Get configs from environment variables."""

from urllib.parse import urlparse
import environ  # https://environ-config.readthedocs.io/en/stable/index.html


@environ.config(prefix="")
class StaytusExporterConfig:
    """Overall staytus exporter configuration."""

    polling_interval_seconds: int = environ.var(2, int)
    exporter_port: int = environ.var(9877, int)
    staytus_api_url: str = environ.var("http://localhost:8787/")
    staytus_api_token: str = environ.var()
    staytus_api_secret: str = environ.var()
    debug: bool = environ.bool_var(False)

    @polling_interval_seconds.validator
    def _ensure_interval_correct(self, var, interval) -> None:
        if not 0 < interval <= 60:
            raise ValueError(f"invalid polling_interval_seconds (1...60) {var=} {interval=}")

    @exporter_port.validator
    def _ensure_port_correct(self, var, port) -> None:
        if not 1024 < port <= 65535:
            raise ValueError(f"invalid exporter_port {var=} {port=}")

    @staytus_api_url.validator
    def _ensure_url_correct(self, var, _url) -> None:
        url = urlparse(_url)
        if url.scheme not in ("", "http", "https"):
            raise ValueError(f"invalid {var=} {url.scheme=}")
        if not url.netloc:
            raise ValueError(f"invalid {var=} {url.netloc=}")


def get_config() -> StaytusExporterConfig:
    """Parse config from envs and return it"""
    return environ.to_config(StaytusExporterConfig)
