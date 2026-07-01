import os
import sys
import re
import types
from pathlib import Path
from dotenv import load_dotenv
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

# 1. Thêm thư mục 'backend' vào sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)


# 2. CHẶN ĐỨNG LỖI GHI FILE TRONG LIFESPAN BẰNG CÁCH MOCK PATH.WRITE_TEXT
# Tạo một context/fixture chạy ngầm tự động để "bịt" lệnh write_text tuyệt đối của /app lại
@pytest.fixture(autouse=True, scope="session")
def mock_global_path_write():
    original_write_text = Path.write_text
    
    def patched_write_text(self, *args, **kwargs):
        # Nếu code thật cố gắng ghi vào đường dẫn tuyệt đối /app/backend/logs thì bỏ qua
        if "/app/" in str(self):
            return 0
        return original_write_text(self, *args, **kwargs)
        
    with patch.object(Path, "write_text", patched_write_text):
        yield


# 3. MOCK TẦNG THẤP: SYSTEM MODULES (Chặn đứng ModuleNotFoundError cho 'datasets')
datasets_mod = types.ModuleType("datasets")
seed_submod = types.ModuleType("datasets.seed")

DEMO_DATASETS = {
    "acme": "demo/sample_data.json",
    "google": "demo/sample_data1.json",
    "internal": "demo/sample_data2.json"
}
TEST_DATASETS = {
    "phishing": "test/phishing.json",
    "ransomware": "test/ransomeware.json",
    "insider_threat": "test/insider_threat.json"
}
SEED_MATRIX = {
    "DEMO": DEMO_DATASETS,
    "TEST": TEST_DATASETS
}

seed_submod.SEED = SEED_MATRIX

sys.modules["datasets"] = datasets_mod
sys.modules["datasets.seed"] = seed_submod
sys.modules["backend.datasets"] = datasets_mod
sys.modules["backend.datasets.seed"] = seed_submod

# Mock module audit log phòng hờ
mock_audit_log_mod = types.ModuleType("logs.audit_log")
mock_audit_log_mod.write_audit_log = MagicMock()
sys.modules["logs.audit_log"] = mock_audit_log_mod
sys.modules["backend.logs.audit_log"] = mock_audit_log_mod


# 4. Tải các biến môi trường
load_dotenv(os.path.join(backend_dir, ".env"))
if not os.getenv("NEO4J_URI"):
    os.environ["NEO4J_URI"] = "neo4j://localhost:7687"

# ── Cấu hình Fake Constraints cho Mock Database Router ──────────────────────

MAPPING_ENTITIES_TYPE = {
    "users": "User", "hosts": "Host", "ips": "IP", "domains": "Domain",
    "file_hashes": "FileHash", "urls": "URL", "processes": "Process",
    "emails": "Email", "cloud_resources": "CloudResource", "cves": "CVE"
}
MAPPING_RELATIONSHIPS = {
    ("User", "Host"): "LOGGED_IN", ("IP", "Host"): "CONNECTED_TO",
    ("Host", "IP"): "CONNECTED_TO", ("Host", "Domain"): "RESOLVED",
    ("FileHash", "Host"): "EXECUTED_ON", ("Process", "Host"): "RUNS_ON",
    ("Process", "Process"): "SPAWNED", ("Email", "Email"): "SENT_TO"
}
SIEM_INCLUDE = {
    "nodes": {"users": ["user"], "ips": ["source_ip"], "hosts": ["destination_host"]},
    "edges": [("source_ip", "destination_host"), ("user", "destination_host")]
}
EDR_INCLUDE = {
    "nodes": {
        "users": ["user"], "hosts": ["destination_host"], "ips": ["destination_ip"],
        "domains": ["destination_domain"], "file_hashes": ["file_hash"],
        "processes": ["process_name"], "parent_processes": ["parent_process"]
    },
    "edges": [
        ("destination_host", "destination_ip"), ("destination_host", "destination_domain"),
        ("user", "destination_host"), ("file_hash", "destination_host"),
        ("process_name", "destination_host"), ("parent_process", "process_name")
    ]
}
CLOUD_INCLUDE = {
    "nodes": {"hosts": ["source_host"], "ips": ["destination_ip"], "domains": ["destination_domain"]},
    "edges": [("source_host", "destination_ip"), ("source_host", "destination_domain")]
}
ALL_PATTERNS = {
    "ips": [re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')],
    "domains": [re.compile(r'\b(?:[a-z0-9\-]+\.)+(?:com|ru|net|org|io|local)\b')],
    "file_hashes": [re.compile(r'\b[a-fA-F0-9]{32}\b|\b[a-fA-F0-9]{40}\b|\b[a-fA-F0-9]{64}\b')]
}
REVERSED_TYPE = {v: k for k, v in MAPPING_ENTITIES_TYPE.items()}
MAPPING_ENTITIES_KEY = {
    "User": "username", "Host": "hostname", "IP": "value", "Domain": "name", "FileHash": "hash_value"
}
TENANT_DATABASE = {
    "default": "default", "acme": "acme", "google": "google_db", "internal": "internal_db"
}

@pytest.fixture(autouse=True)
def patch_constraints():
    """Patch backend.database.constraints để cô lập logic kiểm tra tenant."""
    const_mod = types.ModuleType("backend.database.constraints")
    const_mod.MAPPING_ENTITIES_TYPE = MAPPING_ENTITIES_TYPE
    const_mod.MAPPING_RELATIONSHIPS = MAPPING_RELATIONSHIPS
    const_mod.SIEM_INCLUDE = SIEM_INCLUDE
    const_mod.EDR_INCLUDE = EDR_INCLUDE
    const_mod.CLOUD_INCLUDE = CLOUD_INCLUDE
    const_mod.ALL_PATTERNS = ALL_PATTERNS
    const_mod.REVERSED_TYPE = REVERSED_TYPE
    const_mod.MAPPING_ENTITIES_KEY = MAPPING_ENTITIES_KEY
    const_mod.TENANT_DATABASE = TENANT_DATABASE

    sys.modules["backend.database.constraints"] = const_mod
    yield

# ── Mô phỏng kiến trúc Async Neo4j Driver cho tầng Service ───────────────────

@pytest.fixture
def mock_neo4j_session():
    """Async mock Neo4j session mô phỏng AsyncResult.data() coroutine."""
    session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.data = AsyncMock(return_value=[])
    session.run = AsyncMock(return_value=mock_result)
    return session

@pytest.fixture
def mock_neo4j_driver(mock_neo4j_session):
    """Mock Driver quản lý vòng đời Context Manager Async."""
    driver = MagicMock()
    driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_neo4j_session)
    driver.session.return_value.__aexit__ = AsyncMock(return_value=False)
    return driver