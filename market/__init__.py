from flask import Flask
from google.cloud.sql.connector import Connector
import sqlalchemy
app = Flask(__name__)
app.config['SECRET_KEY'] = '65d7a2d001a0ac6fd0f40f7d'


def connection():
    connector = Connector()
    INSTANCE_CONNECTION_NAME = "flaskmarket:us-central1:sem4project"
    DB_USER = "sqlserver"
    DB_PASS = "Muhammad167"
    DB_NAME = "market"

    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pytds",
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME
    )
    connector.close()
    return conn


pool = sqlalchemy.create_engine(
    "mssql+pytds://localhost",
    creator=connection,
)
from market import routes
