import json
import os

_settings = {
    "DB_HOST": os.getenv('DB_HOST', 'http://localhost:8080'),
    "AD_HOST": os.getenv('AD_HOST', 'zhaw.ch'),
    "AD_USER": os.getenv('AD_USER'),
    "AD_PASS": os.getenv('AD_PASS'),
    "BATCH_SIZE": int(os.getenv('BATCH_SIZE', 100)),
    "BATCH_INTERVAL": int(os.getenv('BATCH_INTERVAL', 180)),
    "LOG_LEVEL": os.getenv('LOG_LEVEL', ' DEBUG')
}

if os.path.exists('/etc/app/secrets.json'):
    with open('/etc/app/secrets.json') as secrets_file:
        config = json.load(secrets_file)
        for key in config.keys():
            if config[key] is not None:
                _settings[str.upper(key)] = config[key]

AD_HOST = _settings['AD_HOST']
AD_USER = _settings['AD_USER']
AD_PASS = _settings['AD_PASS']
DB_HOST = _settings['DB_HOST']
BATCH_SIZE = _settings['BATCH_SIZE']
BATCH_INTERVAL = _settings['BATCH_INTERVAL']
LOG_LEVEL = _settings['LOG_LEVEL']
