alpaca-django
=============

This is a Alpaca reporter for Django-based applications.

See https://github.com/msiedlarek/alpaca

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
                'level': 'WARNING',
                'propagate': False,
            },
        }
    }

    ALPACA_ENDPOINT_URL = 'http://localhost:6543/api/report'
    ALPACA_ENVIRONMENT = 'stage0'
    ALPACA_API_KEY = 'KK8TRdGFQeHs0qgIMo8ONyJuITs5TqxEi6CoHBQ56Zj3CZIomh'
