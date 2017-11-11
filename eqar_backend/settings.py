from split_settings.tools import optional, include

include(
    'settings_components/application.py',
    'settings_components/database.py',
    'settings_components/special.py',
    'settings_components/production.py',
    optional('settings_components/local.py')
)