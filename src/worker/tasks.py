from .worker import CelerySingleton
from celery import Celery
from typing import cast



celery_app = cast(Celery, CelerySingleton().get_celery())


@celery_app.task(
    bind = True,
    name = "calculate_diffs"
)
def calculate_diffs(self, *args):
    pass