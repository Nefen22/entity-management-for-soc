from pathlib import Path

import pytest

from unittest.mock import MagicMock, patch

from mocks.enrichment import mock_city, mock_asn
from mocks import audit_log
from mocks import datasets
from mocks import constraints
from mocks import neo4j

datasets.install()
audit_log.install()
constraints.install()
neo4j.build_driver()

@pytest.fixture(scope="session", autouse=True)
def patch_write_text():

    original = Path.write_text

    def fake(self, *args, **kwargs):

        if "/app/" in str(self):
            return 0

        return original(self, *args, **kwargs)

    with patch.object(Path, "write_text", fake):

        yield


@pytest.fixture
def geoip_reader():
    with patch("geoip2.database.Reader") as reader_cls:

        reader = MagicMock()

        reader.city.return_value = mock_city()
        reader.asn.return_value = mock_asn()

        reader_cls.return_value = reader

        yield reader


@pytest.fixture
def vt_dataset():
    return {
        "44d88612fea8a8f36de82e1278abb02f": {
            "malicious": True,
            "family": "Eicar-Test-File",
            "detections": 52
        }
    }

