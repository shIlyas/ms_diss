# flask_api/app.p
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import config
from dotenv import load_dotenv
from flask_migrate import Migrate
import os
import logging
from flask_cors import CORS

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
db = SQLAlchemy()
migrate = Migrate() 

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(f"config.{os.getenv('FLASK_ENV').capitalize()}Config")
    db.init_app(app)
    migrate.init_app(app, db)
    # Enable CORS for the app
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
    from controllers.user_controller import user_bp
    from controllers.assistant_scenario_controller import assistant_bp
    from controllers.rubric_question_controller import rubric_bp
    from controllers.openai_controller import openai_assistant_bp
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(assistant_bp, url_prefix='/api')
    app.register_blueprint(rubric_bp, url_prefix='/api')
    app.register_blueprint(openai_assistant_bp, url_prefix='/api')
    return app



if __name__ == '__main__':
    app = create_app()
    # Enable CORS for the app
    #
    # CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
    app.run(debug=os.getenv('FLASK_ENV') == 'development')
