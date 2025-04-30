from config_loader import (
    load_config,
)
from flask_init import create_app
from logger import setup_logger

config = load_config()
logger = setup_logger()
logger.info(f"Starting [WSGI] {config['app']['name']} v{config['app']['version']}")
flask_app = create_app()
