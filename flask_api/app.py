# flask_api/app.py

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import config
from dotenv import load_dotenv
from flask_migrate import Migrate
import os
db = SQLAlchemy()
migrate = Migrate() 

load_dotenv()

def create_app():
    app = Flask(__name__)
 
    app.config.from_object(f"config.{os.getenv('FLASK_ENV').capitalize()}Config")
    db.init_app(app)

    with app.app_context():
        db.create_all()
    from controllers.user_controller import user_bp
    app.register_blueprint(user_bp, url_prefix='/api')
    
    migrate.init_app(app, db)

    return app




if __name__ == '__main__':
    app = create_app()
    app.run()
