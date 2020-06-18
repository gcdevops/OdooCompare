from src import create_app
import os 


APP_ENV = os.environ.get("APP_ENV")
FLASK_ENV = os.environ.get("FLASK_ENV")

if FLASK_ENV is None:
    if APP_ENV is None:
        FLASK_ENV = "production"
    else:
        FLASK_ENV = APP_ENV

app = create_app(FLASK_ENV)

if __name__ == "__main__":
    app.run_server()