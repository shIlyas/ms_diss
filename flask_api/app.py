from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config
from controllers.user_controller import user_bp
from dotenv import load_dotenv
import os
app = Flask(__name__)


# Load environment variables based on FLASK_ENV
if os.getenv('FLASK_ENV') == 'production':
    load_dotenv('.env.prod')  # Load production environment variables
else:
    load_dotenv('.env')       # Load development environment variables

#env_config = config[os.getenv('FLASK_ENV') or 'development']
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

db = SQLAlchemy(app)

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(user_bp, url_prefix='/api')
    
    migrate.init_app(app, db)

    return app


# Optional: Define a CLI command to initialize the database
@app.cli.command()
def init_db():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)