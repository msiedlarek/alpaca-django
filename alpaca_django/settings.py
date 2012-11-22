try:
    import cPickle as pickle
except ImportError:
    import pickle

from django.conf import settings

def is_alpaca_enabled():
    return getattr(settings, 'ALPACA_ENABLED', True)

def get_alpaca_project_path_fragment():
    return getattr(settings, 'ALPACA_PROJECT_PATH_FRAGMENT', '')

def get_alpaca_pickling_protocol():
    return getattr(
        settings,
        'ALPACA_PICKLING_PROTOCOL',
        (3 if pickle.HIGHEST_PROTOCOL >= 3 else pickle.HIGHEST_PROTOCOL)
    )

def get_alpaca_connection_timeout():
    return getattr(settings, 'ALPACA_CONNECTION_TIMEOUT', 5)

def get_alpaca_environment():
    try:
        return settings.ALPACA_ENVIRONMENT
    except ValueError:
        raise ValueError("ALPACA_ENVIRONMENT setting is required.")

def get_alpaca_api_key():
    try:
        return settings.ALPACA_API_KEY
    except ValueError:
        raise ValueError("ALPACA_API_KEY setting is required.")

def get_alpaca_endpoint_url():
    try:
        return settings.ALPACA_ENDPOINT_URL
    except ValueError:
        raise ValueError("ALPACA_ENDPOINT_URL setting is required.")

def get_alpaca_ca_bundle():
    return getattr(settings, 'ALPACA_CA_BUNDLE', None)
