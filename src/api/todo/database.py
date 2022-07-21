import databases
import os
import urllib
from sqlalchemy import create_engine


host_server     = os.environ.get('host_server', 'localhost')
db_server_port  = urllib.parse.quote_plus(str(os.environ.get('db_server_port', '5432')))
database_name   = os.environ.get('database_name', 'fastapi')
db_username     = urllib.parse.quote_plus(str(os.environ.get('db_username', 'postgres')))
db_password     = urllib.parse.quote_plus(str(os.environ.get('db_password', 'docker')))
ssl_mode        = urllib.parse.quote_plus(str(os.environ.get('ssl_mode','prefer')))
DATABASE_URL    = 'postgresql://{}:{}@{}:{}/{}?sslmode={}'.format(db_username,db_password, host_server, db_server_port, database_name, ssl_mode)

database = databases.Database(DATABASE_URL)

engine = create_engine(
    DATABASE_URL, pool_size=3, max_overflow=0
)