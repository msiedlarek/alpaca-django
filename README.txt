alpaca-django
=============

This is an Alpaca error logger for Django-based applications.

See https://github.com/msiedlarek/alpaca

Installation
------------

    $ pip install alpaca-django

Example configuration
---------------------

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '%(asctime)s %(levelname)s %(name)s #%(lineno)s: %(message)s',
            },
        },
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'mail_admins': {
                'level': 'ERROR',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler'
            },
            'alpaca': {
                'level': 'ERROR',
                'filters': [],
                'class': 'alpaca_django.log_handler.AlpacaLogHandler',
            },
        },
        'loggers': {
            'django.request': {
                'handlers': ['mail_admins', 'alpaca',],
                'level': 'ERROR',
                'propagate': True,
            },
            'alpaca_django': {
                'handlers': ['mail_admins', 'console',],
                'level': 'DEBUG',
                'propagate': False,
            },
        }
    }

    ALPACA_PROJECT_PATH_FRAGMENT = 'myproject'
    ALPACA_ENVIRONMENT = 'staging'
    ALPACA_MONITOR_HOST = 'monitoring.example.com'

License
-------

Copyright 2013 Mikołaj Siedlarek <msiedlarek@nctz.net>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
