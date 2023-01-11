import os

AD_HOST = os.getenv('AD_HOST', 'zhaw.ch')
AD_USER = os.getenv('AD_USER')
AD_PASS = os.getenv('AD_PASS')
DB_HOST = os.getenv('DB_HOST')
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 100))
BATCH_INTERVAL = int(os.getenv('BATCH_INTERVAL', 180))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'ERROR')
