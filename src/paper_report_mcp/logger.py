import logging.handlers
from paper_report_mcp.utils import root_dir

logger = logging.getLogger("logger")
logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(
    f"{root_dir}/logs/run.log", maxBytes=(1048576*5), backupCount=2
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
