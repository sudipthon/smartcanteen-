from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core", broker="amqp://celery:celery@localhost/celeryvhost")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()



# # for docker


# from __future__ import absolute_import, unicode_literals
# import os
# from celery import Celery

# # Set the default Django settings module for the 'celery' program.
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "canteen.settings")

# app = Celery("canteen", broker="amqp://user:password@rabbitmq:5672/celeryvhost")

# # Using a string here means the worker doesn't have to serialize
# # the configuration object to child processes.
# app.config_from_object("django.conf:settings", namespace="CELERY")

# # Load task modules from all registered Django app configs.
# app.autodiscover_tasks()