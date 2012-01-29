import os,sys
os.environ['ggj12_SETTINGS'] = '/path/to/settings.py'
os.environ['ggj12_DATABASE_URI'] = '/path/to/database.db'
os.environ['ggj12_twilio_account_sid'] = 'fun numbers'
os.environ['ggj12_twilio_auth_token'] = 'fun numbers'
os.environ['ggj12_secret_key'] = 'fun numbers'

sys.path.insert(0,"/path/to/app")
from app import app as application