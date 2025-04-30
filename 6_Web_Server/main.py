from config_loader import (
    load_config,
)
from logger import setup_logger
from flask_init import create_app

def main():
    config = load_config()
    logger = setup_logger()
    logger.info(f"Starting {config['app']['name']} v{config['app']['version']}")
    flask_app = create_app()
    flask_app.run(host="0.0.0.0")
    
if __name__ == "__main__":
    main()
