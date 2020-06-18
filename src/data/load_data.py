import logging
import pandas
from flask import Flask
import os 
from src.utils.connect_to_odoo import connect_to_rpc
from datetime import datetime
from typing import cast


def download_odoo_data(
    username,
    password,
    database,
    url,
    path
):
    models, uid, db, password = connect_to_rpc(
        username, password,
        database, url
    )

    employees = models.execute_kw(
        db, uid, password,
        'hr.employee',
        'search_read',
        [[['active', '=', True]]],
        {
            'fields': [
                'x_employee_work_criticality',
                'job_id',
                'branch_id',
                'address_id',
                'region_id',
                'x_employee_status',
                'x_employee_device_type',
                'x_employee_remote_access_network',
                'x_employee_remote_access_tool',
            ]
        }
    )

    df = pandas.DataFrame(
        columns = [
            "job",
            "branch",
            "address",
            "region",
            "x_employee_work_criticality",
            "x_employee_status",
            "x_employee_device_type",
            "x_employee_remote_access_network",
            "x_employee_remote_access_tool"
        ]
    )

    if employees:
        count = 0 
        for row in employees:
            job_id = row["job_id"]
            job = None
            if job_id and len(job_id) > 0:
                job = job_id[1]
            
            branch_id = row["branch_id"]
            branch = None
            if branch_id and len(branch_id) > 0:
                branch = branch_id[1]

            address_id = row["address_id"]
            address = None
            if address_id and len(address_id) > 0:
                address = address_id[1]

            region_id = row["region_id"]
            region = None
            if region_id and len(region_id) > 0:
                region = region_id[1]

            df.loc[count] = [
                job,
                branch,
                address,
                region,
                row['x_employee_work_criticality'],
                row['x_employee_status'],
                row['x_employee_device_type'],
                row['x_employee_remote_access_network'],
                row['x_employee_remote_access_tool']
            ]

            count += 1
        
        df.to_csv(
            path,
            encoding="utf-8",
            index=False
        )
    
    return df
         

def find_latest_file(
    data_folder_path
): 
    csv_files = [ f for f in os.listdir(data_folder_path) if os.path.isfile(
        os.path.join(
            data_folder_path,
            f
        )
        ) and f.endswith(".csv") and f.startswith("data_")
    ]
    csv_files.sort()

    if len(csv_files) > 0:
        return csv_files[-1]
    
    return False

def load_odoo_data(
    username,
    password,
    database,
    url,
    app: Flask
):
    static_path = os.path.join(
                    cast(str, app.root_path),
                    cast(str, app.static_folder)
                )
    
    data_folder = os.path.join(
        static_path,
        "data"
    )

    current_time = datetime.now()

    data_exists = True 

    if not os.path.isdir(data_folder):
        os.mkdir(data_folder)
        data_exists = False
    
    data_file_name = "data_" + current_time.strftime(
        '%Y-%m-%dT%H'
    ) + ".csv"

    data_file_path = os.path.join(
        data_folder, data_file_name
    )

    df = None 
    if data_exists is False:
        with app.app_context():
            df = download_odoo_data(
                username,
                password,
                database,
                url,
                data_file_path
            )
    else:
        latest_file = find_latest_file(
            data_folder
        )

        if not latest_file:
            with app.app_context():
                df = download_odoo_data(
                    username,
                    password,
                    database,
                    url,
                    data_file_path
                )
        
        else:
            if app.config["ENV"] != "production":
                return pandas.read_csv(
                    os.path.join(
                        data_folder,
                        latest_file
                    ),
                    encoding="utf-8"
                )

            latest_file_array = latest_file.split("_")
            file_date = datetime.strptime(
                latest_file_array[1].rstrip(".csv"),
                '%Y-%m-%dT%H'
            )

            timeSinceLastRefresh = current_time - file_date
            timeSinceLastRefreshSeconds = abs(
                timeSinceLastRefresh.total_seconds()
            )

            if timeSinceLastRefreshSeconds >= 3600:
                with app.app_context():
                    df = download_odoo_data(
                        username,
                        password,
                        database,
                        url,
                        data_file_path
                    )
            else:
                df = pandas.read_csv(
                    os.path.join(
                        data_folder,
                        latest_file
                    ),
                    encoding="utf-8"
                )
    return df






            

    

    

