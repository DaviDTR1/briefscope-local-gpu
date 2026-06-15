"""
Logging centralizado para BriefScope.

Uso en cualquier módulo:
    from app.logging_config import logger
    logger.info("Proyecto %s creado", project_id)
    logger.exception("Error inesperado")   # incluye traceback
"""
import logging
import sys
from pathlib import Path
from app.config import DATA_DIR

LOG_FILE = DATA_DIR / "briefscope.log"
LOG_FORMAT = "[%(asctime)s] %(levelname)-8s %(name)s — %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _setup() -> logging.Logger:
    log = logging.getLogger("briefscope")
    if log.handlers:
        return log  # already configured

    log.setLevel(logging.DEBUG)

    # Console handler — INFO and above
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

    # File handler — DEBUG and above (rotates manually; add RotatingFileHandler for production)
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        log.addHandler(fh)
    except OSError as e:
        print(f"[briefscope] Could not create the log file: {e}")

    log.addHandler(ch)
    log.propagate = False
    return log


logger = _setup()
