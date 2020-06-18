import xmlrpc.client
import logging
from flask import g, Flask

def connect_to_rpc(
    username: str, 
    password: str,
    db: str,
    url: str
):
    if not "models" in g:
        try:
            common = xmlrpc.client.ServerProxy(
                url + "/xmlrpc/2/common"
            )
            common.version()
            uid = common.authenticate(
                db, 
                username, 
                password, 
                {}
            )

            models = xmlrpc.client.ServerProxy(
                url + "/xmlrpc/2/object"
            )

            g.models = models
            g.uid = uid
            g.db = db 
            g.password = password
            return models, uid, db, password
        except Exception as e:
            logging.critical(
                "Failed to authenticate against Odoo Endpoint"
            )
            raise e

    return g.models, g.uid, g.db, g.password


def close_rpc_connection(e=None):
    g.pop('db', None)
    g.pop("uid", None)
    g.pop("password", None)
    g.pop("models", None)


def init_app(app:Flask):
    app.teardown_appcontext(close_rpc_connection)




