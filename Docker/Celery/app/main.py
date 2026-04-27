from celery import Celery

app = Celery(
  'ThunderInsightsBackgroundTasksCelery',
  broker='redis://192.168.3.1:16379/0'
)