import logging
import os
from datetime import datetime

def setup_logger(log_file: str = "app.log"):
    """
    Thiết lập logger: ghi log vào logs/app.log và hiển thị ra console.
    Gọi tự động khi file được import.
    """
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    full_path = os.path.join(log_dir, log_file)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(full_path, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    logging.info(" Logger started at %s", datetime.now().isoformat())

# Gọi tự động khi file được import
setup_logger()
