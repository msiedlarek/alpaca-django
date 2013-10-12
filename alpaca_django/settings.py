from django.conf import settings


def is_alpaca_enabled():
    return getattr(settings, 'ALPACA_ENABLED', True)


def get_alpaca_project_path_fragment():
    return getattr(settings, 'ALPACA_PROJECT_PATH_FRAGMENT', '')


def get_alpaca_environment():
    try:
        return settings.ALPACA_ENVIRONMENT
    except ValueError:
        raise ValueError("ALPACA_ENVIRONMENT setting is required.")


def get_alpaca_monitor_host():
    try:
        return settings.ALPACA_MONITOR_HOST
    except ValueError:
        raise ValueError("ALPACA_MONITOR_HOST setting is required.")


def get_alpaca_monitor_port():
    return getattr(settings, 'ALPACA_MONITOR_PORT', 8195)


def get_alpaca_connection_pool_size():
    return getattr(settings, 'ALPACA_CONNECTION_POOL_SIZE', 3)
