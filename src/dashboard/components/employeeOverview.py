from flask import Flask 
from src.data.load_data import load_odoo_data
from dash import Dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import logging 



def employeeOverview(**props):

    flask_app = props["app"] # type: Flask
    dash_app = props["dash_app"] # type: Dash

    def calculate_critical_employees(
        username,
        password,
        database,
        url 
    ):
        data = load_odoo_data(
            username,
            password,
            database,
            url,
            flask_app
        )

        critical_employees = None
        non_critical_employees = None
        number_of_employees = data.shape[0] 
        if number_of_employees > 0 :
            critical_employees = 0
            for index, row in data.iterrows():
                if row['x_employee_work_criticality'] is True:
                    critical_employees += 1
            
            non_critical_employees = number_of_employees - critical_employees
        
        return {
            'critical_employees' : critical_employees, 
            'non_critical_employees': non_critical_employees,
            'employees': number_of_employees if number_of_employees > 0 else None
        }

    username = None
    password = None
    database = None
    url = None 


    with flask_app.app_context():
        username = flask_app.config["ODOO_USERNAME"]
        password = flask_app.config["ODOO_PASSWORD"]
        database = flask_app.config["ODOO_DATABASE"]
        url = flask_app.config["ODOO_URL"]
        data_dict = calculate_critical_employees(
            username,
            password,
            database,
            url
        )
        
    pieChart = px.pie(
        {
            "Name Of Section": ["Critical Employees", "Non Critical Employees"],
            "Number of Employees": [
                data_dict.get("critical_employees"), 
                data_dict.get("non_critical_employees")
            ]
        },
        names="Name Of Section",
        values="Number of Employees"
    )

    
    @dash_app.callback(
        [
            Output(
                component_id = "employee-overview-number-of-employees",
                component_property="children"
            ),
            Output(
                component_id= "employee-overview-number-of-critical-employees",
                component_property="children"
            ),
            Output(
                component_id= "employee-overview-pie-chart",
                component_property="figure"
            )
        ],
        [
            Input(
                component_id='interval-component',
                component_property='n_intervals'
            )
        ]
    )
    def calculate_changes(n):
        data_dict = calculate_critical_employees(
            username,
            password,
            database,
            url
        )

        pieChart = px.pie(
            {
                "Name Of Section": ["Critical Employees", "Non Critical Employees"],
                "Number of Employees": [
                    data_dict.get("critical_employees"), 
                    data_dict.get("non_critical_employees")
                ]
            },
            names="Name Of Section",
            values="Number of Employees"
        )

        num_employees = str(data_dict.get("employees"))
        critical_employees = str(data_dict.get("critical_employees"))

        return num_employees, critical_employees, pieChart
    

    return  html.Div(
        className="elementContainer",
        children = [
            html.Div(
                className="numberOfEmployeesContainer",
                children = [
                    html.H2("Number of Employees"),
                    html.P(
                        id="employee-overview-number-of-employees",
                        children = str(data_dict.get("employees"))
                    )
                ]
            ),
            html.Div(
                className="numberOfCriticalEmployeesContainer",
                children = [
                    html.H3("Number of Critical Employees"),
                    html.P(
                        id="employee-overview-number-of-critical-employees",
                        children = str(data_dict.get('critical_employees'))
                    )
                ]
            ),
            html.Div(
                className="employeesPieChartContainer",
                children = [
                    html.H3("Employees Criticality Pie Chart"),
                    dcc.Graph(
                        id="employee-overview-pie-chart",
                        responsive=True,
                        figure = pieChart,
                        style = {
                            "width": "100%",
                            "height": "300px"
                        }
                    )
                ]
            )
        ]
    )