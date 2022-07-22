import time
from celery import Celery

celery = Celery(__name__)

celery.conf.broker_url = 'redis://localhost:6379/0'
celery.conf.result_backend = 'redis://localhost:6379/0'


@celery.task()
def simple_func():
    a = 5
    b = 5
    time.sleep(20)
    for i in range(1, 10):
        a *= b
        b = a
        print(f"res {a} и {b}")
    time.sleep(20)
    return a, b
