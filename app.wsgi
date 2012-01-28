import os,sys
os.environ['ggj12_SETTINGS'] = '/path/to/settings.py'
os.environ['ggj12_DATABASE_URI'] = '/path/to/database.db'

sys.path.insert(0,"/path/to/app")
from datamemos import app as application