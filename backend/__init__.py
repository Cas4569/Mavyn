"""Enable the backend package path when Vercel imports ``backend.src.main``."""

import sys
from pathlib import Path

backend_root = str(Path(__file__).resolve().parent)
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)
