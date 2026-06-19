import sys
from pathlib import Path
from loguru import logger

LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)

logger.remove()

logger.add(sys.stdout, format='<green>{time:YYYY-MM-DD HH:mm:ss}</green> | '
                              '<level>{level: <8}</level> |'
                              '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - '
                              '<level>{message}</level>',
           level='INFO', enqueue=True)

logger.add(LOG_DIR / 'app.log', format='<green>{time:YYYY-MM-DD HH:mm:ss}</green> | '
                              '<level>{level: <8}</level> |'
                              '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - '
                              '<level>{message}</level>',
           level='DEBUG', rotation='10 MB', retention='5 days', compression='zip', enqueue=True)
