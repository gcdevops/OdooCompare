from flask import Flask


def create_app(env="production") -> Flask:

    app = Flask(__name__)

    @app.route("/")
    def hello_world():
        return "hello world"

    return app