from flask import Flask
from env_config import Config
from database import init_db
from routes import bp as api_bp
from flask_cors import CORS

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    init_db(app)
    
    CORS(app)
    
    app.register_blueprint(api_bp)
    
    return app