import dash_html_components as html 
import dash_core_components as dcc
from .components.employeeOverview import employeeOverview
from .components.devicesOverview import devicesOverview


def appLayout(app, dash_app):
    return html.Div(
        children = [
            html.H1("Whitelisting App Dashboard"),
            employeeOverview(
                app=app,
                dash_app=dash_app
            ),
            devicesOverview(
                app=app,
                dash_app=dash_app
            ),
            dcc.Interval(
                id="interval-component",
                interval=60*1000,
                n_intervals = 0
            )
        ]
    )