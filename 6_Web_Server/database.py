from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    get_db_path = f"sqlite:////app/db/{app.config['WS_DATABASE_NAME']}"
    app.config['SQLALCHEMY_DATABASE_URI'] = get_db_path 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)