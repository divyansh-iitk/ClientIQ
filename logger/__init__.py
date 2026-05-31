import logging
import os

from from_root import from_root
from datetime import datetime


project_root = from_root()

log_dir = 'logs'

LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

logs_path = os.path.join(project_root, log_dir, LOG_FILE)

os.makedirs(log_dir, exist_ok=True)


logging.basicConfig(
    filename=logs_path,
    format="[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)


if __name__=="__main__":
    logging.info("Logger woking properly")