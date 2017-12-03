from split_settings.tools import optional, include

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

include(
    'settings_components/application.py',
    'settings_components/database.py',
    'settings_components/special.py',
    'settings_components/production.py',
    optional('settings_components/local.py')
)