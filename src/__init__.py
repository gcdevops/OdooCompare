from flask import Flask
import os 
import dash
import dash_html_components as html
from dotenv import load_dotenv
from typing import Tuple
import logging

load_dotenv()
 
def create_app(env="production") -> Tuple[dash.Dash, Flask]:

    server = Flask(__name__)

    # load environment variables into application configuration
    ODOO_URL = os.environ.get("ODOO_URL")
    ODOO_USERNAME = os.environ.get("ODOO_USERNAME")
    ODOO_PASSWORD = os.environ.get("ODOO_PASSWORD")
    ODOO_DATABASE = os.environ.get("ODOO_DATABASE")
    
    if env != "production" and ODOO_URL is None:
        ODOO_URL="http://localhost:8069"
    elif env == "production" and ODOO_URL is None:
        raise ValueError("ODOO_URL is required")

    if env != "production" and ODOO_DATABASE is None:
        ODOO_DATABASE="dev"
    elif env == "production" and ODOO_DATABASE is None:
        raise ValueError("ODOO_DATABASE is required")

    if env != "production" and ODOO_PASSWORD is None:
        ODOO_PASSWORD="odoo"
    elif env == "production" and ODOO_PASSWORD is None:
        raise ValueError("ODOO_PASSWORD is required")

    if env != "production" and ODOO_USERNAME is None:
        ODOO_USERNAME="odoo"
    elif env == "production" and ODOO_USERNAME is None:
        raise ValueError("ODOO_USERNAME is required")

    server.config["ODOO_URL"] = ODOO_URL
    server.config["ODOO_USERNAME"] = ODOO_USERNAME
    server.config["ODOO_PASSWORD"] = ODOO_PASSWORD
    server.config["ODOO_DATABASE"] = ODOO_DATABASE
    server.config["ENV"] = env
    
    @server.route("/api")
    def hello_world():
        return "hello world"
    
    # handler errors in the application context
    @server.errorhandler(Exception)
    def unknown_exception_handler(error):
        if (env != "production"):
            raise error
        else:
            logging.critical(str(error))
        return "An unknown error has occured, the exception is most likely logged", 500

    

    from src.utils.connect_to_odoo import init_app as init_rpc_connection 
    init_rpc_connection(server)

    # register dashly application with flask server
    app = dash.Dash(
        __name__,
        server=server,
        routes_pathname_prefix="/"
    )

    from src.dashboard import appLayout
    
    app.layout = appLayout(app = server, dash_app=app)

    return (app, server)