"""Generate a local secret once. Never overwrites an existing .env file."""
from pathlib import Path
import secrets

target = Path(__file__).resolve().parent.parent / ".env"
if target.exists():
    print(".env already exists; preserved your settings.")
else:
    with target.open("x", encoding="utf-8") as handle:
        handle.write("DJANGO_DEBUG=True\nDJANGO_SECRET_KEY=" + secrets.token_urlsafe(60) + "\nDJANGO_ALLOWED_HOSTS=localhost,127.0.0.1\n")
    target.chmod(0o600)
    print("Created local .env. Do not upload this file. Production must use DEBUG=False and a new secret.")
