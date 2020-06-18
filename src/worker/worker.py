from celery import Celery, Task
from flask import Flask
from typing import Optional

class CelerySingleton:
    # create a class variable which will hold the celery instance
    celery: Optional[Celery] = None
    def __init__(self, app: Optional[Flask]  = None):
        # if the class variable does not hold an instance currently create a new one with 
        if CelerySingleton.celery is None and app is not None:
            # configure the celery broker 
            CelerySingleton.celery = Celery(
                app.import_name,
                broker = app.config["BROKER_URI"],
                results = app.config["BROKER_URI"]
            )

            # create an inherited class from celety task where the special method __call__
            # is overrided such that the run method is called within the flask application context
            class ContextClass(Task):
                def __call__(self, *args,**kwargs):
                    with app.app_context():
                        return self.run(*args, **kwargs)
            
            # monkeypatch the Task class with the ContextClass defined
            CelerySingleton.celery.Task = ContextClass
    
    # return the current celery instance
    def get_celery(self) -> Optional[Celery]:
        return self.celery