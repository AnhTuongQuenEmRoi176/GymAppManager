import os
import sys
import types

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

# bcrypt có trong requirements; đoạn fallback này chỉ giúp một số môi trường CI
# có thể import app trước khi cài dependency native.
try:
    import bcrypt  # noqa: F401
except ImportError:  # pragma: no cover
    module = types.ModuleType("bcrypt")
    module.checkpw = lambda plain, hashed: True
    module.hashpw = lambda plain, salt: b"fake"
    module.gensalt = lambda rounds=12: b"salt"
    sys.modules["bcrypt"] = module

from app.main import app


def test_required_flutter_routes_exist():
    paths = {route.path for route in app.routes}
    required = {
        "/api/auth/login",
        "/api/auth/me",
        "/api/member/dashboard",
        "/api/trainer/dashboard",
        "/api/schedules",
        "/api/qr/token",
        "/api/checkins/history",
        "/api/trainer/members",
        "/api/notifications",
        "/ws",
    }
    assert required.issubset(paths)
