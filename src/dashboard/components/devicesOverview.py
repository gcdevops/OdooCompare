from flask import Flask
from src.data.load_data import load_odoo_data
from dash import Dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import pandas as pd 
import logging 

def devicesOverview(**props):
    
    flask_app = props["app"] # type: Flask
    dash_app = props["dash_app"] # type: Dash


    def calculate_devices(
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
        unique_employee_status = list(data[~data['x_employee_status'].isna()]['x_employee_status'].unique())
        unique_branches = list(data[~data['branch'].isna()]['branch'].unique())
        unique_jobs = list(data[~data['job'].isna()]['job'].unique())

        try:
            unique_employee_status.remove('False')
        except:
            pass

        try:
            unique_branches.remove('False')
        except:
            pass

        try:
            unique_jobs.remove('False')
        except:
            pass
    
        return {
            "unique_employee_status": unique_employee_status,
            "unique_branches": unique_branches,
            "unique_jobs": unique_jobs,
            "data": data
        }

    
    def calculate_device_numbers(
        data,
        branch_filters = [],
        status_filter = [],
        job_filter = [],
        critical_only = False
    ):
        count_dict = {
            'desktop': 0,
            'laptop': 0,
            'tablet': 0,
            'none': 0
        }

        filtered_data = data

        if critical_only:
            filtered_data = filtered_data[
                filtered_data['x_employee_work_criticality'] == True
            ]
        
        if len(branch_filters) > 0:
            filtered_data = filtered_data[
                filtered_data['branch'].isin(branch_filters)
            ]
        
        if len(job_filter) > 0:
            filtered_data = filtered_data[
                filtered_data['job'].isin(job_filter)
            ]
        
        if len(status_filter) > 0:
            filtered_data = filtered_data[
                filtered_data['x_employee_status'].isin(status_filter)
            ]
        
        if filtered_data.shape[0] > 0:
            for index, row in filtered_data.iterrows():
                device_type = row['x_employee_device_type']
                if device_type == 'desktop':
                    count_dict['desktop'] += 1
                elif device_type == 'laptop':
                    count_dict['laptop'] += 1
                elif device_type == 'tablet':
                    count_dict['tablet'] += 1
                else:
                    count_dict['none'] += 1
        
        return pd.DataFrame(
            {
                'devices': ['desktop', 'laptop', 'tablet', 'none'],
                'counts': [
                    count_dict['desktop'],
                    count_dict['laptop'],
                    count_dict['tablet'],
                    count_dict['none']
                ]
            }
        ), count_dict

    
    username = None 
    password = None
    database = None
    url = None 

    with flask_app.app_context():
        username = flask_app.config["ODOO_USERNAME"]
        password = flask_app.config["ODOO_PASSWORD"]
        database = flask_app.config["ODOO_DATABASE"]
        url = flask_app.config["ODOO_URL"]

        data_dict = calculate_devices(
            username,
            password,
            database,
            url
        )

        calculated_counts_df, calculated_counts_dict = calculate_device_numbers(data_dict['data'])
    
    barChart = px.bar(
        calculated_counts_df,
        x='devices',
        y='counts',
        labels={
            'devices': 'Devices',
            'counts': 'Number Of Devices'
        },
        text='counts'
    )
    @dash_app.callback(
        [
            Output(
                component_id = "device-overview-number-of-laptops",
                component_property="children"
            ),
            Output(
                component_id = "device-overview-number-of-desktops",
                component_property="children"
            ),
            Output(
                component_id = "device-overview-number-of-tablets",
                component_property="children"
            ),
            Output(
                component_id = "device-overview-number-of-no-devices",
                component_property="children"
            ),
            Output(
                component_id = "device-overview-bar-chart",
                component_property="figure"
            )
        ]
        ,
        [
            Input(
                component_id='device-overview-branch-filter',
                component_property="value"
            ),
            Input(
                component_id='device-overview-employee-status-filter',
                component_property="value"
            ),
            Input(
                component_id='device-overview-employee-jobs-filter',
                component_property="value"
            ),
            Input(
                component_id="device-overview-critial-employee-filter",
                component_property="value"
            ),
            Input(
                component_id='interval-component',
                component_property='n_intervals'
            )
        ]
    )
    def recalculate_devices(branches, statuses, jobs, criticality, n):
        data_dict = calculate_devices(
            username,
            password,
            database,
            url
        )

        
        if isinstance(criticality, list) and len(criticality) > 0:
            criticality = True
        else:
            criticality = False
        
        calculated_counts_df, calculated_counts_dict = calculate_device_numbers(
            data_dict['data'],
            branches or [],
            statuses or [],
            jobs or [],
            criticality
        )

        barChart = px.bar(
            calculated_counts_df,
            x='devices',
            y='counts',
            labels={
                'devices': 'Devices',
                'counts': 'Number Of Devices'
            },
            text='counts'
        )

        return (
            calculated_counts_dict['laptop'],
            calculated_counts_dict['desktop'],
            calculated_counts_dict['tablet'],
            calculated_counts_dict['none'],
            barChart
        )

    return html.Div(
        className="elementContainer",
        children = [
            html.H2(
                className="deviceOverviewTitle",
                children=[
                    "Device Overview"
                ]
            ),
            html.Div(
                className = "deviceFilterContainer",
                children = [
                    html.Label(
                        children = [
                            "Branches",
                            dcc.Dropdown(
                                id="device-overview-branch-filter",
                                options = [{'label': i, 'value': i } for i in data_dict['unique_branches']],
                                multi=True,
                                style = {
                                    "width": "100%"
                                }
                            )
                        ]
                    )
                ]
            ),
            html.Div(
                className = "deviceFilterContainer",
                children = [
                    html.Label(
                        children = [
                            "Employee Status",
                            dcc.Dropdown(
                                id="device-overview-employee-status-filter",
                                options = [{'label': i, 'value': i } for i in data_dict['unique_employee_status']],
                                multi=True,
                                style = {
                                    "width": "100%"
                                }
                            )
                        ]
                    )
                ]
            ),
            html.Div(
                className = "deviceFilterContainer",
                children = [
                    html.Label(
                        children = [
                            "Jobs",
                            dcc.Dropdown(
                                id="device-overview-employee-jobs-filter",
                                options = [{'label': i, 'value': i } for i in data_dict['unique_jobs']],
                                multi=True,
                                style = {
                                    "width": "100%"
                                }
                            )
                        ]
                    )
                ]
            ),
            html.Div(
                className = "deviceFilterContainer",
                children = [
                    html.P(
                        style = {
                            "fontSize": "20px",
                            "fontWeight": "600",
                            "margin": "5px 2px"
                        },
                        children = [
                            "Critical Employees Only"
                        ]
                    ),
                    dcc.Checklist(
                        id="device-overview-critial-employee-filter",
                        options = [
                            {'label': "", 'value': 'True'}
                        ]
                    )
                ]
            ),
            html.Div(
                className = "deviceNumbersContainer",
                children = [
                    html.Div(
                        className = "deviceNumberContainer",
                        children = [
                            html.H3(
                                children = "Desktops",
                                style = {
                                    "margin": "0 2px"
                                }
                            ),
                            html.P(
                                id = "device-overview-number-of-desktops",
                                children = calculated_counts_dict['desktop']
                            )
                        ]
                    ),
                    html.Div(
                        className = "deviceNumberContainer",
                        children = [
                            html.H3(
                                children = "Laptops",
                                style = {
                                    "margin": "0 2px"
                                }
                            ),
                            html.P(
                                id = "device-overview-number-of-laptops",
                                children = calculated_counts_dict['laptop']
                            )
                        ]
                    ),
                    html.Div(
                        className = "deviceNumberContainer",
                        children = [
                            html.H3(
                                children = "Tablets",
                                style = {
                                    "margin": "0 2px"
                                }
                            ),
                            html.P(
                                id = "device-overview-number-of-tablets",
                                children = calculated_counts_dict['tablet']
                            )
                        ]
                    ),
                    html.Div(
                        className = "deviceNumberContainer",
                        children = [
                            html.H3(
                                children = "No Assigned Device",
                                style = {
                                    "margin": "0 2px"
                                }
                            ),
                            html.P(
                                id = "device-overview-number-of-no-devices",
                                children = calculated_counts_dict['none']
                            )
                        ]
                    ),
                    
                ]
            ),
            html.Div(
                className="deviceBarChartContainer",
                children = [
                    html.H3("Device Bar Chart"),
                    dcc.Graph(
                        id='device-overview-bar-chart',
                        responsive=True,
                        figure = barChart,
                        style = {
                            "width": "100%",
                            "height": "600px"
                        }
                    )
                ]
            )
        ]
    )

        

        