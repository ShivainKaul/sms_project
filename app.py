from flask import Flask
from config import Config
from db import init_indexes
from auth import auth_bp, login_manager
from main import main_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    login_manager.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    init_indexes()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
