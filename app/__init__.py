from flask import Flask
from loglan_db import db, CLIConfig


def create_app(config, database):
    """
    Create app
    """

    # app initialization
    new_app = Flask(__name__)

    new_app.config.from_object(config)

    # db initialization
    database.init_app(new_app)

    # database.create_all(app=app) when use need to re-initialize db
    return new_app


app = create_app(config=CLIConfig, database=db)

from app import routes
