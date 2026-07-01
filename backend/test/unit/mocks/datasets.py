import sys
import types

datasets_mod = types.ModuleType("datasets")
seed_mod = types.ModuleType("datasets.seed")

DEMO_DATASETS = {
    "acme": "demo/sample_data.json",
    "google": "demo/sample_data1.json",
    "internal": "demo/sample_data2.json",
}

TEST_DATASETS = {
    "phishing": "test/phishing.json",
    "ransomware": "test/ransomware.json",
    "insider_threat": "test/insider_threat.json",
}

seed_mod.SEED = {
    "DEMO": DEMO_DATASETS,
    "TEST": TEST_DATASETS,
}


def install():
    sys.modules["datasets"] = datasets_mod
    sys.modules["datasets.seed"] = seed_mod

    sys.modules["backend.datasets"] = datasets_mod
    sys.modules["backend.datasets.seed"] = seed_mod