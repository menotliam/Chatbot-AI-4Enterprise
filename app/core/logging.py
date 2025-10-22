import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Tạo thư mục logs nếu chưa có
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"

def init_logging():
    # Tạo logger
    logger = logging.getLogger()
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Format log
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler ghi ra console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Handler ghi ra file (với rotate log - mỗi file tối đa 1MB, giữ 3 bản)
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=1_000_000, backupCount=3
    )
    file_handler.setFormatter(formatter)

    # Tránh nhân bản logger nếu đã add handler trước đó
    if not logger.hasHandlers():
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
