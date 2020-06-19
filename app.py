from src import create_app
import os 
import argparse
import sys
import getopt
from typing import Tuple

argumentlist = sys.argv[1:]
shortOps = "gh"
gnuOptions = ["generate", "help"]


APP_ENV = os.environ.get("APP_ENV")
FLASK_ENV = os.environ.get("FLASK_ENV")

if FLASK_ENV is None:
    if APP_ENV is None:
        FLASK_ENV = "production"
    else:
        FLASK_ENV = APP_ENV

if __name__ == "__main__":
    try:
        arg_values: tuple = getopt.getopt(
            argumentlist,
            shortOps,
            gnuOptions
        )
    except getopt.error as err:
        print(str(err))
        sys.exit(2)
    
    options: list = []
    if (len(arg_values) > 0):
        options = [arg[0][0] for arg in arg_values if len(arg) > 0 and len(arg[0]) > 0]
    
    if "--help" in options or "-h" in options:
        print(
"""
Usage: python app.py [Options]

app.py is used to run the development WSGI server or 
to generate the initial data csv from ODOO by id you
use the -g or --generate flag

Options
-------
--help -h Print this message 
--generate -g Generate the data csv from Odoo
"""
        )

        sys.exit(0)
    
    elif not "--generate" in options and not "-g" in options:
        app, server = create_app(FLASK_ENV)
        app.run_server()
    else: 
        create_app(FLASK_ENV)

else:
    app, server = create_app(FLASK_ENV)