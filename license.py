"""Org license checks for paid pipeline-kit areas.

Customers activate a token. A maintainer signs one from a kit checkout.
Verification uses the Ed25519 public key in license_public_key.txt.
"""

from __future__ import annotations

import base64
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ENV_LICENSE = "PIPELINE_KIT_LICENSE"
ENV_SIGNING_KEY = "PIPELINE_KIT_LICENSE_SIGNING_KEY"
EXIT_LICENSE = 73

FEATURES = ("orchestrator", "jira", "governance", "evidence")
JIRA_WORKFLOWS = frozenset({"jira-story", "jira-epic", "jira-bug"})
GOVERNANCE_WORKFLOWS = frozenset(
    {
        "security-review",
        "ci-audit",
        "dependency-audit",
        "accessibility-review",
    }
)
PAID_FLAGS = {
    "jira-intake": "jira",
    "agent-observability": "evidence",
}


class LicenseError(ValueError):
    """Token cannot be accepted."""


def feature_for_workflow(name: str) -> str:
    key = name.strip().lower()
    if key in JIRA_WORKFLOWS:
        return "jira"
    if key in GOVERNANCE_WORKFLOWS:
        return "governance"
    return "orchestrator"


def license_path(home: Path | None = None) -> Path:
    return (home or Path.home()) / ".pipeline" / "license.json"


def public_key_path() -> Path:
    return Path(__file__).resolve().parent / "license_public_key.txt"


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64_decode(text: str) -> bytes:
    pad = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + pad)


def _ed25519():
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PrivateKey,
            Ed25519PublicKey,
        )
    except ImportError as exc:
        raise LicenseError("cryptography is required to check a license") from exc
    return Ed25519PrivateKey, Ed25519PublicKey


def _public_key():
    _, public_type = _ed25519()
    from cryptography.hazmat.primitives.serialization import load_pem_public_key

    try:
        text = public_key_path().read_text(encoding="utf-8")
    except OSError as exc:
        raise LicenseError("license public key is missing") from exc
    body = "".join(
        line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")
    )
    pem = "-----BEGIN PUBLIC KEY-----\n" + body + "\n-----END PUBLIC KEY-----\n"
    try:
        key = load_pem_public_key(pem.encode("ascii"))
    except Exception as exc:
        raise LicenseError("license public key is invalid") from exc
    if not isinstance(key, public_type):
        raise LicenseError("license public key must be Ed25519")
    return key


def sign_token(signing_key, *, org: str, exp: int, features: list[str]) -> str:
    org_name = org.strip()
    if not org_name:
        raise LicenseError("org is required")
    unknown = [item for item in features if item not in FEATURES]
    if unknown:
        raise LicenseError("unknown feature: " + ", ".join(unknown))
    if not features:
        raise LicenseError("at least one feature is required")
    payload = json.dumps(
        {"exp": int(exp), "features": sorted(set(features)), "org": org_name},
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return f"{_b64(payload)}.{_b64(signing_key.sign(payload))}"


def verify_token(token: str) -> dict:
    parts = token.strip().split(".")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise LicenseError("missing")
    try:
        payload = _b64_decode(parts[0])
        signature = _b64_decode(parts[1])
        _public_key().verify(signature, payload)
        data = json.loads(payload.decode("utf-8"))
    except LicenseError:
        raise
    except Exception as exc:
        raise LicenseError("missing") from exc
    if not isinstance(data, dict):
        raise LicenseError("missing")
    org = data.get("org")
    exp = data.get("exp")
    features = data.get("features")
    if not isinstance(org, str) or not org.strip():
        raise LicenseError("missing")
    if not isinstance(exp, int) or isinstance(exp, bool):
        raise LicenseError("missing")
    if not isinstance(features, list) or not all(isinstance(item, str) for item in features):
        raise LicenseError("missing")
    if exp < int(time.time()):
        raise LicenseError("expired")
    return {"org": org.strip(), "exp": exp, "features": features}


def read_token(*, home: Path | None = None) -> str:
    env = os.environ.get(ENV_LICENSE, "").strip()
    if env:
        return env
    path = license_path(home)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LicenseError("missing") from exc
    token = data.get("token") if isinstance(data, dict) else None
    if not isinstance(token, str) or not token.strip():
        raise LicenseError("missing")
    return token.strip()


def require(feature: str, *, home: Path | None = None) -> int:
    if feature not in FEATURES:
        raise LicenseError(f"unknown feature: {feature}")
    try:
        claims = verify_token(read_token(home=home))
    except LicenseError as exc:
        print(
            f"license: {exc}. Run: pipeline-kit license activate",
            file=sys.stderr,
        )
        return EXIT_LICENSE
    if feature not in claims["features"]:
        print(
            f"license: {feature} is not on this license. Run: pipeline-kit license activate",
            file=sys.stderr,
        )
        return EXIT_LICENSE
    return 0


def _expiry_day(text: str) -> int:
    try:
        day = datetime.strptime(text.strip(), "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise LicenseError("--expires must be YYYY-MM-DD") from exc
    end = day + timedelta(days=1) - timedelta(seconds=1)
    return int(end.timestamp())


def _load_signing_key(path: Path):
    signing_type, _ = _ed25519()
    from cryptography.hazmat.primitives.serialization import load_pem_private_key

    try:
        key = load_pem_private_key(path.read_bytes(), password=None)
    except Exception as exc:
        raise LicenseError(f"cannot read signing key: {path}") from exc
    if not isinstance(key, signing_type):
        raise LicenseError("signing key must be Ed25519")
    return key


def _parse_features(text: str) -> list[str]:
    items = [part.strip() for part in text.split(",") if part.strip()]
    unknown = [item for item in items if item not in FEATURES]
    if unknown or not items:
        raise LicenseError("features must be a comma list of: " + ", ".join(FEATURES))
    return items


def signing_key_path() -> str:
    configured = os.environ.get(ENV_SIGNING_KEY, "").strip()
    if configured:
        return configured
    return os.environ.get("PIPELINE_KIT_LICENSE_PRIVATE_KEY", "").strip()


def cmd_issue(*, org: str, expires: str, features: str) -> int:
    key_path = signing_key_path()
    if not key_path:
        print(f"set {ENV_SIGNING_KEY} to the Ed25519 signing key file", file=sys.stderr)
        return 64
    path = Path(key_path).expanduser()
    if not path.is_file():
        print(f"signing key not found: {path}", file=sys.stderr)
        return 64
    try:
        token = sign_token(
            _load_signing_key(path),
            org=org,
            exp=_expiry_day(expires),
            features=_parse_features(features),
        )
    except LicenseError as exc:
        print(str(exc), file=sys.stderr)
        return 64
    print(f"issued {org.strip()} through {expires.strip()}", file=sys.stderr)
    print(token)
    return 0


def cmd_activate(*, home: Path | None = None) -> int:
    token = os.environ.get(ENV_LICENSE, "").strip()
    if not token:
        print(f"set {ENV_LICENSE} to the token you were given", file=sys.stderr)
        return EXIT_LICENSE
    try:
        claims = verify_token(token)
    except LicenseError as exc:
        print(
            f"license: {exc}. Run: pipeline-kit license activate",
            file=sys.stderr,
        )
        return EXIT_LICENSE
    path = license_path(home)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"token": token}) + "\n", encoding="utf-8")
    path.chmod(0o600)
    print(f"license active for {claims['org']}")
    return 0


def cmd_status(*, home: Path | None = None) -> int:
    try:
        claims = verify_token(read_token(home=home))
    except LicenseError as exc:
        print(
            f"license: {exc}. Run: pipeline-kit license activate",
            file=sys.stderr,
        )
        return EXIT_LICENSE
    expires = datetime.fromtimestamp(claims["exp"], timezone.utc).strftime("%Y-%m-%d")
    print(f"org: {claims['org']}")
    print(f"expires: {expires}")
    enabled = set(claims["features"])
    for feature in FEATURES:
        print(f"{feature}: {'on' if feature in enabled else 'off'}")
    return 0
