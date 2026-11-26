import os
import sys
from pathlib import Path

source_dir = str(Path(__file__).resolve().parents[1])
if source_dir not in sys.path:
    sys.path.insert(0, source_dir)

from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_wsgi_application()
