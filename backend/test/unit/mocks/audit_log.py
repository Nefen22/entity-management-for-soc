import sys
import types

from unittest.mock import MagicMock


def install():

    mod = types.ModuleType("logs.audit_log")

    mod.write_audit_log = MagicMock()

    sys.modules["logs.audit_log"] = mod
    sys.modules["backend.logs.audit_log"] = mod