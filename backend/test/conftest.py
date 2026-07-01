# conftest.py
import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from main import app  
from dotenv import load_dotenv

backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# 1. Load file .env cục bộ lên trước (nếu có)
load_dotenv(backend_dir / ".env")

@pytest.fixture(scope="session")
def api():
    with TestClient(app) as client:
        yield client