# backend/test/integration/conftest.py
import os
import json
import pytest
from services.graph import ingest_sample
from database.constraints import TENANT_DATABASE
import os
import pytest

TEST_DATASETS = {
    "phishing": "test/phishing.json",
    "ransomware": "test/ransomware.json",
    "insider_threat": "test/insider_threat.json",
}
