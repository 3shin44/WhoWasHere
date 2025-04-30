from config_loader import (
    load_config,
)
from logger import setup_logger
from flask_init import create_app


config = load_config()
logger = setup_logger()
logger.info(f"Starting [WSGI] {config['app']['name']} v{config['app']['version']}")
flask_app = create_app()