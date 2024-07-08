# flask_api/app.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from dotenv import load_dotenv
from flask_migrate import Migrate
import os

# Load environment variables based on FLASK_ENV
if os.getenv('FLASK_ENV') == 'production':
    load_dotenv('.env.prod')  # Load production environment variables
else:
    load_dotenv('.env')       # Load development environment variables

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        from controllers.user_controller import user_bp
        app.register_blueprint(user_bp, url_prefix='/api')
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
